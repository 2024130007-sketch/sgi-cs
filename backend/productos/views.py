from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Producto, CodigoBarras
from .serializers import ProductoSerializer, CodigoBarrasCrearSerializer
from config.permisos import roles_permitidos


class ProductoListaCrearView(generics.ListCreateAPIView):
    serializer_class = ProductoSerializer
    permission_classes = [roles_permitidos("ADMINISTRADOR", "JEFE_ALMACEN", "COMPRADOR")]

    def get_queryset(self):
        queryset = Producto.objects.prefetch_related("codigos_barras").order_by("nombre")
        buscar = self.request.query_params.get("buscar", "").strip()

        if buscar:
            queryset = queryset.filter(
                Q(sku__icontains=buscar) |
                Q(nombre__icontains=buscar) |
                Q(marca__icontains=buscar)
            )

        return queryset


class ProductoDetalleView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Producto.objects.prefetch_related("codigos_barras")
    serializer_class = ProductoSerializer
    permission_classes = [roles_permitidos("ADMINISTRADOR", "JEFE_ALMACEN")]


class CodigoBarrasCrearView(generics.CreateAPIView):
    serializer_class = CodigoBarrasCrearSerializer
    permission_classes = [roles_permitidos("ADMINISTRADOR", "JEFE_ALMACEN", "COMPRADOR")]


class BuscarCodigoBarrasView(APIView):
    permission_classes = [roles_permitidos(
        "ADMINISTRADOR", "JEFE_ALMACEN", "OPERARIO", "COMPRADOR"
    )]

    def get(self, request):
        codigo = request.query_params.get("codigo", "").strip()

        if not codigo:
            return Response(
                {"detail": "Debe ingresar un código de barras."},
                status=400
            )

        barra = get_object_or_404(
            CodigoBarras.objects.select_related("producto"),
            codigo=codigo
        )

        return Response(ProductoSerializer(barra.producto).data)