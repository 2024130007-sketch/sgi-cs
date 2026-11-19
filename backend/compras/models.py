from django.conf import settings
from django.db import models

from almacenes.models import Almacen
from productos.models import Producto
from proveedores.models import Proveedor


class OrdenCompra(models.Model):
    """RF-35: orden de compra a un proveedor, destinada a un almacén."""

    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        PENDIENTE = "PENDIENTE", "Pendiente de aprobación"
        APROBADA = "APROBADA", "Aprobada"
        RECHAZADA = "RECHAZADA", "Rechazada"
        ENVIADA = "ENVIADA", "Enviada al proveedor"
        RECIBIDA_PARCIAL = "RECIBIDA_PARCIAL", "Recibida parcialmente"
        RECIBIDA = "RECIBIDA", "Recibida"
        CANCELADA = "CANCELADA", "Cancelada"

    proveedor = models.ForeignKey(Proveedor, related_name="ordenes", on_delete=models.PROTECT)
    almacen_destino = models.ForeignKey(Almacen, related_name="+", on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR)
    observacion = models.CharField(max_length=200, blank=True)
    creada_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.PROTECT)
    aprobada_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", null=True, blank=True,
                                     on_delete=models.SET_NULL)
    motivo_rechazo = models.CharField(max_length=200, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"OC-{self.pk}"

    @property
    def total(self):
        return sum(d.subtotal for d in self.detalles.all())


class DetalleOrdenCompra(models.Model):
    orden = models.ForeignKey(OrdenCompra, related_name="detalles", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_recibida = models.PositiveIntegerField(default=0)  # la actualiza la recepción (RF-37)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    @property
    def pendiente(self):
        return self.cantidad - self.cantidad_recibida
