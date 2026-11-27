import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import override_settings
from rest_framework.test import APITestCase

from respaldos.models import RegistroRespaldo
from respaldos.services.backup import crear_respaldo, rotar_respaldos
from usuarios.models import Usuario


CLAVE = "Clave12345"


def crear_usuario(email, rol):
    return Usuario.objects.create_user(
        username=email,
        email=email,
        password=CLAVE,
        first_name="Prueba",
        rol=rol,
    )


class PruebasDeRespaldos(APITestCase):

    def setUp(self):
        self.admin = crear_usuario("admin@sgi.com", "ADMINISTRADOR")
        self.operario = crear_usuario("operario@sgi.com", "OPERARIO")

    def autenticar(self, usuario):
        respuesta = self.client.post(
            "/api/auth/login",
            {"email": usuario.email, "password": CLAVE},
            format="json",
        )
        self.assertEqual(respuesta.status_code, 200)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + respuesta.data["access"]
        )

    def test_sin_autenticacion_no_puede_listar(self):
        respuesta = self.client.get("/api/respaldos/")
        self.assertEqual(respuesta.status_code, 401)

    def test_operario_no_puede_listar_ni_crear(self):
        self.autenticar(self.operario)

        lista = self.client.get("/api/respaldos/")
        creacion = self.client.post("/api/respaldos/")

        self.assertEqual(lista.status_code, 403)
        self.assertEqual(creacion.status_code, 403)

    def test_administrador_puede_listar_respaldos(self):
        self.autenticar(self.admin)

        respuesta = self.client.get("/api/respaldos/")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.data, [])

    def test_administrador_puede_crear_respaldo(self):
        self.autenticar(self.admin)

        with TemporaryDirectory() as temporal:
            with override_settings(BASE_DIR=Path(temporal)):
                respuesta = self.client.post("/api/respaldos/")

                self.assertEqual(respuesta.status_code, 201)
                self.assertTrue(respuesta.data["ok"])
                self.assertEqual(respuesta.data["usuario"], self.admin.pk)

    def test_rotacion_conserva_siete_respaldos(self):
        with TemporaryDirectory() as temporal:
            carpeta = Path(temporal)

            with override_settings(BASE_DIR=carpeta):
                for numero in range(8):
                    archivo = carpeta / f"respaldo_{numero}.sqlite3"
                    archivo.write_bytes(b"copia")

                    RegistroRespaldo.objects.create(
                        archivo=archivo.name,
                        tamano=5,
                        ok=True,
                    )

                rotar_respaldos()

                self.assertEqual(
                    RegistroRespaldo.objects.filter(ok=True).count(),
                    7,
                )
                self.assertFalse(
                    (carpeta / "respaldo_0.sqlite3").exists()
                )

    def test_error_de_creacion_no_se_registra_como_exitoso(self):
        with patch(
            "respaldos.services.backup.obtener_contenido_bd",
            side_effect=sqlite3.OperationalError("Error simulado"),
        ):
            with self.assertRaises(sqlite3.OperationalError):
                crear_respaldo()

        registro = RegistroRespaldo.objects.latest("id")

        self.assertFalse(registro.ok)
        self.assertIn("Error simulado", registro.error)