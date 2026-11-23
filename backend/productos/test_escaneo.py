from datetime import date

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from . import gs1
from .models import CodigoBarras, Producto

Usuario = get_user_model()

GTIN14 = "07791234567898"   # GTIN-14 con dígito de control válido
EAN13 = "7791234567898"     # el mismo producto como EAN-13


class Gs1ParserTests(SimpleTestCase):
    def test_formato_legible(self):
        d = gs1.parsear_gs1(f"(01){GTIN14}(17)261231(10)L001")
        self.assertEqual(d["gtin"], GTIN14)
        self.assertEqual(d["lote"], "L001")
        self.assertEqual(d["vencimiento"], date(2026, 12, 31))

    def test_formato_crudo_con_separador(self):
        d = gs1.parsear_gs1(f"01{GTIN14}10LOTE-7{gs1.GS}17270630")
        self.assertEqual(d["lote"], "LOTE-7")
        self.assertEqual(d["vencimiento"], date(2027, 6, 30))

    def test_lote_al_final_sin_separador(self):
        d = gs1.parsear_gs1(f"01{GTIN14}17261231" + "10ABC")
        self.assertEqual(d["lote"], "ABC")

    def test_dia_cero_es_fin_de_mes(self):
        d = gs1.parsear_gs1(f"(01){GTIN14}(17)280200")
        self.assertEqual(d["vencimiento"], date(2028, 2, 29))   # 2028 es bisiesto

    def test_gtin_con_digito_erroneo(self):
        with self.assertRaises(gs1.CodigoInvalido):
            gs1.parsear_gs1("(01)07791234567893(17)261231")

    def test_identificador_no_soportado(self):
        with self.assertRaises(gs1.CodigoInvalido):
            gs1.parsear_gs1("99XYZ")

    def test_fecha_invalida(self):
        with self.assertRaises(gs1.CodigoInvalido):
            gs1.parsear_gs1(f"(01){GTIN14}(17)261345")

    def test_codigo_vacio(self):
        with self.assertRaises(gs1.CodigoInvalido):
            gs1.parsear_gs1("  ")


class EscaneoAPITests(APITestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="operario_escaneo", email="operario_escaneo@sgi.com",
            password="Operario123", rol="OPERARIO")
        self.client.force_authenticate(user=self.usuario)
        self.producto = Producto.objects.create(sku="SKU-ESC", nombre="Leche en polvo")
        CodigoBarras.objects.create(producto=self.producto, codigo=EAN13)

    def _escanear(self, codigo):
        return self.client.post("/api/productos/escaneo/", {"codigo": codigo}, format="json")

    def test_gs1_legible_devuelve_producto_lote_y_vencimiento(self):
        r = self._escanear(f"(01){GTIN14}(17)261231(10)L001")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["producto"]["sku"], "SKU-ESC")
        self.assertEqual(r.data["lote"], "L001")
        self.assertEqual(r.data["vencimiento"], "2026-12-31")

    def test_ean13_simple(self):
        r = self._escanear(EAN13)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIsNone(r.data["lote"])

    def test_por_sku(self):
        r = self._escanear("SKU-ESC")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["producto"]["nombre"], "Leche en polvo")

    def test_producto_inexistente_da_404(self):
        self.assertEqual(self._escanear("0000000000000").status_code, 404)

    def test_gs1_invalido_da_400(self):
        self.assertEqual(self._escanear("(01)07791234567893(10)X").status_code, 400)

    def test_codigo_vacio_da_400(self):
        self.assertEqual(self._escanear("").status_code, 400)

    def test_sin_sesion_da_401(self):
        self.client.force_authenticate(user=None)
        self.assertEqual(self._escanear(EAN13).status_code, 401)
