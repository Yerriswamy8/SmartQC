from __future__ import annotations
from threading import Lock


class MockPLC:
    _tags = {"cycle_start": False, "machine_ready": True, "inspection_complete": False, "result_good": False}
    _lock = Lock()

    @classmethod
    def read(cls, tag: str):
        with cls._lock:
            if tag not in cls._tags:
                raise KeyError(f"Unknown demo PLC tag: {tag}")
            return cls._tags[tag]

    @classmethod
    def write(cls, tag: str, value):
        with cls._lock:
            cls._tags[tag] = value
            return cls._tags[tag]

    @classmethod
    def snapshot(cls):
        with cls._lock:
            return dict(cls._tags)
