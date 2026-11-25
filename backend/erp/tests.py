from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APITestCase
from usuarios.models import Usuario
from .models import ColaERP, EquivalenciaERP
from . import services

class ErpTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user("admin@t.pe", "Clave1234!", rol="ADMINISTRADOR")
        self.client.force_authenticate(self.user)

    def test_encolar_y_procesar(self):
        services.encolar("RECEPCION", {"lineas": []})
        self.assertEqual(ColaERP.objects.filter(estado="PENDIENTE").count(), 1)
        services.procesar_pendientes()
        self.assertEqual(ColaERP.objects.filter(estado="ENVIADO").count(), 1)

    @override_settings(ERP_SIMULAR_CAIDA=True)
    def test_fallo_erp_reintenta(self):
        services.encolar("RECEPCION", {"lineas": []})
        services.procesar_pendientes()
        item = ColaERP.objects.first()
        self.assertEqual(item.estado, "PENDIENTE")
        self.assertEqual(item.intentos, 1)

    @override_settings(ERP_SIMULAR_CAIDA=True)
    def test_maximo_intentos(self):
        services.encolar("RECEPCION", {"lineas": []})
        item = ColaERP.objects.first()
        # Forzamos 5 intentos
        for _ in range(5):
            item.proximo_intento = timezone.now() - timezone.timedelta(minutes=1)
            item.save()
            services.procesar_pendientes()
        item.refresh_from_db()
        self.assertEqual(item.estado, "ERROR")