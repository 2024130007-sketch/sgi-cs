from rest_framework import viewsets 
 
from config.permisos import roles_permitidos 
from usuarios.models import Usuario 
from .models import Almacen 
from .serializers import AlmacenSerializer 

 
class AlmacenViewSet(viewsets.ModelViewSet): 
    """RF-09. Escritura: Administrador. DELETE = desactivar.""" 
    queryset = Almacen.objects.all() 
    serializer_class = AlmacenSerializer 
    permission_classes = [roles_permitidos(Usuario.Rol.ADMINISTRADOR)] 
 
    def perform_destroy(self, instance): 
        instance.activo = False 
        instance.save(update_fields=["activo"]) 