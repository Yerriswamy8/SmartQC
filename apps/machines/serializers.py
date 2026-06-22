from rest_framework import serializers
from .models import Machine, Camera, Laser, DeviceEvent


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = "__all__"


class LaserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laser
        fields = "__all__"


class MachineSerializer(serializers.ModelSerializer):
    camera_count = serializers.IntegerField(source="cameras.count", read_only=True)
    laser_count = serializers.IntegerField(source="lasers.count", read_only=True)

    class Meta:
        model = Machine
        fields = "__all__"


class DeviceEventSerializer(serializers.ModelSerializer):
    machine_code = serializers.CharField(source="machine.code", read_only=True)

    class Meta:
        model = DeviceEvent
        fields = "__all__"
