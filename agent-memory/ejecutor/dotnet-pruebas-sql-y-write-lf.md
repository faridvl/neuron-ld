---
name: dotnet-pruebas-sql-y-write-lf
description: Trampas al escribir pruebas xUnit con SQL en Docker desde Windows: LF del Write, Record.ExceptionAsync, CHECK de IntegrationEvent, variable propia
metadata:
  type: feedback
---

- El Write deja archivos LF; en repos CRLF normalizar con `sed -i 's/$/\r/'`.
- `Record.ExceptionAsync(metodo)` con method group da CS1503: usar lambda `() => x.MetodoAsync()`.
- Pruebas SQL: usar variable de entorno propia con cadena plana (la existente de SqlServerFact trae la clave codificada); saltar si no esta. La clave de SA se lee del env del contenedor con docker inspect, sin imprimirla.
- IntegrationEvent tiene CHECK: EventType en CATALOG/WEBHOOK/SYNC_JOB, Direction INBOUND/OUTBOUND.
- `dotnet build` pide la ruta del .sln (esta en la raiz del worktree, no en src).
**Why:** cada una costo un ciclo de compilar/probar. **How to apply:** al armar pruebas nuevas en repos .NET de LD.
