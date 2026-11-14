from django.conf import settings 
from django.db import models 
 
from almacenes.models import Almacen 
from inventario.models import Lote 
 
 
class Transferencia(models.Model): 
    """RF-21: Pendiente -> En tránsito -> Completada.""" 
 
    class Estado(models.TextChoices): 
        PENDIENTE = "PENDIENTE", "Pendiente" 
        EN_TRANSITO = "EN_TRANSITO", "En tránsito" 
        COMPLETADA = "COMPLETADA", "Completada" 
        CANCELADA = "CANCELADA", "Cancelada" 
 
    origen = models.ForeignKey(Almacen, related_name="+", on_delete=models.PROTECT) 
    destino = models.ForeignKey(Almacen, related_name="+", on_delete=models.PROTECT) 
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE) 
    creada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT) 
    fecha = models.DateTimeField(auto_now_add=True) 
 
    class Meta: 
        ordering = ["-fecha"] 
 
 
class DetalleTransferencia(models.Model): 
    transferencia = models.ForeignKey(Transferencia, related_name="detalles", on_delete=models.CASCADE) 
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT) 
    cantidad = models.PositiveIntegerField() 
    cantidad_recibida = models.PositiveIntegerField(null=True, blank=True)  # RF-22 