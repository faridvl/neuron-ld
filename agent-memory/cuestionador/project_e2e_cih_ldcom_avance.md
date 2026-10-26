---
name: e2e-cih-ldcom-avance-cuestionador
description: Resultado de la revision cuestionadora final E2E de las 5 sincronizaciones CIH->LDCOM (2026-10-26): hallazgos reproducidos, estado del sandbox y limites del hook
metadata:
  type: project
---

Hook de este agente: bloquea Write fuera de memoria y cualquier Bash con `>`, `<`, `>>`, `<>` (tambien dentro de SQL o de textos de apoyo como '<LF>'); usar `!=`, BETWEEN, `[LF]`. `python -I -c`, curl POST, `_sql.sh` y `run_in_background` si pasan. No se pudo escribir avance-cuestionador.md ni BUGS.md en Desktop: las filas B-170+ viajaron en el informe final por SubagentHandback.

Reproducido en el sandbox (04:10-05:05): reproceso viejo sobre nuevo en cadena de reintentos (B-170), bloqueo sin limite + job en serie (B-171), publicacion consumida y perdida por sobre con tipos distintos (B-172), error por registro = reintento inutil + correo OK (B-173), doble corrida con 2 nodos (B-174), TC 1e-9 aceptado, usuario real de DP en ChangeLog (30 filas), claves en texto plano en IntegrationConnection. Candado entre 2 nodos y 3 paralelos: aguanta (409).

Estado al terminar: LDCOM_DOS_PINOS_E2E restaurada con q4-restaurar-ldcom.sh (baseline listo: 27.596 clientes, 4.840 articulos, 278 proveedores); IntegrationDB E2E NO restaurada (limpiado por llave); horarios de eventos devueltos a '0 3 1 1 ? *'; sets CUEST-* quitados del simulador; publicaciones ajenas que consumi quedaron Pendiente otra vez. NO usar reiniciar-sandbox.sh --configurado: el .bak de las 21:25 no tiene SourceQueueLog.AppliedAt.
