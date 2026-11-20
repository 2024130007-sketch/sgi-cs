from django.conf import settings
from django.db import models
from compras.models import DetalleOrdenCompra, OrdenCompra
from inventario.models import Lote

class Recepcion(models.Model):
    """RF-37 y RF-38: Recepción total o parcial de una orden de compra."""
    class Estado(models.TextChoices):
        COMPLETA = "COMPLETA", "Completa"
        PARCIAL = "PARCIAL", "Parcial"

    orden_compra = models.ForeignKey(OrdenCompra, on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    documento = models.CharField(max_length=60, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PARCIAL)

    class Meta:
        ordering = ["-fecha"]

class DetalleRecepcion(models.Model):
    recepcion = models.ForeignKey(Recepcion, related_name="detalles", on_delete=models.CASCADE)
    detalle_orden = models.ForeignKey(DetalleOrdenCompra, on_delete=models.PROTECT)
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()