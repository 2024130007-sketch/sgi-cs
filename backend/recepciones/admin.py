from django.contrib import admin
from .models import DetalleRecepcion, Recepcion

admin.site.register([Recepcion, DetalleRecepcion])