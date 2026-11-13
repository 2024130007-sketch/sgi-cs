from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as ErrorDeDjango
from rest_framework import serializers

from .models import Usuario


def datos_de_sesion(usuario):
    """Lo que recibe Angular al iniciar sesión (coincide con UsuarioSesion en auth.service.ts)."""
    return {
        "id": usuario.id,
        "email": usuario.email,
        "first_name": usuario.first_name,
        "rol": usuario.rol,
        "rol_display": usuario.get_rol_display(),
    }


class UsuarioSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(error_messages={
        "required": "El correo es obligatorio.",
        "blank": "El correo es obligatorio.",
        "invalid": "Escribe un correo con formato válido.",
    })
    first_name = serializers.CharField(max_length=150, error_messages={
        "required": "El nombre es obligatorio.",
        "blank": "El nombre es obligatorio.",
    })
    password = serializers.CharField(write_only=True, required=False, error_messages={
        "blank": "La contraseña no puede estar vacía.",
    })
    rol_display = serializers.CharField(source="get_rol_display", read_only=True)
    bloqueado = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ["id", "email", "first_name", "rol", "rol_display", "is_active",
                  "password", "bloqueado", "intentos_fallidos"]
        read_only_fields = ["intentos_fallidos"]

    def get_bloqueado(self, usuario):
        return usuario.esta_bloqueado()

    def validate_email(self, valor):
        correo = valor.strip().lower()
        otros = Usuario.objects.filter(email__iexact=correo)
        if self.instance is not None:
            otros = otros.exclude(pk=self.instance.pk)
        if otros.exists():
            raise serializers.ValidationError("Ese correo ya está registrado.")
        return correo

    def validate_password(self, valor):
        try:
            validate_password(valor)   # usa la regla de mínimo 8 caracteres de settings.py
        except ErrorDeDjango as e:
            raise serializers.ValidationError(list(e.messages))
        return valor

    def validate(self, datos):
        # al crear, la contraseña es obligatoria
        if self.instance is None and not datos.get("password"):
            raise serializers.ValidationError({"password": "La contraseña es obligatoria."})

        # el administrador no puede quitarse a sí mismo el acceso
        usuario_actual = self.context["request"].user
        if self.instance is not None and self.instance == usuario_actual:
            if "rol" in datos and datos["rol"] != Usuario.Rol.ADMINISTRADOR:
                raise serializers.ValidationError("No puedes quitarte tu propio rol de administrador.")
            if datos.get("is_active") is False:
                raise serializers.ValidationError("No puedes desactivar tu propio usuario.")
        return datos

    def create(self, datos):
        clave = datos.pop("password")
        return Usuario.objects.create_user(username=datos["email"], password=clave, **datos)

    def update(self, usuario, datos):
        clave = datos.pop("password", None)
        for campo, valor in datos.items():
            setattr(usuario, campo, valor)
        if "email" in datos:
            usuario.username = datos["email"]
        if clave:
            usuario.set_password(clave)
        usuario.save()
        return usuario
