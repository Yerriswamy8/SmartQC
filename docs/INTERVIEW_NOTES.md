# Interview Talking Points

- Designed a modular industrial inspection platform with a PyQt operator application and a Django REST backend.
- Implemented machine, project, recipe, inspection, image, detection, annotation and operator-monitoring workflows.
- Used adapter patterns to isolate PLC, camera, laser, AI and object-storage integrations.
- Added local-first defaults so reviewers can run the repository without factory hardware or cloud credentials.
- Integrated an OpenCV demo detector and an optional Ultralytics YOLO adapter.
- Added AWS S3-compatible upload, download, list and delete operations with a local storage fallback.
- Supported SQLite for quick evaluation and MySQL for a production-like deployment.
- Protected employer and customer IP by rebuilding the public demo with synthetic data and mocks.
