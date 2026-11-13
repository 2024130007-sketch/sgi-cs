from django.urls import path

from .views import DesbloquearView, RolesView, UsuarioDetalleView, UsuarioListaView

urlpatterns = [
    path("", UsuarioListaView.as_view()),
    path("roles/", RolesView.as_view()),
    path("<int:pk>/", UsuarioDetalleView.as_view()),
    path("<int:pk>/desbloquear/", DesbloquearView.as_view()),
]
