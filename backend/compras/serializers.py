from rest_framework import serializers

from almacenes.models import Almacen
from productos.models import Producto
from proveedores.models import Proveedor
from .models import DetalleOrdenCompra, OrdenCompra


class ItemEntradaSerializer(serializers.Serializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    cantidad = serializers.IntegerField()
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)


class OrdenEntradaSerializer(serializers.Serializer):
    proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all())
    almacen_destino = serializers.PrimaryKeyRelatedField(queryset=Almacen.objects.all())
    observacion = serializers.CharField(required=False, allow_blank=True, default="")
    items = ItemEntradaSerializer(many=True)


class RechazoSerializer(serializers.Serializer):
    motivo = serializers.CharField(required=False, allow_blank=True, default="")


class DetalleSerializer(serializers.ModelSerializer):
    sku = serializers.CharField(source="producto.sku", read_only=True)
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    pendiente = serializers.IntegerField(read_only=True)

    class Meta:
        model = DetalleOrdenCompra
        fields = ["id", "producto", "sku", "producto_nombre", "cantidad", "precio_unitario",
                  "subtotal", "cantidad_recibida", "pendiente"]


class OrdenSerializer(serializers.ModelSerializer):
    detalles = DetalleSerializer(many=True, read_only=True)
    proveedor_nombre = serializers.CharField(source="proveedor.razon_social", read_only=True)
    proveedor_correo = serializers.CharField(source="proveedor.correo", read_only=True)
    almacen_nombre = serializers.CharField(source="almacen_destino.nombre", read_only=True)
    estado_display = serializers.CharField(source="get_estado_display", read_only=True)
    creada_por_email = serializers.CharField(source="creada_por.email", read_only=True)
    aprobada_por_email = serializers.CharField(source="aprobada_por.email", read_only=True, default="")
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrdenCompra
        fields = ["id", "proveedor", "proveedor_nombre", "proveedor_correo", "almacen_destino", "almacen_nombre", "estado",
                  "estado_display", "observacion", "creada_por_email", "aprobada_por_email",
                  "motivo_rechazo", "fecha", "fecha_aprobacion", "fecha_envio", "total", "detalles"]
