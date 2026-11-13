from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [path("admin/", admin.site.urls)]
if "usuarios" in settings.INSTALLED_APPS:
    urlpatterns += [
        path("api/auth/", include("usuarios.urls_auth")),
        path("api/usuarios/", include("usuarios.urls")),
    ]
# Cada app expone sus rutas bajo /api/
for _app in ["productos", "almacenes", "proveedores", "inventario", "transferencias", "reposicion"]:
    if _app in settings.INSTALLED_APPS:
        urlpatterns.append(path("api/", include(f"{_app}.urls")))