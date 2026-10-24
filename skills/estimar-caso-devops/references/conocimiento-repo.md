# Conocimiento acumulado del repo LDCOM13_DOS_PINOS

Hallazgos reutilizables de casos anteriores. Consultar durante la investigacion; agregar lo nuevo al
cerrar un caso.

## Contenido
- Facturacion y caja
- Auditoria y bitacoras
- Catalogos y datos
- Dinamicas comerciales (Descuentos/Bonificaciones/Combos)
- Ambientes y bases
- Archivos adjuntos sin Python

## Facturacion y caja

- `Verificar_Cambio_FormasPago` esta duplicada en 5 archivos: factura normal, apartado, FACTCEDI (x2)
  y entrada/salida de caja. Un bug de calculo de pago casi siempre se repite en varias copias.
- Ese `Select Case item.Text.ToUpper` solo reconoce `TARJETA`, `TRANSFERENCIA`, `EFECTIVO`, `CHEQUE`,
  `MONEDAEXT`; un item con otro texto (ej. "Sinpe") no suma en la reconciliacion y el error culpa al
  ultimo item procesado. Pendiente confirmar de donde sale "Sinpe" (sospecha: `CargarFormaPagoOrdenExpress`,
  flujo Preventa/Orden Express). Relevante para los tickets 2128/2238.
- Vuelto en transferencia: controlado por el permiso `TTipo_Function.Transferencia_Vuelto`
  (`Frm_Factura_Pago.vb` y `Frm_Caja_Entrada_Salida_Pago.vb`). Calculo corregido en el fix del 2051.
- `Frm_Articulo_Cantidad.Articulo_Caja` es una `ReadOnly Property` que muta la linea (llama a
  `Cambiar_Cantidad`). Ante bugs de "algo se duplico o se perdio", revisar properties de solo lectura
  con efectos secundarios sobre objetos pasados por referencia.
- Parametro de sucursal `Solicita_Cant_Art_Fact_Prev = SI` activo en las 20 sucursales (Staging).
- Devoluciones: la opcion "Crear Nota de Reconocimiento" esta oculta desde el Issue 1231
  (`Frm_Devolucion_Detalle.vb`), y `SP_ReporteFormasPagoTransaccion.sql` no tiene rama para
  `Devolucion_FP=1`: cae al `ELSE` que fuerza Nota de Credito.

## Auditoria y bitacoras

- Patron comun a promociones (Descuentos, Bonificaciones, Combos, Premios, Cupones, Patrocinadores) y
  Seguridad: SP `Audit_Registrar` + trigger `TR_<Tabla>_Audit` + `Audit_Config.Columnas_Excluidas`.
  Compara todas las columnas no excluidas: un timestamp propio no excluido genera falsas
  "modificaciones".
- `SP_RepBitacoraArticuloSugerido.sql` ya resuelve "Id - Nombre" con JOIN a `Sucursal`/`Articulo_Info`:
  patron a copiar en otras bitacoras. Un JOIN en `SP_RepBitacoraPromociones.sql` aplica a todas las
  entidades de promociones a la vez.

## Catalogos y datos

- Carga masiva generica: `CX_Tabla` + `CargaMasivaController.cs` (ADMIN_LDCOM). Cobertura parcial.
- Las pantallas de carga masiva exportaban HTML disfrazado de `.xls` (config de `tableExport`),
  corregido en `fix/carga-masiva-xlsx-real-y-casteo-numerico` (WI 2068) y portado a `release/5.3`.
- `CECO`: `Ceco_Id` inestable entre ambientes (`GetNext_Identity()`); llave estable `Codigo_Interfaz`.
- `Cliente_Telefono` quedo cruzado con `Cliente_Celular` por la remediacion `20260812__actualiza_cedula_cliente`.

## Dinamicas comerciales (Descuentos/Bonificaciones/Combos)

- Patron de vigencia por dia de semana + horario, ya construido en **Descuentos** (Articulo/Categoria/
  Departamento/Proveedor comparten `Descuento_Venta`): columnas `Descuento_Hora_Inicio`/
  `Descuento_Hora_Final` (datetime) + `Descuento_Dia1`..`Descuento_Dia7` (bit, Lunes=1..Domingo=7)
  (`NEGOCIO\Database\GENERAL\seeds\schema\02-schema.sql:3923-3925`). UI: 7 `bootstrapSwitch` +
  2 `bootstrap-datetimepicker` en `Views\DescuentoArticulo\Index.cshtml:163-204`. JS:
  `descuentoArticuloController.js` mapea switches/horas (~2603-2606, 2833-2837) y valida
  `Hora_Final > Hora_Inicio` (~3833). Aplicacion en el flujo de venta: `NEGOCIO\CATALOGOS\
  TArticuloXSucursal.vb:1992-1996` (repetido para Articulo/Categoria/Departamento/Proveedor, 8 veces
  en el archivo): `Descuento_Dia" & Now.DayOfWeek`, `Hora_Inicio <= GetTime(Now)`,
  `Hora_Final >= GetTime(Now)`. Molde a copiar para cualquier otra dinamica comercial (Bonificaciones,
  Combos, Premios, Cupones, Patrocinadores) a la que le pidan la misma configuracion (caso 2235).
