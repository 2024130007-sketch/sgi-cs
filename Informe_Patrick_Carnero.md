# Informe de Trabajo Individual - Hito 2

*Alumno:* Patrick Carnero Lino
*Curso:* Ingeniería de Software
*Proyecto:* SGI-CS (Sistema de Gestión de Inventarios y Cadena de Suministro)
*Rama de trabajo:* hito2-patrick-reposicion

## 1. Rol en el Equipo y Módulos Asignados
*   *Mi rol:* Responsable de la base del proyecto y del Módulo 3.
*   *Parte A (Base del Proyecto):* Configuración inicial de Django, seguridad (JWT), permisos por roles, menú dinámico y conexión con Angular.
*   *Parte B (Módulo de Reposición):* Creación de la lógica de reglas de reposición, cálculo del punto de reorden, generación de alertas (stock y vencimiento) y desarrollo de las pantallas en Angular.

## 2. Descripción del Trabajo Realizado
*   *Configuración Base:* Se estructuró el backend con Django REST Framework y el frontend con Angular 19. Se implementó la autenticación con JSON Web Tokens (JWT) y un sistema de permisos personalizado para que cada rol (Administrador, Jefe de Almacén, Operario, Comprador) solo vea lo que le corresponde.
*   *Reglas de Reposición:* Se desarrolló el modelo ReglaReposicion que calcula automáticamente el punto de reorden usando la fórmula: (Demanda diaria × Tiempo de entrega) + Stock de seguridad.
*   *Gestión de Alertas:* Se creó el servicio evaluar_reposicion que verifica si el stock disponible bajó del punto de reorden (creando una alerta sin duplicados). También se programó la lógica de alertas de vencimiento revisando los lotes próximos a vencer en 30, 60 o 90 días.
*   *Interfaz de Usuario:* Se crearon las pantallas reglas.component.ts y alertas.component.ts en Angular para que el Jefe de Almacén pueda configurar las reglas y atender/descartar las alertas con un motivo.

## 3. Evidencias del Código
*   *Backend:* Lógica en backend/reposicion/models.py y backend/reposicion/services.py.
*   *Frontend:* Pantallas en frontend/src/app/features/reposicion/.
*   *Pruebas:* Archivo de tests en backend/reposicion/tests.py.

## 4. Enlaces de Interés
*   *Repositorio (Rama individual):* https://github.com/2024130007-sketch/sgi-cs/tree/hito2-patrick-reposicion
*   *Pull Request de la Parte B:* https://github.com/2024130007-sketch/sgi-cs/pull/7
