# SGI-CS - Sistema de Gestión de Inventarios y Cadena de Suministro

Sistema web para una empresa distribuidora con varios almacenes. Controla el stock por producto, almacén y lote (con salidas FEFO), gestiona transferencias, reglas de reposición y alertas.

Proyecto grupal de Ingeniería de Software - Universidad de Huánuco - Grupo 3 - 2026.

## Tecnologías
| Capa | Tecnología |
|---|---|
| Backend (API REST) | Python 3.11+ · Django 5 · Django REST Framework · JWT (simplejwt) |
| Frontend | Angular 19 (componentes standalone) |
| Base de datos | SQLite (desarrollo) |

## Módulos del Hito 2
Módulos funcionales a nivel básico (con validaciones, pruebas automáticas y pantalla en el menú):

1. **Seguridad y datos maestros:** inicio de sesión, usuarios y roles, productos con códigos de barras, almacenes y proveedores.
2. **Movimientos de inventario y stock:** ingreso con lote y vencimiento, salida con FEFO, consulta de stock y kardex.

Avance adicional ya integrado: transferencias entre almacenes y reglas de reposición con alertas.

| Módulo | Responsable |
|---|---|
| Base del proyecto, menú, rutas, reposición y alertas | Patrick Carnero |
| Login, usuarios y productos | Linda Herrera |
| Almacenes y transferencias | Ashly Zuñiga |
| Proveedores y kardex | Adrian Carlos |
| Ingreso, salida FEFO y stock | Dresly Pineda |

## Módulos del Hito 3
Avance proyectado: 97 de 121 puntos (80,2 %). Se suman a los del Hito 2:

| Módulo | Qué hace | Responsable |
|---|---|---|
| Órdenes de compra (`backend/compras`) | Crear y modificar órdenes, enviarlas a aprobación, aprobar o rechazar con motivo | Adrian Carlos |
| Recepción (`backend/recepciones`) | Recibir mercadería contra una orden (total o parcial) y registrar el ingreso al stock | Patrick Carnero |
| Ajustes y bajas (`backend/ajustes`) | Conteo físico con corrección de stock; bajas por vencimiento o daño y devolución a proveedor | Ashly Zuñiga |
| Trazabilidad y concurrencia (`backend/inventario`) | Historial por lote, cuarentena, bloqueo optimista con reintentos | Dresly Pineda |
| Bitácora (`backend/auditoria`) | Registro automático de quién hizo qué; consulta con filtros (solo administrador) | Linda Herrera |
| Correo (`backend/notificaciones`) | Envío de órdenes aprobadas al proveedor y resumen de alertas al personal | Linda Herrera |

Pendiente para el Hito 4: sincronización con el ERP, reportes PDF y Excel, lectura por cámara y GS1-128, modo sin conexión y copias de seguridad.

## Cómo ejecutar

### Requisitos
- Python 3.11 o superior
- Node.js 20 o superior (incluye npm)
- Git

### 1. Backend (Django)
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # en Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_usuarios_prueba
python manage.py cargar_productos_prueba
python manage.py runserver
```
La API queda en `http://localhost:8000/api`.

### 2. Frontend (Angular)
En otra terminal:
```bash
cd frontend
npm install
npm start
```
La aplicación queda en `http://localhost:4200`.

### Usuarios de prueba
| Correo | Contraseña | Rol |
|---|---|---|
| admin@sgi.com | Admin12345 | Administrador |
| jefe@sgi.com | Jefe12345 | Jefe de almacén |
| operario@sgi.com | Operario123 | Operario |
| comprador@sgi.com | Comprador123 | Comprador |

Son credenciales solo para pruebas.

### Pruebas automáticas
```bash
cd backend
python manage.py test
```
