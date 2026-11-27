from rest_framework import serializers

from .models import RegistroRespaldo


class RegistroRespaldoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroRespaldo
        fields = [
            "id",
            "archivo",
            "tamano",
            "fecha",
            "ok",
            "error",
            "usuario",
        ]
        read_only_fields = fields
