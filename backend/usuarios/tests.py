from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from .models import MAX_INTENTOS, Usuario

CLAVE = "Clave12345"


def crear_usuario(email, rol="OPERARIO", clave=CLAVE, **extra):
    return Usuario.objects.create_user(username=email, email=email, password=clave,
                                       first_name="Prueba", rol=rol, **extra)


class PruebasDeLogin(APITestCase):
    def setUp(self):
        self.usuario = crear_usuario("operario@sgi.com", "OPERARIO")

    def entrar(self, email="operario@sgi.com", clave=CLAVE):
        return self.client.post("/api/auth/login", {"email": email, "password": clave}, format="json")

    def test_login_correcto_devuelve_token_y_datos_del_usuario(self):
        r = self.entrar()
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)
        self.assertEqual(r.data["usuario"]["email"], "operario@sgi.com")
        self.assertEqual(r.data["usuario"]["rol"], "OPERARIO")
        self.assertEqual(r.data["usuario"]["rol_display"], "Operario")

    def test_login_con_clave_incorrecta_da_401(self):
        r = self.entrar(clave="otra-clave")
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.data["detail"], "Correo o contraseña incorrectos.")

    def test_login_con_correo_que_no_existe_da_el_mismo_mensaje(self):
        r = self.entrar(email="nadie@sgi.com")
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.data["detail"], "Correo o contraseña incorrectos.")

    def test_login_sin_datos_da_400(self):
        r = self.client.post("/api/auth/login", {}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_cuenta_se_bloquea_al_quinto_intento_fallido(self):
        for _ in range(MAX_INTENTOS - 1):
            self.assertEqual(self.entrar(clave="mal").status_code, 401)
        r = self.entrar(clave="mal")
        self.assertEqual(r.status_code, 423)
        self.assertIn("bloqueada", r.data["detail"])

    def test_cuenta_bloqueada_no_entra_ni_con_la_clave_correcta(self):
        for _ in range(MAX_INTENTOS):
            self.entrar(clave="mal")
        r = self.entrar()
        self.assertEqual(r.status_code, 423)

    def test_el_bloqueo_termina_despues_del_tiempo(self):
        for _ in range(MAX_INTENTOS):
            self.entrar(clave="mal")
        Usuario.objects.filter(pk=self.usuario.pk).update(bloqueado_hasta=timezone.now() - timedelta(minutes=1))
        self.assertEqual(self.entrar().status_code, 200)

    def test_login_correcto_reinicia_los_intentos(self):
        self.entrar(clave="mal")
        self.entrar(clave="mal")
        self.entrar()
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.intentos_fallidos, 0)

    def test_usuario_desactivado_no_puede_entrar(self):
        Usuario.objects.filter(pk=self.usuario.pk).update(is_active=False)
        r = self.entrar()
        self.assertEqual(r.status_code, 403)
        self.assertIn("desactivado", r.data["detail"])

    def test_sin_token_no_se_puede_entrar_a_una_ruta_protegida(self):
        self.assertEqual(self.client.get("/api/usuarios/").status_code, 401)

    def test_logout_responde_ok_con_token(self):
        token = self.entrar().data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.assertEqual(self.client.post("/api/auth/logout").status_code, 200)

    def test_el_superusuario_creado_con_createsuperuser_es_administrador(self):
        superusuario = Usuario.objects.create_superuser("jefe", "super@sgi.com", CLAVE)
        self.assertEqual(superusuario.rol, "ADMINISTRADOR")


class PruebasDeGestionDeUsuarios(APITestCase):
    def setUp(self):
        self.admin = crear_usuario("admin@sgi.com", "ADMINISTRADOR")
        self.operario = crear_usuario("operario@sgi.com", "OPERARIO")

    def entrar_como(self, usuario):
        r = self.client.post("/api/auth/login", {"email": usuario.email, "password": CLAVE}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + r.data["access"])

    def datos_nuevos(self, **cambios):
        datos = {"email": "nuevo@sgi.com", "first_name": "Nuevo", "rol": "COMPRADOR", "password": "Nueva12345"}
        datos.update(cambios)
        return datos

    def test_administrador_puede_listar_usuarios(self):
        self.entrar_como(self.admin)
        r = self.client.get("/api/usuarios/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 2)

    def test_operario_no_puede_listar_usuarios(self):
        self.entrar_como(self.operario)
        r = self.client.get("/api/usuarios/")
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.data["detail"], "No tiene permiso para realizar esta acción con su rol.")

    def test_administrador_crea_usuario_con_rol_y_ese_usuario_puede_entrar(self):
        self.entrar_como(self.admin)
        r = self.client.post("/api/usuarios/", self.datos_nuevos(), format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["rol"], "COMPRADOR")
        self.assertNotIn("password", r.data)
        self.client.credentials()   # sin token
        r = self.client.post("/api/auth/login", {"email": "nuevo@sgi.com", "password": "Nueva12345"}, format="json")
        self.assertEqual(r.status_code, 200)

    def test_no_se_crea_usuario_con_correo_repetido(self):
        self.entrar_como(self.admin)
        r = self.client.post("/api/usuarios/", self.datos_nuevos(email="operario@sgi.com"), format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("Ese correo ya está registrado.", str(r.data))

    def test_no_se_crea_usuario_con_clave_corta(self):
        self.entrar_como(self.admin)
        r = self.client.post("/api/usuarios/", self.datos_nuevos(password="abc"), format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("password", r.data)

    def test_no_se_crea_usuario_sin_nombre_ni_clave(self):
        self.entrar_como(self.admin)
        r = self.client.post("/api/usuarios/", {"email": "x@sgi.com", "rol": "OPERARIO"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("first_name", r.data)

    def test_administrador_cambia_el_rol_de_otro_usuario(self):
        self.entrar_como(self.admin)
        r = self.client.patch(f"/api/usuarios/{self.operario.pk}/", {"rol": "JEFE_ALMACEN"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.operario.refresh_from_db()
        self.assertEqual(self.operario.rol, "JEFE_ALMACEN")

    def test_administrador_no_puede_quitarse_su_propio_rol(self):
        self.entrar_como(self.admin)
        r = self.client.patch(f"/api/usuarios/{self.admin.pk}/", {"rol": "OPERARIO"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_administrador_no_puede_desactivarse_a_si_mismo(self):
        self.entrar_como(self.admin)
        r = self.client.delete(f"/api/usuarios/{self.admin.pk}/")
        self.assertEqual(r.status_code, 400)

    def test_delete_solo_desactiva_al_usuario(self):
        self.entrar_como(self.admin)
        r = self.client.delete(f"/api/usuarios/{self.operario.pk}/")
        self.assertEqual(r.status_code, 200)
        self.operario.refresh_from_db()
        self.assertFalse(self.operario.is_active)

    def test_administrador_desbloquea_un_usuario(self):
        for _ in range(MAX_INTENTOS):
            self.client.post("/api/auth/login", {"email": "operario@sgi.com", "password": "mal"}, format="json")
        self.entrar_como(self.admin)
        r = self.client.post(f"/api/usuarios/{self.operario.pk}/desbloquear/")
        self.assertEqual(r.status_code, 200)
        self.operario.refresh_from_db()
        self.assertFalse(self.operario.esta_bloqueado())

    def test_lista_de_roles_tiene_los_cuatro_roles(self):
        self.entrar_como(self.admin)
        r = self.client.get("/api/usuarios/roles/")
        self.assertEqual([x["valor"] for x in r.data],
                         ["ADMINISTRADOR", "JEFE_ALMACEN", "OPERARIO", "COMPRADOR"])
