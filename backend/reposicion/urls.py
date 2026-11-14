from rest_framework.routers import DefaultRouter
from .views import AlertaViewSet, ReglaViewSet

router = DefaultRouter()
router.register("reglas-reposicion", ReglaViewSet, basename="regla")
router.register("alertas", AlertaViewSet, basename="alerta")
urlpatterns = router.urls