- **Bonificaciones** (`Bonificacion_Venta`) solo tiene vigencia por rango de fechas
  (`Bonificacion_Fecha_Inicio`/`Fin`, migracion `20260527145340__511_bonificaciones_mantenimiento\
  002_LDCOM_002_Create_BonificacionVenta.sql:13-26`); no tiene dia/hora. Se aplica en
  `NEGOCIO\FACTURACION\TFacturaLinea.vb` en 2 consultas (~4891-4892 y ~4950-4951) — ahi es donde
  entraria el filtro si se agrega dia/hora.
- El User Story 511 "Mantenimiento de bonificaciones" (Closed 2026-09-14) pedia dia/horario en su
  Description original, pero los Acceptance Criteria finales no lo incluyeron: quedo fuera del
  alcance entregado sin que quedara documentado en ADO por que. Un caso que reabra ese tema no es
  necesariamente "alcance nuevo" puro: puede ser una brecha contra el spec original (ver
  `validacion.md`, fila "la spec lo exige y el codigo no lo cumple").
- **Filtros multi-seleccion numericos en reportes (TValue vs. TConjuntoString):** `NEGOCIO\ACCESO
  DATOS\Expression\Data\Data.vb` tiene dos clases para armar parametros de SP. `TValue.ValueMSSQL()`
  (~215-227, y copias identicas en `Get_Param_Value` ~103-111 y `ValueORACLE` ~175-187) hace
  `If IsNumeric(_Value) Then _Value = _Value.ToString.Replace(",", "")`: pensada para un solo valor
  numerico (quitarle separador de miles), pero bajo `culture="es-MX"` (fijada en el `Web.config` de
  ADMIN_LDCOM) `IsNumeric()` tambien da `True` para una lista CSV como `"12,45,78"` (la coma es
  separador de miles en esa cultura), y el Replace le borra todas las comas: una lista de IDs
  seleccionados en un filtro multi-checkbox se convierte en un solo numero corrupto. `TConjuntoString`
  (~310-322) no tiene ese problema: no llama `IsNumeric`, solo envuelve el valor en comillas. Reportes
  como `TRepFact_VentasXCombo.vb` ya usan `TConjuntoString` para sus filtros multi-seleccion
  (Sucursales/Clientes/Combos) y no sufren el bug; `TRepFact_BonificacionVentaAplicada.vb` fue el que
  se codifico con `TValue` para esos mismos filtros (caso 2261). Antes de asumir que hay que tocar
  `TValue` (clase compartida por todo el motor de reportes), revisar si el reporte/formulario hermano
  ya usa `TConjuntoString` para el mismo tipo de filtro: copiar ese patron es un fix de una sola
  linea por parametro, sin tocar codigo compartido.
- Existe un documento de seguridad separado (`documentos/04 - Fase 3 - Codigo/05 - Profundizacion/
  sql-injection-sistemico-tconjunto-sin-sanitizar.md`) sobre una clase **distinta** en el mismo
  archivo, `TConjunto` (~263-309, sin la "String" al final), que no escapa comillas simples y se usa
  en >300 lugares: no confundir con `TConjuntoString` (~310-322), que si es segura para este tipo de
  parametro (lista de IDs numericos). No es parte del alcance de un ticket de bug salvo que el
  usuario pida investigarlo aparte.

## Carga masiva generica (TCargaXTabla.vb / CargaMasivaController.cs)

- El motor compartido (~99 tablas, `CargaMasivaController.cs:325 SubirArchivo` + `NEGOCIO\CATALOGOS\
  TCargaXTabla.vb`) marca cada fila de la tabla temporal con una columna `MsgError` (vacia si esta
  bien). El INSERT final generico (~linea 4016) filtra `WHERE MsgError = ''`: para la mayoria de las
  tablas, YA se inserta lo valido y se descarta lo invalido fila por fila, sin tumbar el archivo
  completo. No es necesario construir esto — ya existe.
