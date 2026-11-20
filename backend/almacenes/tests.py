from rest_framework.test import APITestCase 
 
from usuarios.models import Usuario 


class AlmacenTests(APITestCase): 
    def setUp(self): 
        self.client.force_authenticate(Usuario.objects.create_user("a@t.pe", "a@t.pe", "Clave1234!", rol="ADMINISTRADOR")) 
 
    def test_crud_basico(self): 
        r = self.client.post("/api/almacenes/", {"nombre": "Central", "direccion": "Jr. 1"}, format="json") 
        self.assertEqual(r.status_code, 201) 
        aid = r.data["id"] 
        self.client.patch(f"/api/almacenes/{aid}/", {"direccion": "Jr. 2"}, format="json") 
        self.assertEqual(self.client.get(f"/api/almacenes/{aid}/").data["direccion"], "Jr. 2") 
        self.client.delete(f"/api/almacenes/{aid}/") 
        self.assertFalse(self.client.get(f"/api/almacenes/{aid}/").data["activo"]) 
 
    def test_nombre_duplicado_y_direccion_vacia(self): 
        self.client.post("/api/almacenes/", {"nombre": "Central", "direccion": "Jr. 1"}, format="json") 
        r = self.client.post("/api/almacenes/", {"nombre": "central", "direccion": "Jr. 2"}, format="json") 
        self.assertEqual(r.status_code, 400) 
        r = self.client.post("/api/almacenes/", {"nombre": "Otro", "direccion": " "}, format="json") 
        self.assertEqual(r.status_code, 400) 
 
    def test_operario_no_escribe(self): 
        self.client.force_authenticate(Usuario.objects.create_user("o@t.pe", "o@t.pe", "Clave1234!", rol="OPERARIO")) 
        r = self.client.post("/api/almacenes/", {"nombre": "X", "direccion": "Y"}, format="json") 
        self.assertEqual(r.status_code, 403)