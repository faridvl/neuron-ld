# Trampas de SITE_INVENTARIO_WEB

## Login y sesión
- El front rechaza "_" en el usuario (loginActions.jsx): en el Docker se usa `qaauto`, no `qa_auto`.
- El 404 de `Imagenes/Usuarios/<id>N.jpeg` es ruido (foto de usuario inexistente); no es un fallo.
- Tras entrar hay que elegir sucursal en `#cb_Sucursal` y pulsar "Utilizar parámetros" antes de ver Movimientos.

## Pantalla de traslado nuevo
- `#articulo` y los selectores de la cabecera están deshabilitados hasta que `#form-sucursal-origen` trae valor:
  esperar ese valor, no un tiempo fijo.
- El destino es un react-select cuyo id (`#react-select-N-input`) cambia entre cargas. Selector estable: el primer
  input `react-select*` que sigue a la etiqueta "SUCURSAL DESTINO" (la etiqueta está en minúscula y el CSS la pone en
  mayúscula, por eso el xpath usa `translate`). Esperar también a que no esté `disabled`.
- Agregar un artículo = escribir el código en `#articulo` y Enter. La respuesta de `TrasladoInventario_AgregarArticulo`
  trae `{Error, Mensaje, Linea}`.
- La fila nueva queda ARRIBA de la tabla, no al final. Antes de llenarla, esperar a que la primera fila muestre el código.
- `fill()` no actualiza el estado de la cantidad: hay que hacer clic, Ctrl+A, teclear y Tab. Al salir del campo la
  pantalla reformatea ("2" pasa a "2.00"): comparar como número.
- Agregar el mismo artículo dos veces no manda ningún request: una espera de `AgregarArticulo` se cuelga.
- Guardar (`TrasladoInventario_GuardarMovimiento`) responde `"ID:<n>"`; la pantalla pone ese número en `#form-numero`
  y muestra el aviso "El Traslado de Inventario ha sido almacenado".

## Aviso POS-26 (melaza)
- La melaza es el material 19000257 y es lo único que dispara el aviso (MOLASSES_TRANSFER, IntegrationEvent 4009).
- El aviso sale solo al guardar un traslado nuevo (estado GU), no al editar uno existente.
- Vínculo: `JSON_VALUE(OutboundNotification.DocumentJson,'$.MovimientoId')`; los Events usan el mismo TransactionId.
- Si falta `IntegrationStage` en el despliegue, el notificador nulo no avisa y no deja error: un traslado con melaza sin
  aviso no siempre es un bug del código.
- El sitio se publica con `rig` (ver skill `rig`); no republicar sin necesidad.

## Scripts de exploración viejos
- `libS.js` apuntaba a un sitio SIM ya borrado; no reutilizarlo. Todo está en `scripts\lib.js`.
- Evitar `waitForTimeout` fijos: esperar elementos o respuestas.
