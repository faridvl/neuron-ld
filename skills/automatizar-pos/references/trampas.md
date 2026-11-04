# Trampas del POS automatizado

Cada una nos costó tiempo. Las de modales y clics ya están resueltas en `poslib`; se listan para entender por qué el
código es como es.

## Hilos, UIA y modales
1. **UIA se cuelga con modales abiertas** (`children()`/`descendants()`), sobre todo en Búsqueda de Artículos. Con modales
   usar Win32: `base.ventanas`, `base.modales`, `base.botones`, `sesion.hay_login`. Lanzar los scripts con un tope de tiempo.
2. **`Invoke` sobre un botón que abre una modal no regresa** hasta que se cierre la modal: `base.en_hilo` o `BM_CLICK`.
3. **Frm_Mensaje se cierra solo en pocos segundos** y comparte título con la principal. La principal es la ventana visible
   más grande. Para leer el mensaje: `scripts\vigilar_modales.py` (sondeo de 0.25 s con captura).
4. **Las preguntas tienen dos botones sin texto**: check a la izquierda y ESC a la derecha
   (`modales.responder_pregunta`). Cancelar o dejar pasar el tiempo equivale a ESC.
5. **Teclado numérico**: los botones de denominaciones aceptan `BM_CLICK`, pero el teclado numérico necesita clic físico
   (`fisico.clic_relativo`) con el POS al frente. Escribir los números y el ENTER en pasos separados.
6. **Doble clic**: el doble clic por mensajes NO reproduce el bug del clic físico (por ejemplo el ícono de imprimir
   `Lbl_Imprimir_Factura`). Para reproducirlo hace falta un clic físico real, que mueve el mouse del usuario ~1 s.
7. **Captura**: `PrintWindow` funciona con la ventana tapada. Nunca `click_input`, `type_keys` ni `SendKeys`.

## Pantallas
8. **Enter dentro del cuadro de búsqueda selecciona** el primer resultado (abre Modificar Cantidad): para buscar pulsar la lupa.
9. **La barra de funciones** (F1..F12) es un `ToolStrip` paginado: sus botones salen en UIA con el texto ("Buscar\r\nArtículo")
   y sin `auto_id`; si el botón no aparece, la barra está en otra página.
10. **Validación de Rol** al guardar una preventa (F6): hace falta un usuario con permiso del tipo en `Seg_TipoPreventa_Rol`
    por `Seg_Usuario_x_Rol`, un vendedor real de la sucursal (no el "por defecto"), pago en efectivo ("+" e "Imprimir") y la
    pregunta de impresión. Contado se guarda en `Ticket_Encabezado`; crédito en `Factura_Encabezado`.
11. **Facturación normal exige abrir caja** (monto 0.00, "Abrir Caja" y confirmar la pregunta) antes de facturar.

## Arranque y estado
12. **Respaldo de documento**: al arrancar, el POS recupera el documento sin guardar ("Se ha recuperado un documento") desde
    `BD\Factura_Backup*.xml` (preventa: `Factura_Backup_Preventa.xml`) junto al ejecutable. Borrarlo con el POS cerrado
    antes de cada escenario.
13. **Cada reinicio**: cerrar el POS (`Stop-Process -Name LD.Facturacion`), borrar el respaldo, abrir con
    `rig pos -SinCompilar` en la terminal real y esperar ~10 s antes del login: si se pulsa Ingresar muy pronto el clic no
    hace nada (`sesion.iniciar_sesion` reintenta).
14. **Parámetros**: los de sucursal destino se leen en línea en cada elección de tipo; los de la caja, al arrancar el POS
    (cambiar `Caja.Caja_Facturacion_Negativa` exige reiniciar).

## Datos y tiempo
15. **El SQL del contenedor corre en UTC**: no filtrar por `GETDATE()` el día local.
16. **Token a medianoche**: una prueba que cruza la medianoche puede perder el token o el día de negocio; lanzar los
    escenarios largos antes de las 23:30 o volver a iniciar sesión.
17. **Argumentos con espacios en PowerShell**: pasarlos entre comillas dobles dentro de comillas simples
    (`'"MANGUERA LECHE"'`); si no, Python recibe dos argumentos.
18. pywinauto avisa que el POS es de 32 bits y Python de 64: es solo una advertencia.
