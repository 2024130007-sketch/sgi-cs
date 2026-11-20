from rest_framework import serializers 
  
from almacenes.models import Almacen 
from inventario.models import Existencia 
from proveedores.models import Proveedor 
from .models import Ajuste, Baja, DetalleAjuste 
  
  
class DetalleAjusteSerializer(serializers.ModelSerializer): 
    sku = serializers.CharField(source="lote.producto.sku", read_only=True) 
    producto = serializers.CharField(source="lote.producto.nombre", read_only=True) 
    lote_numero = serializers.CharField(source="lote.numero", read_only=True) 
    diferencia = serializers.IntegerField(read_only=True) 
  
    class Meta: 
        model = DetalleAjuste 
        fields = ["id", "sku", "producto", "lote_numero", "cantidad_sistema", "cantidad_contada", "diferencia"] 
  
  
class AjusteSerializer(serializers.ModelSerializer): 
    detalles = DetalleAjusteSerializer(many=True, read_only=True) 
    almacen_nombre = serializers.CharField(source="almacen.nombre", read_only=True) 
    usuario_email = serializers.CharField(source="usuario.email", read_only=True) 
    estado_display = serializers.CharField(source="get_estado_display", read_only=True) 
  
    class Meta: 
        model = Ajuste 
        fields = ["id", "almacen", "almacen_nombre", "usuario_email", "estado", "estado_display", 
                  "observacion", "fecha_inicio", "fecha_cierre", "detalles"] 
  
  
class IniciarConteoSerializer(serializers.Serializer): 
    almacen = serializers.PrimaryKeyRelatedField(queryset=Almacen.objects.all()) 
    observacion = serializers.CharField(required=False, allow_blank=True, default="") 
  
  
class ConteoSerializer(serializers.Serializer): 
    conteos = serializers.DictField(child=serializers.CharField(allow_blank=True, allow_null=True)) 
  
  
class BajaSerializer(serializers.ModelSerializer): 
    almacen_nombre = serializers.CharField(source="almacen.nombre", read_only=True) 
    sku = serializers.CharField(source="lote.producto.sku", read_only=True) 
    producto = serializers.CharField(source="lote.producto.nombre", read_only=True) 
    lote_numero = serializers.CharField(source="lote.numero", read_only=True) 
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True) 
    proveedor_nombre = serializers.CharField(source="proveedor.razon_social", read_only=True, default="") 
    usuario_email = serializers.CharField(source="usuario.email", read_only=True) 
  
    class Meta: 
        model = Baja 
        fields = ["id", "almacen_nombre", "sku", "producto", "lote_numero", "cantidad", "tipo", 
                  "tipo_display", "motivo", "proveedor_nombre", "usuario_email", "fecha"] 
  
  
class BajaEntradaSerializer(serializers.Serializer): 
    existencia = serializers.PrimaryKeyRelatedField( 
        queryset=Existencia.objects.select_related("lote__producto", "almacen")) 
    cantidad = serializers.IntegerField() 
    tipo = serializers.ChoiceField(choices=Baja.Tipo.choices) 
    motivo = serializers.CharField(required=False, allow_blank=True, default="") 
    proveedor = serializers.PrimaryKeyRelatedField(queryset=Proveedor.objects.all(), required=False, 
                                                   allow_null=True, default=None) 