---
nombre: LDCOM13_INTEGRATIONS
carpeta: DP/LDCOM13_INTEGRATIONS
alias: integraciones, la api de integraciones, colas, datos maestros, int
resumen: Plataforma .NET 8 que sincroniza datos maestros entre LDCOM13 (Dos Pinos) y sistemas externos por REST y colas
estado: activo
cliente: dospinos
---

**Reglas del repo**: `CLAUDE.md` del propio repo (build, pruebas, arquitectura). Mandan sobre esta ficha.
**Decisiones**: `.claude/DECISIONS.md` del repo (auditoría de corridas en Events, consola de pruebas).

## Stack
.NET 8, puertos y adaptadores, multi-tenant, idempotencia y auditoría. `dotnet build LDCOM13_INTEGRATIONS.sln`,
`dotnet test src/Integration.Tests/Integration.Tests.csproj`.

## Ramas
`develop` y `release/*` (el vigente es el de versión más alta; al 2026-10-24: `release/3.2.0`). `main`: producción.
Worktrees de trabajo hermanos: `LDCOM13_INTEGRATIONS-<tema>` (por ejemplo `-colas`).

## Repos relacionados
- **Postman_LDCOM13_DOSPINOS**: colección Bruno (YAML Open Collection) con ejemplos reales de las APIs y colas.
  Cada endpoint LD-01…LD-10 que cambia se documenta en tres lugares: Swagger, Postman y Confluence
  (skill `documentar-endpoint-integraciones`).
- LDCOM13_DOS_PINOS: el Admin configura las integraciones; se comunica por SDK/Runner por proceso, nunca HTTP. El POS llega por el WCF, que necesita su propio IntegrationStage/Tenant (guía: `aprendizajes/integrar-endpoint-pos-dos-pinos.md`).

## Riesgos
- Existencia de maestros: clientes, materiales y proveedores se buscan en LDCOM por código SAP sin ceros;
  CrossReference no decide.
- Cada campo cola → LDCOM con su prueba en el `*QueueRecordMapperTests` (sin prueba no está mapeado).
- Contrato de las APIs (cambios rompen a Dos Pinos), datos reales de clientes en las colas.
- Todo endpoint deja fila en `dbo.Events`, consultas GET incluidas; el monitor del Admin la lee tal cual.
- La consola de pruebas no tiene login: no publicarla en un ambiente compartido sin protegerla.
- Scripts manuales: solo los 4 de `Database/seeds` (catálogos, conexiones, eventos, webhooks). Un cambio se agrega al que
  corresponde; nunca un seed nuevo por ticket. Reglas completas en el `CLAUDE.md` del repo.
