"""Servicio de envío de resumen de alertas por correo."""

from django.core.mail import send_mail

from usuarios.models import Usuario
from .models import Alerta


def enviar_resumen_alertas():
    """Envía las alertas abiertas al personal autorizado."""

    destinatarios = Usuario.objects.filter(
        is_active=True,
        rol__in=[
            Usuario.Rol.ADMINISTRADOR,
            Usuario.Rol.JEFE_ALMACEN,
            Usuario.Rol.COMPRADOR,
        ],
    ).exclude(email="")

    alertas = Alerta.objects.filter(
        estado=Alerta.Estado.ABIERTA
    ).select_related("producto", "almacen")

    if not destinatarios.exists():
        return {"enviados": 0, "alertas": alertas.count()}

    if not alertas.exists():
        return {"enviados": 0, "alertas": 0}

    lineas = [
        "Resumen de alertas abiertas del Sistema de Gestión de Inventarios",
        "",
    ]

    for alerta in alertas:
        lineas.append(
            f"- {alerta.tipo}: {alerta.producto.nombre} | "
            f"Almacén: {alerta.almacen.nombre if alerta.almacen else 'No asignado'} | "
            f"{alerta.mensaje}"
        )

    mensaje = "\n".join(lineas)
    enviados = 0

    for usuario in destinatarios:
        enviados += send_mail(
            subject="SGI - Resumen de alertas abiertas",
            message=mensaje,
            from_email=None,
            recipient_list=[usuario.email],
            fail_silently=False,
        )

    return {"enviados": enviados, "alertas": alertas.count()}