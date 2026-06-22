from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
import cv2
import numpy as np
from django.conf import settings


@dataclass
class DetectionResult:
    label: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float
    area_px: float
    metadata: dict

    def as_dict(self):
        return asdict(self)


class OpenCVDemoDetector:
    """Detects red demo markers and strong dark anomalies on a neutral surface."""

    def __init__(self, min_area: int = 80):
        self.min_area = min_area

    @staticmethod
    def _boxes_from_mask(mask: np.ndarray, label: str, image_area: int) -> list[DetectionResult]:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        results = []
        for contour in contours:
            area = float(cv2.contourArea(contour))
            if area < 80 or area > image_area * 0.35:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            fill_ratio = min(1.0, area / max(1.0, w * h))
            confidence = min(0.99, 0.55 + 0.35 * fill_ratio + 0.10 * min(1.0, area / 3000.0))
            results.append(
                DetectionResult(
                    label=label,
                    confidence=round(confidence, 4),
                    x1=float(x), y1=float(y), x2=float(x + w), y2=float(y + h),
                    area_px=round(area, 2),
                    metadata={"backend": "opencv", "fill_ratio": round(fill_ratio, 4)},
                )
            )
        return results

    def predict(self, image: np.ndarray) -> list[DetectionResult]:
        if image is None or image.size == 0:
            raise ValueError("Empty image supplied to inference service")
        h, w = image.shape[:2]
        image_area = h * w
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        red1 = cv2.inRange(hsv, np.array([0, 90, 60]), np.array([12, 255, 255]))
        red2 = cv2.inRange(hsv, np.array([168, 90, 60]), np.array([180, 255, 255]))
        red_mask = cv2.bitwise_or(red1, red2)
        kernel = np.ones((5, 5), np.uint8)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        results = self._boxes_from_mask(red_mask, "demo_surface_defect", image_area)

        if not results:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (7, 7), 0)
            threshold = max(15, int(np.percentile(blurred, 8)))
            dark_mask = cv2.inRange(blurred, 0, threshold)
            dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
            dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            results = self._boxes_from_mask(dark_mask, "dark_anomaly", image_area)
        return sorted(results, key=lambda item: item.confidence, reverse=True)


class YOLODetector:
    def __init__(self, model_path: str, confidence: float):
        if not model_path or not Path(model_path).exists():
            raise FileNotFoundError("YOLO_MODEL_PATH does not exist")
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError("Install requirements-ai.txt to enable YOLO") from exc
        self.model = YOLO(model_path)
        self.confidence = confidence

    def predict(self, image: np.ndarray) -> list[DetectionResult]:
        prediction = self.model.predict(source=image, conf=self.confidence, verbose=False)[0]
        names = prediction.names
        output = []
        if prediction.boxes is None:
            return output
        for box in prediction.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            output.append(
                DetectionResult(
                    label=str(names[class_id]), confidence=round(confidence, 4),
                    x1=x1, y1=y1, x2=x2, y2=y2,
                    area_px=max(0.0, (x2 - x1) * (y2 - y1)),
                    metadata={"backend": "yolo", "class_id": class_id},
                )
            )
        return output


class InferenceService:
    def __init__(self):
        if settings.AI_BACKEND == "yolo":
            self.detector = YOLODetector(settings.YOLO_MODEL_PATH, settings.AI_CONFIDENCE_THRESHOLD)
        else:
            self.detector = OpenCVDemoDetector()

    def infer_bytes(self, payload: bytes) -> tuple[np.ndarray, list[DetectionResult]]:
        array = np.frombuffer(payload, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Uploaded file is not a readable image")
        return image, self.detector.predict(image)
