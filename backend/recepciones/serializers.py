from rest_framework import serializers
from .models import Recepcion, DetalleRecepcion

class DetalleRecepcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleRecepcion
        fields = ["id", "detalle_orden", "lote", "cantidad"]

class RecepcionSerializer(serializers.ModelSerializer):
    detalles = DetalleRecepcionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Recepcion
        fields = ["id", "orden_compra", "usuario", "documento", "fecha", "estado", "detalles"]