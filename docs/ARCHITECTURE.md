# Architecture

```text
PyQt Desktop Client
        |
        | HTTP/JSON + multipart upload
        v
Django REST Framework API
  |        |          |           |
Machines Projects  Inspections  Operator Monitoring
  |                   |
Mock PLC/Camera/Laser |--> AI inference service
                      |      |- OpenCV demo detector
                      |      `- Optional YOLO adapter
                      |
                      `--> Storage adapter
                             |- Local filesystem (default)
                             `- AWS S3 / MinIO compatible

Database: SQLite by default; MySQL supported through environment variables.
```

The demo deliberately separates interfaces from production implementations. Real PLC, camera, laser, model and customer-specific code must live in private adapters outside this public repository.
