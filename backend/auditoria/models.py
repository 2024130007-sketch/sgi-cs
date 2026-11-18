
from django.conf import settings
from django.db import models


class Bitacora(models.Model):

    class Accion(models.TextChoices):
        CREAR = "CREAR", "Crear"
        MODIFICAR = "MODIFICAR", "Modificar"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+"
    )

    accion = models.CharField(
        max_length=12,
        choices=Accion.choices
    )

    entidad = models.CharField(max_length=40)
    entidad_id = models.PositiveIntegerField(null=True, blank=True)
    detalle = models.CharField(max_length=250, blank=True)
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-fecha", "-id"]
        verbose_name = "registro de bitácora"
        verbose_name_plural = "bitácora"

    def __str__(self):
        return f"{self.fecha} - {self.accion} - {self.entidad} #{self.entidad_id}"
