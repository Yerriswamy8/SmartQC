from pathlib import Path
from services.storage import LocalStorageAdapter


def test_local_storage_round_trip(tmp_path: Path):
    adapter = LocalStorageAdapter(tmp_path)
    adapter.upload("demo/a.txt", b"hello", "text/plain")
    data, mime = adapter.download("demo/a.txt")
    assert data == b"hello"
    assert adapter.list("demo")[0].key == "demo/a.txt"
    adapter.delete("demo/a.txt")
    assert adapter.list("demo") == []
