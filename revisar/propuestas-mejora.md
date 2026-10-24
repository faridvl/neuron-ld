# Propuestas de mejora al estándar LDCOM

Patrones que hoy **existen y se aceptan** en LDCOM, pero que causan bugs o dificultan el
mantenimiento. El revisor los reporta como `[PROPUESTA]`: nunca bloquean y solo aparecen cuando el
diff convive con el patrón (se agrega código nuevo que lo repite, o se toca el método que lo tiene).

Cuando se decide adoptar una propuesta, pasa a `reglas-vigentes.md` con su número de regla y deja
de estar aquí.

Estados: `ABIERTA` (el revisor la sugiere) · `ADOPTADA` (movida a reglas vigentes) · `DESCARTADA`
(con el motivo).

---

## P01 ABIERTA — Métodos hermanos copiados en vez de compartidos

**Hoy:** `Cambiar_Cliente` / `Cambiar_Cliente_Preventa`, `Imprimir_Documento` /
`Imprimir_Documento_Preventa` / `Imprimir_Tiket_Factura_Local`, y `Frm_Facturacion.vb` /
`Frm_Facturacion_Autonoma.vb` (203 métodos con el mismo nombre) repiten lógica.

**Por qué mejorarlo:** es la causa de fondo de R05 ("arreglado en un solo camino"), el motivo de
devolución más frecuente.

**Propuesta:** cuando un fix toca la misma lógica en dos hermanos, extraer esa parte a un método
compartido (en `FacturacionOBJ` si no depende del formulario) en vez de copiar el cambio. Solo la parte
que se toca; no refactorizar el formulario entero (regla 04 del equipo: no introducir patrones nuevos en
módulos legacy sin necesidad).

## P02 ABIERTA — `Catch` que devuelve `Nothing` sin registrar

**Hoy:** el camino de preventa en `FacturacionOBJ/TCatalogo.vb` hace `Catch ex As Exception: Return
Nothing` sin `Save_Msg(ex)`.

**Por qué mejorarlo:** el error real se pierde y aparece después como "Referencia a objeto no
establecida" en otra pantalla.

**Propuesta:** en código nuevo, siempre `Save_Msg(ex)` antes de devolver `Nothing`, igual que el camino
PV del mismo archivo.

## P03 ABIERTA — Enums declarados dentro de formularios

**Hoy:** `TTipo_Bonificacion`, `Estado_Preventa`, `FormaPagoDescuento`, `TTipo_Tarjeta` viven al inicio de
`Frm_Facturacion.vb`; `TTipo_Tarjeta` existe también en `TManagerTable.vb`.

**Por qué mejorarlo:** otro formulario o la capa de negocio no los puede usar sin depender del
formulario, y aparecen duplicados con el mismo nombre.

**Propuesta:** un enum nuevo de dominio va en `NEGOCIO/OBJETOS COMUNES/TManagerTable.vb` (o en
`FacturacionOBJ/TFacturacion.vb` si es solo del POS), nunca en un formulario.

## P04 ABIERTA — Contrato de error del WCF por nombre de tabla

**Hoy:** el servidor devuelve errores como un DataSet con tabla `"Errores"` y el cliente pregunta
`Tables(0).TableName = "Errores"` en cada llamada (o no pregunta).

**Por qué mejorarlo:** un llamador que olvida la pregunta trata el mensaje de error como datos.

**Propuesta:** en código nuevo del POS, usar una sola función auxiliar para "¿este DataSet es un
error?" en vez de repetir la comparación. Verificar antes si ya existe una en `AccesoDatosEnLinea`.

## P05 ABIERTA — Montos en `Double`

**Hoy:** `Verificar_Cambio_Bonificaciones(ByVal pCantidad As Double, ...)` y `Modificar_Cantidad(...,
ByVal pCantidad As Double)`, mientras `Agregar_Articulo` usa `Decimal`.

**Por qué mejorarlo:** mezclar `Double` y `Decimal` en cantidades y montos produce diferencias de
redondeo (relacionado con 1603).

**Propuesta:** en firmas nuevas, `Decimal` para cantidades y montos.
