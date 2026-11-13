from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from config.permisos import roles_permitidos
from usuarios.models import Usuario
from . import services
from .models import Alerta, ReglaReposicion
from .serializers import AlertaSerializer, ReglaSerializer

R = Usuario.Rol

class ReglaViewSet(viewsets.ModelViewSet):
    """CU-13. Escritura: Jefe de Almacén y Administrador."""
    queryset = ReglaReposicion.objects.select_related("producto", "almacen")
    serializer_class = ReglaSerializer
    permission_classes = [roles_permitidos(R.ADMINISTRADOR, R.JEFE_ALMACEN)]

class AlertaViewSet(viewsets.ReadOnlyModelViewSet):
    """CU-15."""
    queryset = Alerta.objects.select_related("producto", "almacen")
    serializer_class = AlertaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        estado = self.request.query_params.get("estado")
        return qs.filter(estado=estado) if estado else qs

    @action(detail=False, methods=["post"], permission_classes=[roles_permitidos(R.ADMINISTRADOR, R.JEFE_ALMACEN, R.COMPRADOR)])
    def generar(self, request):
        return Response({"nuevas": services.generar_alertas()})

    def _cerrar(self, request, pk, estado):
        alerta = self.get_object()
        motivo = (request.data.get("motivo") or "").strip()
        if not motivo:
            raise ValidationError("Debe indicar el motivo.")  # RF-47
        alerta.estado, alerta.motivo = estado, motivo
        alerta.save()
        return Response(AlertaSerializer(alerta).data)

    @action(detail=True, methods=["post"], permission_classes=[roles_permitidos(R.ADMINISTRADOR, R.JEFE_ALMACEN, R.COMPRADOR)])
    def atender(self, request, pk=None):
        return self._cerrar(request, pk, Alerta.Estado.ATENDIDA)

    @action(detail=True, methods=["post"], permission_classes=[roles_permitidos(R.ADMINISTRADOR, R.JEFE_ALMACEN, R.COMPRADOR)])
    def descartar(self, request, pk=None):
        return self._cerrar(request, pk, Alerta.Estado.DESCARTADA)