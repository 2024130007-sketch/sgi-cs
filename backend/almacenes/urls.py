from rest_framework.routers import DefaultRouter 
 
from .views import AlmacenViewSet 

router = DefaultRouter() 
router.register("almacenes", AlmacenViewSet, basename="almacen") 
urlpatterns = router.urls