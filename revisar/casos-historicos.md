# Casos históricos para medir el revisor

Commits reales que **introdujeron** un bug que después llegó a QA. Sirven de eval: se le da al revisor el
diff del commit que introdujo el bug (no el del fix) y se mide si lo detecta.

Cómo correr un caso:

```bash
git -C C:/FUENTES/DP/LDCOM13_DOS_PINOS show <commit> -- <archivo>
```

y pedirle al revisor que revise ese diff como si fuera un cambio propio.

| Resultado | Significado |
|---|---|
| DETECTA | Reporta el problema con la regla esperada y un escenario equivalente al del ticket |
| PARCIAL | Marca la zona o la regla correcta, pero sin el escenario concreto |
| NO | No lo menciona |

## La cadena 1476 → 1529 → 1602

Tres tickets seguidos en el mismo método; cada fix rompió el siguiente. Es el caso principal.

### C1 — `fceffbdd` fix(POS): 1476,1472,1478 → causó 1529

- **Archivo:** `INTERFACE/FACTURACION/Facturacion/Frm_Facturacion.vb`; métodos `Cambiar_Cliente`,
  `Cambiar_Tipo_Documento`, `Refrescar_Datos_Lista`.
- **Bug que introdujo:** 1529, *"Cantidades del artículo se duplican al cambiar de cliente"* (1 → 2, 8 → 16).
  QA: *"El caso se generó al resolver el caso 1476"*.
- **Regla esperada:** R07 (invariante I1) y R05 (familia "Cambio de cliente").

### C2 — `34c058d8` fix(pos): 1529 → causó 1602 y fue devuelto por QA

- **Qué cambió:** agregó un tercer booleano a `Evento_Enter_Articulo(..., True, True)` y dejó
  `If Verificar_Cambio_Bonificaciones(Linea, pCantidad, True) Then`.
- **Bugs que introdujo:**
  - 1602, *"Total de factura no se actualiza al modificar cantidad"* (el fix `ebca3145` cambió la
    condición a `If Not ...`).
  - Devolución de QA en 1529: *"al cambiar de cliente vuelve a cargar el o los artículos para colocar
    cantidades... si no se agregan nuevamente no aparecen en la factura"*.
- **Reglas esperadas:** R09 (condición), R02 (booleanos posicionales), R07 (I1, I2), R08 si se revisa
  después de C1.

### C3 — `d4bf18f5` feat(pos): 535, 545, 834, 1477 → causó 2244

- **Qué cambió:** comparación de líneas solo por artículo:
  `If CType(Item, TFacturaLine).Art_id = Linea.Art_id Then`.
- **Bug que introdujo:** 2244, *"Descuento escalonado modifica incorrectamente la cantidad del
  artículo"*; el fix `4a24e2f1` agregó `AndAlso ... Combo_Id = Linea.Combo_Id`.
- **Regla esperada:** R07 (invariante I3).

## Pendientes de armar

Se sabe el ticket y el fix, falta ubicar el commit que introdujo el bug:

- 1797: al modificar la cantidad de un bonificado se borran otras bonificaciones (I4).
- 1898: al cambiar de cliente se pierde el combo (I4).
- 1603: devolución sin redondear (I8, R11).
- 1532, 1495: impresión en contingencia y local (R05, R06, I7).
- 776: parámetro de caja que no sincroniza a la BD local (R06).

## Casos ciegos (no citados en ninguna regla)

Se encontraron con `git blame` de las líneas que un fix posterior quitó o cambió.

### B1 — `ef83dc12` corrección de bugs de bonificaciones → causó 1615 y 1658

- **Alcance:** `NEGOCIO/CATALOGOS/TBonificacionVenta.vb`.
- **Qué cambió:** `Dim hoy As DateTime = Now` y comparaciones `Fecha_Inicio < hoy`, `Fecha_Fin < hoy`.
- **Bugs:** 1615 (Fecha Inicial no permite el día actual; fix `fa9178ca`) y 1658 (tampoco Fecha Final;
  fix `09a990c8`).
- **Regla esperada:** R12.

### B2 — `0a244188` feat 553 combos → causó 1473

- **Alcance:** `INTERFACE/FACTURACION/Facturacion/Frm_Facturacion.vb` (+1013 −496).
- **Qué cambió:** entre cientos de líneas, se perdió `TTipo_Function.ReimprimirBoletaAutorizado` de un
  `Case` de la barra de opciones.
- **Bug:** 1473, reimpresiones de Boleta de Autorizados (fix `7dc633d9`, que vuelve a agregar ese valor).
- **Regla esperada:** R15 / R05.

## Contaminación

`reglas-vigentes.md` y el mapa citan como evidencia justamente estos commits (R09, R02, R15, I1, I3). Un
DETECTA en C1–C3 puede deberse a que la regla le "sopló" el ejemplo. Para medir de verdad hacen falta
**casos ciegos**: commits que causaron bugs y que no aparezcan en ninguna regla (ver "Pendientes").

## Registro de corridas

| Fecha | Versión de reglas | C1 | C2 | C3 | Notas |
|---|---|---|---|---|---|
| 2026-09-27 | inicial (R01–R14) | NO (1529) | DETECTA (1602 y la devolución de QA de 1529) | NO (2244) | C1 predijo el bug 1532 (tiquete sin "Cliente:"), corregido 7 días después en `83b9e610`. C2 encontró además la bonificación aceptada que no se agregaba (restaurada en `ed90071a`). C3 encontró el diálogo de bonificación duplicado (quitado en `34c058d8`) y el cambio de bonificación que no agregaba. C2 contaminado: R09 cita este commit. Tras la corrida se agregaron R15 y la pasada explícita de invariantes. |
| 2026-09-27 | + R15 y pasada de invariantes | DETECTA (contaminado: R15 cita el caso) | — | DETECTA como RIESGO I3 (contaminado) | Ciegos: **B1 DETECTA** (1615 y 1658 en un solo hallazgo, con la corrección exacta) · **B2 DETECTA** (el valor perdido del `Case` entre +1013/−496, corrección igual al fix de 1473). En B2 también encontró que combo y suelto del mismo artículo se mezclan al refrescar la lista (la corrección que propuso, agrupar por `Combo_Id`, es la del hotfix de 2244, 3 meses después; parcialmente sugerido por I3) y que "marcar regalo" por doble clic no bloquea líneas de combo (sigue abierto hoy). El reporte de B2 degeneró al final (texto basura en el 4.º hallazgo, faltó el 5.º): `rig revisar` ahora avisa si el reporte no llega a "Pruebas sugeridas". |
