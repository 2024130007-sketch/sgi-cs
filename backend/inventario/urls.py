from django.urls import path

from .views import (IngresoView, LoteEstadoView, LoteListView, LoteTrazabilidadView,
                    MovimientoListView, SalidaView, StockView)

urlpatterns = [
    path("inventario/ingresos/", IngresoView.as_view()),
    path("inventario/salidas/", SalidaView.as_view()),
    path("inventario/stock/", StockView.as_view()),
    path("inventario/movimientos/", MovimientoListView.as_view()),
    path("inventario/lotes/", LoteListView.as_view()),
    path("inventario/lotes/<int:pk>/trazabilidad/", LoteTrazabilidadView.as_view()),
    path("inventario/lotes/<int:pk>/estado/", LoteEstadoView.as_view()),
]
