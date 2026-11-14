from django.db import transaction 
from rest_framework.exceptions import ValidationError 
 
from inventario.models import DetalleMovimiento, Existencia, Movimiento 
from inventario.services import existencias_fefo 
from .models import DetalleTransferencia, Transferencia 
 
E = Transferencia.Estado 
 
 
@transaction.atomic 
def crear_transferencia(usuario, origen, destino, producto, cantidad): 
    """Reserva el stock del origen por FEFO (RF-18, RF-19).""" 
    if origen == destino: 
        raise ValidationError("El almacén de origen y destino deben ser distintos.") 
    if origen.en_conteo or destino.en_conteo: 
        raise ValidationError("Un almacén está en conteo físico; no admite movimientos.") 
    if int(cantidad) <= 0: 
        raise ValidationError("La cantidad debe ser mayor a cero.") 
    cantidad = int(cantidad) 
    existencias = existencias_fefo(producto, origen) 
    disponible = sum(e.disponible for e in existencias) 
    if cantidad > disponible: 
        raise ValidationError(f"Stock insuficiente: hay {disponible} disponibles en {origen.nombre}.") 
    t = Transferencia.objects.create(origen=origen, destino=destino, creada_por=usuario) 
    restante = cantidad 
    for e in existencias: 
        tomar = min(e.disponible, restante) 
        if tomar <= 0: 
            continue 
        e.reservada += tomar 
        e.version += 1 
        e.save() 
        DetalleTransferencia.objects.create(transferencia=t, lote=e.lote, cantidad=tomar) 
        restante -= tomar 
        if restante == 0: 
            break 
    return t 
 
 
@transaction.atomic 
def confirmar_salida(usuario, t): 
    if t.estado != E.PENDIENTE: 
        raise ValidationError("Solo una transferencia pendiente puede confirmar su salida.") 
    mov = Movimiento.objects.create(tipo=Movimiento.Tipo.TRANSFERENCIA_SALIDA, almacen=t.origen, 
                                    usuario=usuario, documento_origen=f"TRF-{t.pk}") 
    for d in t.detalles.all(): 
        e = Existencia.objects.select_for_update().get(lote=d.lote, almacen=t.origen) 
        e.cantidad -= d.cantidad 
        e.reservada -= d.cantidad 
        e.version += 1 
        e.save() 
        DetalleMovimiento.objects.create(movimiento=mov, lote=d.lote, cantidad=d.cantidad) 
    t.estado = E.EN_TRANSITO 
    t.save(update_fields=["estado"]) 
    return t 
 
 
@transaction.atomic 
def confirmar_ingreso(usuario, t, recibidas=None): 
    """`recibidas`: {detalle_id: cantidad}. Si no se indica, se asume todo lo enviado.""" 
    if t.estado != E.EN_TRANSITO: 
        raise ValidationError("Solo una transferencia en tránsito puede confirmar su ingreso.") 
    recibidas = recibidas or {} 
    mov = Movimiento.objects.create(tipo=Movimiento.Tipo.TRANSFERENCIA_INGRESO, almacen=t.destino, 
                                    usuario=usuario, documento_origen=f"TRF-{t.pk}") 
    for d in t.detalles.all(): 
        cant = int(recibidas.get(str(d.pk), recibidas.get(d.pk, d.cantidad))) 
        if cant < 0 or cant > d.cantidad: 
            raise ValidationError("La cantidad recibida no puede ser negativa ni mayor a la enviada.") 
        d.cantidad_recibida = cant 
        d.save(update_fields=["cantidad_recibida"]) 
        e, _ = Existencia.objects.select_for_update().get_or_create(lote=d.lote, almacen=t.destino) 
        e.cantidad += cant 
        e.version += 1 
        e.save() 
        DetalleMovimiento.objects.create(movimiento=mov, lote=d.lote, cantidad=cant) 
    t.estado = E.COMPLETADA 
    t.save(update_fields=["estado"]) 
    return t 
 
 
@transaction.atomic 
def cancelar(t): 
    if t.estado != E.PENDIENTE: 
        raise ValidationError("Solo se puede cancelar una transferencia pendiente.") 
    for d in t.detalles.all():  # libera la reserva (RF-18) 
        e = Existencia.objects.select_for_update().get(lote=d.lote, almacen=t.origen) 
        e.reservada -= d.cantidad 
        e.version += 1 
        e.save() 
    t.estado = E.CANCELADA 
    t.save(update_fields=["estado"]) 
    return t 