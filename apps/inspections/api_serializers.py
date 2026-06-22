from rest_framework import serializers


class UploadAndInspectRequestSerializer(serializers.Serializer):
    inspection_id = serializers.IntegerField()
    image = serializers.ImageField()
    side = serializers.CharField(required=False, default="surface")
    source = serializers.CharField(required=False, default="UPLOAD")


class StandaloneInferenceRequestSerializer(serializers.Serializer):
    image = serializers.ImageField()


class StorageObjectSerializer(serializers.Serializer):
    key = serializers.CharField()
    size = serializers.IntegerField()
    last_modified = serializers.CharField(required=False, allow_null=True)


class StorageUploadRequestSerializer(serializers.Serializer):
    key = serializers.CharField()
    file = serializers.FileField()


class StorageDeleteRequestSerializer(serializers.Serializer):
    key = serializers.CharField()


class PLCWriteRequestSerializer(serializers.Serializer):
    tag = serializers.CharField()
    value = serializers.JSONField()
