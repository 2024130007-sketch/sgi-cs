"""Vistas para el envío de correos."""

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from compras.models import OrdenCompra
from compras.serializers import OrdenSerializer
from config.permisos import roles_permitidos
from usuarios.models import Usuario

from . import services


@api_view(["POST"])
@permission_classes([
    roles_permitidos(Usuario.Rol.ADMINISTRADOR, Usuario.Rol.COMPRADOR)
])
def enviar_orden(request, pk):
    """Envía una orden de compra aprobada al proveedor."""

    orden = get_object_or_404(
        OrdenCompra.objects.select_related(
            "proveedor", "almacen_destino"
        ).prefetch_related("detalles__producto"),
        pk=pk,
    )

    orden = services.enviar_orden_compra(orden)

    return Response({
        "mensaje": "Orden enviada correctamente al proveedor.",
        "orden": OrdenSerializer(orden).data,
    })
