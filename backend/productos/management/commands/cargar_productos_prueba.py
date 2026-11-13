
from django.core.management.base import BaseCommand

from productos.models import Producto, CodigoBarras

# SKU, nombre, descripcion, marca, unidad, precio, codigo de barras
PRODUCTOS_DE_PRUEBA = [
    ("SKU001", "Laptop Lenovo", "Laptop para oficina", "Lenovo", "UNIDAD", "2500.00", "7750000000011"),
    ("SKU002", "Mouse inalámbrico", "Mouse óptico inalámbrico", "Logitech", "UNIDAD", "45.90", "7750000000028"),
    ("SKU003", "Teclado USB", "Teclado para computadora", "HP", "UNIDAD", "65.00", "7750000000035"),
    ("SKU004", "Monitor LED 24", "Monitor LED de 24 pulgadas", "Samsung", "UNIDAD", "650.00", "7750000000042"),
    ("SKU005", "Memoria USB 64GB", "Memoria USB de 64 GB", "Kingston", "UNIDAD", "35.50", "7750000000059"),
]


class Command(BaseCommand):
    help = "Crea productos y códigos de barras de prueba"

    def handle(self, *args, **opciones):
        for sku, nombre, descripcion, marca, unidad, precio, codigo in PRODUCTOS_DE_PRUEBA:

            producto, creado = Producto.objects.get_or_create(
                sku=sku,
                defaults={
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "marca": marca,
                    "unidad_medida": unidad,
                    "precio": precio,
                    "activo": True,
                }
            )

            if creado:
                self.stdout.write(
                    self.style.SUCCESS(f"Producto creado: {nombre}")
                )
            else:
                self.stdout.write(f"Ya existe: {nombre}")

            codigo_barras, codigo_creado = CodigoBarras.objects.get_or_create(
                codigo=codigo,
                defaults={"producto": producto}
            )

            if codigo_creado:
                self.stdout.write(
                    self.style.SUCCESS(f"Código de barras creado: {codigo}")
                )
            else:
                self.stdout.write(f"Ya existe el código: {codigo}")
