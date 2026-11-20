from datetime import date, timedelta

from rest_framework.test import APITestCase

from almacenes.models import Almacen
from inventario import services
from inventario.models import Lote
from productos.models import Producto
from usuarios.models import Usuario


class TrazabilidadTests(APITestCase):
    """RF-33 y RF-34: trazabilidad por lote y cuarentena."""

    def setUp(self):
        self.operario = Usuario.objects.create_user("oper", "o@t.pe", "Clave1234!", rol="OPERARIO")
        self.jefe = Usuario.objects.create_user("jefe", "j@t.pe", "Clave1234!", rol="JEFE_ALMACEN")
        self.alm = Almacen.objects.create(nombre="Central", direccion="Jr. 1")
        self.prod = Producto.objects.create(sku="L-1", nombre="Leche", requiere_lote=True,
                                            requiere_vencimiento=True)
        services.registrar_ingreso(self.operario, self.alm, self.prod, 50, "A",
                                   date.today() + timedelta(days=30), documento="GUIA-1")
        services.registrar_salida(self.operario, self.alm, self.prod, 20, documento="PED-1")
        self.lote = Lote.objects.get()

    def test_trazabilidad_muestra_ingreso_salida_y_stock_actual(self):
        self.client.force_authenticate(self.operario)
        r = self.client.get(f"/api/inventario/lotes/{self.lote.id}/trazabilidad/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([m["tipo"] for m in r.data["movimientos"]], ["INGRESO", "SALIDA"])
        self.assertEqual(r.data["movimientos"][1]["documento"], "PED-1")
        self.assertEqual(r.data["existencias"][0]["cantidad"], 30)
        self.assertEqual(r.data["lote"]["stock_total"], 30)

    def test_lote_inexistente_responde_404(self):
        self.client.force_authenticate(self.operario)
        self.assertEqual(self.client.get("/api/inventario/lotes/9999/trazabilidad/").status_code, 404)

    def test_cuarentena_exige_motivo(self):
        self.client.force_authenticate(self.jefe)
        r = self.client.post(f"/api/inventario/lotes/{self.lote.id}/estado/",
                             {"estado": "CUARENTENA"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("motivo", str(r.data))

    def test_cuarentena_bloquea_la_salida_y_la_liberacion_la_habilita(self):
        self.client.force_authenticate(self.jefe)
        url = f"/api/inventario/lotes/{self.lote.id}/estado/"
        r = self.client.post(url, {"estado": "CUARENTENA", "motivo": "Envase dañado"}, format="json")
        self.assertEqual((r.status_code, r.data["estado"]), (200, "CUARENTENA"))
        salida = {"almacen": self.alm.id, "producto": self.prod.id, "cantidad": 1}
        self.assertEqual(self.client.post("/api/inventario/salidas/", salida, format="json").status_code, 400)
        self.client.post(url, {"estado": "ACTIVO"}, format="json")
        self.assertEqual(self.client.post("/api/inventario/salidas/", salida, format="json").status_code, 201)

    def test_operario_no_puede_cambiar_el_estado(self):
        self.client.force_authenticate(self.operario)
        r = self.client.post(f"/api/inventario/lotes/{self.lote.id}/estado/",
                             {"estado": "CUARENTENA", "motivo": "x"}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_listado_filtra_por_estado_y_busqueda(self):
        self.client.force_authenticate(self.jefe)
        services.cambiar_estado_lote(self.lote, "CUARENTENA", "Prueba")
        self.assertEqual(len(self.client.get("/api/inventario/lotes/?estado=CUARENTENA").data), 1)
        self.assertEqual(len(self.client.get("/api/inventario/lotes/?estado=ACTIVO").data), 0)
        self.assertEqual(len(self.client.get("/api/inventario/lotes/?search=leche").data), 1)
