from django.urls import path
from .views import (
    ProductoListaCrearView,
    ProductoDetalleView,
    CodigoBarrasCrearView,
    BuscarCodigoBarrasView,
    EscaneoView,
)

urlpatterns = [
    path("productos/", ProductoListaCrearView.as_view(), name="productos"),
    path("productos/<int:pk>/", ProductoDetalleView.as_view(), name="producto-detalle"),
    path("codigos-barras/", CodigoBarrasCrearView.as_view(), name="codigo-barras"),
    path("codigos-barras/buscar/", BuscarCodigoBarrasView.as_view(), name="buscar-codigo-barras"),
    path("productos/escaneo/", EscaneoView.as_view(), name="escaneo"),
]