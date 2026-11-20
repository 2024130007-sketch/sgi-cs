from django.contrib import admin

from .models import Ajuste, Baja, DetalleAjuste

admin.site.register([Ajuste, DetalleAjuste, Baja])