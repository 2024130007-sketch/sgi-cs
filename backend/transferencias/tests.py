from datetime import date, timedelta 
 
from rest_framework.test import APITestCase 
 
from almacenes.models import Almacen 
from inventario.models import Existencia 
from inventario.services import registrar_ingreso 
from productos.models import Producto 
from usuarios.models import Usuario 
 
 
class TransferenciaTests(APITestCase): 
    def setUp(self): 
        self.u = Usuario.objects.create_user("j@t.pe", "Clave1234!", rol="JEFE_ALMACEN") 
        self.client.force_authenticate(self.u) 
        self.a = Almacen.objects.create(nombre="A", direccion="x") 
        self.b = Almacen.objects.create(nombre="B", direccion="y") 
        self.p = Producto.objects.create(sku="P", nombre="Prod", categoria="c") 
        registrar_ingreso(self.u, self.a, self.p, 100) 
 
    def _crear(self, cant=40, destino=None): 
        return self.client.post("/api/transferencias/", { 
            "origen": self.a.id, "destino": (destino or self.b).id, "producto": self.p.id, 
            "cantidad": cant}, format="json") 
 
    def test_flujo_completo(self): 
        t = self._crear().data 
        self.assertEqual(Existencia.objects.get(almacen=self.a).reservada, 40) 
        self.client.post(f"/api/transferencias/{t['id']}/confirmar-salida/") 
        self.assertEqual(Existencia.objects.get(almacen=self.a).cantidad, 60) 
        r = self.client.post(f"/api/transferencias/{t['id']}/confirmar-ingreso/") 
        self.assertEqual(r.data["estado"], "COMPLETADA") 
        self.assertEqual(Existencia.objects.get(almacen=self.b).cantidad, 40) 
 
    def test_origen_igual_destino_y_stock_insuficiente(self): 
        self.assertEqual(self._crear(destino=self.a).status_code, 400) 
        self.assertEqual(self._crear(500).status_code, 400) 
 
    def test_cancelar_libera_reserva(self): 
        t = self._crear().data 
        self.client.post(f"/api/transferencias/{t['id']}/cancelar/") 
        self.assertEqual(Existencia.objects.get(almacen=self.a).reservada, 0) 