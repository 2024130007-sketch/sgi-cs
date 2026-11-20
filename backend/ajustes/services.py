from datetime import date 
  
from django.db import transaction 
from django.utils import timezone 
from rest_framework.exceptions import ValidationError 
  
from inventario.models import DetalleMovimiento, Existencia, Movimiento 
from .models import Ajuste, Baja, DetalleAjuste 
  
E = Ajuste.Estado 
  
  
@transaction.atomic 
def iniciar_conteo(usuario, almacen, observacion=""): 
    """RF-23 y RF-24: congela los movimientos del almacén y toma una foto del stock.""" 
    if not almacen.activo: 
        raise ValidationError("El almacén está desactivado.") 
    if almacen.en_conteo: 
        raise ValidationError("El almacén ya está en conteo físico.") 
    ajuste = Ajuste.objects.create(almacen=almacen, usuario=usuario, observacion=observacion) 
    for e in Existencia.objects.filter(almacen=almacen, cantidad__gt=0).select_related("lote"): 
        DetalleAjuste.objects.create(ajuste=ajuste, lote=e.lote, cantidad_sistema=e.cantidad) 
    if not ajuste.detalles.exists(): 
        raise ValidationError("El almacén no tiene stock para contar.") 
    almacen.en_conteo = True 
    almacen.save(update_fields=["en_conteo"]) 
    return ajuste 
  
  
@transaction.atomic 
def registrar_conteo(ajuste, conteos): 
    """`conteos`: {detalle_id: cantidad_contada}. Se puede llamar varias veces.""" 
    if ajuste.estado != E.EN_CONTEO: 
        raise ValidationError("Solo se puede registrar conteo en un ajuste en conteo.") 
    if not conteos: 
        raise ValidationError("Indique al menos una cantidad contada.") 
    detalles = {d.pk: d for d in ajuste.detalles.all()} 
    for clave, valor in conteos.items(): 
        detalle = detalles.get(int(clave)) 
        if detalle is None: 
            raise ValidationError(f"La línea {clave} no pertenece a este ajuste.") 
        if valor is None or str(valor).strip() == "": 
            continue 
        cantidad = int(valor) 
        if cantidad < 0: 
            raise ValidationError("La cantidad contada no puede ser negativa.") 
        detalle.cantidad_contada = cantidad 
        detalle.save(update_fields=["cantidad_contada"]) 
    return ajuste 
  
  
@transaction.atomic 
def cerrar_conteo(usuario, ajuste): 
    """RF-24: aplica las diferencias al stock y registra los movimientos de ajuste en el kardex.""" 
    if ajuste.estado != E.EN_CONTEO: 
        raise ValidationError("Solo se puede cerrar un ajuste en conteo.") 
    detalles = list(ajuste.detalles.select_related("lote")) 
    sin_contar = [d for d in detalles if d.cantidad_contada is None] 
    if sin_contar: 
        raise ValidationError(f"Faltan {len(sin_contar)} línea(s) por contar.") 
    movimientos = {} 
    for d in detalles: 
        e = Existencia.objects.select_for_update().get(lote=d.lote, almacen=ajuste.almacen) 
        diferencia = d.cantidad_contada - e.cantidad 
        if d.cantidad_contada < e.reservada: 
            raise ValidationError( 
                f"La cantidad contada del lote {d.lote.numero} es menor que la reservada ({e.reservada}).") 
        if diferencia == 0: 
            continue 
        signo = "+" if diferencia > 0 else "-" 
        if signo not in movimientos:  # un movimiento por signo, para que el kardex muestre sobrante y faltante 
            movimientos[signo] = Movimiento.objects.create( 
                tipo=Movimiento.Tipo.AJUSTE, almacen=ajuste.almacen, usuario=usuario, 
                documento_origen=f"AJ-{ajuste.pk} ({signo})") 
        e.cantidad = d.cantidad_contada 
        e.version += 1 
        e.save() 
        DetalleMovimiento.objects.create(movimiento=movimientos[signo], lote=d.lote, cantidad=abs(diferencia)) 
    ajuste.estado = E.CERRADO 
    ajuste.fecha_cierre = timezone.now() 
    ajuste.save(update_fields=["estado", "fecha_cierre"]) 
    ajuste.almacen.en_conteo = False 
    ajuste.almacen.save(update_fields=["en_conteo"]) 
    return ajuste 
  
  
@transaction.atomic 
def cancelar_conteo(ajuste): 
    if ajuste.estado != E.EN_CONTEO: 
        raise ValidationError("Solo se puede cancelar un ajuste en conteo.") 
    ajuste.estado = E.CANCELADO 
    ajuste.fecha_cierre = timezone.now() 
    ajuste.save(update_fields=["estado", "fecha_cierre"]) 
    ajuste.almacen.en_conteo = False 
    ajuste.almacen.save(update_fields=["en_conteo"]) 
    return ajuste 
  
  
@transaction.atomic 
def registrar_baja(usuario, existencia, cantidad, tipo, motivo, proveedor=None): 
    """RF-25 y RF-26: descuenta stock por vencimiento, daño o devolución a un proveedor.""" 
    almacen, lote = existencia.almacen, existencia.lote 
    if not almacen.activo: 
        raise ValidationError("El almacén está desactivado.") 
    if almacen.en_conteo: 
        raise ValidationError("El almacén está en conteo físico; no admite movimientos.") 
    if tipo not in Baja.Tipo.values: 
        raise ValidationError("Tipo de baja no válido.") 
    cantidad = int(cantidad) 
    if cantidad <= 0: 
        raise ValidationError("La cantidad debe ser mayor a cero.") 
    motivo = (motivo or "").strip() 
    if not motivo: 
        raise ValidationError("Indique el motivo de la baja.") 
    if tipo == Baja.Tipo.VENCIMIENTO and not (lote.fecha_vencimiento and lote.fecha_vencimiento < date.today()): 
        raise ValidationError("Solo se puede dar de baja por vencimiento un lote ya vencido.") 
    if tipo == Baja.Tipo.DEVOLUCION: 
        if proveedor is None: 
            raise ValidationError("La devolución exige indicar el proveedor.") 
        if not proveedor.activo: 
            raise ValidationError("El proveedor está desactivado.") 
    else: 
        proveedor = None 
    existencia = Existencia.objects.select_for_update().get(pk=existencia.pk) 
    if cantidad > existencia.disponible: 
        raise ValidationError( 
            f"Stock insuficiente: solicitó {cantidad} y hay {existencia.disponible} disponibles.") 
    existencia.cantidad -= cantidad 
    existencia.version += 1 
    existencia.save() 
    mov = Movimiento.objects.create(tipo=Movimiento.Tipo.BAJA, almacen=almacen, usuario=usuario, 
                                    documento_origen=f"BAJA-{tipo}") 
    DetalleMovimiento.objects.create(movimiento=mov, lote=lote, cantidad=cantidad) 
    return Baja.objects.create(almacen=almacen, lote=lote, cantidad=cantidad, tipo=tipo, motivo=motivo, 
                               proveedor=proveedor, usuario=usuario, movimiento=mov)