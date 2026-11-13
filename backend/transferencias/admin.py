from django.contrib import admin 
from .models import DetalleTransferencia, Transferencia 
 
admin.site.register([Transferencia, DetalleTransferencia]) 