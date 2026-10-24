# Reglas vigentes del revisor LDCOM

Estas son las reglas que el revisor **exige**. Cada una existe porque algo parecido ya llegó a QA o al
cliente: el ticket de origen va en **Evidencia**. Si una regla no tiene evidencia, no va acá: va en
`propuestas-mejora.md`.

Antes de aplicar estas reglas, el revisor lee también las del equipo en el repo (no se duplican aquí):

- `.claude/rules/04-vbnet-standards.md` — DBNull y existencia de columna en `DataRow`.
- `.claude/rules/05-sql-standards.md` — DEFAULT por tipo, IDs de catálogo inestables, menús, versionado de SPs.
- `.claude/rules/07-pr-review-checklist.md` — checklist de PR.
- `.claude/rules/03-operating-mode.md` — comentarios sin narrativa de sesión (fechas, conteos, "se encontró que").

## Severidades

```
[ROMPE]     algo que ya funcionaba deja de funcionar
[ERROR]     hay que corregirlo antes del PR
[RIESGO]    puede fallar en algún escenario; el dev confirma que lo probó
[PROPUESTA] patrón viejo de LDCOM que se podría mejorar; nunca bloquea
```

## Alcance

- Estilo y estándar (R01–R04, R10): **solo líneas agregadas o modificadas** del diff.
- Riesgo de romper (R05–R09, R11–R13): el diff **y lo que depende de él** (llamadores, métodos
  hermanos, capa local, SPs, dbml). Aquí sí se lee código fuera del diff.
- El código viejo que el dev no tocó no se reporta, salvo como `[PROPUESTA]` cuando el cambio convive
  con el mismo problema.

## Reglas para reportar un hallazgo

1. Cada hallazgo lleva `archivo:línea`, el fragmento de código y un **escenario concreto de falla**.
   Si no se puede escribir el escenario, no se reporta.
2. Antes de reportar, intentar refutarlo (leer el llamador, el SP, el otro camino). Si no se puede
   confirmar, se marca "posible" y se dice qué faltó verificar.
3. No inventar objetos, tablas ni reglas de negocio. Si algo depende de la BD y no se consultó, decirlo.

---

## R01 [ERROR] Números mágicos

Un literal numérico o de texto que representa un valor de dominio (tipo de documento, tipo de cliente,
estado, tipo de bonificación, código de flete, etc.) es un defecto, no una preferencia.

**Qué hacer según el caso:**

| Caso | Acción |
|---|---|
| Ya existe un enum con ese valor | ERROR: usar el enum. Citar dónde está (`archivo:línea`). |
| No existe y el catálogo es **fijo** (mismos valores en todos los ambientes) | ERROR: proponer el enum con valores explícitos, junto a los enums parecidos. |
| No existe y el catálogo tiene **IDs asignados a mano** (regla 05 del equipo) | ERROR: no proponer enum. Proponer buscar por nombre o código estable. |
| No se pudo verificar qué significa el valor | ERROR con "significado sin verificar"; no inventar el nombre. |

- El significado del valor se verifica contra la tabla catálogo (BD Desarrollo, solo lectura) o contra
  otros usos en el código. Nunca se adivina.
- El enum propuesto lleva valores explícitos (`Asociado = 3`), porque el número viene de la BD.
- **No son mágicos:** `0` y `1` como cantidad, contador, índice o comparación con vacío (`Count = 0`,
  `Monto = 0`), colores y tamaños de UI (`Color.FromArgb(220, 230, 242)`), formatos (`"dd/MM/yyyy"`).

**Los códigos de texto también son mágicos**, en cualquier lenguaje y aunque vayan dentro de un SQL
armado como cadena: `Articulo_Tipo_Flete <> 'NI'` en un `TConjunto`, `TValue("SI")`, `=== 'A'` en JS,
`WHERE Estado = 'P'` en un SP. Igual que un número: enum, constante o función con nombre
(`Es_Flete_Granel(tipo)`), nunca el literal repetido.

- Antes de proponer la corrección, `git grep` del literal con su columna en todo el repo y **leer los
  comentarios cercanos a los otros usos**. Ahí suele estar documentada la trampa. Ejemplo real:
  `Frm_Facturacion.vb` (`Es_Flete_Granel`) avisa que "no es flete" tiene dos valores en datos reales
  (`'NI'` y `'N'`) y que filtrar por descarte bloquea artículos normales; el PR 763 agregó otro
  `<> 'NI'` en `TCargaXTabla.vb` sin verlo.
