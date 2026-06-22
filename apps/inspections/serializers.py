from rest_framework import serializers
from .models import Inspection, InspectionImage, Detection, Annotation, OperatorHeartbeat


class DetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detection
        fields = "__all__"


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = "__all__"


class InspectionImageSerializer(serializers.ModelSerializer):
    detections = DetectionSerializer(many=True, read_only=True)
    annotations = AnnotationSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = InspectionImage
        fields = "__all__"

    def get_image_url(self, obj) -> str | None:
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class InspectionSerializer(serializers.ModelSerializer):
    machine_code = serializers.CharField(source="machine.code", read_only=True)
    project_code = serializers.CharField(source="project.code", read_only=True)
    image_count = serializers.IntegerField(source="images.count", read_only=True)

    class Meta:
        model = Inspection
        fields = "__all__"


class InspectionDetailSerializer(InspectionSerializer):
    images = InspectionImageSerializer(many=True, read_only=True)


class OperatorHeartbeatSerializer(serializers.ModelSerializer):
    machine_code = serializers.CharField(source="machine.code", read_only=True)

    class Meta:
        model = OperatorHeartbeat
        fields = "__all__"
