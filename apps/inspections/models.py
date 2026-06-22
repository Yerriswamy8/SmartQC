from pathlib import Path
from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.machines.models import Machine
from apps.projects.models import Project, Recipe


def inspection_upload_path(instance, filename):
    safe_name = Path(filename).name
    return f"inspections/{instance.inspection_id}/{safe_name}"


class Inspection(models.Model):
    class Status(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        RUNNING = "RUNNING", "Running"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    class Decision(models.TextChoices):
        UNKNOWN = "UNKNOWN", "Unknown"
        GOOD = "GOOD", "Good"
        DEFECT = "DEFECT", "Defect"

    machine = models.ForeignKey(Machine, on_delete=models.PROTECT, related_name="inspections")
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="inspections")
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True, related_name="inspections")
    serial_number = models.CharField(max_length=120, db_index=True)
    operator_name = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    decision = models.CharField(max_length=20, choices=Decision.choices, default=Decision.UNKNOWN)
    defect_count = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    cycle_time_ms = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Inspection {self.id} - {self.serial_number}"


class InspectionImage(models.Model):
    class Source(models.TextChoices):
        UPLOAD = "UPLOAD", "Upload"
        MOCK_CAMERA = "MOCK_CAMERA", "Mock Camera"
        API = "API", "API"

    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=inspection_upload_path)
    storage_key = models.CharField(max_length=500, blank=True)
    source = models.CharField(max_length=30, choices=Source.choices, default=Source.UPLOAD)
    side = models.CharField(max_length=60, default="surface")
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Image {self.id} for inspection {self.inspection_id}"


class Detection(models.Model):
    image = models.ForeignKey(InspectionImage, on_delete=models.CASCADE, related_name="detections")
    label = models.CharField(max_length=100)
    confidence = models.FloatField(default=0.0)
    x1 = models.FloatField()
    y1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()
    area_px = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-confidence"]

    def __str__(self):
        return f"{self.label} ({self.confidence:.2f})"


class Annotation(models.Model):
    image = models.ForeignKey(InspectionImage, on_delete=models.CASCADE, related_name="annotations")
    label = models.CharField(max_length=100)
    x1 = models.FloatField()
    y1 = models.FloatField()
    x2 = models.FloatField()
    y2 = models.FloatField()
    created_by = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.label} annotation on image {self.image_id}"


class OperatorHeartbeat(models.Model):
    class State(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        BREAK = "BREAK", "Break"
        OFFLINE = "OFFLINE", "Offline"

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="operator_heartbeats")
    operator_name = models.CharField(max_length=120)
    state = models.CharField(max_length=20, choices=State.choices, default=State.ACTIVE)
    message = models.CharField(max_length=300, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-last_seen"]

    def __str__(self):
        return f"{self.operator_name} - {self.state}"
