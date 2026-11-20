from django.conf import settings
from django.db import models

from almacenes.models import Almacen
from inventario.models import Lote, Movimiento
from proveedores.models import Proveedor

class Ajuste(models.Model):

    class Estado(models.TextChoices):
        EN_CONTEO = "EN_CONTEO", "En_conteo"
        CERRADO = "CERRADO", "Cerrado"
        CANCELADO = "CANCELADO", "Cancelado"


    almacen= models.ForeignKey(Almacen, related_name='+', on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='+', on_delete=models.PROTECT)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.EN_CONTEO)
    observacion = models.CharField(max_length=200, blank=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_inicio", "-id"]


    def __srt___(self):
        return f"AJ-{self.pk}"


class DetalleAjuste(models.Model):
    ajuste = models.ForeignKey(Ajuste, related_name="detalles", on_delete=models.CASCADE)
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT)
    cantidad_sistema = models.PositiveIntegerField()
    cantidad_contada = models.PositiveIntegerField(null=True, blank=True)


    @property
    def diferencia(self):
        return None if self.cantidad_contada is None else self.cantidad_contada - self.cantidad_sistema


class Baja(models.Model):

    class Tipo(models.TextChoices):
        VENCIMIENTO= "VENCIMIENTO", "Vencimiento"
        DANO = "DANO", "Porducto dañado"
        DEVOLUCION = "DEVOLUCION", "Devolucion a proveedor"

    almacen = models.ForeignKey(Almacen, related_name="+", on_delete=models.PROTECT)
    lote = models.ForeignKey(Lote, related_name="+", on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    motivo = models.CharField(max_length=200)
    proveedor = models.ForeignKey(Proveedor, null=True, blank=True, related_name="+",
                                  on_delete=models.SET_NULL)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="+", on_delete=models.PROTECT)
    movimiento = models.ForeignKey(Movimiento, null=True, blank=True,related_name="+",
                                   on_delete=models.SET_NULL )
    fecha = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-fecha", "-id"]