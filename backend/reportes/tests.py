from io import BytesIO
from openpyxl import load_workbook
from rest_framework.test import APITestCase
from almacenes.models import Almacen
from inventario.models import Movimiento
from usuarios.models import Usuario


class ReportesTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="rep@sgi.test",
            username="rep@sgi.test",
            password="Clave123!",
            rol="ADMINISTRADOR",
        )
        self.client.force_authenticate(self.user)

    def test_stock_pdf_inicia_con_cabecera_pdf(self):
        r = self.client.get("/api/reportes/stock/?formato=pdf")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.content.startswith(b"%PDF"))

    def test_stock_excel_se_abre_con_openpyxl(self):
        r = self.client.get("/api/reportes/stock/?formato=xlsx")
        self.assertEqual(r.status_code, 200)
        wb = load_workbook(BytesIO(r.content))
        ws = wb.active
        self.assertEqual(ws.cell(1, 1).value, "SKU")

    def test_kardex_y_ordenes_sin_datos_devuelven_encabezados(self):
        r1 = self.client.get("/api/reportes/kardex/?formato=xlsx")
        r2 = self.client.get("/api/reportes/ordenes/?formato=xlsx")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 200)
        wb = load_workbook(BytesIO(r2.content))
        self.assertEqual(wb.active.cell(1, 1).value, "N.º Orden")

    def test_formato_desconocido_cae_a_pdf(self):
        r = self.client.get("/api/reportes/ordenes/?formato=csv")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.content.startswith(b"%PDF"))

    def test_usuario_sin_sesion_recibe_401(self):
        self.client.force_authenticate(None)
        r = self.client.get("/api/reportes/stock/")
        self.assertEqual(r.status_code, 401)

    def test_kardex_con_movimientos_incluye_el_documento(self):
        almacen = Almacen.objects.create(nombre="Central")
        Movimiento.objects.create(tipo=Movimiento.Tipo.INGRESO, almacen=almacen,
                                  usuario=self.user, documento_origen="GR-001")
        for formato in ("pdf", "xlsx"):
            r = self.client.get(f"/api/reportes/kardex/?formato={formato}")
            self.assertEqual(r.status_code, 200)
        wb = load_workbook(BytesIO(r.content))
        self.assertEqual(wb.active.cell(2, 5).value, "GR-001")
