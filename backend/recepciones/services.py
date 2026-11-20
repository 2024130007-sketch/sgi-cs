from django.db import transaction
from rest_framework.exceptions import ValidationError
from inventario.models import Lote
from .models import Recepcion, DetalleRecepcion

@transaction.atomic
def registrar_recepcion(usuario, orden_compra, detalles, documento=""):
    """RF-37 y RF-38: Procesa la recepción total o parcial."""
    # 1. Validar que la orden esté aprobada o enviada
    if orden_compra.estado not in ["APROBADA", "ENVIADA"]:
        raise ValidationError("Solo se pueden recibir órdenes aprobadas o enviadas.")

    # 2. Crear la cabecera de la recepción
    recepcion = Recepcion.objects.create(
        orden_compra=orden_compra,
        usuario=usuario,
        documento=documento,
        estado=Recepcion.Estado.PARCIAL # Por defecto parcial, se actualiza al final
    )

    todo_completo = True

    # 3. Procesar cada línea recibida
    for item in detalles:
        # Aquí se buscaría el detalle de la orden de Adrian, su lote y cantidad
        # (Como Adrian no ha subido su parte, dejamos la estructura base)
        pass

    # 4. Actualizar estado final
    if todo_completo:
        recepcion.estado = Recepcion.Estado.COMPLETA
        recepcion.save()
        
    return recepcion