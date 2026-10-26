---
name: api-con-planificador-y-sqlcmd-trampas
description: Levantar un API .NET con BackgroundService contra Docker corre sus jobs al arrancar; trampas de sqlcmd (-I, -f, -Q largo) al probar E2E
metadata:
  type: feedback
---

Al levantar un API .NET que registra un planificador (`AddHostedService<...SchedulerJob>`) contra una BD real o Docker, el job corre todos los eventos al arrancar con los archivos de ejemplo del repo y modifica datos y estado (LastRunAt, ActiveTransactionId).

**Why:** en el E2E de clientes/proveedores (2026-10-24) el primer arranque aplico el mock de materiales (10 articulos tocados) y dejo un reintento activo de TIPO_CAMBIO.

**How to apply:** antes del primer arranque, en la COPIA del repo comentar los `AddHostedService` y vaciar los mocks (`[]`); levantar y probar con `POST /api/sync/<EVENTO>/run`. Si ya corrio, matar el proceso y restaurar `IntegrationEvent` (LastRunAt/LastRetryAt/ActiveTransactionId).

Trampas de sqlcmd en Windows:
- `-f o:65001` combinado con `-I` (quoted identifier) devuelve cp850 en parte de las salidas: usar `-f i:65001,o:65001`, decodificar con respaldo cp850 y poner `SET QUOTED_IDENTIFIER ON;` dentro del batch en vez de `-I`.
- `-W` y `-y` son excluyentes; `-h -1` y `-y 0` tambien.
- `-Q` con un batch muy largo falla con "Unexpected argument": escribir el SQL en archivo (con BOM y `SET QUOTED_IDENTIFIER ON` al inicio) y usar `-i`.
- Un INSERT/UPDATE a Cliente/Proveedor necesita QUOTED_IDENTIFIER ON por el indice filtrado de Codigo_Interfaz.

Python `-I` ignora PYTHONIOENCODING: para imprimir acentos usar `python -I -X utf8`.
