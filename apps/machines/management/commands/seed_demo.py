from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone

from apps.machines.models import Machine, Camera, Laser, DeviceEvent
from apps.projects.models import Project, Recipe, AIModel
from apps.inspections.models import Inspection, InspectionImage, Detection
from integrations.mock_camera import MockIndustrialCamera
from services.inference import InferenceService


class Command(BaseCommand):
    help = "Create non-sensitive sample records and a synthetic inspection image."

    def handle(self, *args, **options):
        machine, _ = Machine.objects.get_or_create(
            code="DEMO-LINE-01",
            defaults={"name": "Demo Inspection Line", "location": "Simulation Lab", "status": Machine.Status.IDLE},
        )
        Camera.objects.get_or_create(machine=machine, serial_number="MOCK-CAM-001", defaults={"name": "Mock Area Camera"})
        Laser.objects.get_or_create(machine=machine, serial_number="MOCK-LASER-001", defaults={"name": "Mock Laser Profiler"})
        project, _ = Project.objects.get_or_create(
            code="DEMO-TYRE-QC",
            defaults={"name": "Demo Surface Inspection", "description": "Synthetic portfolio project", "status": Project.Status.ACTIVE},
        )
        recipe, _ = Recipe.objects.get_or_create(
            project=project, name="Default Demo Recipe", version="1.0.0",
            defaults={"configuration": {"camera": "MOCK-CAM-001", "threshold": 0.35, "sides": ["surface"]}},
        )
        AIModel.objects.get_or_create(
            project=project, name="OpenCV Demo Detector", version="1.0.0",
            defaults={"framework": AIModel.Framework.OPENCV, "status": AIModel.Status.READY, "metrics": {"note": "Synthetic demo only"}},
        )
        if not Inspection.objects.filter(serial_number="DEMO-0001").exists():
            inspection = Inspection.objects.create(
                machine=machine, project=project, recipe=recipe, serial_number="DEMO-0001",
                operator_name="Demo Operator", status=Inspection.Status.RUNNING,
            )
            payload = MockIndustrialCamera().capture(add_defects=True)
            image, results = InferenceService().infer_bytes(payload)
            h, w = image.shape[:2]
            image_record = InspectionImage.objects.create(
                inspection=inspection,
                image=ContentFile(payload, name="synthetic_demo_inspection.png"),
                source=InspectionImage.Source.MOCK_CAMERA,
                side="surface", width=w, height=h,
            )
            Detection.objects.bulk_create([
                Detection(image=image_record, label=x.label, confidence=x.confidence, x1=x.x1, y1=x.y1, x2=x.x2, y2=x.y2, area_px=x.area_px, metadata=x.metadata)
                for x in results
            ])
            inspection.status = Inspection.Status.COMPLETED
            inspection.decision = Inspection.Decision.DEFECT if results else Inspection.Decision.GOOD
            inspection.defect_count = len(results)
            inspection.completed_at = timezone.now()
            inspection.cycle_time_ms = 120
            inspection.save()
        DeviceEvent.objects.get_or_create(
            machine=machine, message="Demo environment initialized.", defaults={"device_type": "SYSTEM", "severity": DeviceEvent.Severity.INFO}
        )
        self.stdout.write(self.style.SUCCESS("SmartQC demo data is ready."))
