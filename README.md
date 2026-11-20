# SGI-CS - Sistema de Gestión de Inventarios y Cadena de Suministro

Sistema web para una empresa distribuidora con varios almacenes. Controla el stock por producto, almacén y lote (con salidas FEFO), gestiona transferencias, reglas de reposición y alertas.

Proyecto grupal de Ingeniería de Software - Universidad de Huánuco - Grupo 3 - 2026.

## Tecnologías
| Capa | Tecnología |
|---|---|
| Backend (API REST) | Python 3.11+ · Django 5 · Django REST Framework · JWT (simplejwt) |
| Frontend | Angular 19 (componentes standalone) |
| Base de datos | SQLite (desarrollo) |

## Módulos funcionales del Hito 2
1. **Seguridad y datos maestros:** inicio de sesión, usuarios y roles, productos con códigos de barras, almacenes y proveedores.
2. **Movimientos de inventario y stock:** ingreso con lote y vencimiento, salida con FEFO, consulta de stock y kardex.
Además, en proceso: transferencias entre almacenes y reglas de reposición con alertas.

## Cómo ejecutar

### Requisitos
- Python 3.11 o superior
- Node.js 20 o superior (incluye npm)
- Git

### 1. Backend (Django)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate # en Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py cargar_datos_prueba
python manage.py runserver

## Hito 3 - Nuevos Módulos (Noviembre 2026)

En este hito se implementaron las siguientes funcionalidades clave para el sistema:

### Módulo de Recepción de Órdenes de Compra (Patrick Carnero Lino)
*   **Modelos:** Se crearon las tablas `Recepcion` y `DetalleRecepcion` para registrar la llegada de mercadería.
*   **Lógica de Negocio:** El servicio `registrar_recepcion` permite recibir órdenes de compra de forma total o parcial. Utiliza transacciones atómicas (`@transaction.atomic`), lo que garantiza que si una línea de la recepción falla, no se ingresa ninguna al stock (todo o nada).
*   **API REST:** Se expusieron los endpoints necesarios para que el frontend pueda consultar y registrar recepciones.
*   **Interfaz:** Se desarrolló la pantalla `recepcion.component.ts` en Angular para que el Jefe de Almacén pueda ingresar el ID de la orden, el documento de guía y la cantidad recibida.

### (Aquí irán los otros módulos cuando tus compañeros los terminen)
*   *Módulo de Compras (Adrian)*
*   *Módulo de Ajustes (Ashly)*
*   *Módulo de Trazabilidad (Dresly)*
*   *Módulo de Auditoría (Linda)*