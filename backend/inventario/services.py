"""Servicio de inventario (clase ServicioInventario del Hito 1)."""
from datetime import date
from functools import wraps

from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import APIException, ValidationError

from .models import DetalleMovimiento, Existencia, Lote, Movimiento

MAX_REINTENTOS = 3  # RF-29: intentos antes de avisar que el stock está en disputa


class ConflictoVersion(Exception):
    """Otra operación modificó la existencia entre su lectura y su escritura."""


class ConflictoStock(APIException):
    status_code = 409
    default_detail = "El stock fue modificado por otro usuario al mismo tiempo. Intente nuevamente."


def actualizar_existencia(existencia, delta_cantidad=0, delta_reservada=0):
    """Bloqueo optimista (RF-29): solo escribe si la `version` leída sigue vigente."""
    filas = Existencia.objects.filter(pk=existencia.pk, version=existencia.version).update(
        cantidad=F("cantidad") + delta_cantidad,
        reservada=F("reservada") + delta_reservada,
        version=F("version") + 1)
    if filas == 0:
        raise ConflictoVersion()
    existencia.refresh_from_db()


def con_reintentos(funcion):
    """Repite toda la operación si hubo conflicto de versión; al agotar los intentos responde 409."""
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        for intento in range(1, MAX_REINTENTOS + 1):
            try:
                return funcion(*args, **kwargs)
            except ConflictoVersion:
                if intento == MAX_REINTENTOS:
                    raise ConflictoStock()
    return envoltura


def _validar_almacen(almacen):
    if not almacen.activo:
        raise ValidationError("El almacén está desactivado.")
    if almacen.en_conteo:
        raise ValidationError("El almacén está en conteo físico; no admite movimientos.")  # RF-24


@con_reintentos
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
    actualizar_existencia(existencia, delta_cantidad=cantidad)
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


@con_reintentos
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
        actualizar_existencia(e, delta_cantidad=-tomar)
        DetalleMovimiento.objects.create(movimiento=mov, lote=e.lote, cantidad=tomar)
        restante -= tomar
    from reposicion.services import evaluar_reposicion  # RF-41: se evalúa tras cada salida
    evaluar_reposicion(producto, almacen)
    return mov


def cambiar_estado_lote(lote, estado, motivo=""):
    """RF-34: pone un lote en cuarentena o lo libera. La cuarentena exige motivo."""
    if estado not in Lote.Estado.values:
        raise ValidationError("Estado de lote no válido.")
    motivo = (motivo or "").strip()
    if estado == Lote.Estado.CUARENTENA and not motivo:
        raise ValidationError("Indique el motivo de la cuarentena.")
    if lote.estado == estado:
        raise ValidationError(f"El lote ya está en estado {lote.get_estado_display().lower()}.")
    lote.estado = estado
    lote.motivo_estado = motivo if estado == Lote.Estado.CUARENTENA else ""
    lote.save(update_fields=["estado", "motivo_estado"])
    return lote


def trazabilidad_lote(lote):
    """RF-33: dónde está el lote hoy y todos los movimientos que lo tocaron."""
    existencias = [
        {"almacen": e.almacen.nombre, "cantidad": e.cantidad, "reservada": e.reservada,
         "disponible": e.disponible}
        for e in lote.existencias.select_related("almacen").order_by("almacen__nombre")]
    detalles = (DetalleMovimiento.objects.filter(lote=lote)
                .select_related("movimiento__almacen", "movimiento__usuario")
                .order_by("movimiento__fecha", "id"))
    movimientos = [
        {"fecha": d.movimiento.fecha, "tipo": d.movimiento.tipo,
         "tipo_display": d.movimiento.get_tipo_display(), "almacen": d.movimiento.almacen.nombre,
         "usuario": d.movimiento.usuario.email, "cantidad": d.cantidad,
         "documento": d.movimiento.documento_origen}
        for d in detalles]
    return {"existencias": existencias, "movimientos": movimientos}
