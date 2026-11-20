from rest_framework.routers import DefaultRouter
from .views import RecepcionViewSet

router = DefaultRouter()
router.register("recepciones", RecepcionViewSet, basename="recepcion")
urlpatterns = router.urls