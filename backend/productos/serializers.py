from rest_framework import serializers
from .models import Producto, CodigoBarras


class CodigoBarrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigoBarras
        fields = ["id", "codigo", "fecha_registro"]
        read_only_fields = ["id", "fecha_registro"]


class ProductoSerializer(serializers.ModelSerializer):
    codigos_barras = CodigoBarrasSerializer(many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "sku",
            "nombre",
            "descripcion",
            "marca",
            "categoria",
            "requiere_lote",
            "requiere_vencimiento",
            "unidad_medida",
            "precio",
            "activo",
            "fecha_creacion",
            "fecha_actualizacion",
            "codigos_barras",
        ]
        read_only_fields = [
            "id",
            "fecha_creacion",
            "fecha_actualizacion",
        ]


class CodigoBarrasCrearSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodigoBarras
        fields = ["id", "producto", "codigo", "fecha_registro"]
        read_only_fields = ["id", "fecha_registro"]