- Comparar **por descarte** (`<> 'NI'`, `NOT IN (...)`) contra un catálogo de códigos es `[RIESGO]`
  además del `[ERROR]`: si aparece un valor nuevo o sucio, entra por el lado equivocado.
- Si el literal **ya existía** en la línea que el diff reemplaza (el dev solo tocó la línea), es
  `[PROPUESTA]`, no `[ERROR]`: la deuda es previa.
- La etapa de chequeos automáticos entrega los candidatos (`numero-magico`, `texto-magico`,
  `decimales-quemados`); el agente del módulo confirma o descarta cada uno. Uno descartado no se
  reporta; los confirmados van **agrupados en un solo hallazgo por archivo**.

**Dónde viven los enums hoy:** `NEGOCIO/OBJETOS COMUNES/TManagerTable.vb` (`TTipoDoc`, `TTipo_FormasPago`,
`TFacturaClase`, ...), `INTERFACE/FACTURACION/FacturacionOBJ/TFacturacion.vb`, y al inicio de
`Frm_Facturacion.vb` (`TTipo_Bonificacion`, `Estado_Preventa`, ...).

**Evidencia:** `Frm_Facturacion.vb` asigna `.Tipo_Doc = 1` en `Refrescar_Monitor_Preventa_Pasillo` y
compara `dr("Orden_TipoDoc") = 1` en `Refrescar_Monitor_Express`, existiendo `TTipoDoc.Factura_Contado = 1`.

```vb
' MAL
.Tipo_Doc = 1

' BIEN
.Tipo_Doc = TTipoDoc.Factura_Contado
```

## R02 [ERROR] Parámetros booleanos posicionales

Una llamada nueva o modificada con dos o más `True`/`False` seguidos no se entiende sin abrir la firma.

**Qué hacer:** argumentos con nombre (`pEs_Scaneo:=True`) o, si el booleano representa un modo, un enum.

**Evidencia:** el fix de 1529 agregó un tercer booleano:
`Evento_Enter_Articulo(_ClsArticuloSelec.Id, True, True)`. Ese mismo método y sus vecinos
(`Verificar_Cambio_Bonificaciones(Linea, pCantidad, True)`) están en la cadena de regresión
1476 → 1529 → 1602 (ver `casos-historicos.md`).

```vb
' MAL
Evento_Enter_Articulo(_ClsArticuloSelec.Id, True, True)

' BIEN
Evento_Enter_Articulo(_ClsArticuloSelec.Id, pEsArtFavorito:=True, pEs_Scaneo:=True)
```

## R03 [ERROR] Nombres abreviados o sin significado

Variables, parámetros y métodos nuevos llevan nombres completos y descriptivos: nunca `r`, `dr2`,
`tmp`, `aux`, `x`, `obj`, `ds1`, `i` fuera de un `For` trivial.

- Se respeta el prefijo que ya usa LDCOM (`p` para parámetros, `_` para campos privados), pero el resto
  del nombre debe decir qué es: `pCantidadBonificada`, no `pCant2`.
- Aplica también a pruebas y ejemplos.

## R04 [ERROR] Mensajes al usuario

