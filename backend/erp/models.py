from django.db import models
from django.utils import timezone

class EquivalenciaERP(models.Model):
    """#30: Relación entre el SKU del sistema y el código del ERP."""
    producto = models.OneToOneField("productos.Producto", on_delete=models.CASCADE, related_name="equivalencia_erp")
    codigo_erp = models.CharField(max_length=40, unique=True)
    unidad_erp = models.CharField(max_length=20, default="UN")

    def __str__(self):
        return f"{self.producto.sku} -> {self.codigo_erp}"

class ColaERP(models.Model):
    """#29: Cola de eventos pendientes de enviar al ERP."""
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        ENVIADO = "ENVIADO", "Enviado"
        ERROR = "ERROR", "Error"

    tipo = models.CharField(max_length=30)  # "RECEPCION" | "ORDEN_APROBADA"
    payload = models.JSONField()  # Los datos que se enviarán al ERP
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)
    intentos = models.PositiveSmallIntegerField(default=0)
    proximo_intento = models.DateTimeField(default=timezone.now)
    ultimo_error = models.CharField(max_length=300, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["creado"]