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