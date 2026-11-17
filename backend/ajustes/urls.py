from rest_framework.routers import DefaultRouter 
  
from .views import AjusteViewSet, BajaViewSet 
  
router = DefaultRouter() 
router.register("ajustes", AjusteViewSet, basename="ajuste") 
router.register("bajas", BajaViewSet, basename="baja") 
urlpatterns = router.urls