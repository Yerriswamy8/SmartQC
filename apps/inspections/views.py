from rest_framework import viewsets
from .models import Inspection, InspectionImage, Detection, Annotation, OperatorHeartbeat
from .serializers import (
    InspectionSerializer,
    InspectionDetailSerializer,
    InspectionImageSerializer,
    DetectionSerializer,
    AnnotationSerializer,
    OperatorHeartbeatSerializer,
)


class InspectionViewSet(viewsets.ModelViewSet):
    queryset = Inspection.objects.select_related("machine", "project", "recipe").prefetch_related("images__detections").all()
    serializer_class = InspectionSerializer
    search_fields = ["serial_number", "operator_name", "machine__code", "project__code"]
    ordering_fields = ["created_at", "status", "decision", "cycle_time_ms", "defect_count"]

    def get_serializer_class(self):
        return InspectionDetailSerializer if self.action == "retrieve" else InspectionSerializer


class InspectionImageViewSet(viewsets.ModelViewSet):
    queryset = InspectionImage.objects.select_related("inspection").prefetch_related("detections", "annotations").all()
    serializer_class = InspectionImageSerializer
    search_fields = ["side", "source", "inspection__serial_number"]
    ordering_fields = ["created_at", "side"]


class DetectionViewSet(viewsets.ModelViewSet):
    queryset = Detection.objects.select_related("image", "image__inspection").all()
    serializer_class = DetectionSerializer
    search_fields = ["label", "image__inspection__serial_number"]
    ordering_fields = ["confidence", "area_px", "created_at"]


class AnnotationViewSet(viewsets.ModelViewSet):
    queryset = Annotation.objects.select_related("image", "image__inspection").all()
    serializer_class = AnnotationSerializer
    search_fields = ["label", "created_by", "image__inspection__serial_number"]
    ordering_fields = ["created_at", "label"]


class OperatorHeartbeatViewSet(viewsets.ModelViewSet):
    queryset = OperatorHeartbeat.objects.select_related("machine").all()
    serializer_class = OperatorHeartbeatSerializer
    search_fields = ["operator_name", "machine__code", "state"]
    ordering_fields = ["last_seen", "operator_name", "state"]
