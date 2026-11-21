from django.urls import path

from .views import enviar_orden

urlpatterns = [
    path(
        "notificaciones/ordenes/<int:pk>/enviar/",
        enviar_orden,
        name="enviar-orden",
    ),
]
