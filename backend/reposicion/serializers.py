from rest_framework import serializers
from .models import Alerta, ReglaReposicion

class ReglaSerializer(serializers.ModelSerializer):
    punto_reorden = serializers.IntegerField(read_only=True)
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    almacen_nombre = serializers.CharField(source="almacen.nombre", read_only=True)

    class Meta:
        model = ReglaReposicion
        fields = ["id", "producto", "producto_nombre", "almacen", "almacen_nombre", "stock_minimo", "stock_seguridad", "stock_maximo", "demanda_diaria", "tiempo_entrega_dias", "punto_reorden"]
        validators = []

    def validate(self, d):
        if d["stock_maximo"] < d["stock_minimo"]:
            raise serializers.ValidationError("El stock máximo no puede ser menor al mínimo.")
        return d

class AlertaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    almacen_nombre = serializers.CharField(source="almacen.nombre", read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = Alerta
        fields = ["id", "tipo", "tipo_display", "producto", "producto_nombre", "almacen", "almacen_nombre", "mensaje", "cantidad_sugerida", "estado", "motivo", "fecha"]