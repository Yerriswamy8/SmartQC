# Validation Performed

The generated demo was validated with the following checks:

- Python bytecode compilation for all source files
- Django system check with zero issues
- Fresh migrations for machine, project and inspection applications
- Demo seed command using only synthetic records
- Pytest suite for API health, OpenCV inference and local storage
- End-to-end API smoke test covering inspection creation, multipart image upload, inference, detection persistence and storage
- Mock PLC, mock camera and mock laser endpoints
- PyQt desktop startup in off-screen mode against a live Django server
- OpenAPI generation with zero errors

Validated API surface at generation time: **36 paths and 87 HTTP operations**.