- No mostrar `ex.Message` ni errores de SQL crudos al usuario (1593: "Guardar sin fechas muestra un
  error crudo de SQL").
- Mensajes en español, con mayúscula inicial y el resto según el estándar del texto vecino (402:
  alertas en inglés; 1689: "Y" mayúscula a mitad de mensaje).
- Un mensaje por acción (1490, 1596: "muestra 2 mensajes de advertencia").
- Archivos con tildes o ñ: el diff no debe cambiar la codificación del archivo. Si un `.vb` pasa de
  UTF-8 a otra codificación, o aparecen `Ã`/`�` en el diff, es ERROR (1527, 1601, 1932).

---

## R05 [RIESGO → ROMPE] Arreglado en un solo camino

El patrón que **más devoluciones** genera. Un cambio en un flujo tiene casi siempre un flujo hermano
que hace lo mismo por otro lado.

**Qué hacer:** si el diff modifica un método de una familia (ver `mapa-riesgo-facturacion.md`,
"Familias"), revisar cada hermano. Si el hermano tiene la misma lógica y no se tocó, se reporta:
`[ROMPE]` si el hermano queda con el bug que se corrigió, `[RIESGO]` si no se puede confirmar.

**Antes de marcar `[ROMPE]` un hermano sin corregir**, confirmar las dos cosas; si falta una, es
`[RIESGO]` como máximo:

1. **Tiene un llamador real en el repo** (no solo la interfaz WCF o el `Reference.vb`). Un método
   publicado que nadie de este repo llama puede ser código muerto o de un consumidor externo: se
   reporta como pregunta, no como rotura.
2. **El valor llega a algo que importa**: se cobra, se guarda en la factura o se le muestra al cliente.
   Si el hermano solo valida existencia (`Verificar_EsArticulo`) o muestra un dato informativo, no rompe.

Lección del PR 763: se marcaron como `[ROMPE]` `BuscarArticulo` (sus llamadores de facturación solo
validan que el artículo exista) y `ListScaneoNombre` (nadie lo llama en el repo). Los dos eran `[RIESGO]`.

**Evidencia:** 1495 se devolvió varias veces. Comentario de QA: *"validar varios escenarios... modalidad
local y en línea, subdocumento factura electrónica de contado y de crédito, reimpresiones"*. También
231 ("si se realiza otro escenario..."), 1532 (contingencia).

## R06 [RIESGO → ROMPE] Local vs en línea

El POS funciona en tres modos (`TCatalogo`): Preventa → WCF; PV en línea con respaldo local; y
`Forma_Local` → solo BD local. Una regla nueva que solo existe en línea deja al POS sin ella cuando
se cae la conexión.

**Qué hacer:** si el diff toca la capa en línea, revisar si necesita su par local:

| Se tocó | Revisar también |
|---|---|
| `AccesoDatosEnLinea/TCatalogoOnLine.vb`, `NEGOCIO/ServiciosWCF/*` | `FacturacionLOCAL/TCatalogoLocal.vb`, `TFacturacionLocal.vb` |
| Tabla o columna nueva que el POS lee | `FacturacionLOCAL/BDLocal.dbml` + script de `LDControlDBLocalAutomatico` + `TDatosServerToLocal.vb` |
| Parámetro nuevo de caja/sucursal | que se sincronice a la BD local |
| Método nuevo en `FacturacionOBJ/TCatalogo.vb` | que tenga el camino `Forma_Local`, o que el llamador tolere que no exista |

**Evidencia:** 776 (*"el parámetro de Caja Solicita Depósito al Retirar sigue sin sincronizar en la DB
local"*), 1526, 1532, 1981, 2166, 863, 698, 687.

## R07 [ROMPE] Estado de la factura en eventos

Cambiar cliente, cambiar tipo de documento y modificar cantidad **reconstruyen** la lista de líneas.
Es donde más se rompe `Frm_Facturacion`.

**Qué hacer:** si el diff toca esos manejadores, verificar las invariantes de
`mapa-riesgo-facturacion.md` (cantidades se conservan, bonificaciones y combos no se mezclan, totales
se refrescan) y escribir el escenario de prueba mínimo en el reporte.

**Evidencia:** 1529 (cantidades se duplican al cambiar de cliente), 1602 (total no se actualiza al
modificar cantidad), 1898 (se pierde el combo), 1975 (se eliminan bonificaciones), 1797, 2244.

## R08 [RIESGO] Regresión sobre un fix reciente

**Qué hacer:** `git blame` de las líneas modificadas o borradas. Si las introdujo un commit `fix(...)`
de los últimos 60 días, avisar: *"esta línea la puso el fix 1529 (34c058d8) hace 8 días; confirmar que
el escenario de 1529 sigue funcionando"*. Incluir el título del fix.

**Evidencia:** cadena 1476 → 1529 → 1602: cada fix rompió el siguiente, en el mismo método.

## R09 [ROMPE] Condición booleana invertida o cambiada

Un cambio de `If X Then` a `If Not X Then`, o de `And` a `Or`, `<` a `<=`, en una validación.

**Qué hacer:** leer qué devuelve la función (¿`True` = "hubo cambio" o "está bien"?) y los otros
llamadores. Reportar con la tabla de verdad del caso.

**Evidencia:** el fix de 1529 dejó `If Verificar_Cambio_Bonificaciones(Linea, pCantidad, True) Then`;
el fix de 1602 lo corrigió a `If Not ...`.

## R10 [ERROR] Excepciones tragadas

Un `Catch` nuevo que no registra (`Save_Msg(ex)`) ni avisa, o que devuelve `Nothing` sin que el
llamador lo verifique, termina en "Referencia a objeto no establecida" lejos del origen.

**Evidencia:** 1619, 1643, 583, 166, 782 (errores no controlados / object reference).

## R11 [RIESGO] Dinero, impuestos y redondeo

- Montos en `Double` en código nuevo → `Decimal`.
- `Math.Round` sin regla explícita, o redondeo aplicado en un camino y no en su inverso
  (1603: la devolución registra 50.22 cuando la factura se cobró en 50).
- Comparar montos con IVA contra montos sin IVA (2260: premiación valida con IVA).
- Impuestos: el grupo de impuesto del cliente vs el del artículo (1523, 1524, 686).

## R12 [RIESGO] Fechas y rangos

- `Now` vs `Today`/`.Date` al comparar vigencias (1779: combo que inicia y termina hoy, guardado con
  la misma hora).
- `<` vs `<=` en fecha final (1615, 1657, 1658: no permite la fecha actual).
- Fecha final anterior a la inicial sin validar en backend (1594, 1644, 1725).

## R13 [ERROR] Configuración y ambiente

- `Web.config`/`App.config`/`.LD` en el diff: confirmar que es intencional y que no va con valores de
  docker/testing (`rig ambiente -Restaurar`). Evidencia: 588 (era el `web.config` de testing), 1710, 1713.
- Tabla, columna, parámetro o menú nuevo sin su migración en `NEGOCIO/Database/*/migrations`
  (1968: preventa no se crea en ambientes sin la migración).
- SP modificado: seguir el versionado de la regla 05 y la herramienta `migrate` (skill `migraciones-ldcom`).

## R15 [ROMPE] Código desactivado

Una línea ejecutable que el diff **comenta o borra** (no reemplaza) cambia el comportamiento aunque
parezca inofensiva. Es fácil pasarla por alto porque el diff se ve chico y a veces trae un comentario que
la justifica.

**Qué hacer:** por cada línea ejecutable comentada o borrada sin reemplazo, escribir qué hacía y qué pasa
ahora sin ella. Prioridad máxima si es un `Clear`, un reset de estado, un `Exit`/`Return`, una
validación, o una llamada que recalcula (`Cambiar_Cliente`, `Refrescar_*`), y sobre todo si está antes de
un bucle que vuelve a agregar elementos: sin el `Clear`, el bucle duplica.

Un comentario que justifica la desactivación ("se comenta porque...") **no** la vuelve segura: hay que
verificar qué otro flujo dependía de esa línea.

**Evidencia:** el fix de 1476 comentó `ListaArt.Items.Clear()` en `Refrescar_Datos_Lista` con un
comentario explicando por qué; al cambiar de cliente, las líneas se volvían a agregar sobre las
existentes y las cantidades se duplicaban (1529).

## R14 [RIESGO] Cargas masivas

`NEGOCIO/CATALOGOS/TCargaXTabla.vb` es el tercer archivo con más fixes (49). Cada carga masiva nueva o
modificada debe validar en el servidor: archivo vacío (840), columnas de más o de menos (1582, 1645),
tipos de artículo permitidos (1583, 1605–1607), duplicados, negativos y ceros (2304), fechas (R12), y
dar mensajes entendibles que digan fila y columna (456, 1534, 2237).

---

Las reglas R16 a R20 las aplica **la etapa de chequeos automáticos** (`chequeos.ps1` de rig), sin IA.
El agente no las vuelve a reportar; solo las usa como contexto. Se documentan aquí para saber qué
significa cada código del reporte.

## R16 [ERROR] Commits sin formato o sin ticket

Asunto `tipo(MODULO): <ticket> - <descripción>` (`fix(POS): 2297 - ...`). Regla 02 del equipo. Commits
como "ajustes por comentarios" o "Agregar scripts" no dicen qué ticket tocan.

## R17 [RIESGO] Lógica nueva sin pruebas

Un `Public`/`Friend` `Function`/`Sub` nuevo en `NEGOCIO` (fuera de formularios y WCF) sin ningún
archivo de pruebas en el diff. Regla 10 del equipo: la lógica nueva lleva sus pruebas en el mismo PR.

## R18 [ERROR] Migraciones y SQL

Chequeo automático de la regla 05 del equipo: migración ya existente editada o borrada; carpeta fuera de
formato `AAAAMMDDhhmmss__<ticket>_<desc>`; `ALTER PROCEDURE/FUNCTION/TRIGGER/VIEW` (no idempotente,
usar `CREATE OR ALTER`); `DEFAULT ('getdate()')` (`[ROMPE]`) o número entre comillas; columna nueva
`NULL`; `SELECT *`; menús con `Menu_Id` literal, `MAX(Menu_Id)` o `Menu_Padre = 0` sin
`MENU-RAIZ-APROBADO`; objeto programable en la migración sin su archivo en `routines/`, o al revés.

## R19 [ERROR] Fuente de datos de un `.rdl`

`rd:SecurityType` = `None`, `ConnectString` = `=Parameters!ConexionString.Value`, sin
`DataSourceReference`. Si no, SSRS ignora la conexión que manda el Admin y consulta otra base.

## R20 [ERROR] Restos de depuración y formato

`console.log`, `debugger`, `alert(` en JS; `Debug.Print`, `Console.WriteLine`, `Stop` en VB; guion
largo (`—`, `–`) en cualquier archivo; archivo que cambió de codificación o con tildes corruptas (R04);
comentario XML con `--` adentro.

## R23 [ERROR] Lista de ids pasada con `TValue`

Un parámetro que trae varios ids separados por coma (`_Param.Sucursales`, `Clientes`, `Articulos`,
`Bodegas`, `Proveedores`, ... o un `String.Join(",", ...)`) se pasa con `New TConjuntoString(...)` a un
SP, o con `New TConjunto(...)` en un filtro `OperadoresFiltros.En`. Nunca con `New TValue(...)`:
`TValue.ValueMSSQL` hace `Replace(",", "")` cuando `IsNumeric` da verdadero, y bajo la cultura `es-MX`
del Admin `IsNumeric("1,2,3")` es verdadero (coma = separador de miles). La lista llega como `"123"`
y el reporte sale vacío (o trae de más) justo al elegir "todas las sucursales"; con un solo id pasa
inadvertido.

**Evidencia:** 1769 (Ventas con Combos), 2261 (Bonificaciones Aplicadas), 2336 (Bonificaciones
Vigentes); la misma auditoría encontró 439, 440 y 441 con el mismo defecto.

---

Las reglas R21 y R22 las revisa **el agente**, porque necesitan leer código fuera del diff.

## R21 [RIESGO → ROMPE] SQL por conjuntos: joins que multiplican filas y NULL

- `UPDATE destino ... FROM ... JOIN` donde el join puede traer **más de una fila fuente por fila
  destino**: SQL Server aplica una cualquiera, sin error. Pasa cuando varias filas del origen apuntan al
  mismo destino (ej. varios padres con el mismo hijo).
- `<>`, `NOT IN` o `=` contra una columna que acepta `NULL` sin `ISNULL`: la fila se salta en silencio.
- `UPDATE`/`DELETE` que depende de un id de catálogo inestable entre ambientes (regla 05 del equipo).

**Qué hacer:** por cada `UPDATE ... FROM` o `MERGE` nuevo, escribir cuál es la llave del destino y
confirmar que el join la vuelve única. Si no se puede confirmar desde el código, reportarlo como
`[RIESGO]` con la consulta que lo verifica en la BD (el dev la corre; el agente no consulta bases).

**Evidencia:** PR 763, `SP_Ajuste_Flete_Aplicar`: el `UPDATE` del flete del hijo hace join desde el
detalle del ajuste por el padre; si dos padres del mismo ajuste comparten hijo, el flete del hijo queda
con el de cualquiera. En Testing hay 4 hijos con más de un padre.

## R22 [RIESGO → ROMPE] Contrato entre capas

Un cambio en una capa que otra consume por nombre, sin compilador que lo detecte:

| Se cambió | Revisar que coincida |
|---|---|
| Columnas o alias de una consulta en `NEGOCIO` (`TField(..., "Alias")`, `TableName`) | quien las lee por nombre: `row["X"]` en los `Models/*.cs` del Admin, `.Item("X")` en el POS, el `.dbml` local |
| Propiedad de un modelo del Admin (`Models/*.cs`) | el `field:` de las tablas bootstrap y los `regArt.X` del JS |
| `id`/`name` en un `.cshtml` | los `jq.find('#id')` del controlador JS |
| Firma de un método WCF (`IWCF*.vb`) | los `Reference.vb` de los clientes (POS, Inventario) y los llamadores |
| Parámetros o columnas de un SP | los `TStoreProcedure`/`EXEC` que lo llaman y el `.rdl` que lo usa |

**Evidencia:** PR 763: `ArticuloSucursalModel.cs` lee `row["AxS_Precio_Flete"]` y
`row2["Precio_Flete_Total"]`, columnas que agrega `TArticuloXSucursal.vb` en el mismo PR. Si una de las
consultas que alimentan ese DataSet no la trae, `double.Parse` explota en la pantalla.
