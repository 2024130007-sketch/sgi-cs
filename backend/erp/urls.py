from rest_framework.routers import DefaultRouter
from .views import ColaViewSet, EquivalenciaViewSet

router = DefaultRouter()
router.register("erp/cola", ColaViewSet, basename="erp-cola")
router.register("erp/equivalencias", EquivalenciaViewSet, basename="erp-equivalencia")
urlpatterns = router.urls