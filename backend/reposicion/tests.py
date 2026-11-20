from datetime import date, timedelta
from rest_framework.test import APITestCase
from almacenes.models import Almacen
from inventario.services import registrar_ingreso, registrar_salida
from productos.models import Producto
from usuarios.models import Usuario
from .models import Alerta
from django.core import mail

class ReposicionTests(APITestCase):
    def setUp(self):
        self.u = Usuario.objects.create_user(
            username="jefe",
            email="jefe@sgi.test",
            password="Clave1234!",
            rol=Usuario.Rol.JEFE_ALMACEN,
        )
        self.client.force_authenticate(self.u)
        self.a = Almacen.objects.create(nombre="A", direccion="x")
        self.p = Producto.objects.create(sku="P", nombre="Prod")
        self.p.requiere_lote = False
        self.p.requiere_vencimiento = False
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
        p2 = Producto.objects.create(sku="V", nombre="Vence")
        p2.requiere_lote = True
        p2.requiere_vencimiento = True

        registrar_ingreso(self.u, self.a, p2, 10, "L1", date.today() + timedelta(days=20))

        self.assertEqual(self.client.post("/api/alertas/generar/").data["nuevas"], 1)

    def test_enviar_resumen_a_personal_autorizado(self):
        Usuario.objects.create_user(
            username="admin",
            email="admin@sgi.test",
            password="Clave1234!",
            rol=Usuario.Rol.ADMINISTRADOR,
        )
        Usuario.objects.create_user(
            username="comprador",
            email="comprador@sgi.test",
            password="Clave1234!",
            rol=Usuario.Rol.COMPRADOR,
        )

        Alerta.objects.create(
            tipo=Alerta.Tipo.REPOSICION,
            producto=self.p,
            almacen=self.a,
            mensaje="Stock bajo",
        )

        respuesta = self.client.post("/api/alertas/enviar_resumen/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["enviados"], 3)
        self.assertEqual(len(mail.outbox), 3)

    def test_no_enviar_resumen_si_no_hay_alertas(self):
        respuesta = self.client.post("/api/alertas/enviar_resumen/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data["enviados"], 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_operario_no_puede_enviar_resumen(self):
        operario = Usuario.objects.create_user(
            username="operario",
            email="operario@sgi.test",
            password="Clave1234!",
            rol=Usuario.Rol.OPERARIO,
        )
        self.client.force_authenticate(operario)

        respuesta = self.client.post("/api/alertas/enviar_resumen/")

        self.assertEqual(respuesta.status_code, 403)