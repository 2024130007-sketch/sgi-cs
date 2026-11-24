from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from inventario.models import Existencia
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