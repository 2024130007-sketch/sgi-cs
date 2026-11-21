from django.core import mail
from django.test import TestCase
from rest_framework.test import APIClient

from almacenes.models import Almacen
from compras.models import DetalleOrdenCompra, OrdenCompra
from productos.models import Producto
from proveedores.models import Proveedor
from usuarios.models import Usuario


class EnvioOrdenCompraTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = Usuario.objects.create_user(
            username="admin_envios",
            email="admin@sgi.test",
            password="Clave1234!",
            rol=Usuario.Rol.ADMINISTRADOR,
        )

        self.operario = Usuario.objects.create_user(
            username="operario_envios",
            email="operario@sgi.test",
            password="Clave1234!",
            rol=Usuario.Rol.OPERARIO,
        )

        self.proveedor = Proveedor.objects.create(
            ruc="20123456789",
            razon_social="Proveedor de prueba",
            correo="proveedor@sgi.test",
        )

        self.almacen = Almacen.objects.create(
            nombre="Almacén de prueba",
            direccion="Huánuco",
        )

        self.producto = Producto.objects.create(
            sku="ENV-001",
            nombre="Producto de prueba",
        )

        self.orden = OrdenCompra.objects.create(
            proveedor=self.proveedor,
            almacen_destino=self.almacen,
            creada_por=self.admin,
            estado=OrdenCompra.Estado.APROBADA,
        )

        DetalleOrdenCompra.objects.create(
            orden=self.orden,
            producto=self.producto,
            cantidad=5,
            precio_unitario="10.00",
        )

        self.url = (
            f"/api/notificaciones/ordenes/{self.orden.id}/enviar/"
        )

    def test_enviar_orden_aprobada_al_proveedor(self):
        self.client.force_authenticate(self.admin)

        respuesta = self.client.post(self.url)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to,
            ["proveedor@sgi.test"],
        )
        self.assertEqual(
            mail.outbox[0].subject,
            f"SGI-CS - Orden de compra N.° {self.orden.id}",
        )

        self.orden.refresh_from_db()

        self.assertEqual(
            self.orden.estado,
            OrdenCompra.Estado.ENVIADA,
        )
        self.assertIsNotNone(self.orden.fecha_envio)

    def test_no_enviar_orden_no_aprobada(self):
        self.orden.estado = OrdenCompra.Estado.BORRADOR
        self.orden.save(update_fields=["estado"])

        self.client.force_authenticate(self.admin)
        respuesta = self.client.post(self.url)

        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

    def test_operario_no_puede_enviar_orden(self):
        self.client.force_authenticate(self.operario)

        respuesta = self.client.post(self.url)

        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(len(mail.outbox), 0)
