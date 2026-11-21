from rest_framework import serializers

from compras.models import DetalleOrdenCompra, OrdenCompra
from .models import DetalleRecepcion, Recepcion


class LineaEntradaSerializer(serializers.Serializer):
    detalle_orden = serializers.PrimaryKeyRelatedField(queryset=DetalleOrdenCompra.objects.all())
    cantidad = serializers.IntegerField()
    numero_lote = serializers.CharField(required=False, allow_blank=True, default="")
    fecha_vencimiento = serializers.DateField(required=False, allow_null=True, default=None)


class RecepcionEntradaSerializer(serializers.Serializer):
    orden_compra = serializers.PrimaryKeyRelatedField(queryset=OrdenCompra.objects.all())
    documento = serializers.CharField(required=False, allow_blank=True, default="")
    detalles = LineaEntradaSerializer(many=True)


class DetalleRecepcionSerializer(serializers.ModelSerializer):
    sku = serializers.CharField(source="detalle_orden.producto.sku", read_only=True)
    producto = serializers.CharField(source="detalle_orden.producto.nombre", read_only=True)
    numero_lote = serializers.CharField(source="lote.numero", read_only=True)

    class Meta:
        model = DetalleRecepcion
        fields = ["id", "detalle_orden", "sku", "producto", "lote", "numero_lote", "cantidad"]


class RecepcionSerializer(serializers.ModelSerializer):
    detalles = DetalleRecepcionSerializer(many=True, read_only=True)
    estado_orden = serializers.CharField(source="orden_compra.estado", read_only=True)

    class Meta:
        model = Recepcion
        fields = ["id", "orden_compra", "estado_orden", "usuario", "documento", "fecha", "estado", "detalles"]