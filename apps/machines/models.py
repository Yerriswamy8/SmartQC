from django.db import models


class Machine(models.Model):
    class Status(models.TextChoices):
        IDLE = "IDLE", "Idle"
        RUNNING = "RUNNING", "Running"
        ERROR = "ERROR", "Error"
        OFFLINE = "OFFLINE", "Offline"

    class PLCMode(models.TextChoices):
        MOCK = "MOCK", "Mock"
        SOFTWARE = "SOFTWARE", "Software Trigger"
        HARDWARE = "HARDWARE", "Hardware Trigger"

    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50, unique=True)
    location = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IDLE)
    plc_mode = models.CharField(max_length=20, choices=PLCMode.choices, default=PLCMode.MOCK)
    is_active = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Camera(models.Model):
    class Status(models.TextChoices):
        READY = "READY", "Ready"
        CAPTURING = "CAPTURING", "Capturing"
        ERROR = "ERROR", "Error"
        OFFLINE = "OFFLINE", "Offline"

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="cameras")
    name = models.CharField(max_length=120)
    serial_number = models.CharField(max_length=100, unique=True)
    station = models.CharField(max_length=80, default="Inspection Station")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.READY)
    exposure_us = models.PositiveIntegerField(default=2500)
    mock_enabled = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["machine", "name"]

    def __str__(self):
        return f"{self.name} ({self.serial_number})"


class Laser(models.Model):
    class Status(models.TextChoices):
        READY = "READY", "Ready"
        SCANNING = "SCANNING", "Scanning"
        ERROR = "ERROR", "Error"
        OFFLINE = "OFFLINE", "Offline"

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="lasers")
    name = models.CharField(max_length=120)
    serial_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.READY)
    mock_enabled = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["machine", "name"]

    def __str__(self):
        return f"{self.name} ({self.serial_number})"


class DeviceEvent(models.Model):
    class Severity(models.TextChoices):
        INFO = "INFO", "Info"
        WARNING = "WARNING", "Warning"
        ERROR = "ERROR", "Error"

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="events")
    device_type = models.CharField(max_length=30, default="SYSTEM")
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.INFO)
    message = models.CharField(max_length=500)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.severity}: {self.message[:60]}"
