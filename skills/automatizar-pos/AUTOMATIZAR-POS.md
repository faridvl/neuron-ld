# Cómo probar el POS (WinForms) de forma automática, sin mouse ni teclado

Probado el 2026-10-23 con el POS de Preventa de `preventa-sucursal-destino` (Docker). Los scripts viven en
`evidencias\preventa-sucursal-destino\auto\`; copiarlos o reutilizarlos tal cual.

## Requisitos (ya instalados en esta PC)
- Python 3.12 con `pywinauto 0.6.9`, `pywin32`, `comtypes`, `pillow` (`python -I -m pip install pywinauto pillow`).
- Usuario de prueba **qa_auto** (Usuario_Id 9001) creado SOLO en el Docker local con
  `pruebas-sql\preventa-sucursal-destino\03-usuario-prueba-docker.sql`; se borra con el `04-...`.
  Clave en `pruebas-sql\preventa-sucursal-destino\credenciales-prueba.txt` (nunca en chats ni commits).
- Docker arriba (`dp docker` en la terminal real) y el slot de `dp` apuntando al worktree a probar
  (`asignar-slot-otros.ps1`, correrlo en la terminal real: lo que Claude escribe en AppData no llega al usuario).

## Abrir el POS
En la terminal real (`mcp__terminal__run_in_terminal`), parado en el worktree: `dp pos -Preventa`
(`-SinCompilar` si ya está compilado). Para recompilar con pruebas: `compilar-rama-facturacion.ps1 -Carpeta <worktree>`
(el POS abierto bloquea el .exe: cerrarlo antes con `Stop-Process -Name LD.Facturacion`).

## Reglas para no molestar al usuario
- Nada de `click_input`, `type_keys`, `SendKeys`: mueven el mouse o roban el foco.
- Escribir con `set_edit_text` (UIA ValuePattern o WM_SETTEXT), pulsar con `invoke()` (UIA) o `BM_CLICK` por `PostMessage`.
- Capturas con `PrintWindow` (`pos_ui.capturar`): funcionan con la ventana tapada.

## Trampas que ya nos mordieron
1. **`Invoke` sobre un botón que abre una ventana modal no regresa** hasta que se cierre la modal. Usar
   `pos_ui.invocar_sin_bloquear` (hilo aparte) o `PostMessage BM_CLICK`.
2. **UIA se cuelga** (`children()`/`descendants()`) en ventanas con ciertos controles, sobre todo la de Búsqueda de
   Artículos y cuando hay una modal abierta. Para esas ventanas usar la Windows API: `pos_ui.manejador_por_titulo`,
   `hijos_win32`, y `pywinauto` con `backend="win32"` (lee las grillas `SysListView32` con `.texts()`).
   Correr los scripts con `Start-Process ... -WindowStyle Hidden` y un tope de tiempo (`WaitForExit`) para no quedar colgado.
3. En PowerShell, un argumento con espacios hay que pasarlo entre comillas dobles dentro de comillas simples:
   `-ArgumentList ...,'"MANGUERA LECHE"'`; si no, Python recibe dos argumentos.
4. Enter dentro del cuadro de búsqueda **selecciona** el primer resultado (abre "Modificar Cantidad"): para buscar,
   pulsar la lupa (`pulsar_boton_win32(manejador, indice_sin_texto=0)`).
5. La barra de funciones (F1..F12) es un `ToolStrip`: sus botones salen en UIA con el texto ("Buscar\r\nArtículo"),
   sin `auto_id`. Se pulsan con `invocar_sin_bloquear`.
6. pywinauto avisa que el POS es de 32 bits y Python de 64: es solo una advertencia, funciona.

7. **Los mensajes del POS (Frm_Mensaje) se cierran solos en pocos segundos** y su cuerpo no es texto de ventana: hay que
   sondear cada 0.25 s y capturar (`modales.py <pid> <prefijo> <segundos>`), luego leer la imagen.
8. **Mensajes y la ventana principal comparten título** ("LDCOM - Preventa"): la principal es la ventana visible más grande
   (`pos_ui.manejador_principal`). Los diálogos tipo pregunta tienen dos botones sin texto: check (izq.) y ESC (der.);
   `confirmar_pregunta.py` responde. ESC o el tiempo equivalen a cancelar.
9. **El POS recupera el documento sin guardar al arrancar** ("Se ha recuperado un documento"): se guarda en
   `Facturacion\bin\Debug\BD\Factura_Backup_Preventa.xml` (Facturación normal: `Factura_Backup*.xml`). Borrarlo con el POS
   cerrado antes de cada escenario para que no contamine.
10. **Cada reinicio**: cerrar el POS con `Stop-Process -Name LD.Facturacion`, borrar el respaldo, abrirlo con `dp pos -Preventa
    -SinCompilar` (o `dp pos -SinCompilar` para Facturación normal) en la terminal real, esperar ~10 s antes del login
    (si se envía muy pronto el clic de Ingresar no hace nada) y volver a correr el script. Máximo 6 pestañas de terminal.
11. **Los parámetros de sucursal destino se leen en cada elección de tipo (en línea); los de la caja, al arrancar el POS.**
    Cambiar `Caja.Caja_Facturacion_Negativa` exige reiniciar; `Parametro_Sucursal` no.
12. **Guardar una preventa** (F6) pide: Validación de Rol (usuario con permiso del tipo en `Seg_TipoPreventa_Rol` por
    `Seg_Usuario_x_Rol`), vendedor distinto del "por defecto" (buscar un vendedor real de la sucursal), pago en efectivo
    (botón "+" y "Imprimir") y pregunta de impresión. Contado se guarda como ticket en `Ticket_Encabezado`; crédito en
    `Factura_Encabezado`. El SQL del contenedor corre en UTC: no filtrar por `GETDATE()` el día local.
13. Facturación normal exige **abrir caja** (monto 0.00, "Abrir Caja" y confirmar la pregunta) antes de facturar.

## Mapa de pantallas (auto_id)
| Pantalla | Controles |
|---|---|
| Login `Frm_Login` | `tbUsuario`, `tbContrasena`, `bConectar`, `bSalir` |
| Tipo de Preventa `Frm_Lista` | `Bn_F1` General, `Bn_F2`.. (un botón por tipo, orden de la lista), `Bn_Cancel` Salir |
| Principal `Frm_Facturacion` | `Text_Articulo`, `Btn_Agregar_Articulo`, `Barra` (ToolStrip), `ListaArt` |
| Búsqueda de Artículos (título "LDCOM - Búsqueda de Artículos") | EDIT de búsqueda, 3 botones sin texto (lupa, check, teclado), 3 `SysListView32` (Artículos, Sustitutos, Sugeridos), `lblExistenciasSucursal` |

## Scripts (carpeta `auto\`)
Lanzador con tope de tiempo: `ejecutar.ps1 -Script <x.py> -Argumentos <pid>,... -Segundos N`.
- Librería: `pos_ui.py`.
- Preventa: `entrar.py` (login + tipo), `escenario_preventa.py` (tipo + agregar artículo + alertas), `abrir_busqueda_y_buscar.py`,
  `guardar_preventa.py` (F6 con rol y vendedor), `pagar_preventa.py` (pago y Imprimir), `lista_seleccionar.py`, `validar_rol.py`.
- Facturación normal: `entrar_facturacion.py`, `confirmar_pregunta.py` (abrir caja), `facturar_contado.py`,
  `doble_click_imprimir.py` (doble clic en `Lbl_Imprimir_Factura`, el ícono de "3 puntos" junto al total).
- Utilidades: `modales.py`, `ventanas_win32.py`, `hijos_win32.py`, `cerrar_dialogo.py`, `vaciar_documento.py`, `estado.py`,
  `buscar_controles.py`, `controles_de_ventana.py`.
Preparación en BD (Docker local): `pruebas-sql\preventa-sucursal-destino\` scripts 03-06 (usuario qa_auto y permisos), 10-12
(snapshots de solo lectura); sus reversiones están al lado.
