from rest_framework.test import APITestCase

from almacenes.models import Almacen
from compras.models import OrdenCompra
from productos.models import Producto
from proveedores.models import Proveedor
from usuarios.models import Usuario

URL = "/api/compras/ordenes/"


class ComprasTests(APITestCase):
    def setUp(self):
        mk = Usuario.objects.create_user
        self.comprador = mk("comp", "c@t.pe", "Clave1234!", rol="COMPRADOR")
        self.jefe = mk("jefe", "j@t.pe", "Clave1234!", rol="JEFE_ALMACEN")
        self.operario = mk("oper", "o@t.pe", "Clave1234!", rol="OPERARIO")
        self.prov = Proveedor.objects.create(ruc="20123456789", razon_social="Lácteos SAC", correo="v@l.pe")
        self.alm = Almacen.objects.create(nombre="Central", direccion="Jr. 1")
        self.p1 = Producto.objects.create(sku="L-1", nombre="Leche")
        self.p2 = Producto.objects.create(sku="Q-1", nombre="Queso")

    def _datos(self, **extra):
        d = {"proveedor": self.prov.id, "almacen_destino": self.alm.id, "observacion": "Urgente",
             "items": [{"producto": self.p1.id, "cantidad": 10, "precio_unitario": "2.50"},
                       {"producto": self.p2.id, "cantidad": 5, "precio_unitario": "8.00"}]}
        d.update(extra)
        return d

    def _crear(self, **extra):
        self.client.force_authenticate(self.comprador)
        return self.client.post(URL, self._datos(**extra), format="json")

    def test_crear_orden_calcula_total_y_queda_en_borrador(self):
        r = self._crear()
        self.assertEqual(r.status_code, 201)
        self.assertEqual((r.data["estado"], r.data["total"]), ("BORRADOR", "65.00"))
        self.assertEqual(len(r.data["detalles"]), 2)

    def test_orden_sin_productos_se_rechaza(self):
        self.assertEqual(self._crear(items=[]).status_code, 400)

    def test_cantidad_cero_o_producto_repetido_se_rechaza(self):
        self.assertEqual(self._crear(items=[{"producto": self.p1.id, "cantidad": 0}]).status_code, 400)
        r = self._crear(items=[{"producto": self.p1.id, "cantidad": 1}, {"producto": self.p1.id, "cantidad": 2}])
        self.assertEqual(r.status_code, 400)
        self.assertIn("repetido", str(r.data))

    def test_proveedor_desactivado_se_rechaza(self):
        self.prov.activo = False
        self.prov.save()
        self.assertEqual(self._crear().status_code, 400)

    def test_solo_el_borrador_se_puede_editar(self):
        oid = self._crear().data["id"]
        r = self.client.put(f"{URL}{oid}/", self._datos(observacion="Cambio"), format="json")
        self.assertEqual((r.status_code, r.data["observacion"]), (200, "Cambio"))
        self.client.post(f"{URL}{oid}/enviar-aprobacion/")
        self.assertEqual(self.client.put(f"{URL}{oid}/", self._datos(), format="json").status_code, 400)

    def test_flujo_completo_hasta_aprobada(self):
        oid = self._crear().data["id"]
        self.assertEqual(self.client.post(f"{URL}{oid}/enviar-aprobacion/").data["estado"], "PENDIENTE")
        self.client.force_authenticate(self.jefe)
        r = self.client.post(f"{URL}{oid}/aprobar/")
        self.assertEqual((r.status_code, r.data["estado"]), (200, "APROBADA"))
        self.assertEqual(r.data["aprobada_por_email"], "j@t.pe")

    def test_quien_creo_la_orden_no_puede_aprobarla(self):
        oid = self._crear().data["id"]
        self.client.post(f"{URL}{oid}/enviar-aprobacion/")
        admin = Usuario.objects.create_user("adm", "a@t.pe", "Clave1234!", rol="ADMINISTRADOR")
        orden = OrdenCompra.objects.get(pk=oid)
        orden.creada_por = admin
        orden.save()
        self.client.force_authenticate(admin)
        r = self.client.post(f"{URL}{oid}/aprobar/")
        self.assertEqual(r.status_code, 400)
        self.assertIn("no puede aprobarla", str(r.data))

    def test_rechazo_exige_motivo(self):
        oid = self._crear().data["id"]
        self.client.post(f"{URL}{oid}/enviar-aprobacion/")
        self.client.force_authenticate(self.jefe)
        self.assertEqual(self.client.post(f"{URL}{oid}/rechazar/", {}, format="json").status_code, 400)
        r = self.client.post(f"{URL}{oid}/rechazar/", {"motivo": "Precio alto"}, format="json")
        self.assertEqual((r.data["estado"], r.data["motivo_rechazo"]), ("RECHAZADA", "Precio alto"))

    def test_operario_no_puede_crear_ni_aprobar(self):
        self.client.force_authenticate(self.operario)
        self.assertEqual(self.client.post(URL, self._datos(), format="json").status_code, 403)
        self.assertEqual(self.client.get(URL).status_code, 200)
        oid = self._crear().data["id"]
        self.client.force_authenticate(self.operario)
        self.assertEqual(self.client.post(f"{URL}{oid}/aprobar/").status_code, 403)

    def test_cancelar_y_no_cancelar_una_recibida(self):
        oid = self._crear().data["id"]
        self.assertEqual(self.client.post(f"{URL}{oid}/cancelar/").data["estado"], "CANCELADA")
        self.assertEqual(self.client.post(f"{URL}{oid}/cancelar/").status_code, 400)

    def test_listado_filtra_por_estado(self):
        self._crear()
        self.assertEqual(len(self.client.get(URL + "?estado=BORRADOR").data), 1)
        self.assertEqual(len(self.client.get(URL + "?estado=APROBADA").data), 0)
