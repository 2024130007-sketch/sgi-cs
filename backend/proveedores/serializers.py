from rest_framework import serializers
from .models import Proveedor

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ["id", "ruc", "razon_social", "correo", "tiempo_entrega_dias", "activo"]
        extra_kwargs = {"ruc": {"validators": []}}

    def validate_ruc(self, valor):
        valor = valor.strip()
        if not (valor.isdigit() and len(valor) == 11):
            raise serializers.ValidationError("El RUC debe tener exactamente 11 dígitos.")  # RF-10
        qs = Proveedor.objects.filter(ruc=valor)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un proveedor con ese RUC.")
        return valor

    def validate_tiempo_entrega_dias(self, valor):
        if valor < 1:
            raise serializers.ValidationError("El tiempo de entrega debe ser de al menos 1 día.")
        return valor
