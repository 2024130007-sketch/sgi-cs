from datetime import date, timedelta 
  
from rest_framework.test import APITestCase 
  
from almacenes.models import Almacen 
from inventario import services as inv 
from inventario.models import Existencia, Movimiento 
from productos.models import Producto 
from proveedores.models import Proveedor 
from usuarios.models import Usuario 
  
  
class BaseAjustes(APITestCase): 
    def setUp(self): 
        mk = Usuario.objects.create_user 
        self.jefe = mk("jefe", "j@t.pe", "Clave1234!", rol="JEFE_ALMACEN") 
        self.operario = mk("oper", "o@t.pe", "Clave1234!", rol="OPERARIO") 
        self.alm = Almacen.objects.create(nombre="Central", direccion="Jr. 1") 
        self.prod = Producto.objects.create(sku="L-1", nombre="Leche", requiere_lote=True, 
                                            requiere_vencimiento=True) 
        inv.registrar_ingreso(self.jefe, self.alm, self.prod, 100, "A", date.today() + timedelta(days=30)) 
        self.client.force_authenticate(self.jefe) 
  
  
class AjusteTests(BaseAjustes): 
    def _iniciar(self): 
        return self.client.post("/api/ajustes/", {"almacen": self.alm.id}, format="json") 
  
    def test_iniciar_conteo_marca_el_almacen_y_toma_la_foto_del_stock(self): 
        r = self._iniciar() 
        self.assertEqual(r.status_code, 201) 
        self.assertEqual(r.data["detalles"][0]["cantidad_sistema"], 100) 
        self.alm.refresh_from_db() 
        self.assertTrue(self.alm.en_conteo) 
  
    def test_no_se_puede_iniciar_dos_veces_ni_mover_stock_durante_el_conteo(self): 
        self._iniciar() 
        self.assertEqual(self._iniciar().status_code, 400) 
        salida = self.client.post("/api/inventario/salidas/", { 
            "almacen": self.alm.id, "producto": self.prod.id, "cantidad": 1}, format="json") 
        self.assertEqual(salida.status_code, 400) 
        self.assertIn("conteo", str(salida.data)) 
  
    def test_cerrar_sin_contar_todo_se_rechaza(self): 
        aid = self._iniciar().data["id"] 
        r = self.client.post(f"/api/ajustes/{aid}/cerrar/") 
        self.assertEqual(r.status_code, 400) 
        self.assertIn("Faltan", str(r.data)) 
  
    def test_cantidad_negativa_se_rechaza(self): 
        r = self._iniciar() 
        did = str(r.data["detalles"][0]["id"]) 
        out = self.client.post(f"/api/ajustes/{r.data['id']}/conteo/", {"conteos": {did: "-3"}}, format="json") 
        self.assertEqual(out.status_code, 400) 
  
    def test_cerrar_con_faltante_corrige_el_stock_y_deja_kardex(self): 
        r = self._iniciar() 
        aid, did = r.data["id"], str(r.data["detalles"][0]["id"]) 
        self.client.post(f"/api/ajustes/{aid}/conteo/", {"conteos": {did: "92"}}, format="json") 
        cierre = self.client.post(f"/api/ajustes/{aid}/cerrar/") 
        self.assertEqual((cierre.status_code, cierre.data["estado"]), (200, "CERRADO")) 
        self.assertEqual(Existencia.objects.get().cantidad, 92) 
        mov = Movimiento.objects.get(tipo="AJUSTE") 
        self.assertEqual((mov.documento_origen, mov.detalles.get().cantidad), (f"AJ-{aid} (-)", 8)) 
        self.alm.refresh_from_db() 
        self.assertFalse(self.alm.en_conteo) 
  
    def test_conteo_igual_al_sistema_no_genera_movimientos(self): 
        r = self._iniciar() 
        aid, did = r.data["id"], str(r.data["detalles"][0]["id"]) 
        self.client.post(f"/api/ajustes/{aid}/conteo/", {"conteos": {did: "100"}}, format="json") 
        self.client.post(f"/api/ajustes/{aid}/cerrar/") 
        self.assertFalse(Movimiento.objects.filter(tipo="AJUSTE").exists()) 
  
    def test_cancelar_libera_el_almacen_sin_cambiar_stock(self): 
        aid = self._iniciar().data["id"] 
        self.assertEqual(self.client.post(f"/api/ajustes/{aid}/cancelar/").data["estado"], "CANCELADO") 
        self.alm.refresh_from_db() 
        self.assertFalse(self.alm.en_conteo) 
        self.assertEqual(Existencia.objects.get().cantidad, 100) 
  
    def test_operario_no_puede_iniciar_conteo(self): 
        self.client.force_authenticate(self.operario) 
        self.assertEqual(self._iniciar().status_code, 403) 
  
  
class BajaTests(BaseAjustes): 
    def _baja(self, **extra): 
        d = {"existencia": Existencia.objects.get().id, "cantidad": 10, "tipo": "DANO", "motivo": "Envase roto"} 
        d.update(extra) 
        return self.client.post("/api/bajas/", d, format="json") 
  
    def test_baja_por_dano_descuenta_stock_y_registra_kardex(self): 
        r = self._baja() 
        self.assertEqual(r.status_code, 201) 
        self.assertEqual(Existencia.objects.get().cantidad, 90) 
        self.assertEqual(Movimiento.objects.filter(tipo="BAJA").count(), 1) 
  
    def test_baja_exige_motivo_y_cantidad_valida(self): 
        self.assertEqual(self._baja(motivo="").status_code, 400) 
        self.assertEqual(self._baja(cantidad=0).status_code, 400) 
        r = self._baja(cantidad=101) 
        self.assertEqual(r.status_code, 400) 
        self.assertIn("insuficiente", str(r.data)) 
  
    def test_baja_por_vencimiento_solo_si_el_lote_vencio(self): 
        self.assertEqual(self._baja(tipo="VENCIMIENTO").status_code, 400) 
        e = Existencia.objects.get() 
        e.lote.fecha_vencimiento = date.today() - timedelta(days=1) 
        e.lote.save() 
        self.assertEqual(self._baja(tipo="VENCIMIENTO").status_code, 201) 
  
    def test_devolucion_exige_proveedor_activo(self): 
        self.assertEqual(self._baja(tipo="DEVOLUCION").status_code, 400) 
        prov = Proveedor.objects.create(ruc="20123456789", razon_social="Lácteos SAC", correo="v@l.pe") 
        r = self._baja(tipo="DEVOLUCION", proveedor=prov.id) 
        self.assertEqual((r.status_code, r.data["proveedor_nombre"]), (201, "Lácteos SAC")) 
  
    def test_baja_no_toca_lo_reservado(self): 
        e = Existencia.objects.get() 
        e.reservada = 95 
        e.save() 
        self.assertEqual(self._baja(cantidad=10).status_code, 400) 
  
    def test_operario_no_puede_dar_de_baja(self): 
        self.client.force_authenticate(self.operario) 
        self.assertEqual(self._baja().status_code, 403)