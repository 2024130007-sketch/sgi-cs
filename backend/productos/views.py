from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from . import gs1
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


class EscaneoView(APIView):
    """POST /api/productos/escaneo/ (RF #33).

    Recibe lo que leyó la cámara o el lector: un código de barras simple, un SKU
    o un GS1-128. Devuelve el producto y, si el código lo trae, el lote y el
    vencimiento, para rellenar los formularios de ingreso y salida.
    """
    permission_classes = [roles_permitidos(
        "ADMINISTRADOR", "JEFE_ALMACEN", "OPERARIO", "COMPRADOR"
    )]

    def post(self, request):
        crudo = str(request.data.get("codigo", "")).strip()
        if not crudo:
            return Response({"detail": "Debe enviar el código leído."}, status=400)

        lote = vencimiento = serie = None
        candidatos = [crudo]
        if gs1.parece_gs1(crudo):
            try:
                datos = gs1.parsear_gs1(crudo)
            except gs1.CodigoInvalido as e:
                return Response({"detail": str(e)}, status=400)
            lote, serie, vencimiento = datos["lote"], datos["serie"], datos["vencimiento"]
            gtin = datos["gtin"] or ""
            # el EAN-13 se guarda sin el cero inicial del GTIN-14
            candidatos = [gtin, gtin.lstrip("0")] if gtin else []

        producto = None
        for c in candidatos:
            barra = CodigoBarras.objects.select_related("producto").filter(codigo=c).first()
            if barra:
                producto = barra.producto
                break
            producto = Producto.objects.filter(sku=c, activo=True).first()
            if producto:
                break
        if producto is None:
            return Response({"detail": "No existe un producto con ese código."}, status=404)

        return Response({
            "producto": ProductoSerializer(producto).data,
            "lote": lote,
            "serie": serie,
            "vencimiento": vencimiento.isoformat() if vencimiento else None,
        })
