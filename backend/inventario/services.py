"""Servicio de inventario (clase ServicioInventario del Hito 1)."""
from datetime import date

from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import DetalleMovimiento, Existencia, Lote, Movimiento


def _validar_almacen(almacen):
    if not almacen.activo:
        raise ValidationError("El almacén está desactivado.")
    if almacen.en_conteo:
        raise ValidationError("El almacén está en conteo físico; no admite movimientos.")  # RF-24


@transaction.atomic
def registrar_ingreso(usuario, almacen, producto, cantidad, numero_lote="", fecha_vencimiento=None,
                      proveedor=None, documento="", fecha_fabricacion=None):
    """RF-14, RF-15, RF-31."""
    _validar_almacen(almacen)
    if not producto.activo:
        raise ValidationError("El producto está desactivado.")
    if cantidad is None or int(cantidad) <= 0:
        raise ValidationError("La cantidad debe ser mayor a cero.")  # RF-15
    cantidad = int(cantidad)
    numero_lote = (numero_lote or "").strip()
    if producto.requiere_lote and not numero_lote:
        raise ValidationError("Este producto exige indicar el número de lote.")
    if producto.requiere_vencimiento:
        if not fecha_vencimiento:
            raise ValidationError("Este producto exige indicar la fecha de vencimiento.")
        if fecha_vencimiento < date.today():
            raise ValidationError("La fecha de vencimiento no puede ser anterior a hoy.")  # RF-15
    lote, _ = Lote.objects.get_or_create(
        producto=producto, numero=numero_lote or "SIN-LOTE",
        defaults={"proveedor": proveedor, "fecha_vencimiento": fecha_vencimiento,
                  "fecha_fabricacion": fecha_fabricacion})
    existencia, _ = Existencia.objects.select_for_update().get_or_create(lote=lote, almacen=almacen)
    existencia.cantidad += cantidad
    existencia.version += 1
    existencia.save()
    mov = Movimiento.objects.create(tipo=Movimiento.Tipo.INGRESO, almacen=almacen, usuario=usuario,
                                    documento_origen=documento)
    DetalleMovimiento.objects.create(movimiento=mov, lote=lote, cantidad=cantidad)
    return mov


def existencias_fefo(producto, almacen):
    """Existencias utilizables ordenadas por vencimiento (RF-17); excluye vencidos y cuarentena (RF-19)."""
    qs = (Existencia.objects.select_for_update()
          .filter(producto_filtro(producto), almacen=almacen, cantidad__gt=0,
                  lote__estado=Lote.Estado.ACTIVO)
          .exclude(lote__fecha_vencimiento__lt=date.today()))
    # Sin vencimiento al final; con vencimiento, el más próximo primero.
    return sorted(qs, key=lambda e: (e.lote.fecha_vencimiento is None, e.lote.fecha_vencimiento or date.max))


def producto_filtro(producto):
    from django.db.models import Q
    return Q(lote__producto=producto)


@transaction.atomic
def registrar_salida(usuario, almacen, producto, cantidad, documento=""):
    """RF-16, RF-17, RF-19: descuenta por FEFO y rechaza si supera el disponible."""
    _validar_almacen(almacen)
    if cantidad is None or int(cantidad) <= 0:
        raise ValidationError("La cantidad debe ser mayor a cero.")
    cantidad = int(cantidad)
    existencias = existencias_fefo(producto, almacen)
    disponible = sum(e.disponible for e in existencias)
    if cantidad > disponible:
        raise ValidationError(
            f"Stock insuficiente: solicitó {cantidad} y hay {disponible} disponibles en {almacen.nombre}.")
    mov = Movimiento.objects.create(tipo=Movimiento.Tipo.SALIDA, almacen=almacen, usuario=usuario,
                                    documento_origen=documento)
    restante = cantidad
    for e in existencias:
        if restante == 0:
            break
        tomar = min(e.disponible, restante)
        if tomar <= 0:
            continue
        e.cantidad -= tomar
        e.version += 1
        e.save()
        DetalleMovimiento.objects.create(movimiento=mov, lote=e.lote, cantidad=tomar)
        restante -= tomar
    from reposicion.services import evaluar_reposicion  # RF-41: se evalúa tras cada salida
    evaluar_reposicion(producto, almacen)
    return mov
