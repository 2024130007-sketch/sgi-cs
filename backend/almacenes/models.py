from django.db import models


class Almacen(models.Model):
    """RF-09."""

    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=200)
    activo = models.BooleanField(default=True)
    en_conteo = models.BooleanField(default=False)  # RF-24 (se usará en el ajuste de inventario)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "almacenes"

    def __str__(self):
        return self.nombre
