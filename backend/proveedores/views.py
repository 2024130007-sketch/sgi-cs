from rest_framework import filters, viewsets
from config.permisos import roles_permitidos
from usuarios.models import Usuario
from .models import Proveedor
from .serializers import ProveedorSerializer

R = Usuario.Rol

class ProveedorViewSet(viewsets.ModelViewSet):
    """RF-10. Escritura: Administrador y Comprador. DELETE desactivar."""
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    permission_classes = [roles_permitidos(R.ADMINISTRADOR, R.COMPRADOR)]
    filter_backends = [filters.SearchFilter]
    search_fields = ["ruc", "razon_social"]

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save(update_fields=["activo"])
