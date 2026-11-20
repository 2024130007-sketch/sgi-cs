
from rest_framework import generics

from config.permisos import roles_permitidos
from usuarios.models import Usuario
from .models import Bitacora
from .serializers import BitacoraSerializer


class BitacoraListView(generics.ListAPIView):
    """
    Consulta de bitácora:
    GET /api/auditoria/?usuario=&accion=&entidad=&fecha_desde=&fecha_hasta=
    """
    serializer_class = BitacoraSerializer
    permission_classes = [
        roles_permitidos(
            Usuario.Rol.ADMINISTRADOR,
            solo_escritura=False
        )
    ]

    def get_queryset(self):
        queryset = Bitacora.objects.select_related("usuario").all()
        params = self.request.query_params

        if params.get("usuario"):
            queryset = queryset.filter(usuario_id=params["usuario"])

        if params.get("accion"):
            queryset = queryset.filter(accion=params["accion"].upper())

        if params.get("entidad"):
            queryset = queryset.filter(
                entidad__icontains=params["entidad"]
            )

        if params.get("fecha_desde"):
            queryset = queryset.filter(fecha__date__gte=params["fecha_desde"])

        if params.get("fecha_hasta"):
            queryset = queryset.filter(fecha__date__lte=params["fecha_hasta"])

        if params.get("detalle"):
            queryset = queryset.filter(
                detalle__icontains=params["detalle"]
            )

        return queryset.order_by("-fecha", "-id")[:500]
