from django.urls import path
from .views import ReporteStockView

urlpatterns = [
    path("stock/", ReporteStockView.as_view(), name="reporte-stock"),
]