---
name: rig
description: Cómo usar y configurar rig, la herramienta de ambientes de LDCOM (antes dp) — instalarla, iniciar un cliente, compilar y abrir el POS o el Admin, publicar en IIS, levantar Docker, cambiar de ambiente. Usar al configurar el ambiente, preguntar qué comando correr o levantar la base local.
---

# rig

`rig` arma y opera el ambiente local de LDCOM. Funciona sin Claude; tú guías al desarrollador y corres lo que
es seguro. `dp` es el nombre viejo y sigue funcionando.

## Lo que corres tú y lo que corre el desarrollador

| Tú puedes correr | Lo corre el desarrollador (tú le dices el comando) |
|---|---|
| `rig status`, `rig ambiente` (sin argumento), `rig info`, `rig init -Plan`, `rig setup -Plan`, `rig publicar -Plan` | `rig pos`, `rig admin`, `rig publicar`, `rig seguridad` (compilan y abren) |
| Leer `clientes/<cliente>/rig.json` y `config.local.json` | `rig setup` y `rig init` sin `-Plan` (preguntan e instalan) |
| | `rig docker` (siempre en su terminal real, no en una consola tuya) |
| | `rig ambiente <x>`, `rig ambiente -Restaurar`, `rig setup-iis` (pide administrador) |

## Configurar una PC nueva ("ayúdame a configurar rig")

1. ¿Tiene rig? `Get-Command rig`. Si no, que pegue en PowerShell (cambiando `$carpeta` si lo quiere en otro lado):
   `$carpeta = "$HOME\rig"; git clone https://dev.azure.com/LD-Vacas/AV%20Retail%20Dos%20Pinos/_git/ldcom.rig $carpeta; powershell -ExecutionPolicy Bypass -File "$carpeta\rig.ps1" setup`
   y abra una terminal nueva.
2. `rig setup -Plan`: muéstrale qué falta. Él corre `rig setup` (instala con winget tras mostrar la lista y pregunta
   su carpeta de proyectos).
3. En la carpeta del cliente (`C:\FUENTES\DP` para Dos Pinos, o la suya): `rig init -Plan` para ver qué detecta;
   luego él corre `rig init`.
4. IIS: si usa los slots estándar, `rig setup-iis` (administrador). Si ya publica en su propio IIS, va en `iis`
   de su `config.local.json` (`rig open config-local`).
5. Base: `rig docker`, luego la primera vez `rig docker refrescar` (30 a 40 min; pide la clave del usuario
   `logical` de TESTINGSQL, que se pide al equipo) y `rig docker jobs`. Ajustes manuales del clon: `rig open docs`.
6. Base local del POS: receta manual en `rig open docs`; sus datos van en `config.local.json` (`posLocal`).
7. Primer POS: `rig ambiente docker`, `rig publicar`, `rig pos`.

## Día a día

- Cambió NEGOCIO → `rig publish` antes de `rig pos` (el POS usa los WCF publicados, no lo compilado). Se puede elegir: `rig publish wcf` (ServiciosWCF y WS Express), `rig publish linq` (solo WS Express), `rig publish admin`. La restauración de paquetes de Azure DevOps es sin interacción y usa la variable de usuario `AZURE_DEVOPS_PAT` (nuget.config temporal en `%TEMP%`); si falta, falla rápido. Con los paquetes ya restaurados: `-SinRestaurar` (también en `rig pos`, `rig admin`, `rig seguridad`).
- Solo cambió Facturación → `rig pos -SoloFacturacion -Reiniciar`. Preventa → `-Preventa`.
- Cambió JS/CSS del Admin → `rig admin -ConAssets`.
- Se apagó la PC → `rig docker`.
- Antes de commit → `rig ambiente -Restaurar`.
- Antes del PR → `rig revisar` (contra `release/*` o `develop`).

## Configuración en tres capas

rig (genérico) ← `clientes/<cliente>/rig.json` (viene con rig; el de neuron-ld gana si existe) ← `config.local.json` en
`%LOCALAPPDATA%\dp-tools\` (solo de esa PC: rutas, IIS, impresora, base local del POS). El cliente sale de la
carpeta actual. Un cliente sin perfil: `rig init <cliente>` lo crea desde una plantilla y se sube a neuron-ld por PR.

## Problemas comunes

- "El worktree no esta asignado a ningun slot": correr `rig init` en la carpeta del cliente para registrarlo.
- "La version es incorrecta" al abrir el POS en Docker: `rig pos` registra las versiones del bin; volver a correrlo.
- Docker no levanta (socket trabado de Docker Desktop): `rig docker` lo resuelve; si sale el diálogo de error, Quit
  y volver a correr `rig docker` en su terminal.
- Detalle de cualquier comando: `Get-Help <carpeta de rig>\comandos\<comando>.ps1 -Full`.
