
from django.urls import path

from .views import BitacoraListView

urlpatterns = [
    path("auditoria/", BitacoraListView.as_view(), name="auditoria-list"),
]
