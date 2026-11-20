from datetime import date, timedelta
from unittest import mock

from rest_framework.test import APITestCase

from almacenes.models import Almacen
from inventario import services
from inventario.models import Existencia
from productos.models import Producto
from usuarios.models import Usuario


class ConcurrenciaTests(APITestCase):
    """RF-29: bloqueo optimista con reintentos."""

    def setUp(self):
        self.usuario = Usuario.objects.create_user("o@t.pe", "Clave1234!", rol="OPERARIO")
        self.client.force_authenticate(self.usuario)
        self.alm = Almacen.objects.create(nombre="Central", direccion="Jr. 1")
        self.prod = Producto.objects.create(sku="L-1", nombre="Leche", requiere_lote=True,
                                            requiere_vencimiento=True)
        services.registrar_ingreso(self.usuario, self.alm, self.prod, 100, "A",
                                   date.today() + timedelta(days=30))

    def test_actualizar_con_version_vieja_falla(self):
        e = Existencia.objects.get()
        copia_vieja = Existencia.objects.get(pk=e.pk)
        services.actualizar_existencia(e, delta_cantidad=-10)       # otra operación gana
        with self.assertRaises(services.ConflictoVersion):
            services.actualizar_existencia(copia_vieja, delta_cantidad=-10)
        self.assertEqual(Existencia.objects.get().cantidad, 90)      # no se pisó el cambio

    def test_la_salida_reintenta_tras_un_conflicto(self):
        real = services.actualizar_existencia
        llamadas = {"n": 0}

        def falla_una_vez(existencia, **kw):
            llamadas["n"] += 1
            if llamadas["n"] == 1:
                raise services.ConflictoVersion()
            return real(existencia, **kw)

        with mock.patch.object(services, "actualizar_existencia", side_effect=falla_una_vez):
            services.registrar_salida(self.usuario, self.alm, self.prod, 30)
        self.assertEqual(llamadas["n"], 2)
        self.assertEqual(Existencia.objects.get().cantidad, 70)      # descontó una sola vez

    def test_conflicto_persistente_responde_409_y_no_cambia_stock(self):
        with mock.patch.object(services, "actualizar_existencia", side_effect=services.ConflictoVersion):
            r = self.client.post("/api/inventario/salidas/", {
                "almacen": self.alm.id, "producto": self.prod.id, "cantidad": 5}, format="json")
        self.assertEqual(r.status_code, 409)
        self.assertIn("modificado", str(r.data))
        self.assertEqual(Existencia.objects.get().cantidad, 100)

    def test_salida_normal_sigue_funcionando_y_sube_la_version(self):
        version_antes = Existencia.objects.get().version
        r = self.client.post("/api/inventario/salidas/", {
            "almacen": self.alm.id, "producto": self.prod.id, "cantidad": 40}, format="json")
        self.assertEqual(r.status_code, 201)
        e = Existencia.objects.get()
        self.assertEqual((e.cantidad, e.version), (60, version_antes + 1))
