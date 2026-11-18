from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permisos import roles_permitidos
from usuarios.models import Usuario
from . import services
from .models import Existencia, Lote, Movimiento
from .serializers import (EstadoLoteSerializer, ExistenciaSerializer, IngresoSerializer,
                          LoteSerializer, MovimientoSerializer, SalidaSerializer)

R = Usuario.Rol
PuedeMover = roles_permitidos(R.ADMINISTRADOR, R.JEFE_ALMACEN, R.OPERARIO)
PuedeGestionarLotes = roles_permitidos(R.ADMINISTRADOR, R.JEFE_ALMACEN)


class IngresoView(APIView):
    """POST /api/inventario/ingresos/ (CU-04)."""
    permission_classes = [PuedeMover]

    def post(self, request):
        s = IngresoSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        mov = services.registrar_ingreso(
            request.user, d["almacen"], d["producto"], d["cantidad"], d["numero_lote"],
            d["fecha_vencimiento"], d["proveedor"], d["documento"], d["fecha_fabricacion"])
        return Response(MovimientoSerializer(mov).data, status=status.HTTP_201_CREATED)


class SalidaView(APIView):
    """POST /api/inventario/salidas/ (CU-05, FEFO)."""
    permission_classes = [PuedeMover]

    def post(self, request):
        s = SalidaSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        mov = services.registrar_salida(request.user, d["almacen"], d["producto"], d["cantidad"],
                                        d["documento"])
        return Response(MovimientoSerializer(mov).data, status=status.HTTP_201_CREATED)


class StockView(generics.ListAPIView):
    """GET /api/inventario/stock/?almacen=&producto=&search= (CU-08, RF-27/28)."""
    serializer_class = ExistenciaSerializer

    def get_queryset(self):
        qs = Existencia.objects.select_related("lote__producto", "almacen").filter(
            cantidad__gt=0).order_by("lote__producto__nombre", "lote__fecha_vencimiento")
        p = self.request.query_params
        if p.get("almacen"):
            qs = qs.filter(almacen_id=p["almacen"])
        if p.get("producto"):
            qs = qs.filter(lote__producto_id=p["producto"])
        if p.get("search"):
            q = p["search"]
            qs = (qs.filter(lote__producto__nombre__icontains=q) |
                  qs.filter(lote__producto__sku__icontains=q) |
                  qs.filter(lote__numero__icontains=q) |
                  qs.filter(lote__producto__codigos__codigo=q)).distinct()
        return qs


class MovimientoListView(generics.ListAPIView):
    """Kardex: GET /api/inventario/movimientos/ (RF-32)."""
    serializer_class = MovimientoSerializer
    queryset = Movimiento.objects.select_related("almacen", "usuario").prefetch_related(
        "detalles__lote__producto")[:200]


def _lotes_con_stock():
    return (Lote.objects.select_related("producto", "proveedor")
            .annotate(stock_total=Coalesce(Sum("existencias__cantidad"), 0)))


class LoteListView(generics.ListAPIView):
    """GET /api/inventario/lotes/?estado=&producto=&search= (CU-09)."""
    serializer_class = LoteSerializer

    def get_queryset(self):
        qs = _lotes_con_stock().order_by("producto__nombre", "fecha_vencimiento")
        p = self.request.query_params
        if p.get("estado"):
            qs = qs.filter(estado=p["estado"])
        if p.get("producto"):
            qs = qs.filter(producto_id=p["producto"])
        if p.get("search"):
            q = p["search"]
            qs = qs.filter(Q(numero__icontains=q) | Q(producto__nombre__icontains=q)
                           | Q(producto__sku__icontains=q))
        return qs


class LoteTrazabilidadView(APIView):
    """GET /api/inventario/lotes/<id>/trazabilidad/ (RF-33)."""

    def get(self, request, pk):
        lote = get_object_or_404(_lotes_con_stock(), pk=pk)
        return Response({"lote": LoteSerializer(lote).data, **services.trazabilidad_lote(lote)})


class LoteEstadoView(APIView):
    """POST /api/inventario/lotes/<id>/estado/ (RF-34): cuarentena o liberación."""
    permission_classes = [PuedeGestionarLotes]

    def post(self, request, pk):
        lote = get_object_or_404(Lote, pk=pk)
        s = EstadoLoteSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        services.cambiar_estado_lote(lote, s.validated_data["estado"], s.validated_data["motivo"])
        return Response(LoteSerializer(_lotes_con_stock().get(pk=pk)).data)
