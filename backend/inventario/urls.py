from django.urls import path

from .views import IngresoView, MovimientoListView, SalidaView, StockView

urlpatterns = [
    path("inventario/ingresos/", IngresoView.as_view()),
    path("inventario/salidas/", SalidaView.as_view()),
    path("inventario/stock/", StockView.as_view()),
    path("inventario/movimientos/", MovimientoListView.as_view()),
]
