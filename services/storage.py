from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import mimetypes
import boto3
from django.conf import settings


def safe_key(value: str) -> str:
    value = value.replace("\\", "/").lstrip("/")
    path = PurePosixPath(value)
    if not value or ".." in path.parts:
        raise ValueError("Invalid storage key")
    return str(path)


@dataclass
class StoredObject:
    key: str
    size: int
    last_modified: str | None = None


class LocalStorageAdapter:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        key = safe_key(key)
        path = (self.root / key).resolve()
        if self.root not in path.parents and path != self.root:
            raise ValueError("Storage key escapes configured root")
        return path

    def upload(self, key: str, data: bytes, content_type: str | None = None) -> StoredObject:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return StoredObject(key=safe_key(key), size=len(data))

    def download(self, key: str) -> tuple[bytes, str]:
        path = self._path(key)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(key)
        return path.read_bytes(), mimetypes.guess_type(path.name)[0] or "application/octet-stream"

    def list(self, prefix: str = "") -> list[StoredObject]:
        prefix = prefix.replace("\\", "/").lstrip("/")
        base = self._path(prefix) if prefix else self.root
        if base.is_file():
            return [StoredObject(key=base.relative_to(self.root).as_posix(), size=base.stat().st_size)]
        if not base.exists():
            return []
        return [
            StoredObject(key=p.relative_to(self.root).as_posix(), size=p.stat().st_size)
            for p in sorted(base.rglob("*")) if p.is_file()
        ]

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()


class S3StorageAdapter:
    def __init__(self):
        if not settings.AWS_S3_BUCKET:
            raise RuntimeError("AWS_S3_BUCKET is required when STORAGE_BACKEND=s3")
        kwargs = {"region_name": settings.AWS_REGION}
        if settings.AWS_ENDPOINT_URL:
            kwargs["endpoint_url"] = settings.AWS_ENDPOINT_URL
        if settings.AWS_ACCESS_KEY_ID:
            kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
        self.client = boto3.client("s3", **kwargs)
        self.bucket = settings.AWS_S3_BUCKET

    def upload(self, key: str, data: bytes, content_type: str | None = None) -> StoredObject:
        key = safe_key(key)
        extra = {"ContentType": content_type} if content_type else {}
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, **extra)
        return StoredObject(key=key, size=len(data))

    def download(self, key: str) -> tuple[bytes, str]:
        key = safe_key(key)
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read(), response.get("ContentType") or "application/octet-stream"

    def list(self, prefix: str = "") -> list[StoredObject]:
        prefix = prefix.replace("\\", "/").lstrip("/")
        paginator = self.client.get_paginator("list_objects_v2")
        output = []
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for item in page.get("Contents", []):
                output.append(StoredObject(key=item["Key"], size=item["Size"], last_modified=item["LastModified"].isoformat()))
        return output

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=safe_key(key))


def get_storage_adapter():
    return S3StorageAdapter() if settings.STORAGE_BACKEND == "s3" else LocalStorageAdapter(settings.LOCAL_STORAGE_ROOT)
