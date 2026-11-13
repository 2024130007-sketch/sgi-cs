from rest_framework import serializers, viewsets 
from rest_framework.decorators import action 
from rest_framework.response import Response 
 
from almacenes.models import Almacen 
from config.permisos import roles_permitidos 
from productos.models import Producto 
from usuarios.models import Usuario 
from . import services 
from .models import DetalleTransferencia, Transferencia 
 
R = Usuario.Rol 
Permiso = roles_permitidos(R.ADMINISTRADOR, R.JEFE_ALMACEN, R.OPERARIO) 
 
 
class DetalleSerializer(serializers.ModelSerializer): 
    lote_numero = serializers.CharField(source="lote.numero", read_only=True) 
    producto = serializers.CharField(source="lote.producto.nombre", read_only=True) 
 
    class Meta: 
        model = DetalleTransferencia 
        fields = ["id", "lote_numero", "producto", "cantidad", "cantidad_recibida"] 
 
 
class TransferenciaSerializer(serializers.ModelSerializer): 
    detalles = DetalleSerializer(many=True, read_only=True) 
    origen_nombre = serializers.CharField(source="origen.nombre", read_only=True) 
    destino_nombre = serializers.CharField(source="destino.nombre", read_only=True) 
    estado_display = serializers.CharField(source="get_estado_display", read_only=True) 
 
    class Meta: 
        model = Transferencia 
        fields = ["id", "origen", "origen_nombre", "destino", "destino_nombre", "estado", 
                  "estado_display", "fecha", "detalles"] 
 
 
class CrearSerializer(serializers.Serializer): 
    origen = serializers.PrimaryKeyRelatedField(queryset=Almacen.objects.filter(activo=True)) 
    destino = serializers.PrimaryKeyRelatedField(queryset=Almacen.objects.filter(activo=True)) 
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all()) 
    cantidad = serializers.IntegerField() 
 
 
class TransferenciaViewSet(viewsets.ReadOnlyModelViewSet): 
    queryset = Transferencia.objects.select_related("origen", "destino").prefetch_related( 
        "detalles__lote__producto") 
    serializer_class = TransferenciaSerializer 
    permission_classes = [Permiso] 
 
    def create(self, request): 
        s = CrearSerializer(data=request.data) 
        s.is_valid(raise_exception=True) 
        d = s.validated_data 
        t = services.crear_transferencia(request.user, d["origen"], d["destino"], d["producto"], 
                                         d["cantidad"]) 
        return Response(TransferenciaSerializer(t).data, status=201) 
 
    @action(detail=True, methods=["post"], url_path="confirmar-salida") 
    def confirmar_salida(self, request, pk=None): 
        return Response(TransferenciaSerializer(services.confirmar_salida(request.user, self.get_object())).data) 
 
    @action(detail=True, methods=["post"], url_path="confirmar-ingreso") 
    def confirmar_ingreso(self, request, pk=None): 
        t = services.confirmar_ingreso(request.user, self.get_object(), request.data.get("recibidas")) 
        return Response(TransferenciaSerializer(t).data) 
 
    @action(detail=True, methods=["post"]) 
    def cancelar(self, request, pk=None): 
        return Response(TransferenciaSerializer(services.cancelar(self.get_object())).data) 