from __future__ import annotations
import time
from pathlib import Path
from uuid import uuid4
import cv2
from django.conf import settings
from django.db.models import Count, Avg
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiTypes

from apps.machines.models import Machine
from .models import Inspection, InspectionImage, Detection
from .serializers import InspectionDetailSerializer
from .api_serializers import (
    UploadAndInspectRequestSerializer, StandaloneInferenceRequestSerializer,
    StorageObjectSerializer, StorageUploadRequestSerializer, StorageDeleteRequestSerializer,
    PLCWriteRequestSerializer,
)
from services.inference import InferenceService
from services.storage import get_storage_adapter
from integrations.mock_camera import MockIndustrialCamera
from integrations.mock_laser import MockLaserProfiler
from integrations.mock_plc import MockPLC


class HealthAPIView(APIView):
    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        return Response({
            "status": "ok",
            "service": "SmartQC Demo API",
            "time": timezone.now().isoformat(),
            "ai_backend": settings.AI_BACKEND,
            "storage_backend": settings.STORAGE_BACKEND,
            "hardware_mode": "mock",
        })


class DashboardStatsAPIView(APIView):
    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        inspections = Inspection.objects.all()
        recent = inspections.select_related("machine", "project")[:10]
        decision_counts = {row["decision"]: row["count"] for row in inspections.values("decision").annotate(count=Count("id"))}
        status_counts = {row["status"]: row["count"] for row in inspections.values("status").annotate(count=Count("id"))}
        avg_cycle = inspections.aggregate(value=Avg("cycle_time_ms"))["value"] or 0
        return Response({
            "machines": Machine.objects.count(),
            "machines_running": Machine.objects.filter(status=Machine.Status.RUNNING).count(),
            "total_inspections": inspections.count(),
            "good": decision_counts.get(Inspection.Decision.GOOD, 0),
            "defect": decision_counts.get(Inspection.Decision.DEFECT, 0),
            "unknown": decision_counts.get(Inspection.Decision.UNKNOWN, 0),
            "status_counts": status_counts,
            "average_cycle_time_ms": round(avg_cycle, 2),
            "recent_inspections": [
                {
                    "id": item.id,
                    "serial_number": item.serial_number,
                    "machine": item.machine.code,
                    "project": item.project.code,
                    "decision": item.decision,
                    "defect_count": item.defect_count,
                    "created_at": item.created_at,
                }
                for item in recent
            ],
        })


class UploadAndInspectAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(request=UploadAndInspectRequestSerializer, responses={201: InspectionDetailSerializer})
    def post(self, request):
        upload = request.FILES.get("image")
        inspection_id = request.data.get("inspection_id")
        if not upload or not inspection_id:
            return Response({"detail": "image and inspection_id are required"}, status=status.HTTP_400_BAD_REQUEST)
        if upload.size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            return Response({"detail": "image exceeds configured upload limit"}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        try:
            inspection = Inspection.objects.get(pk=inspection_id)
        except Inspection.DoesNotExist:
            return Response({"detail": "inspection not found"}, status=status.HTTP_404_NOT_FOUND)

        started = time.perf_counter()
        payload = upload.read()
        try:
            image, results = InferenceService().infer_bytes(payload)
        except (ValueError, RuntimeError, FileNotFoundError) as exc:
            inspection.status = Inspection.Status.FAILED
            inspection.notes = str(exc)
            inspection.save(update_fields=["status", "notes"])
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        upload.seek(0)
        h, w = image.shape[:2]
        record = InspectionImage.objects.create(
            inspection=inspection,
            image=upload,
            source=request.data.get("source", InspectionImage.Source.UPLOAD),
            side=request.data.get("side", "surface"),
            width=w,
            height=h,
        )
        storage_key = f"inspection-images/{inspection.id}/{uuid4().hex}_{Path(upload.name).name}"
        try:
            stored = get_storage_adapter().upload(storage_key, payload, upload.content_type)
            record.storage_key = stored.key
            record.save(update_fields=["storage_key"])
        except Exception as exc:
            record.storage_key = ""
            record.save(update_fields=["storage_key"])
            inspection.metadata = {**inspection.metadata, "storage_warning": str(exc)}

        Detection.objects.bulk_create([
            Detection(
                image=record, label=item.label, confidence=item.confidence,
                x1=item.x1, y1=item.y1, x2=item.x2, y2=item.y2,
                area_px=item.area_px, metadata=item.metadata,
            ) for item in results
        ])
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        inspection.status = Inspection.Status.COMPLETED
        inspection.decision = Inspection.Decision.DEFECT if results else Inspection.Decision.GOOD
        inspection.defect_count = len(results)
        inspection.completed_at = timezone.now()
        inspection.cycle_time_ms = elapsed_ms
        inspection.save(update_fields=["status", "decision", "defect_count", "completed_at", "cycle_time_ms", "metadata"])
        return Response(InspectionDetailSerializer(inspection, context={"request": request}).data, status=status.HTTP_201_CREATED)


class StandaloneInferenceAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(request=StandaloneInferenceRequestSerializer, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        upload = request.FILES.get("image")
        if not upload:
            return Response({"detail": "image is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            image, results = InferenceService().infer_bytes(upload.read())
        except (ValueError, RuntimeError, FileNotFoundError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        h, w = image.shape[:2]
        return Response({"width": w, "height": h, "decision": "DEFECT" if results else "GOOD", "detections": [x.as_dict() for x in results]})


class StorageAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(responses=StorageObjectSerializer(many=True))
    def get(self, request):
        prefix = request.query_params.get("prefix", "")
        try:
            objects = get_storage_adapter().list(prefix)
            return Response([obj.__dict__ for obj in objects])
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=StorageUploadRequestSerializer, responses={201: StorageObjectSerializer})
    def post(self, request):
        upload = request.FILES.get("file")
        key = request.data.get("key")
        if not upload or not key:
            return Response({"detail": "file and key are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = get_storage_adapter().upload(key, upload.read(), upload.content_type)
            return Response(obj.__dict__, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=StorageDeleteRequestSerializer, responses={204: None})
    def delete(self, request):
        key = request.data.get("key") or request.query_params.get("key")
        if not key:
            return Response({"detail": "key is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            get_storage_adapter().delete(key)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class StorageDownloadAPIView(APIView):
    @extend_schema(responses=OpenApiTypes.BINARY)
    def get(self, request):
        key = request.query_params.get("key")
        if not key:
            return Response({"detail": "key is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data, content_type = get_storage_adapter().download(key)
            response = HttpResponse(data, content_type=content_type)
            response["Content-Disposition"] = f'attachment; filename="{Path(key).name}"'
            return response
        except FileNotFoundError:
            return Response({"detail": "object not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class MockCameraCaptureAPIView(APIView):
    @extend_schema(responses=OpenApiTypes.BINARY)
    def get(self, request):
        add_defects = request.query_params.get("defects", "true").lower() == "true"
        payload = MockIndustrialCamera().capture(add_defects=add_defects)
        return HttpResponse(payload, content_type="image/png")


class MockLaserProfileAPIView(APIView):
    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        points = min(2000, max(16, int(request.query_params.get("points", 256))))
        return Response({"units": "mm", "points": MockLaserProfiler().scan(points)})


class MockPLCAPIView(APIView):
    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request):
        tag = request.query_params.get("tag")
        try:
            return Response({"tag": tag, "value": MockPLC.read(tag)}) if tag else Response(MockPLC.snapshot())
        except KeyError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(request=PLCWriteRequestSerializer, responses=OpenApiTypes.OBJECT)
    def post(self, request):
        tag = request.data.get("tag")
        if not tag or "value" not in request.data:
            return Response({"detail": "tag and value are required"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"tag": tag, "value": MockPLC.write(tag, request.data["value"])})
