---
nombre: LDCOM13_DOS_PINOS
carpeta: DP/LDCOM13_DOS_PINOS
alias: el POS, ldcom, el core, el admin, dos pinos, dp
resumen: ERP retail LDCOM13 de Dos Pinos (POS de escritorio, Admin web, NEGOCIO, reportes); el proyecto principal de LD
estado: activo
cliente: dospinos
---

**Reglas del repo**: `CLAUDE.md` + `.claude/rules/` (00 a 11) del propio repo. Mandan sobre esta ficha.

## Stack
VB.NET (lógica de negocio, POS WinForms) y C# (.NET Framework 4.7.2, Admin ASP.NET MVC + JS), SQL Server
(migraciones en `NEGOCIO/Database/*/migrations`, herramienta `migrate`), reportes SSRS (`.rdl`).

## Ramas
- `develop`: trabajo del día a día. `release/*`: lo que está en el cliente, donde se resuelven los casos.
  El vigente es el `origin/release/*` de versión más alta (al 2026-10-24: `release/6.2`). No escribirlo fijo.
- `main`: producción.

## Comandos (rig)
- `rig pos -Reiniciar` (`-SoloFacturacion`, `-Preventa`, `-SinCompilar`), `rig admin` (`-ConAssets`),
  `rig publicar`, `rig ambiente docker|dev|testing`, `rig ambiente -Restaurar` antes de commit, `rig revisar`.
- Worktrees por slot (principal, develop, release, interfaces...): ver `clientes/dospinos/rig.json`.

## Riesgos
- Dinero y facturación electrónica (FE 4.4, Hacienda): montos, impuestos, exoneraciones, bonificaciones.
- Lógica duplicada por copy-paste entre FACTURACION, FACTCEDI, CEDI e INVENTARIO.
- Camino en línea (WCF) vs local (BD local del POS y su sincronización).
- El POS usa los WCF **publicados** en IIS, no lo compilado: si cambió NEGOCIO, `rig publicar`.
- Migraciones y SPs (bases compartidas solo lectura), `.rdl` (credenciales), Web.config del Admin.
- Ticket_Encabezado/Factura_Encabezado, `PV_Cerrar_Caja` y la sincronización local→servidor: columna nueva = revisar los SPs que copian el encabezado. Guía para los POS-xx de Dos Pinos: `aprendizajes/integrar-endpoint-pos-dos-pinos.md`.

## Relacionados
LDCOM13_SEGURIDAD_DOS_PINOS (seguridad), LDCOM13_INTEGRATIONS (integraciones), DatabaseMigration (`migrate`).
