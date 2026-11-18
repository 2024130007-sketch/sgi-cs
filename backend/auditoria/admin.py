
from django.contrib import admin
from .models import Bitacora


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ("fecha", "usuario", "accion", "entidad", "entidad_id")
    list_filter = ("accion", "entidad", "fecha")
    search_fields = ("usuario__email", "entidad", "detalle")
