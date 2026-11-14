from datetime import date, timedelta
from rest_framework.test import APITestCase
from almacenes.models import Almacen
from inventario.services import registrar_ingreso, registrar_salida
from productos.models import Producto
from usuarios.models import Usuario
from .models import Alerta

class ReposicionTests(APITestCase):
    def setUp(self):
        self.u = Usuario.objects.create_user("j@t.pe", "Clave1234!", rol="JEFE_ALMACEN")
        self.client.force_authenticate(self.u)
        self.a = Almacen.objects.create(nombre="A", direccion="x")
        self.p = Producto.objects.create(sku="P", nombre="Prod", categoria="c")
        registrar_ingreso(self.u, self.a, self.p, 100)

    def _regla(self):
        return self.client.post("/api/reglas-reposicion/", {
            "producto": self.p.id, "almacen": self.a.id, "stock_minimo": 10, "stock_seguridad": 10,
            "stock_maximo": 200, "demanda_diaria": 5, "tiempo_entrega_dias": 4}, format="json")

    def test_punto_de_reorden(self):
        self.assertEqual(self._regla().data["punto_reorden"], 30) # 5*4 + 10

    def test_salida_bajo_el_punto_genera_alerta_sin_duplicar(self):
        self._regla()
        registrar_salida(self.u, self.a, self.p, 80) # quedan 20 <= 30
        registrar_salida(self.u, self.a, self.p, 5)
        alertas = Alerta.objects.filter(tipo="REPOSICION")
        self.assertEqual(alertas.count(), 1)
        self.assertEqual(alertas[0].cantidad_sugerida, 180) # 200 - 20

    def test_atender_exige_motivo(self):
        self._regla()
        registrar_salida(self.u, self.a, self.p, 80)
        aid = Alerta.objects.get().id
        self.assertEqual(self.client.post(f"/api/alertas/{aid}/atender/", {}, format="json").status_code, 400)
        r = self.client.post(f"/api/alertas/{aid}/atender/", {"motivo": "OC creada"}, format="json")
        self.assertEqual(r.data["estado"], "ATENDIDA")

    def test_alerta_de_vencimiento(self):
        p2 = Producto.objects.create(sku="V", nombre="Vence", categoria="c", requiere_lote=True, requiere_vencimiento=True)
        registrar_ingreso(self.u, self.a, p2, 10, "L1", date.today() + timedelta(days=20))
        self.assertEqual(self.client.post("/api/alertas/generar/").data["nuevas"], 1)