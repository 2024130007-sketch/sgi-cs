from rest_framework.test import APITestCase
from usuarios.models import Usuario

class ProveedorTests(APITestCase):
    def setUp(self):
        self.client.force_authenticate(Usuario.objects.create_user("c@t.pe", "Clave1234!", rol="COMPRADOR"))

    def _datos(self, ruc="20123456789"):
        return {"ruc": ruc, "razon_social": "Andina SAC", "correo": "a@andina.pe", "tiempo_entrega_dias": 5}

    def test_crud_basico(self):
        r = self.client.post("/api/proveedores/", self._datos(), format="json")
        self.assertEqual(r.status_code, 201)
        pid = r.data["id"]
        self.client.patch(f"/api/proveedores/{pid}/", {"tiempo_entrega_dias": 7}, format="json")
        self.assertEqual(self.client.get(f"/api/proveedores/{pid}/").data["tiempo_entrega_dias"], 7)
        self.client.delete(f"/api/proveedores/{pid}/")
        self.assertFalse(self.client.get(f"/api/proveedores/{pid}/").data["activo"])

    def test_ruc_debe_tener_11_digitos(self):
        for ruc in ["123", "2012345678A", "201234567890"]:
            self.assertEqual(self.client.post("/api/proveedores/", self._datos(ruc), format="json").status_code, 400)

    def test_ruc_duplicado(self):
        self.client.post("/api/proveedores/", self._datos(), format="json")
        self.assertEqual(self.client.post("/api/proveedores/", self._datos(), format="json").status_code, 400)

    def test_correo_invalido(self):
        d = self._datos()
        d["correo"] = "no-es-correo"
        self.assertEqual(self.client.post("/api/proveedores/", d, format="json").status_code, 400)
