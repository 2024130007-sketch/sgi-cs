from django.db import models

class Proveedor(models.Model):
    """RF-10."""
    ruc = models.CharField(max_length=11, unique=True)
    razon_social = models.CharField(max_length=150)
    correo = models.EmailField()
    tiempo_entrega_dias = models.PositiveIntegerField(default=1)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["razon_social"]
        verbose_name_plural = "proveedores"

    def __str__(self):
        return f"{self.ruc} {self.razon_social}"
