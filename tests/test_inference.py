import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartqc_demo.settings")
import django
django.setup()
from integrations.mock_camera import MockIndustrialCamera
from services.inference import InferenceService


def test_mock_image_has_demo_detections():
    payload = MockIndustrialCamera().capture(add_defects=True)
    image, detections = InferenceService().infer_bytes(payload)
    assert image.shape[0] > 0
    assert len(detections) >= 1
    assert all(item.x2 > item.x1 and item.y2 > item.y1 for item in detections)
