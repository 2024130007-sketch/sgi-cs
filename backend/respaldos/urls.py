from django.urls import path

from .views import RespaldoListCreateView

urlpatterns = [
    path("respaldos/", RespaldoListCreateView.as_view(), name="respaldos-list-create"),
]
