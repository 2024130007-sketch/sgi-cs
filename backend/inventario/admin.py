from django.contrib import admin
from .models import DetalleMovimiento, Existencia, Lote, Movimiento

admin.site.register([Lote, Existencia, Movimiento, DetalleMovimiento])
