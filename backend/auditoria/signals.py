
from django.db.models.signals import post_save
from django.dispatch import receiver

from auditoria.models import Bitacora
from inventario.models import Lote, Existencia, Movimiento
from transferencias.models import Transferencia


def registrar_cambio(instance, created, usuario=None, detalle=""):
    accion = (
        Bitacora.Accion.CREAR
        if created
        else Bitacora.Accion.MODIFICAR
    )

    Bitacora.objects.create(
        usuario=usuario,
        accion=accion,
        entidad=instance.__class__.__name__,
        entidad_id=instance.pk,
        detalle=str(detalle)[:250],
    )


@receiver(post_save, sender=Lote)
def auditar_lote(sender, instance, created, **kwargs):
    registrar_cambio(
        instance,
        created,
        detalle=f"Lote {instance.numero} - Estado: {instance.estado}",
    )


@receiver(post_save, sender=Existencia)
def auditar_existencia(sender, instance, created, **kwargs):
    registrar_cambio(
        instance,
        created,
        detalle=(
            f"Lote: {instance.lote.numero} - "
            f"Almacén: {instance.almacen.nombre} - "
            f"Cantidad: {instance.cantidad}"
        ),
    )


@receiver(post_save, sender=Movimiento)
def auditar_movimiento(sender, instance, created, **kwargs):
    registrar_cambio(
        instance,
        created,
        usuario=instance.usuario,
        detalle=(
            f"Tipo: {instance.tipo} - "
            f"Almacén: {instance.almacen.nombre} - "
            f"Documento: {instance.documento_origen}"
        ),
    )


@receiver(post_save, sender=Transferencia)
def auditar_transferencia(sender, instance, created, **kwargs):
    registrar_cambio(
        instance,
        created,
        usuario=instance.creada_por,
        detalle=(
            f"Origen: {instance.origen.nombre} - "
            f"Destino: {instance.destino.nombre} - "
            f"Estado: {instance.estado}"
        ),
    )
