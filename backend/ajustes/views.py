from rest_framework import viewsets 
from rest_framework.decorators import action 
from rest_framework.response import Response 
  
from config.permisos import roles_permitidos 
from usuarios.models import Usuario 
from . import services 
from .models import Ajuste, Baja 
from .serializers import (AjusteSerializer, BajaEntradaSerializer, BajaSerializer, ConteoSerializer, 
                          IniciarConteoSerializer) 
  
R = Usuario.Rol 
PuedeAjustar = roles_permitidos(R.ADMINISTRADOR, R.JEFE_ALMACEN)  # lectura para todos, escritura solo ellos 
  
  
class AjusteViewSet(viewsets.ReadOnlyModelViewSet): 
    """/api/ajustes/ (CU-06, RF-23 y RF-24).""" 
    serializer_class = AjusteSerializer 
    permission_classes = [PuedeAjustar] 
    queryset = Ajuste.objects.select_related("almacen", "usuario").prefetch_related( 
        "detalles__lote__producto") 
  
    def create(self, request): 
        s = IniciarConteoSerializer(data=request.data) 
        s.is_valid(raise_exception=True) 
        ajuste = services.iniciar_conteo(request.user, s.validated_data["almacen"], 
                                         s.validated_data["observacion"]) 
        return Response(AjusteSerializer(ajuste).data, status=201) 
  
    @action(detail=True, methods=["post"]) 
    def conteo(self, request, pk=None): 
        s = ConteoSerializer(data=request.data) 
        s.is_valid(raise_exception=True) 
        ajuste = services.registrar_conteo(self.get_object(), s.validated_data["conteos"]) 
        return Response(AjusteSerializer(ajuste).data) 
  
    @action(detail=True, methods=["post"]) 
    def cerrar(self, request, pk=None): 
        return Response(AjusteSerializer(services.cerrar_conteo(request.user, self.get_object())).data) 
  
    @action(detail=True, methods=["post"]) 
    def cancelar(self, request, pk=None): 
        return Response(AjusteSerializer(services.cancelar_conteo(self.get_object())).data) 
  
  
class BajaViewSet(viewsets.ReadOnlyModelViewSet): 
    """/api/bajas/ (CU-07, RF-25 y RF-26).""" 
    serializer_class = BajaSerializer 
    permission_classes = [PuedeAjustar] 
    queryset = Baja.objects.select_related("almacen", "lote__producto", "proveedor", "usuario") 
  
    def create(self, request): 
        s = BajaEntradaSerializer(data=request.data) 
        s.is_valid(raise_exception=True) 
        d = s.validated_data 
        baja = services.registrar_baja(request.user, d["existencia"], d["cantidad"], d["tipo"], 
                                       d["motivo"], d["proveedor"]) 
        return Response(BajaSerializer(baja).data, status=201)