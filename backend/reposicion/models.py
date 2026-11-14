from django.db import models
from almacenes.models import Almacen
from inventario.models import Lote
from productos.models import Producto


class ReglaReposicion(models.Model):
    """RF-40: punto de reorden = demanda diaria x tiempo de entrega + stock de seguridad."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    stock_minimo = models.PositiveIntegerField(default=0)
    stock_seguridad = models.PositiveIntegerField(default=0)
    stock_maximo = models.PositiveIntegerField(default=0)
    demanda_diaria = models.PositiveIntegerField(default=0)
    tiempo_entrega_dias = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = [("producto", "almacen")]

    @property
    def punto_reorden(self):
        return self.demanda_diaria * self.tiempo_entrega_dias + self.stock_seguridad

class Alerta(models.Model):
    class Tipo(models.TextChoices):
        REPOSICION = "REPOSICION", "Reposicion"
        VENCIMIENTO = "VENCIMIENTO", "Vencimiento"

    class Estado(models.TextChoices):
        ABIERTA = "ABIERTA", "Abierta"
        ATENDIDA = "ATENDIDA", "Atendida"
        DESCARTADA = "DESCARTADA", "Descartada"

    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, null=True, on_delete=models.CASCADE)
    lote = models.ForeignKey(Lote, null=True, blank=True, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=250)
    cantidad_sugerida = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.ABIERTA)
    motivo = models.CharField(max_length=200, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]