from rest_framework.test import APITestCase
from usuarios.models import Usuario
from .models import Recepcion

class RecepcionTests(APITestCase):
    def setUp(self):
        # Creamos un usuario Jefe de Almacén para las pruebas
        self.u = Usuario.objects.create_user("test@t.pe", "Clave1234!", rol="JEFE_ALMACEN")
        self.client.force_authenticate(self.u)

    def test_endpoint_recepcion_existe(self):
        # Prueba básica: verifica que el endpoint POST responde (aunque sea con error de validación)
        respuesta = self.client.post("/api/recepciones/", {}, format="json")
        # Como no enviamos datos, esperamos un 400 (Bad Request) o 201 (Created) según la vista
        self.assertIn(respuesta.status_code, [400, 201])