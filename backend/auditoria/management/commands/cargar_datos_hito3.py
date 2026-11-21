from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from almacenes.models import Almacen
from productos.models import Producto
from proveedores.models import Proveedor
from usuarios.models import Usuario
from inventario.models import Lote, Existencia, Movimiento, DetalleMovimiento
from reposicion.models import ReglaReposicion, Alerta


class Command(BaseCommand):
    help = "Carga datos de prueba para el Hito 3 del SGI"

    @transaction.atomic
    def handle(self, *args, **options):
        hoy = date.today()

        # 1. Usuario de prueba
        usuario, creado = Usuario.objects.get_or_create(
            email="admin.hito3@sgi.test",
            defaults={
                "username": "admin.hito3@sgi.test",
                "first_name": "Administrador Hito 3",
                "rol": Usuario.Rol.ADMINISTRADOR,
                "is_active": True,
            },
        )
        if creado:
            usuario.set_password("AdminHito3_2026")
            usuario.save()

        # 2. Almacenes
        almacen, _ = Almacen.objects.get_or_create(
            nombre="Almacen Central Hito 3",
            defaults={"direccion": "Sede principal"},
        )

        almacen_secundario, _ = Almacen.objects.get_or_create(
            nombre="Almacen Secundario Hito 3",
            defaults={"direccion": "Sede secundaria"},
        )

        # 3. Proveedor
        proveedor, _ = Proveedor.objects.get_or_create(
            ruc="20999999991",
            defaults={
                "razon_social": "Proveedor de Prueba Hito 3",
                "correo": "proveedor@sgi.test",
                "tiempo_entrega_dias": 5,
                "activo": True,
            },
        )

        # 4. Productos
        producto1, _ = Producto.objects.get_or_create(
            sku="H3-SKU-001",
            defaults={
                "nombre": "Producto de prueba Hito 3",
                "descripcion": "Producto para verificar inventario y auditoria",
                "marca": "SGI",
                "unidad_medida": "UNIDAD",
                "precio": "50.00",
                "activo": True,
            },
        )

        producto2, _ = Producto.objects.get_or_create(
            sku="H3-SKU-002",
            defaults={
                "nombre": "Producto con stock bajo Hito 3",
                "descripcion": "Producto para probar alertas de reposicion",
                "marca": "SGI",
                "unidad_medida": "UNIDAD",
                "precio": "25.00",
                "activo": True,
            },
        )

        # 5. Lotes
        lote1, _ = Lote.objects.get_or_create(
            producto=producto1,
            numero="H3-LOTE-001",
            defaults={
                "proveedor": proveedor,
                "fecha_fabricacion": hoy - timedelta(days=30),
                "fecha_vencimiento": hoy + timedelta(days=20),
                "estado": Lote.Estado.ACTIVO,
            },
        )

        lote2, _ = Lote.objects.get_or_create(
            producto=producto2,
            numero="H3-LOTE-002",
            defaults={
                "proveedor": proveedor,
                "fecha_fabricacion": hoy - timedelta(days=10),
                "estado": Lote.Estado.ACTIVO,
            },
        )

        # 6. Existencias
        existencia1, _ = Existencia.objects.get_or_create(
            lote=lote1,
            almacen=almacen,
            defaults={"cantidad": 50},
        )

        existencia2, _ = Existencia.objects.get_or_create(
            lote=lote2,
            almacen=almacen,
            defaults={"cantidad": 5},
        )

        # 7. Movimientos de ingreso para dejar trazabilidad
        for lote, cantidad, documento in [
            (lote1, 50, "H3-INGRESO-001"),
            (lote2, 5, "H3-INGRESO-002"),
        ]:
            movimiento, _ = Movimiento.objects.get_or_create(
                tipo=Movimiento.Tipo.INGRESO,
                almacen=almacen,
                usuario=usuario,
                documento_origen=documento,
            )

            DetalleMovimiento.objects.get_or_create(
                movimiento=movimiento,
                lote=lote,
                defaults={"cantidad": cantidad},
            )

        # 8. Reglas de reposición
        ReglaReposicion.objects.get_or_create(
            producto=producto1,
            almacen=almacen,
            defaults={
                "stock_minimo": 10,
                "stock_seguridad": 5,
                "stock_maximo": 100,
                "demanda_diaria": 2,
                "tiempo_entrega_dias": 5,
            },
        )

        ReglaReposicion.objects.get_or_create(
            producto=producto2,
            almacen=almacen,
            defaults={
                "stock_minimo": 10,
                "stock_seguridad": 5,
                "stock_maximo": 50,
                "demanda_diaria": 3,
                "tiempo_entrega_dias": 5,
            },
        )

        # 9. Alertas de prueba
        Alerta.objects.get_or_create(
            tipo=Alerta.Tipo.REPOSICION,
            producto=producto2,
            almacen=almacen,
            estado=Alerta.Estado.ABIERTA,
            defaults={
                "mensaje": "Stock bajo: revisar reposicion del producto",
                "cantidad_sugerida": 20,
            },
        )

        Alerta.objects.get_or_create(
            tipo=Alerta.Tipo.VENCIMIENTO,
            producto=producto1,
            almacen=almacen,
            lote=lote1,
            estado=Alerta.Estado.ABIERTA,
            defaults={
                "mensaje": "Lote proximo a vencer: revisar inventario",
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Datos de prueba del Hito 3 cargados correctamente."
            )
        )
        self.stdout.write(f"Almacenes: {Almacen.objects.count()}")
        self.stdout.write(f"Productos: {Producto.objects.count()}")
        self.stdout.write(f"Proveedores: {Proveedor.objects.count()}")
        self.stdout.write(f"Lotes: {Lote.objects.count()}")
        self.stdout.write(f"Existencias: {Existencia.objects.count()}")
        self.stdout.write(f"Movimientos: {Movimiento.objects.count()}")
        self.stdout.write(f"Alertas: {Alerta.objects.count()}")
        self.stdout.write(f"Reglas de reposicion: {ReglaReposicion.objects.count()}")
