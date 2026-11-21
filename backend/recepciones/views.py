from rest_framework import viewsets
from rest_framework.response import Response

from config.permisos import roles_permitidos
from usuarios.models import Usuario
from . import services
from .models import Recepcion
from .serializers import RecepcionEntradaSerializer, RecepcionSerializer

R = Usuario.Rol
PuedeRecibir = roles_permitidos(R.ADMINISTRADOR, R.JEFE_ALMACEN, R.OPERARIO)


class RecepcionViewSet(viewsets.ReadOnlyModelViewSet):
    """/api/recepciones/ (CU-12, RF-37 y RF-38). Las órdenes por recibir salen de /api/compras/ordenes/."""
    serializer_class = RecepcionSerializer
    permission_classes = [PuedeRecibir]
    queryset = Recepcion.objects.select_related("orden_compra", "usuario").prefetch_related(
        "detalles__detalle_orden__producto", "detalles__lote")

    def create(self, request):
        s = RecepcionEntradaSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        recepcion = services.registrar_recepcion(request.user, d["orden_compra"], d["detalles"], d["documento"])
        return Response(RecepcionSerializer(recepcion).data, status=201)