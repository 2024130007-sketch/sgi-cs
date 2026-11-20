
from .models import Bitacora


def registrar(usuario, accion, entidad, entidad_id=None, detalle=""):
    return Bitacora.objects.create(
        usuario=usuario,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        detalle=str(detalle)[:250]
    )
