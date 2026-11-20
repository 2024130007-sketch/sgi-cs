
from django.urls import reverse
from rest_framework.test import APITestCase

from usuarios.models import Usuario
from auditoria.models import Bitacora


class BitacoraAPITests(APITestCase):

    def setUp(self):
        self.admin = Usuario.objects.create_user(
            username="admin_auditoria",
            email="admin_auditoria@test.com",
            password="Test123456",
            rol=Usuario.Rol.ADMINISTRADOR
        )

        self.operario = Usuario.objects.create_user(
            username="operario_auditoria",
            email="operario_auditoria@test.com",
            password="Test123456",
            rol=Usuario.Rol.OPERARIO
        )

        self.url = reverse("auditoria-list")

        self.registro1 = Bitacora.objects.create(
            usuario=self.admin,
            accion=Bitacora.Accion.CREAR,
            entidad="Lote",
            entidad_id=1,
            detalle="Creación de lote"
        )

        self.registro2 = Bitacora.objects.create(
            usuario=self.operario,
            accion=Bitacora.Accion.MODIFICAR,
            entidad="Movimiento",
            entidad_id=2,
            detalle="Modificación de movimiento"
        )

    def obtener_resultados(self, response):
        data = response.data
        if isinstance(data, dict):
            return data.get("results", [])
        return data

    def test_administrador_puede_consultar_bitacora(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.obtener_resultados(response)), 2)

    def test_operario_no_puede_consultar_bitacora(self):
        self.client.force_authenticate(user=self.operario)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_filtro_por_accion(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.url, {"accion": "CREAR"})

        self.assertEqual(response.status_code, 200)
        resultados = self.obtener_resultados(response)
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["accion"], "CREAR")

    def test_filtro_por_entidad(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.url, {"entidad": "Movimiento"})

        self.assertEqual(response.status_code, 200)
        resultados = self.obtener_resultados(response)
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["entidad"], "Movimiento")
