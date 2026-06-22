from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.machines.views import MachineViewSet, CameraViewSet, LaserViewSet, DeviceEventViewSet
from apps.projects.views import ProjectViewSet, RecipeViewSet, AIModelViewSet
from apps.inspections.views import (
    InspectionViewSet,
    InspectionImageViewSet,
    DetectionViewSet,
    AnnotationViewSet,
    OperatorHeartbeatViewSet,
)
from apps.inspections.api_views import (
    HealthAPIView,
    DashboardStatsAPIView,
    UploadAndInspectAPIView,
    StandaloneInferenceAPIView,
    StorageAPIView,
    StorageDownloadAPIView,
    MockCameraCaptureAPIView,
    MockLaserProfileAPIView,
    MockPLCAPIView,
)

router = DefaultRouter()
router.register("machines", MachineViewSet)
router.register("cameras", CameraViewSet)
router.register("lasers", LaserViewSet)
router.register("device-events", DeviceEventViewSet)
router.register("projects", ProjectViewSet)
router.register("recipes", RecipeViewSet)
router.register("ai-models", AIModelViewSet)
router.register("inspections", InspectionViewSet)
router.register("inspection-images", InspectionImageViewSet)
router.register("detections", DetectionViewSet)
router.register("annotations", AnnotationViewSet)
router.register("operator-heartbeats", OperatorHeartbeatViewSet)

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="swagger-ui", permanent=False), name="home"),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/health/", HealthAPIView.as_view(), name="health"),
    path("api/dashboard/stats/", DashboardStatsAPIView.as_view(), name="dashboard-stats"),
    path("api/upload-image/", UploadAndInspectAPIView.as_view(), name="upload-image"),
    path("api/infer/", StandaloneInferenceAPIView.as_view(), name="infer"),
    path("api/storage/files/", StorageAPIView.as_view(), name="storage-files"),
    path("api/storage/download/", StorageDownloadAPIView.as_view(), name="storage-download"),
    path("api/demo/camera/capture/", MockCameraCaptureAPIView.as_view(), name="mock-camera-capture"),
    path("api/demo/laser/profile/", MockLaserProfileAPIView.as_view(), name="mock-laser-profile"),
    path("api/demo/plc/", MockPLCAPIView.as_view(), name="mock-plc"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
