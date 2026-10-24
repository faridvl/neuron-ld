# Módulo PV (punto de venta / facturación)

Archivos: `INTERFACE/FACTURACION/**`, `NEGOCIO/FACTURACION/**`. Es el módulo con más devoluciones de QA.

## Qué leer

- `reglas-vigentes.md` (siempre) y `mapa-riesgo-facturacion.md` (siempre en este módulo).
- `casos-historicos.md` solo si el diff toca un método de la cadena de regresión que cita el mapa.
- Del equipo: `.claude/rules/04-vbnet-standards.md`.

## Reglas que pesan aquí

R05 (hermanos), R06 (local vs en línea), R07 (estado de la factura), R08 (regresión sobre fix reciente),
R09 (condición invertida), R11 (dinero), R12 (fechas), R15 (código desactivado), R22 (contrato entre
capas) y la pasada de invariantes I1-I8 del mapa.

## Cómo revisar

1. Cada cambio en la capa en línea (`NEGOCIO/FACTURACION`, `AccesoDatosEnLinea`) tiene su par en
   `FacturacionLOCAL` (`TFacturacionLocal.vb`, `TCatalogoLocal.vb`). Si el diff trae los dos, compararlos
   línea a línea: mismo cálculo, mismos alias, mismo tratamiento de `NULL`.
2. Un cambio en una consulta de precio, impuesto o descuento: listar **todas** las funciones que
   devuelven el mismo dato (`Grep` del alias, ej. `"Precio"`) y marcar cuáles quedaron sin el cambio.
   Para cada una aplicar la regla de R05 antes de subirla a `[ROMPE]`: llamador real y que el valor se
   cobre o se muestre.
3. Tablas locales nuevas o columnas que el POS inserta: confirmar el script de `LDControlDBLocalAutomatico`
   y el orden de despliegue (el POS aplica los scripts pendientes al arrancar, antes de facturar).
4. No revisar estándar (R01-R04, R16-R20) de nuevo: ya viene del chequeo automático. Solo confirmar o
   descartar los candidatos que te pasan.
