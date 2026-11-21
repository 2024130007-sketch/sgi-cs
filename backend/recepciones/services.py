from django.db import transaction
from rest_framework.exceptions import ValidationError

from compras.models import DetalleOrdenCompra, OrdenCompra
from inventario.services import registrar_ingreso
from .models import DetalleRecepcion, Recepcion

E = OrdenCompra.Estado
RECIBIBLES = (E.APROBADA, E.ENVIADA, E.RECIBIDA_PARCIAL)


@transaction.atomic
def registrar_recepcion(usuario, orden_compra, detalles, documento=""):
    """RF-37 y RF-38: recepción total o parcial. Todo o nada: si una línea falla, no se ingresa ninguna.
    `detalles`: lista de dicts {detalle_orden, cantidad, numero_lote, fecha_vencimiento}.
    """
    if orden_compra.estado not in RECIBIBLES:
        raise ValidationError("Solo se pueden recibir órdenes aprobadas, enviadas o parcialmente recibidas.")
    if not detalles:
        raise ValidationError("Indique al menos una línea con cantidad recibida.")

    recepcion = Recepcion.objects.create(orden_compra=orden_compra, usuario=usuario, documento=documento)

    for item in detalles:
        detalle = DetalleOrdenCompra.objects.select_for_update().select_related("producto").get(
            pk=item["detalle_orden"].pk)
        if detalle.orden_id != orden_compra.pk:
            raise ValidationError(f"El producto {detalle.producto.sku} no pertenece a esta orden.")
        cantidad = int(item["cantidad"])
        if cantidad <= 0:
            raise ValidationError(f"La cantidad de {detalle.producto.sku} debe ser mayor a cero.")
        if cantidad > detalle.pendiente:
            raise ValidationError(
                f"{detalle.producto.sku}: se pidieron {detalle.cantidad}, ya se recibieron "
                f"{detalle.cantidad_recibida} y solo quedan {detalle.pendiente} por recibir.")

        # El ingreso al stock crea el lote y el movimiento (kardex).
        mov = registrar_ingreso(usuario, orden_compra.almacen_destino, detalle.producto, cantidad,
                                item.get("numero_lote", ""), item.get("fecha_vencimiento"),
                                proveedor=orden_compra.proveedor, documento=documento or f"OC-{orden_compra.pk}")
        lote = mov.detalles.first().lote

        detalle.cantidad_recibida += cantidad
        detalle.save(update_fields=["cantidad_recibida"])
        DetalleRecepcion.objects.create(recepcion=recepcion, detalle_orden=detalle, lote=lote, cantidad=cantidad)

    completa = all(d.pendiente == 0 for d in orden_compra.detalles.all())
    recepcion.estado = Recepcion.Estado.COMPLETA if completa else Recepcion.Estado.PARCIAL
    recepcion.save(update_fields=["estado"])
    orden_compra.estado = E.RECIBIDA if completa else E.RECIBIDA_PARCIAL
    orden_compra.save(update_fields=["estado"])
    return recepcion