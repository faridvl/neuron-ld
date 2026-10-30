---
name: pos-uia-preventa-trampas
description: Trampas nuevas al automatizar el POS de preventas (monitor, Modificar Preventa, Modificar Cantidad, UIA intermitente)
metadata:
  type: reference
---

- UIA `descendants()` a veces devuelve lista vacia/sin el boton: reintentar (pulsar_barra.py reintenta 5 veces). El texto de botones de la barra lleva \r\n; buscar por prefijo sin acentos.
- Clic por mensaje en items del monitor (pnlP_N) NO carga la preventa: WinForms valida WindowFromPoint. Cargar preventa en modo Preventa = Menu(F11) > "Modificar Preventa" > lista (lupa, fila, check). Esa lista solo muestra Estado 0/1 (Estado 4 no sale); el monitor lateral si lista las de Estado 4 y en modo Facturacion pone reloj de arena.
- Modificar Cantidad: el edit no acepta WM_SETTEXT; pulsar el boton "+" (el sin texto mas a la derecha) por BM_CLICK. En preventa con tipo editable pide Validacion de Rol (validar_rol.py).
- Detalle_Total/Impuesto en PV_Preventa_Detalle son POR UNIDAD; Preventa_Total = suma(cant*unitario).
- Contado facturado va a Ticket_Encabezado/Ticket_Detalle (no Factura_Encabezado). Facturar: Menu cicla barras (3 pulsaciones llega a "Cargar Preventa"), "Imprimir Documento" abre Pago de factura precargado; boton Imprimir por BM_CLICK.
- sqlcmd en contenedor: MSYS_NO_PATHCONV=1 exportado en el shell; `-W` y `-y` son excluyentes.
