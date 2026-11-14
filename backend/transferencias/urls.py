from rest_framework.routers import DefaultRouter 
 
from .views import TransferenciaViewSet 
 
router = DefaultRouter() 
router.register("transferencias", TransferenciaViewSet, basename="transferencia") 
urlpatterns = router.urls 