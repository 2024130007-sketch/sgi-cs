from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from config.permisos import roles_permitidos
from usuarios.models import Usuario
from . import services
from .models import OrdenCompra
from .serializers import OrdenEntradaSerializer, OrdenSerializer, RechazoSerializer

R = Usuario.Rol
PuedeComprar = roles_permitidos(R.ADMINISTRADOR, R.COMPRADOR)
PuedeAprobar = roles_permitidos(R.ADMINISTRADOR, R.JEFE_ALMACEN)


class OrdenCompraViewSet(viewsets.ReadOnlyModelViewSet):
    """/api/compras/ordenes/ (CU-10 y CU-11, RF-35 y RF-36)."""
    serializer_class = OrdenSerializer

    def get_queryset(self):
        qs = OrdenCompra.objects.select_related("proveedor", "almacen_destino", "creada_por",
                                                "aprobada_por").prefetch_related("detalles__producto")
        estado = self.request.query_params.get("estado")
        return qs.filter(estado__in=estado.split(",")) if estado else qs

    def get_permissions(self):
        if self.action in ("aprobar", "rechazar"):
            return [PuedeAprobar()]
        return [PuedeComprar()]  # lectura para todos; escritura solo administrador y comprador

    def create(self, request):
        s = OrdenEntradaSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        orden = services.crear_orden(request.user, d["proveedor"], d["almacen_destino"], d["items"],
                                     d["observacion"])
        return Response(OrdenSerializer(orden).data, status=201)

    def update(self, request, pk=None):
        s = OrdenEntradaSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        orden = services.editar_orden(self.get_object(), d["proveedor"], d["almacen_destino"], d["items"],
                                      d["observacion"])
        return Response(OrdenSerializer(orden).data)

    @action(detail=True, methods=["post"], url_path="enviar-aprobacion")
    def enviar_aprobacion(self, request, pk=None):
        return Response(OrdenSerializer(services.enviar_a_aprobacion(self.get_object())).data)

    @action(detail=True, methods=["post"])
    def aprobar(self, request, pk=None):
        return Response(OrdenSerializer(services.aprobar(request.user, self.get_object())).data)

    @action(detail=True, methods=["post"])
    def rechazar(self, request, pk=None):
        s = RechazoSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        orden = services.rechazar(request.user, self.get_object(), s.validated_data["motivo"])
        return Response(OrdenSerializer(orden).data)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        return Response(OrdenSerializer(services.cancelar(self.get_object())).data)
