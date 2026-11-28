from django.http import HttpResponse
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from compras.models import OrdenCompra
from inventario.models import Existencia, Movimiento
from . import services


def _respuesta_archivo(formato, nombre_base, titulo, columnas, filas):
    if formato == "xlsx":
        r = HttpResponse(
            services.excel(titulo, columnas, filas),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        r["Content-Disposition"] = f'attachment; filename="{nombre_base}.xlsx"'
        return r
    r = HttpResponse(
        services.pdf(titulo, columnas, filas),
        content_type="application/pdf",
    )
    r["Content-Disposition"] = f'attachment; filename="{nombre_base}.pdf"'
    return r


class ReporteStockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Existencia.objects.select_related("lote__producto", "almacen").filter(cantidad__gt=0)
        filas = [
            (
                e.lote.producto.sku,
                e.lote.producto.nombre,
                e.lote.numero,
                e.almacen.nombre,
                e.cantidad,
                e.reservada,
                e.cantidad - e.reservada,
            )
            for e in qs
        ]
        cols = ["SKU", "Producto", "Lote", "Almacén", "Físico", "Reservado", "Disponible"]
        formato = request.query_params.get("formato", "pdf").lower()
        return _respuesta_archivo(formato, "stock", "Stock actual", cols, filas)


class ReporteKardexView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Movimiento.objects.select_related("almacen", "usuario").order_by("-fecha", "-id")
        almacen_id = request.query_params.get("almacen")
        if almacen_id:
            qs = qs.filter(almacen_id=almacen_id)
        filas = [
            (
                m.id,
                timezone.localtime(m.fecha).strftime("%Y-%m-%d %H:%M"),
                m.get_tipo_display() if hasattr(m, "get_tipo_display") else m.tipo,
                m.almacen.nombre if m.almacen else "",
                m.documento_origen or "-",
                m.usuario.email if m.usuario else "Sistema",
            )
            for m in qs[:200]
        ]
        cols = ["ID", "Fecha", "Tipo", "Almacén", "Documento", "Usuario"]
        formato = request.query_params.get("formato", "pdf").lower()
        return _respuesta_archivo(formato, "kardex", "Kardex de movimientos", cols, filas)


class ReporteOrdenesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = OrdenCompra.objects.select_related("proveedor", "almacen_destino").order_by("-fecha", "-id")
        estado = request.query_params.get("estado")
        if estado:
            qs = qs.filter(estado=estado)
        filas = [
            (
                f"OC-{o.id}",
                o.proveedor.razon_social,
                o.almacen_destino.nombre,
                o.get_estado_display(),
                timezone.localtime(o.fecha).strftime("%Y-%m-%d"),
                o.observacion or "-",
            )
            for o in qs
        ]
        cols = ["N.º Orden", "Proveedor", "Almacén Destino", "Estado", "Fecha", "Observación"]
        formato = request.query_params.get("formato", "pdf").lower()
        return _respuesta_archivo(formato, "ordenes_compra", "Órdenes de compra", cols, filas)