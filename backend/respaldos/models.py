from django.conf import settings
from django.db import models


class RegistroRespaldo(models.Model):
    archivo = models.CharField(max_length=255)
    tamano = models.PositiveBigIntegerField(default=0)
    fecha = models.DateTimeField(auto_now_add=True)
    ok = models.BooleanField(default=False)
    error = models.TextField(blank=True, default="")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="respaldos",
    )

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        estado = "Correcto" if self.ok else "Fallido"
        return f"{self.archivo} - {estado}"
