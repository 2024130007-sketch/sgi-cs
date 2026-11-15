# Informe de Trabajo Individual - Hito 2

**Alumno:** Adrian Carlos  
**Código:** 2023210222  
**Curso:** Ingeniería de Software  
**Proyecto:** SGI-CS (Sistema de Gestión de Inventarios y Cadena de Suministro)  
**Rama de trabajo:** `hito2-adrian-proveedores`  
**Fecha:** 15/11/2026  

---

## 1. Rol en el Equipo y Módulos Asignados
* **Mi rol:** Desarrollo del Módulo de Gestión de Proveedores en el Backend y vistas de Proveedores y Kardex de Movimientos en el Frontend.
* **Parte A (Backend - Django REST Framework):** Implementación completa de la aplicación `proveedores` (modelo, serializador con validación de RUC, vistas REST, rutas y pruebas unitarias).
* **Parte B (Frontend - Angular 19):** Desarrollo de componentes *standalone* para la gestión de proveedores y la consulta cronológica del Kardex de inventario.

---

## 2. Descripción del Trabajo Realizado
* **Modelo de Datos (`backend/proveedores/models.py`):** Se creó la entidad `Proveedor` (RF-10) con los campos `ruc` (único, máximo 11 caracteres), `razon_social`, `correo`, `tiempo_entrega_dias` y `activo` (borrado lógico para conservar el historial de compras)[cite: 2].
* **Validación de Reglas de Negocio (`backend/proveedores/serializers.py`):** Se implementó `ProveedorSerializer` con validación estricta del RUC peruano (11 dígitos numéricos y prefijo válido `10` o `20`) antes de registrar o actualizar datos[cite: 2].
* **API REST y Seguridad (`views.py` / `urls.py`):** Se expusieron los endpoints bajo `/api/proveedores/` protegidos mediante autenticación JWT (`simplejwt`), permitiendo listar, buscar, crear, editar y cambiar el estado (`Activo`/`Inactivo`) de proveedores[cite: 1].
* **Pruebas Automatizadas (`backend/proveedores/tests.py`):** Se desarrollaron pruebas unitarias que verifican el registro exitoso de proveedores válidos y el rechazo automático de RUCs mal formados.
* **Interfaces en Angular 19 (`proveedores.component.ts` y `kardex.component.ts`):** Se construyeron las pantallas independientes para administrar proveedores (con manejo de alertas de validación) y auditar los movimientos de ingreso y salida de stock en el Kardex[cite: 1].

---

## 3. Evidencias del Código
* **Backend:** `backend/proveedores/models.py`, `serializers.py`, `views.py`, `urls.py`, `tests.py`[cite: 2].
* **Frontend:** `frontend/src/app/features/proveedores/proveedores.component.ts` y `frontend/src/app/features/inventario/kardex.component.ts`.
* **Integración:** Pull Request `#4` (`hito2-adrian-proveedores` $\rightarrow$ `main`) aprobado e integrado sin conflictos[cite: 2].
