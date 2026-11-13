from django.core.management.base import BaseCommand

from usuarios.models import Usuario

# correo, nombre, rol, contraseña (solo para pruebas)
USUARIOS_DE_PRUEBA = [
    ("admin@sgi.com", "Administrador SGI", "ADMINISTRADOR", "Admin12345"),
    ("jefe@sgi.com", "Jefe de Almacén", "JEFE_ALMACEN", "Jefe12345"),
    ("operario@sgi.com", "Operario de Prueba", "OPERARIO", "Operario123"),
    ("comprador@sgi.com", "Comprador de Prueba", "COMPRADOR", "Comprador123"),
]


class Command(BaseCommand):
    help = "Crea un usuario de prueba por cada rol (si todavía no existen)"

    def handle(self, *args, **opciones):
        for email, nombre, rol, clave in USUARIOS_DE_PRUEBA:
            if Usuario.objects.filter(email=email).exists():
                self.stdout.write(f"Ya existe: {email}")
                continue
            Usuario.objects.create_user(username=email, email=email, password=clave,
                                        first_name=nombre, rol=rol)
            self.stdout.write(self.style.SUCCESS(f"Creado: {email} ({rol})"))
