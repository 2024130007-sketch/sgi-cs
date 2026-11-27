from pathlib import Path

from django.conf import settings
from django.db import connection
from django.utils import timezone

from respaldos.models import RegistroRespaldo


MAX_RESPALDOS = 7

def obtener_contenido_bd():
    connection.ensure_connection()
    return connection.connection.serialize()

def crear_respaldo(usuario=None):
    """Genera una copia consistente de SQLite y conserva los últimos 7."""
    if connection.vendor != "sqlite":
        raise RuntimeError("El sistema de respaldos requiere SQLite.")

    carpeta = Path(settings.BASE_DIR) / "respaldos_bd"
    carpeta.mkdir(parents=True, exist_ok=True)

    nombre = f"respaldo_{timezone.localtime():%Y%m%d_%H%M%S_%f}.sqlite3"
    destino = carpeta / nombre

    registro = RegistroRespaldo.objects.create(
        archivo=str(destino.relative_to(settings.BASE_DIR)),
        usuario=usuario,
        ok=False,
    )

    try:
        contenido = obtener_contenido_bd()
        destino.write_bytes(contenido)

        registro.tamano = destino.stat().st_size
        registro.ok = True
        registro.error = ""
        registro.save(update_fields=["tamano", "ok", "error"])

    except Exception as exc:
        registro.error = str(exc)
        registro.ok = False
        registro.save(update_fields=["ok", "error"])

        if destino.exists():
            destino.unlink()

        raise

    rotar_respaldos()
    return registro


def rotar_respaldos():
    """Conserva los siete respaldos exitosos más recientes."""
    registros = list(
        RegistroRespaldo.objects.filter(ok=True).order_by("-fecha", "-id")
    )

    for registro in registros[MAX_RESPALDOS:]:
        ruta = Path(settings.BASE_DIR) / registro.archivo

        if ruta.exists():
            ruta.unlink()

        registro.delete()
