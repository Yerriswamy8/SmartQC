from __future__ import annotations
import cv2
import numpy as np
from datetime import datetime


class MockIndustrialCamera:
    def capture(self, width: int = 1024, height: int = 512, add_defects: bool = True) -> bytes:
        image = np.full((height, width, 3), 185, dtype=np.uint8)
        cv2.rectangle(image, (40, 60), (width - 40, height - 60), (135, 135, 135), -1)
        for x in range(70, width - 70, 90):
            cv2.line(image, (x, 80), (x + 35, height - 80), (155, 155, 155), 3)
        if add_defects:
            cv2.ellipse(image, (width // 3, height // 2), (28, 15), 15, 0, 360, (0, 0, 230), -1)
            cv2.rectangle(image, (int(width * 0.68), int(height * 0.30)), (int(width * 0.74), int(height * 0.39)), (0, 0, 230), -1)
        cv2.putText(image, "SMARTQC DEMO - SYNTHETIC IMAGE", (55, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (35, 35, 35), 2)
        cv2.putText(image, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (55, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (35, 35, 35), 1)
        ok, encoded = cv2.imencode(".png", image)
        if not ok:
            raise RuntimeError("Failed to encode synthetic camera image")
        return encoded.tobytes()
