from django.contrib import admin

from .models import DetalleOrdenCompra, OrdenCompra

admin.site.register([OrdenCompra, DetalleOrdenCompra])
