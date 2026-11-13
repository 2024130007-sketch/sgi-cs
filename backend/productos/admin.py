
from django.contrib import admin

from .models import Producto, CodigoBarras


class CodigoBarrasInline(admin.TabularInline):
    model = CodigoBarras
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "nombre",
        "marca",
        "unidad_medida",
        "precio",
        "activo",
    )

    search_fields = ("sku", "nombre", "marca")
    list_filter = ("activo", "marca")
    inlines = [CodigoBarrasInline]


@admin.register(CodigoBarras)
class CodigoBarrasAdmin(admin.ModelAdmin):
    list_display = ("codigo", "producto", "fecha_registro")
    search_fields = ("codigo", "producto__nombre")
