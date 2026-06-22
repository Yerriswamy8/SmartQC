from __future__ import annotations
from pathlib import Path
import requests


class APIError(RuntimeError):
    pass


class SmartQCClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
        except requests.RequestException as exc:
            raise APIError(f"Cannot reach SmartQC API at {self.base_url}: {exc}") from exc
        if not response.ok:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text
            raise APIError(f"API {response.status_code}: {detail}")
        if response.status_code == 204:
            return None
        content_type = response.headers.get("content-type", "")
        return response.json() if "json" in content_type else response.content

    @staticmethod
    def rows(payload):
        return payload.get("results", []) if isinstance(payload, dict) and "results" in payload else payload

    def get(self, path, params=None):
        return self._request("GET", path, params=params)

    def post(self, path, data=None, json=None, files=None):
        return self._request("POST", path, data=data, json=json, files=files)

    def delete(self, path, json=None, params=None):
        return self._request("DELETE", path, json=json, params=params)

    def list_machines(self):
        return self.rows(self.get("machines/"))

    def create_machine(self, payload):
        return self.post("machines/", json=payload)

    def list_projects(self):
        return self.rows(self.get("projects/"))

    def create_project(self, payload):
        return self.post("projects/", json=payload)

    def list_inspections(self):
        return self.rows(self.get("inspections/?ordering=-created_at"))

    def create_inspection(self, payload):
        return self.post("inspections/", json=payload)

    def upload_and_inspect(self, inspection_id: int, image_path: str, side: str = "surface"):
        path = Path(image_path)
        with path.open("rb") as stream:
            return self.post(
                "upload-image/",
                data={"inspection_id": str(inspection_id), "side": side},
                files={"image": (path.name, stream, "application/octet-stream")},
            )
