from django.urls import path
from .views import ReporteKardexView, ReporteOrdenesView, ReporteStockView

urlpatterns = [
    path("reportes/stock/", ReporteStockView.as_view(), name="reporte-stock"),
    path("reportes/kardex/", ReporteKardexView.as_view(), name="reporte-kardex"),
    path("reportes/ordenes/", ReporteOrdenesView.as_view(), name="reporte-ordenes"),
]