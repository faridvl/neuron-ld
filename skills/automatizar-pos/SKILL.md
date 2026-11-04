---
name: automatizar-pos
description: Automatiza el POS de LDCOM (WinForms) sin mouse ni teclado con Python y poslib — login, cambiar cliente y documento, agregar artículos, facturar, pagar, cerrar caja, leer mensajes. Usar al probar el POS, reproducir un bug de pantalla, armar un recorrido o cerrar la caja.
---

# Automatizar el POS (WinForms)

Todo se hace con `scripts\correr.py` y la librería `scripts\poslib`. No escribir scripts sueltos nuevos: si falta un paso,
se agrega un flujo a `poslib\flujos` y se registra en `flujos\__init__.py`. Los scripts viejos están en
`references\inventario-origen.md`.

## Requisitos
- Python 3.12 con `pywin32`, `pywinauto` y `pillow`. Correr siempre con `python -I`.
- Docker arriba (`rig docker` en la terminal real del usuario) y el POS apuntando a esa base.
- Usuario de prueba **qa_auto**, creado solo en el Docker local. Las credenciales NO van en el repo ni se imprimen:
  variables de entorno `POS_USUARIO` y `POS_CLAVE`, o `POS_CREDENCIALES` con la ruta de un archivo con líneas `Login: ...`
  y `Clave: ...` (por ejemplo el `credenciales-prueba.txt` de los scripts SQL del caso).

## Abrir el POS
En la terminal real del usuario (`mcp__terminal__run_in_terminal`), no con Bash de la sesión: lo que la sesión toca en
`%LOCALAPPDATA%` es una vista aislada. Desde el worktree a probar: `rig pos -SinCompilar` (`-Preventa` para preventa).
Para compilar antes, el script de compilación de la rama (el POS abierto bloquea el .exe: cerrarlo antes).
Borrar `BD\Factura_Backup*.xml` con el POS cerrado antes de cada escenario (ver `references\trampas.md`).

## Usar
```
python -I scripts\correr.py --listar                 # recorridos y flujos disponibles
python -I scripts\correr.py <pid> entrar             # login con qa_auto
python -I scripts\correr.py <pid> cerrar_caja        # ver references\cerrar-caja.md
python -I scripts\correr.py <pid> cerrar_caja --params "{\"efectivo\": 0}"   # parámetros del recorrido en JSON
python -I scripts\vigilar_modales.py <pid> 30        # captura durante 30 s los mensajes que se cierran solos
```
El `pid` es el de `LD.Facturacion`. Los recorridos (`scripts\recorridos.py`) son listas de pasos
`(flujo, parametros)`; el orquestador verifica cada paso antes de seguir y conecta a la ventana principal solo cuando el
paso la necesita (el login y el cierre de caja no la tienen).

## Mapa de poslib
| Módulo | Para qué |
|---|---|
| `base.py` | Win32 y UIA básicos: ventanas, textos, botones, `en_hilo`, `esperar`, capturas con `PrintWindow` |
| `modales.py` | Describir y vigilar modales, responder preguntas (check/ESC), cerrar errores .NET |
| `sesion.py` | Credenciales por entorno, detectar login, iniciar sesión |
| `fisico.py` | Clic físico por coordenadas de captura (factor 1.25) y UIA invoke por `auto_id` |
| `flujos\` | Un archivo por pantalla: `NOMBRE`, `PANTALLA`, `ejecutar(pos, **params)` |
| `orquestador.py` | Ejecuta los pasos en orden y para en el primero que falla |

## Reglas para no molestar al usuario
- Nada de `click_input`, `type_keys` ni `SendKeys`: mueven el mouse y roban el foco.
- Escribir con `set_edit_text` o `WM_SETTEXT`; pulsar con UIA `invoke` en hilo o `BM_CLICK`; capturar con `PrintWindow`.
- No abrir ni cerrar el POS si otro agente o sesión lo está usando. El clic físico (`fisico.py`) mueve el mouse ~1 s: avisar.

## Trampas principales
Detalle completo en `references\trampas.md`. Las que más cuestan: UIA se cuelga con modales abiertas; `Invoke` que abre una
modal no regresa (va en hilo); los mensajes se cierran solos en segundos; las preguntas tienen dos botones sin texto
(check izquierda, ESC derecha); números y ENTER se envían separados; Enter en la búsqueda selecciona; el doble clic por
mensajes no reproduce el clic físico; el SQL del contenedor corre en UTC; Validación de Rol al guardar una preventa;
~10 s de espera antes del login; el token puede vencer a medianoche.

## Pantallas (auto_id)
| Pantalla | Controles |
|---|---|
| Login `Frm_Login` | `tbUsuario`, `tbContrasena`, `bConectar`, `bSalir` |
| Tipo de Preventa `Frm_Lista` | `Bn_F1` General, `Bn_F2`... un botón por tipo, `Bn_Cancel` Salir |
| Principal `Frm_Facturacion` | `Text_Articulo`, `Btn_Agregar_Articulo`, `Barra` (ToolStrip paginado), `ListaArt` |
| Búsqueda de Artículos | EDIT de búsqueda, 3 botones sin texto (lupa, check, teclado), 3 `SysListView32` (Artículos, Sustitutos, Sugeridos) |

## poslib o FlaUI
- **poslib (Python)**: exploración, reproducir bugs, recorridos de QA contra el POS abierto en Docker, cierre de caja, captura
  de evidencia. Rápido de armar y no necesita compilar.
- **FlaUI (C#, `Automatizacion.Facturacion.UI.Tests` en el repo del POS)**: pruebas repetibles que viajan con el código y
  corren en la CI de la rama. Todavía en construcción: ante la duda, probar primero con poslib y pasar a FlaUI lo que se
  repita en cada release.

## Cierre
Cerrar la caja: `references\cerrar-caja.md`. Preparación de la base (usuario qa_auto, permisos, snapshots de solo lectura)
vive en los scripts SQL de cada caso, siempre en el Docker local, nunca en bases compartidas.
