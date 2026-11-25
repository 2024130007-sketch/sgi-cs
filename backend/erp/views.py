from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from config.permisos import roles_permitidos
from usuarios.models import Usuario
from .models import ColaERP, EquivalenciaERP
from .serializers import ColaSerializer, EquivalenciaSerializer
from . import services

R = Usuario.Rol

class ColaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ColaERP.objects.all().order_by("-creado")
    serializer_class = ColaSerializer

    @action(detail=False, methods=["post"], permission_classes=[roles_permitidos(R.ADMINISTRADOR, R.JEFE_ALMACEN)])
    def procesar(self, request):
        services.procesar_pendientes()
        return Response({"detail": "Procesamiento ejecutado."})

class EquivalenciaViewSet(viewsets.ModelViewSet):
    queryset = EquivalenciaERP.objects.all()
    serializer_class = EquivalenciaSerializer
    permission_classes = [roles_permitidos(R.ADMINISTRADOR, R.JEFE_ALMACEN)]