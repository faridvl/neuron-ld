# Módulo Negocio y servicios WCF

Archivos: todo `NEGOCIO/**` fuera de `NEGOCIO/FACTURACION` y `NEGOCIO/Database` (catálogos, control de
negocio, objetos comunes, `ServiciosWCF`), y cualquier otra carpeta de `INTERFACE` que no sea el Admin ni
Facturación (Inventario, etc.).

## Qué leer

- `reglas-vigentes.md`.
- `mapa-riesgo-facturacion.md` solo si el diff toca clientes, bonificaciones, combos, precios o
  impuestos (esos catálogos alimentan al POS).
- Del equipo: `.claude/rules/04-vbnet-standards.md`.

## Reglas que pesan aquí

R05 (hermanos), R06 (el POS lee estos catálogos en línea y en local), R09, R10, R12, R14 (cargas
masivas en `TCargaXTabla.vb`), R15, R22 (contrato entre capas).

## Cómo revisar

1. **Clases de registro (`TReg*`) y catálogos (`T*`)**: una propiedad nueva tiene que llenarse en
   **todos** los lugares donde se arma el registro (el `Select`, el `IIf(IsDBNull(...))` de carga, la
   proyección LINQ, `Clear`). Buscar los hermanos de carga con `Grep` de una propiedad vieja vecina.
2. **Consultas que devuelven DataSet**: una columna o alias nuevo, ¿quién la lee? (R22). El Admin la
   lee en `Models/*.cs` con `row["X"]`; el POS con `.Item("X")`. Si alguna consulta hermana que
   alimenta el mismo consumidor no la trae, el consumidor explota.
3. **Validaciones de negocio nuevas** (fechas, estados, "ya aplicado"): leer la función completa y
   armar la tabla de verdad (R09). Una condición `A OrElse B OrElse C` donde una ya implica a otra es
   un `[PROPUESTA]` de simplificación; una que cambia qué registros quedan bloqueados es `[RIESGO]`.
4. **Métodos WCF** (`IWCF*.vb`, `*.svc.vb`): firma cambiada → clientes en los `Reference.vb` del POS e
   Inventario (no se regeneran solos).
5. **Cargas masivas** (R14): cada validación nueva en el servidor, con mensaje que diga fila.
6. No revisar estándar (R01-R04, R16-R20): ya viene del chequeo automático. Solo confirmar o descartar
   los candidatos que te pasan.
