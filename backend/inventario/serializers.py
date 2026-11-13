from rest_framework import serializers

from almacenes.models import Almacen
from productos.models import Producto
from proveedores.models import Proveedor
from .models import DetalleMovimiento, Existencia, Lote, Movimiento


class IngresoSerializer(serializers.Serializer):
    almacen = serializers.PrimaryKeyRelatedField(queryset=Almacen.objects.all())
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    cantidad = serializers.IntegerField()
    numero_lote = serializers.CharField(required=False, allow_blank=True, default="")
    fecha_vencimiento = serializers.DateField(required=False, allow_null=True, default=None)
    fecha_fabricacion = serializers.DateField(required=False, allow_null=True, default=None)
    proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all(), required=False,
                                                   allow_null=True, default=None)
    documento = serializers.CharField(required=False, allow_blank=True, default="")


class SalidaSerializer(serializers.Serializer):
    almacen = serializers.PrimaryKeyRelatedField(queryset=Almacen.objects.all())
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    cantidad = serializers.IntegerField()
    documento = serializers.CharField(required=False, allow_blank=True, default="")


class DetalleSerializer(serializers.ModelSerializer):
    lote_numero = serializers.CharField(source="lote.numero", read_only=True)
    producto = serializers.CharField(source="lote.producto.nombre", read_only=True)
    vencimiento = serializers.DateField(source="lote.fecha_vencimiento", read_only=True)

    class Meta:
        model = DetalleMovimiento
        fields = ["lote_numero", "producto", "vencimiento", "cantidad"]


class MovimientoSerializer(serializers.ModelSerializer):
    detalles = DetalleSerializer(many=True, read_only=True)
    almacen_nombre = serializers.CharField(source="almacen.nombre", read_only=True)
    usuario_email = serializers.CharField(source="usuario.email", read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = Movimiento
        fields = ["id", "tipo", "tipo_display", "almacen", "almacen_nombre", "usuario_email",
                  "fecha", "documento_origen", "detalles"]


class ExistenciaSerializer(serializers.ModelSerializer):
    producto_id = serializers.IntegerField(source="lote.producto_id", read_only=True)
    sku = serializers.CharField(source="lote.producto.sku", read_only=True)
    producto = serializers.CharField(source="lote.producto.nombre", read_only=True)
    categoria = serializers.CharField(source="lote.producto.categoria", read_only=True)
    almacen_nombre = serializers.CharField(source="almacen.nombre", read_only=True)
    lote_numero = serializers.CharField(source="lote.numero", read_only=True)
    vencimiento = serializers.DateField(source="lote.fecha_vencimiento", read_only=True)
    estado_lote = serializers.CharField(source="lote.estado", read_only=True)
    disponible = serializers.IntegerField(read_only=True)

    class Meta:
        model = Existencia
        fields = ["id", "producto_id", "sku", "producto", "categoria", "almacen", "almacen_nombre",
                  "lote_numero", "vencimiento", "estado_lote", "cantidad", "reservada",
                  "en_transito", "disponible"]
