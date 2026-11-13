from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Producto, CodigoBarras

Usuario = get_user_model()


class ProductoAPITests(APITestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="adminproductos",
            email="adminproductos@sgi.com",
            password="Admin12345",
            rol="ADMINISTRADOR"
        )
        self.client.force_authenticate(user=self.usuario)

        self.producto = Producto.objects.create(
            sku="PROD001",
            nombre="Laptop Lenovo",
            descripcion="Laptop de prueba",
            marca="Lenovo",
            unidad_medida="UNIDAD",
            precio=Decimal("2500.00")
        )

    def test_listar_productos(self):
        respuesta = self.client.get("/api/productos/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data), 1)

    def test_registrar_producto(self):
        datos = {
            "sku": "PROD002",
            "nombre": "Mouse Logitech",
            "marca": "Logitech",
            "unidad_medida": "UNIDAD",
            "precio": "80.00",
            "activo": True
        }
        respuesta = self.client.post("/api/productos/", datos)
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Producto.objects.filter(sku="PROD002").exists())

    def test_sku_duplicado(self):
        datos = {
            "sku": "PROD001",
            "nombre": "Otro producto",
            "marca": "Prueba",
            "unidad_medida": "UNIDAD",
            "precio": "50.00",
            "activo": True
        }
        respuesta = self.client.post("/api/productos/", datos)
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_editar_producto(self):
        respuesta = self.client.patch(
            f"/api/productos/{self.producto.id}/",
            {"nombre": "Laptop Lenovo ThinkPad"}
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, "Laptop Lenovo ThinkPad")

    def test_eliminar_producto(self):
        respuesta = self.client.delete(
            f"/api/productos/{self.producto.id}/"
        )
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Producto.objects.filter(id=self.producto.id).exists()
        )

    def test_registrar_codigo_barras(self):
        datos = {
            "producto": self.producto.id,
            "codigo": "7751234567890"
        }
        respuesta = self.client.post("/api/codigos-barras/", datos)
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CodigoBarras.objects.filter(codigo="7751234567890").exists()
        )

    def test_buscar_codigo_barras(self):
        CodigoBarras.objects.create(
            producto=self.producto,
            codigo="7751234567890"
        )
        respuesta = self.client.get(
            "/api/codigos-barras/buscar/",
            {"codigo": "7751234567890"}
        )
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["sku"], "PROD001")