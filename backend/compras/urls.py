from rest_framework.routers import DefaultRouter

from .views import OrdenCompraViewSet

router = DefaultRouter()
router.register("compras/ordenes", OrdenCompraViewSet, basename="orden-compra")
urlpatterns = router.urls
