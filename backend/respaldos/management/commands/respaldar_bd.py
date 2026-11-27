
from django.core.management.base import BaseCommand, CommandError

from respaldos.services.backup import crear_respaldo


class Command(BaseCommand):
    help = "Genera un respaldo de la base de datos SQLite."

    def handle(self, *args, **options):
        try:
            registro = crear_respaldo()
        except Exception as exc:
            raise CommandError(f"No se pudo generar el respaldo: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Respaldo creado correctamente: {registro.archivo} "
                f"({registro.tamano} bytes)"
            )
        )
