from rest_framework import serializers 
 
from .models import Almacen 

class AlmacenSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = Almacen 
        fields = ["id", "nombre", "direccion", "activo", "en_conteo"] 
        read_only_fields = ["en_conteo"] 
        extra_kwargs = {"nombre": {"validators": []}} 

    def validate_nombre(self, valor): 
        valor = valor.strip() 
        if not valor: 
            raise serializers.ValidationError("El nombre es obligatorio.") 
        qs = Almacen.objects.filter(nombre__iexact=valor) 
        if self.instance: 
            qs = qs.exclude(pk=self.instance.pk) 
        if qs.exists(): 
            raise serializers.ValidationError("Ya existe un almacén con ese nombre.") 
        return valor 
 
    def validate_direccion(self, valor): 
        if not valor.strip(): 
            raise serializers.ValidationError("La dirección es obligatoria.") 
        return valor.strip() 