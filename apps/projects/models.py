from django.conf import settings
from django.db import models


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        ARCHIVED = "ARCHIVED", "Archived"

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Recipe(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="recipes")
    name = models.CharField(max_length=150)
    version = models.CharField(max_length=30, default="1.0.0")
    configuration = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["project", "name", "version"], name="unique_recipe_version")]
        ordering = ["project", "name", "-created_at"]

    def __str__(self):
        return f"{self.project.code}/{self.name}:{self.version}"


class AIModel(models.Model):
    class Framework(models.TextChoices):
        OPENCV = "OPENCV", "OpenCV"
        YOLO = "YOLO", "Ultralytics YOLO"
        PYTORCH = "PYTORCH", "PyTorch"
        ONNX = "ONNX", "ONNX Runtime"

    class Status(models.TextChoices):
        VALIDATING = "VALIDATING", "Validating"
        READY = "READY", "Ready"
        RETIRED = "RETIRED", "Retired"
        FAILED = "FAILED", "Failed"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="models")
    name = models.CharField(max_length=150)
    version = models.CharField(max_length=30)
    framework = models.CharField(max_length=20, choices=Framework.choices, default=Framework.OPENCV)
    model_type = models.CharField(max_length=80, default="object_detection")
    file_url = models.CharField(max_length=500, blank=True)
    checksum = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.READY)
    metrics = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["project", "name", "version"], name="unique_model_version")]
        ordering = ["project", "name", "-created_at"]

    def __str__(self):
        return f"{self.name}:{self.version}"
