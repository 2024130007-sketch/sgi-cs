from rest_framework.test import APITestCase

from almacenes.models import Almacen
from compras.models import OrdenCompra
from inventario.models import Existencia
from productos.models import Producto
from proveedores.models import Proveedor
from usuarios.models import Usuario

URL = "/api/recepciones/"


class RecepcionTests(APITestCase):
    def setUp(self):
        mk = Usuario.objects.create_user
        self.jefe = mk("jefe", "j@t.pe", "Clave1234!", rol="JEFE_ALMACEN")
        self.comprador = mk("comp", "c@t.pe", "Clave1234!", rol="COMPRADOR")
        prov = Proveedor.objects.create(ruc="20123456789", razon_social="Lácteos SAC", correo="v@l.pe")
        self.alm = Almacen.objects.create(nombre="Central", direccion="Jr. 1")
        self.p1 = Producto.objects.create(sku="L-1", nombre="Leche")
        self.p2 = Producto.objects.create(sku="Q-1", nombre="Queso")
        self.orden = OrdenCompra.objects.create(proveedor=prov, almacen_destino=self.alm,
                                                estado="APROBADA", creada_por=self.comprador)
        self.d1 = self.orden.detalles.create(producto=self.p1, cantidad=10, precio_unitario=2)
        self.d2 = self.orden.detalles.create(producto=self.p2, cantidad=5, precio_unitario=8)
        self.client.force_authenticate(self.jefe)

    def _recibir(self, lineas, **extra):
        datos = {"orden_compra": self.orden.id, "documento": "G-001", "detalles": lineas}
        datos.update(extra)
        return self.client.post(URL, datos, format="json")

    def _stock(self, producto):
        return sum(e.cantidad for e in Existencia.objects.filter(lote__producto=producto, almacen=self.alm))

    def test_recepcion_total_ingresa_stock_y_cierra_la_orden(self):
        r = self._recibir([{"detalle_orden": self.d1.id, "cantidad": 10},
                           {"detalle_orden": self.d2.id, "cantidad": 5}])
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["estado"], "COMPLETA")
        self.assertEqual((self._stock(self.p1), self._stock(self.p2)), (10, 5))
        self.orden.refresh_from_db()
        self.assertEqual(self.orden.estado, "RECIBIDA")

    def test_recepcion_parcial_deja_la_orden_parcial_y_luego_se_completa(self):
        r = self._recibir([{"detalle_orden": self.d1.id, "cantidad": 4}])
        self.assertEqual((r.status_code, r.data["estado"]), (201, "PARCIAL"))
        self.orden.refresh_from_db()
        self.assertEqual(self.orden.estado, "RECIBIDA_PARCIAL")
        r = self._recibir([{"detalle_orden": self.d1.id, "cantidad": 6},
                           {"detalle_orden": self.d2.id, "cantidad": 5}])
        self.assertEqual((r.status_code, r.data["estado"]), (201, "COMPLETA"))
        self.orden.refresh_from_db()
        self.assertEqual(self.orden.estado, "RECIBIDA")

    def test_no_se_puede_recibir_mas_de_lo_pendiente(self):
        r = self._recibir([{"detalle_orden": self.d1.id, "cantidad": 11}])
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self._stock(self.p1), 0)

    def test_es_todo_o_nada_si_una_linea_falla(self):
        r = self._recibir([{"detalle_orden": self.d1.id, "cantidad": 10},
                           {"detalle_orden": self.d2.id, "cantidad": 99}])
        self.assertEqual(r.status_code, 400)
        self.assertEqual((self._stock(self.p1), self._stock(self.p2)), (0, 0))
        self.d1.refresh_from_db()
        self.assertEqual(self.d1.cantidad_recibida, 0)

    def test_solo_se_reciben_ordenes_aprobadas_o_enviadas(self):
        self.orden.estado = "BORRADOR"
        self.orden.save()
        r = self._recibir([{"detalle_orden": self.d1.id, "cantidad": 1}])
        self.assertEqual(r.status_code, 400)

    def test_cantidad_cero_o_negativa_se_rechaza(self):
        for c in (0, -3):
            self.assertEqual(self._recibir([{"detalle_orden": self.d1.id, "cantidad": c}]).status_code, 400)

    def test_comprador_no_puede_recibir(self):
        self.client.force_authenticate(self.comprador)
        r = self._recibir([{"detalle_orden": self.d1.id, "cantidad": 1}])
        self.assertEqual(r.status_code, 403)

    def test_la_recepcion_aparece_en_el_listado(self):
        self._recibir([{"detalle_orden": self.d1.id, "cantidad": 3}])
        lista = self.client.get(URL)
        self.assertEqual(lista.status_code, 200)
        self.assertEqual(len(lista.data["results"] if isinstance(lista.data, dict) else lista.data), 1)