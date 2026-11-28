from rest_framework import serializers
from .models import ColaERP, EquivalenciaERP

class EquivalenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquivalenciaERP
        fields = ["id", "producto", "codigo_erp", "unidad_erp"]

class ColaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColaERP
        fields = ["id", "tipo", "payload", "estado", "intentos", "proximo_intento", "ultimo_error", "creado"]