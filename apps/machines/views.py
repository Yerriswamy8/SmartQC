from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import Machine, Camera, Laser, DeviceEvent
from .serializers import MachineSerializer, CameraSerializer, LaserSerializer, DeviceEventSerializer


class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer
    search_fields = ["name", "code", "location"]
    ordering_fields = ["name", "code", "status", "created_at"]

    def _set_status(self, request, status):
        machine = self.get_object()
        machine.status = status
        machine.save(update_fields=["status", "updated_at"])
        DeviceEvent.objects.create(
            machine=machine,
            device_type="PLC",
            severity=DeviceEvent.Severity.INFO,
            message=f"Machine status changed to {status} by demo API.",
            metadata={"at": timezone.now().isoformat()},
        )
        return Response(self.get_serializer(machine).data)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        return self._set_status(request, Machine.Status.RUNNING)

    @action(detail=True, methods=["post"])
    def stop(self, request, pk=None):
        return self._set_status(request, Machine.Status.IDLE)

    @action(detail=True, methods=["post"], url_path="simulate-error")
    def simulate_error(self, request, pk=None):
        return self._set_status(request, Machine.Status.ERROR)


class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.select_related("machine").all()
    serializer_class = CameraSerializer
    search_fields = ["name", "serial_number", "station", "machine__code"]
    ordering_fields = ["name", "status", "created_at"]


class LaserViewSet(viewsets.ModelViewSet):
    queryset = Laser.objects.select_related("machine").all()
    serializer_class = LaserSerializer
    search_fields = ["name", "serial_number", "machine__code"]
    ordering_fields = ["name", "status", "created_at"]


class DeviceEventViewSet(viewsets.ModelViewSet):
    queryset = DeviceEvent.objects.select_related("machine").all()
    serializer_class = DeviceEventSerializer
    search_fields = ["message", "device_type", "machine__code"]
    ordering_fields = ["created_at", "severity"]
