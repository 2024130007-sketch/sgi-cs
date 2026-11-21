"""Servicios de envío de correos del SGI-CS."""

from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from compras.models import OrdenCompra


def enviar_orden_compra(orden):
    """Envía una orden aprobada al correo de su proveedor."""

    if orden.estado != OrdenCompra.Estado.APROBADA:
        raise ValidationError(
            "Solo se pueden enviar órdenes de compra aprobadas."
        )

    proveedor = orden.proveedor

    if not proveedor.correo:
        raise ValidationError(
            "El proveedor no tiene un correo electrónico registrado."
        )

    lineas = [
        "Estimado proveedor:",
        "",
        "Adjuntamos los datos de la orden de compra.",
        f"Orden: {orden.id}",
        f"Proveedor: {proveedor.razon_social}",
        f"Almacén de destino: {orden.almacen_destino.nombre}",
        "",
        "Detalle de productos:",
    ]

    for detalle in orden.detalles.select_related("producto").all():
        lineas.append(
            f"- {detalle.producto.nombre} "
            f"(SKU: {detalle.producto.sku}) | "
            f"Cantidad: {detalle.cantidad} | "
            f"Precio unitario: S/ {detalle.precio_unitario} | "
            f"Subtotal: S/ {detalle.subtotal}"
        )

    lineas.extend([
        "",
        f"Total de la orden: S/ {orden.total}",
        "",
        "Atentamente,",
        "Sistema de Gestión de Inventarios y Cadena de Suministro",
    ])

    enviados = send_mail(
        subject=f"SGI-CS - Orden de compra N.° {orden.id}",
        message="\n".join(lineas),
        from_email=None,
        recipient_list=[proveedor.correo],
        fail_silently=False,
    )

    if enviados != 1:
        raise ValidationError(
            "No se pudo confirmar el envío del correo."
        )

    orden.estado = OrdenCompra.Estado.ENVIADA
    orden.fecha_envio = timezone.now()
    orden.save(update_fields=["estado", "fecha_envio"])

    return orden