- **Pero no todas las validaciones especificas por tabla respetan ese patron.** Al menos
  `Validar_EncabezadoCombo` (Tabla_id=92, linea 3219-3320) y su gemela copy-paste
  `Validar_EncabezadoBonificacion` (Tabla_id=93, linea ~3770) acumulan errores de validaciones que SI
  son por fila (fecha invalida, nombre duplicado) en un string y hacen `Throw New Exception(_Mensaje)`
  al final si algo fallo — eso tumba el archivo COMPLETO, incluyendo filas validas del mismo archivo.
  Antes de asumir que una tabla especifica sigue el patron "marca y sigue" del motor, confirmar si su
  validador especifico usa `Throw` en vez de `SetValue("MsgError",...)`.
- **Cifras de control** (total archivo / insertado / con error al finalizar una carga masiva): NO
  EXISTE en ninguna de las ~99 tablas. Identificado desde el diseño original como "Gap ID 9 de la
  oferta" (test case ADO #1160, nunca ejecutado/entregado). No es un defecto de ninguna tabla en
  particular — es una funcionalidad de plataforma nunca construida. Ya conteo, sobre los 75
  `Throw New Exception(...)` de `TCargaXTabla.vb`: ~58-63 son guardas tecnicas (SQL/timeout, no
  tocar), ~13-16 en ~11 funciones son candidatas reales a convertir a "marcar y seguir" (ya tienen la
  query que identifica las filas malas, solo falta envolverla en `TUpdate` en vez de `TQuery`+throw), y
  ~19 funciones quedaron sin confirmar. Desglose completo y estimado (17-25h) en
  `handoff-carga-masiva-cifras-control.md` (fuera de ADO, en la sesion de Farid).

## Combo (mantenimiento y carga masiva)

- Tabla `Combo` (migracion `20260430213501__560_MantenimientoCombo`): tiene `Combo_Fecha_Inicio`/
  `Combo_Fecha_Final` (vigencia por rango de fechas) pero **NO tiene columnas de dia de la semana**
  (a diferencia de `Descuento_Venta`, que si las tiene). Mantenimiento manual en
  `NEGOCIO\CATALOGOS\TCombo.vb` (CRUD e validaciones de fecha, lineas ~44-48, 74-79, 512-526, 619-670),
  `Models\ComboModel.cs` y `Views\Combos\Index.cshtml` (un solo panel con tabs, no hay vista separada
  de "carga masiva").
- **Dos cargas masivas separadas** para Combo, ambas via el motor generico CX_Tabla: Tabla_id=92
  "encabezado" (boton `btnCargaMasivaEncabezado`, `Views\Combos\Index.cshtml:32`; ya captura y valida
  `Combo_Fecha_Inicio`/`Final` desde junio 2026, migracion 836) y Tabla_id=90 "detalle de articulos"
  (boton `btnCargaMasivaArticulo`, `:156`; sin fecha, porque esa vive en el encabezado). Si un ticket
  dice "la carga masiva no captura fechas", verificar cual de las dos uso el reportante antes de
  asumir que es un bug — es un error comun confundir ambos botones.
- **Vigencia aplicada en el flujo de venta:** duplicada en 2 stored procedures —
  `NEGOCIO\Database\GENERAL\routines\procedures\SP_Combo_Consulta_Articulo.sql:112-118` (servidor) y
  `NEGOCIO\Database\INTEGRATIONS\routines\procedures\SP_Combo_Consulta_Articulo_Local.sql:94-99` (POS
  local/offline). Cualquier cambio a como se determina si un Combo esta vigente (ej. agregar filtro de
  dia de semana) hay que replicarlo en los dos.

## Ambientes y bases

- Desarrollo: `172.177.16.230`. Testing: `TESTINGSQL\SQL2022`, con `LDCOM_DOS_PINOS_STAGING(_RC)`.
- Staging y Staging RC son replicas de UAT. "UAT" a veces apunta a `LDCOM_DOS_PINOS_DEMO`.
- Testing tiene datos sucios de pruebas; Staging esta limpio. Triangular antes de concluir.

## Archivos adjuntos sin Python

No hay `python` real ni `az` en esta maquina.
- `.xlsx`: tratarlo como zip y leer el XML, o Excel COM desde PowerShell
  (`New-Object -ComObject Excel.Application`, `.Value2`, `.NumberFormat`, `.Sheets | % Name`).
- `.docx`: descomprimir, texto en `word/document.xml`, capturas en `word/media/`.
