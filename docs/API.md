# Main API Endpoints

The router exposes CRUD endpoints for machines, cameras, lasers, device events, projects, recipes, AI models, inspections, images, detections, annotations and operator heartbeats.

Additional workflow endpoints:

- `GET /api/health/`
- `GET /api/dashboard/stats/`
- `POST /api/upload-image/`
- `POST /api/infer/`
- `GET|POST|DELETE /api/storage/files/`
- `GET /api/storage/download/?key=...`
- `GET /api/demo/camera/capture/`
- `GET /api/demo/laser/profile/`
- `GET|POST /api/demo/plc/`
- `GET /api/docs/` for Swagger UI

## Upload and inspect

```bash
curl -X POST http://127.0.0.1:8000/api/upload-image/   -F inspection_id=1   -F side=surface   -F image=@sample_data/inspection_sample.png
```

## Standalone inference

```bash
curl -X POST http://127.0.0.1:8000/api/infer/   -F image=@sample_data/inspection_sample.png
```
