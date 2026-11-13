from datetime import timedelta

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone

MAX_INTENTOS = 5        # intentos fallidos seguidos antes de bloquear la cuenta
MINUTOS_BLOQUEO = 15    # cuánto dura el bloqueo


class UsuarioManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        # el superusuario que se crea con "createsuperuser" siempre es ADMINISTRADOR
        extra_fields.setdefault("rol", "ADMINISTRADOR")
        return super().create_superuser(username, email, password, **extra_fields)


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
        JEFE_ALMACEN = "JEFE_ALMACEN", "Jefe de almacén"
        OPERARIO = "OPERARIO", "Operario"
        COMPRADOR = "COMPRADOR", "Comprador"

    # el correo es lo que se usa para iniciar sesión, por eso debe ser único
    email = models.EmailField("correo", unique=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.OPERARIO)
    intentos_fallidos = models.PositiveSmallIntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.email} ({self.get_rol_display()})"

    def esta_bloqueado(self):
        return self.bloqueado_hasta is not None and timezone.now() < self.bloqueado_hasta

    def minutos_restantes(self):
        segundos = (self.bloqueado_hasta - timezone.now()).total_seconds()
        return max(1, int(segundos // 60) + 1)

    def registrar_intento_fallido(self):
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= MAX_INTENTOS:
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=MINUTOS_BLOQUEO)
        self.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])

    def reiniciar_intentos(self):
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])
