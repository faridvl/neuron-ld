---
nombre: LDCOM13_SEGURIDAD_DOS_PINOS
carpeta: DP/LDCOM13_SEGURIDAD_DOS_PINOS
alias: seguridad, el de seguridad, seg
resumen: Módulo de Seguridad de LDCOM13 para Dos Pinos: usuarios, roles, menús, permisos y bitácora
estado: activo
cliente: dospinos
---

**Reglas del repo**: `CLAUDE.md` + `.claude/rules/` del propio repo (empezar por `00-contexto-ldcom.md`).

## Stack
VB.NET, soluciones `LD_SEGURIDAD\LD_SEGURIDAD.sln` y `NEGOCIO\LD_COM_Negocio.sln`. Se abre con `rig seguridad`
(IIS Express).

## Ramas
`develop` y `release/*` (al 2026-10-24: `release/2.2`). `main`: producción.

## Riesgos
Permisos y menús (quién puede hacer qué en el POS y el Admin), bitácora, y que algo viva en este repo o en el
core: confirmar antes de asumir.
