# Hito 3 – Evidencias de integración (Grupo 3)

Verificado el 20/11/2026 clonando `main` desde cero.

## E1 – Repositorio actualizado
- Repositorio: https://github.com/2024130007-sketch/sgi-cs
- Último commit de `main`: `d4ea840` – «Agrega la migración de recepciones que faltaba – Dresly Pineda Rumaldo – 12:47 a.m. – 20/11/2026 terminado».
- Cambios de la integración respecto de `main` anterior: 76 archivos, +2455 / −91 líneas.

## E2 – Historial de commits (desde 15/11, sin fusiones)
| Integrante | Commits | Días con commits |
|---|---|---|
| Dresly Pineda (`derke0403`) | 9 | 4 (15, 17, 18, 20) |
| Patrick Carnero Lino | 7 | 3 |
| Ashly Zuñiga (`Ashly-Zharick124`) | 6 | 3 |
| Adrian Carlos | 6 | 2 |
| Linda Herrera (aparece como «Cristina») | 3 | 3 |

Commits por día desde el 13/11: 13/11 (36, Hito 2), 15/11 (1), 16/11 (1), 17/11 (13), 18/11 (11), 19/11 (1), 20/11 (4).

## E3 – Colaboración y revisiones
- PR #10 (Adrian, órdenes de compra): revisado y aprobado por Dresly, fusionado el 18/11 a las 11:29 p.m.
- Integración: 6 ramas fusionadas el 20/11 (`fix/integracion-hito2`, `hito3-dresly-base`, `hito3-ashly-ajustes`, `hito3-linda-auditoria`, `hito3-dresly-inventario`, `hito3-patrick-recepcion`).

## E6 – Pruebas automáticas (clon limpio de `main`)
- `manage.py migrate` desde cero: OK.
- `manage.py check`: sin problemas.
- `manage.py makemigrations --check`: «No changes detected».
- `manage.py test`: **95 pruebas, OK** (52 del Hito 2 + 43 del Hito 3).
- `ng build` del frontend: compila sin errores.

## Problemas encontrados al integrar y cómo se corrigieron
| Problema | Causa | Corrección |
|---|---|---|
| `main` fallaba con `FieldError: 'activo'` | Se fusionó el PR #10 antes de `fix/integracion-hito2` (faltaban migraciones) | Se fusionó `fix/integracion-hito2` |
| Conflictos en `urls.py` y pantallas de compras, ajustes, recepciones | La base del Hito 3 deja archivos provisionales | Se dejó la versión de cada responsable |
| `NodeNotFoundError: ('proveedor','0001_initial')` | La migración de ajustes apuntaba a una app que no existe (`proveedor` en vez de `proveedores`) | Migración de ajustes regenerada |
| `table ajustes_ajuste has no column named usuario_id` | La migración de ajustes escrita a mano no tenía el campo `usuario` | Misma regeneración |
| `no such table: recepciones_detallerecepcion` | La rama de recepciones no incluía su migración | Migración de recepciones agregada |
| Dos pantallas de bitácora (`/bitacora` provisional y `/auditoria` de Linda) | Rutas duplicadas | Se dejó la de Linda y se quitó la provisional |
| README con dos versiones | Conflicto entre las ramas de Dresly y Patrick | Se conservaron ambas secciones |

## Pendientes del Hito 3
- Comando de datos de prueba del Hito 3 (`cargar_datos_hito3`): por agregar; mientras tanto se usan `cargar_usuarios_prueba` y `cargar_productos_prueba`.
- Tabla de pruebas manuales (Anexo C) y sección individual del informe (Anexo B) de cada integrante.
- Recalcular la tabla de avance (Anexo A) con lo que cada módulo entrega en `main`.
- Etiqueta `hito-3` al cerrar la entrega.
