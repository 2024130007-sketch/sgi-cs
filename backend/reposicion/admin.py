from django.contrib import admin
from .models import Alerta, ReglaReposicion
admin.site.register([ReglaReposicion, Alerta])