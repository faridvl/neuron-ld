# Módulo Base de datos y reportes

Archivos: `*.sql` (sobre todo `NEGOCIO/Database/GENERAL/migrations/**` y `routines/**`) y `*.rdl`
(`NEGOCIO/ReportingService/**`).

## Qué leer

- `reglas-vigentes.md` (R01, R12, R13, R21, R22).
- Del equipo: `.claude/rules/05-sql-standards.md` (siempre; es la regla principal de este módulo).
- La etapa automática ya revisó R18 (formato de migraciones) y R19 (fuente de datos del `.rdl`). No
  repetirlos.

## Cómo revisar

1. **Lógica por conjuntos (R21).** Por cada `UPDATE ... FROM`, `DELETE ... FROM`, `MERGE` o `INSERT ...
   SELECT` nuevo o modificado:
   - escribir la llave del destino y confirmar que el join la vuelve única;
   - revisar comparaciones con columnas que aceptan `NULL`;
   - revisar el orden: si un `UPDATE` posterior depende del resultado de uno anterior en el mismo lote.
2. **Transacciones**: `BEGIN TRAN` con su `COMMIT`/`ROLLBACK` en todos los caminos, `XACT_ABORT`, y que
   un `CONTINUE`/`RETURN` dentro de la transacción no la deje abierta.
3. **Base central vs base de la caja** (regla 05): una tabla o columna que el POS usa sin conexión
   necesita el script en `LDControlDBLocalAutomatico` (y `PV_Sincroniza_Tablas` si sincroniza datos).
   Un script local que altera una columna usada por un `INSERT` del POS: confirmar qué pasa en las
   cajas que todavía no aplicaron el script (el POS los aplica al arrancar).
4. **SP modificado**: `Grep` del nombre del SP en `*.vb`, `*.cs` y `*.rdl`. Parámetros o columnas de
   salida cambiados rompen a quien lo llama (R22).
5. **Reportes `.rdl`**: la consulta embebida o el SP que usa; parámetros del reporte vs los que manda
   el Admin; filtros de fecha con `<` vs `<=` en la fecha final (R12); totales que suman montos con y
   sin impuesto (R11).
6. **Idempotencia**: correr la migración dos veces no debe fallar ni duplicar datos (`IF NOT EXISTS`,
   `CREATE OR ALTER`, `INSERT` con guarda).
7. No consultar bases de datos. Si un hallazgo depende de los datos (ej. si hay hijos con dos padres),
   reportarlo como `[RIESGO]` y poner en `probar` la consulta de solo lectura que lo confirma.
