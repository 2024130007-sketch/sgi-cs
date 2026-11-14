from datetime import date, timedelta

from rest_framework.test import APITestCase

from almacenes.models import Almacen
from inventario.models import Existencia
from productos.models import Producto
from usuarios.models import Usuario


class InventarioTests(APITestCase):
    def setUp(self):
        self.client.force_authenticate(Usuario.objects.create_user("o@t.pe", "Clave1234!", rol="OPERARIO"))
        self.alm = Almacen.objects.create(nombre="Central", direccion="Jr. 1")
        self.prod = Producto.objects.create(sku="L-1", nombre="Leche", categoria="Lácteos",
                                            requiere_lote=True, requiere_vencimiento=True)
        self.hoy = date.today()

    def _ingreso(self, cant=100, lote="A", dias=30):
        return self.client.post("/api/inventario/ingresos/", {
            "almacen": self.alm.id, "producto": self.prod.id, "cantidad": cant, "numero_lote": lote,
            "fecha_vencimiento": str(self.hoy + timedelta(days=dias))}, format="json")

    def _salida(self, cant):
        return self.client.post("/api/inventario/salidas/", {
            "almacen": self.alm.id, "producto": self.prod.id, "cantidad": cant}, format="json")

    def test_ingreso_incrementa_stock(self):
        self.assertEqual(self._ingreso(100).status_code, 201)
        self.assertEqual(self.client.get("/api/inventario/stock/").data[0]["cantidad"], 100)

    def test_ingreso_rechaza_cantidad_cero_y_vencido(self):
        self.assertEqual(self._ingreso(0).status_code, 400)
        self.assertEqual(self._ingreso(10, dias=-1).status_code, 400)

    def test_ingreso_exige_lote_y_vencimiento(self):
        r = self.client.post("/api/inventario/ingresos/", {
            "almacen": self.alm.id, "producto": self.prod.id, "cantidad": 5}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_salida_aplica_fefo(self):
        self._ingreso(50, "TARDE", dias=200)
        self._ingreso(50, "PRONTO", dias=10)
        self.assertEqual(self._salida(70).status_code, 201)
        stock = {e.lote.numero: e.cantidad for e in Existencia.objects.all()}
        self.assertEqual(stock, {"PRONTO": 0, "TARDE": 30})

    def test_salida_mayor_al_stock_se_rechaza(self):
        self._ingreso(10)
        r = self._salida(11)
        self.assertEqual(r.status_code, 400)
        self.assertIn("insuficiente", str(r.data))

    def test_lote_vencido_o_cuarentena_no_sale(self):
        self._ingreso(10, "A")
        e = Existencia.objects.get()
        e.lote.estado = "CUARENTENA"
        e.lote.save()
        self.assertEqual(self._salida(1).status_code, 400)

    def test_kardex_registra_movimientos(self):
        self._ingreso(10)
        self._salida(4)
        self.assertEqual(len(self.client.get("/api/inventario/movimientos/").data), 2)
