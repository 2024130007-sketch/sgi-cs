from django.conf import settings
from django.db import models

from almacenes.models import Almacen
from productos.models import Producto
from proveedores.models import Proveedor


class Lote(models.Model):
    """RF-31: lote con producto, proveedor y fechas."""

    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        CUARENTENA = "CUARENTENA", "En cuarentena"

    producto = models.ForeignKey(Producto, related_name="lotes", on_delete=models.PROTECT)
    proveedor = models.ForeignKey(Proveedor, null=True, blank=True, on_delete=models.SET_NULL)
    numero = models.CharField(max_length=50)
    fecha_fabricacion = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.ACTIVO)

    class Meta:
        unique_together = [("producto", "numero")]

    def __str__(self):
        return f"{self.producto.sku} / {self.numero}"


class Existencia(models.Model):
    """Stock de un lote en un almacén. `version` permite el bloqueo optimista (RF-29)."""
    lote = models.ForeignKey(Lote, related_name="existencias", on_delete=models.PROTECT)
    almacen = models.ForeignKey(Almacen, related_name="existencias", on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=0)    # física
    reservada = models.PositiveIntegerField(default=0)
    en_transito = models.PositiveIntegerField(default=0)
    version = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("lote", "almacen")]

    @property
    def disponible(self):
        return self.cantidad - self.reservada


class Movimiento(models.Model):
    """Kardex (RF-32)."""

    class Tipo(models.TextChoices):
        INGRESO = "INGRESO", "Ingreso"
        SALIDA = "SALIDA", "Salida"
        TRANSFERENCIA_SALIDA = "TRANSF_SALIDA", "Transferencia (salida)"
        TRANSFERENCIA_INGRESO = "TRANSF_INGRESO", "Transferencia (ingreso)"
        AJUSTE = "AJUSTE", "Ajuste"
        BAJA = "BAJA", "Baja"

    tipo = models.CharField(max_length=15, choices=Tipo.choices)
    almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    documento_origen = models.CharField(max_length=60, blank=True)

    class Meta:
        ordering = ["-fecha", "-id"]


class DetalleMovimiento(models.Model):
    movimiento = models.ForeignKey(Movimiento, related_name="detalles", on_delete=models.CASCADE)
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
