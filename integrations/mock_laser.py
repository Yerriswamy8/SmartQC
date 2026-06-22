from __future__ import annotations
import math
import random


class MockLaserProfiler:
    def scan(self, points: int = 256) -> list[dict]:
        profile = []
        for index in range(points):
            x = index * 0.25
            z = 8.0 * math.sin(index / 24.0) + random.uniform(-0.35, 0.35)
            profile.append({"x_mm": round(x, 3), "z_mm": round(z, 3)})
        return profile
