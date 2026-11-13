
from django.db import models


class Producto(models.Model):

    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código SKU"
    )

    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre del producto"
    )

    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )

    marca = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Marca"
    )

    unidad_medida = models.CharField(
        max_length=30,
        default="UNIDAD",
        verbose_name="Unidad de medida"
    )

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Precio"
    )

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sku} - {self.nombre}"


class CodigoBarras(models.Model):

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="codigos_barras"
    )

    codigo = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Código de barras"
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.codigo} - {self.producto.nombre}"
