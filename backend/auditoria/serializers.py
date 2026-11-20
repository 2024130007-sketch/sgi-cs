
from rest_framework import serializers

from .models import Bitacora


class BitacoraSerializer(serializers.ModelSerializer):
    usuario_email = serializers.CharField(
        source="usuario.email",
        read_only=True,
        allow_null=True
    )

    accion_display = serializers.CharField(
        source="get_accion_display",
        read_only=True
    )

    class Meta:
        model = Bitacora
        fields = [
            "id",
            "fecha",
            "usuario",
            "usuario_email",
            "accion",
            "accion_display",
            "entidad",
            "entidad_id",
            "detalle",
        ]
        read_only_fields = fields
