"""Servicio de compras (clase ServicioCompras del Hito 1)."""
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import DetalleOrdenCompra, OrdenCompra

E = OrdenCompra.Estado


def _validar_cabecera(proveedor, almacen):
    if not proveedor.activo:
        raise ValidationError("El proveedor está desactivado.")
    if not almacen.activo:
        raise ValidationError("El almacén de destino está desactivado.")


def _limpiar_items(items):
    """Valida las líneas y devuelve [(producto, cantidad, precio)]."""
    if not items:
        raise ValidationError("La orden debe tener al menos un producto.")
    limpios, vistos = [], set()
    for it in items:
        producto = it["producto"]
        if not producto.activo:
            raise ValidationError(f"El producto {producto.sku} está desactivado.")
        if producto.pk in vistos:
            raise ValidationError(f"El producto {producto.sku} está repetido en la orden.")
        vistos.add(producto.pk)
        cantidad = int(it["cantidad"])
        if cantidad <= 0:
            raise ValidationError(f"La cantidad de {producto.sku} debe ser mayor a cero.")
        try:
            precio = Decimal(str(it.get("precio_unitario", 0)))
        except InvalidOperation:
            raise ValidationError(f"El precio de {producto.sku} no es válido.")
        if precio < 0:
            raise ValidationError(f"El precio de {producto.sku} no puede ser negativo.")
        limpios.append((producto, cantidad, precio))
    return limpios


def _guardar_items(orden, items):
    orden.detalles.all().delete()
    for producto, cantidad, precio in _limpiar_items(items):
        DetalleOrdenCompra.objects.create(orden=orden, producto=producto, cantidad=cantidad,
                                          precio_unitario=precio)


@transaction.atomic
def crear_orden(usuario, proveedor, almacen, items, observacion=""):
    """RF-35: crea la orden en estado Borrador."""
    _validar_cabecera(proveedor, almacen)
    orden = OrdenCompra.objects.create(proveedor=proveedor, almacen_destino=almacen,
                                       observacion=observacion, creada_por=usuario)
    _guardar_items(orden, items)
    return orden


@transaction.atomic
def editar_orden(orden, proveedor, almacen, items, observacion=""):
    if orden.estado != E.BORRADOR:
        raise ValidationError("Solo se puede modificar una orden en borrador.")
    _validar_cabecera(proveedor, almacen)
    orden.proveedor, orden.almacen_destino, orden.observacion = proveedor, almacen, observacion
    orden.save()
    _guardar_items(orden, items)
    return orden


def enviar_a_aprobacion(orden):
    if orden.estado != E.BORRADOR:
        raise ValidationError("Solo una orden en borrador puede enviarse a aprobación.")
    orden.estado = E.PENDIENTE
    orden.save(update_fields=["estado"])
    return orden


def aprobar(usuario, orden):
    """RF-36: aprueba la orden. Quien la creó no puede aprobarla (separación de funciones)."""
    if orden.estado != E.PENDIENTE:
        raise ValidationError("Solo una orden pendiente de aprobación puede aprobarse.")
    if orden.creada_por_id == usuario.pk:
        raise ValidationError("Quien creó la orden no puede aprobarla.")
    orden.estado = E.APROBADA
    orden.aprobada_por = usuario
    orden.fecha_aprobacion = timezone.now()
    orden.save(update_fields=["estado", "aprobada_por", "fecha_aprobacion"])
    return orden


def rechazar(usuario, orden, motivo):
    if orden.estado != E.PENDIENTE:
        raise ValidationError("Solo una orden pendiente de aprobación puede rechazarse.")
    motivo = (motivo or "").strip()
    if not motivo:
        raise ValidationError("Indique el motivo del rechazo.")
    orden.estado = E.RECHAZADA
    orden.motivo_rechazo = motivo
    orden.aprobada_por = usuario
    orden.save(update_fields=["estado", "motivo_rechazo", "aprobada_por"])
    return orden


def cancelar(orden):
    if orden.estado not in (E.BORRADOR, E.PENDIENTE, E.APROBADA):
        raise ValidationError("Esta orden ya no puede cancelarse.")
    orden.estado = E.CANCELADA
    orden.save(update_fields=["estado"])
    return orden
