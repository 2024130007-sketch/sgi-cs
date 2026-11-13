from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("email", "first_name", "rol", "is_active", "intentos_fallidos")
    fieldsets = UserAdmin.fieldsets + (
        ("Seguridad del sistema", {"fields": ("rol", "intentos_fallidos", "bloqueado_hasta")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("email", "rol")}),)
