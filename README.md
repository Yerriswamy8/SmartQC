# SmartQC-Demo

A public, portfolio-safe industrial quality inspection platform built with **PyQt5**, **Django REST Framework**, **OpenCV**, optional **YOLO**, **MySQL/SQLite**, and **AWS S3-compatible storage**.

This repository is a clean-room demo. It contains no employer code, company branding, customer data, production PLC addresses, licensed camera/laser SDKs, credentials, recipes, trained weights or inspection images.

## Included modules

- Industrial PyQt desktop application
- Dashboard and operator monitoring
- Machine, camera and laser management
- Project, recipe and AI model management
- Inspection lifecycle and result history
- Image upload and AI inference workflow
- Manual rectangle annotation tool
- Mock PLC, camera and laser integrations
- OpenCV demo detector and optional YOLO adapter
- Local storage and AWS S3/MinIO adapter
- SQLite default and MySQL configuration
- Swagger/OpenAPI documentation with 36 paths and 87 HTTP operations
- Seed data, synthetic sample image and tests

## Project structure

```text
SmartQC-Demo/
├── apps/
│   ├── machines/          # Machine, camera, laser and device events
│   ├── projects/          # Projects, recipes and AI model registry
│   └── inspections/       # Inspection, images, detections, annotations, operators
├── desktop/
│   ├── pages/             # PyQt pages
│   ├── api_client.py
│   └── main.py
├── integrations/          # Mock PLC, camera and laser adapters
├── services/              # Inference and storage adapters
├── smartqc_demo/          # Django settings and URLs
├── scripts/               # Windows/Linux run scripts
├── sample_data/           # Synthetic inspection sample
├── docs/                  # Architecture, API and public-release guidance
├── tests/
├── manage.py
└── requirements.txt
```

## Quick start on Windows

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

Open a second terminal:

```bat
.venv\Scripts\activate
python -m desktop.main
```

Swagger UI: `http://127.0.0.1:8000/api/docs/

Opening `http://127.0.0.1:8000/` redirects to the Swagger API documentation.`

Django admin can be enabled with:

```bat
python manage.py createsuperuser
```

## Quick start on Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

Then run `python -m desktop.main` in a second terminal.

## Demo inspection flow

```text
Create/select machine and project
             ↓
Create inspection record
             ↓
Upload image from PyQt or REST API
             ↓
OpenCV demo detector or optional YOLO
             ↓
Store image and detection records
             ↓
Save to local storage or S3
             ↓
Show decision, boxes and dashboard statistics
```

The included synthetic image uses red regions as artificial defects. This makes the demo deterministic without exposing a real dataset or model.

## Enable optional YOLO

```bash
pip install -r requirements-ai.txt
```

Update `.env`:

```env
AI_BACKEND=yolo
YOLO_MODEL_PATH=C:/path/to/your/public-demo-model.pt
```

Do not commit the weight file unless you own it and its license permits redistribution.

## Enable MySQL

Start the optional database:

```bash
docker compose up -d mysql
```

Set:

```env
DB_ENGINE=mysql
DB_NAME=smartqc_demo
DB_USER=smartqc
DB_PASSWORD=smartqc_demo
DB_HOST=127.0.0.1
DB_PORT=3306
```

## Enable S3 or MinIO

For AWS, set `STORAGE_BACKEND=s3`, bucket, region and credentials through environment variables or an AWS credential profile.

For local MinIO:

```bash
docker compose up -d minio
```

Create a bucket and configure:

```env
STORAGE_BACKEND=s3
AWS_S3_BUCKET=smartqc-demo
AWS_REGION=ap-south-1
AWS_ENDPOINT_URL=http://127.0.0.1:9000
AWS_ACCESS_KEY_ID=smartqc_demo
AWS_SECRET_ACCESS_KEY=smartqc_demo_password
```

## Test

```bash
pytest
python manage.py check
```
See `docs/SECURITY.md` before publishing and `docs/VALIDATION.md` for the completed checks.
