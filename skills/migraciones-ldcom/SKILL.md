---
name: migraciones-ldcom
description: Guía de `migrate` (migraciones de LD) — migración nueva, retocar un SP migrado, checksum distinto, script fallido, baseline. Usar al hablar de `migrate status/up/push/plan/baseline/new`, `_db_migrations` o de editar, borrar o reaplicar una migración.
---

# Herramienta de migraciones de LD (`migrate`)

- **Que es:** CLI propia de Logical Data para SQL Server, estilo Flyway/Prisma. Paquete
  `LogicalData.DatabaseMigration.Cli` (dotnet tool global, comando `migrate`). Instalada en esta PC
  en `%USERPROFILE%\.dotnet\tools\migrate.exe`.
- **Fuente:** https://dev.azure.com/LD-Vacas/AV%20Retail%20Dos%20Pinos/_git/DatabaseMigration
  (trae su propio `README.md` y `CLAUDE.md`). Dueño/feed: Hans Araya <haraya@ld.co.cr>.
  Feed NuGet: `https://pkgs.dev.azure.com/LD-Vacas/_packaging/LogicalData.Tools/nuget/v3/index.json`.
- Si algo de esta guia parece desactualizado, clonar el repo en el scratchpad y leer
  `DatabaseMigration.Core/Services/MigrationService.cs` (`BuildPlan`) y `CLI/Commands/*.cs`.
  Lo de abajo se verifico contra el commit `09aff1a` (2026-09-24), CLI 2.1.0.

## Como funciona (lo que importa para decidir)

- Se corre **desde la carpeta de la BD** (ej. `NEGOCIO/Database/GENERAL`), que tiene el `.env`
  (development) y `.env.testing`, etc. `--env testing` elige ambiente. `--migrations-path` permite
  apuntar a la carpeta `migrations` de otro worktree reutilizando el `.env` de la actual.
- Unidad de registro = **archivo**, no carpeta: `ScriptName = <carpeta>/<archivo.sql>` en
  `dbo._db_migrations` (Id, ScriptName, StartedAt, FinishedAt, Checksum, Logs, ...).
- Checksum = SHA256 del contenido UTF-8 normalizado (sin BOM, CRLF→LF, sin espacios al final de
  linea, lineas en blanco consecutivas colapsadas). Cambiar solo finales de linea o espacios NO lo
  rompe; cambiar cualquier otra cosa si.
- Estados por archivo (`BuildPlan`):
  - no esta en la tabla → **pending** (se aplica aunque su carpeta sea vieja o ya tenga otros
    archivos aplicados).
  - en la tabla con `FinishedAt NULL` → **failed**.
  - en la tabla con checksum distinto → **modified** (en `migrate status` la carpeta sale como
    **Fallido** y abajo el error `Checksum diferente en script ya aplicado`).
  - igual → **applied**.
  - en la tabla pero no en disco → warning "En DB existe ... pero no existe en carpeta (OK,
    advertencia)". Normal en BD compartidas (migraciones de otras ramas); no es error.
- Comandos:
  - `status` / `plan`: solo lectura. Seguros de correr siempre.
  - `up`: **aborta** (exit 2) si hay algun modified o failed. No aplica nada.
  - `push up` / `push --force`: aplica los **pending**; los modified solo los **advierte** y
    **no los re-ejecuta**; los failed igual bloquean. Es lo que usan los pipelines
    (`pipelines/scripts/releases/run-migrations.ps1` en LDCOM13_DOS_PINOS).
  - `baseline --upto <ts>` / `--latest`: inserta como aplicados sin ejecutar. Se niega si hay
    checksums distintos.
  - **No existe comando para "actualizar checksum" ni para "re-aplicar".** Eso solo se hace a
    mano sobre `dbo._db_migrations`.
- Cada archivo corre en su transaccion (`XACT_ABORT` + TRY/CATCH) salvo que empiece con
  `-- @no-wrap`. `THROW 51000, 'SKIP_MIGRATION <razon>', 1;` lo salta y lo registra.
- `ScriptAnalyzer` pide confirmacion ante `UPDATE`/`DELETE` sin WHERE, `DROP TABLE`, `TRUNCATE`,
  `ALTER/DROP COLUMN`, `NOCHECK`.

## Regla de oro

**Un archivo de migracion ya aplicado en cualquier BD es inmutable.** El cambio nuevo va en un
archivo nuevo. Razon concreta: los pipelines usan `push --force`, que no re-ejecuta un archivo
modificado; el cambio **nunca llegaria** a Testing/Staging/Produccion donde ya corrio, y en local
`up` queda bloqueado para todos los que compartan esa BD.

En LDCOM13_DOS_PINOS, preferencia del usuario: si el ticket ya tiene carpeta para ese objeto,
agregar `02_...sql`, `03_...sql` **dentro de esa carpeta** en vez de crear una carpeta nueva
(sale como pending igual). Y actualizar siempre el archivo de `routines/...` (fuente de verdad del
SP; `routines` no la lee `migrate`, asi que editarla nunca rompe checksums).

## Que hacer en cada escenario

Antes de tocar nada: `migrate status` (y si es otro worktree, con `--migrations-path`) para ver el
estado real. **Nunca** `DELETE`/`UPDATE` sobre `_db_migrations` ni re-aplicar sin confirmacion
explicita del usuario: Desarrollo (172.177.16.230) es compartida con otros devs.

| Escenario | Que hacer |
|---|---|
| Cambio nuevo a un objeto ya migrado (retoque de SP, fix de review) | Archivo nuevo (en la carpeta del ticket si existe) + actualizar `routines/`. `migrate up`. No tocar el archivo aplicado. |
| Se edito por error un archivo ya aplicado y `status` marca checksum distinto | **Revertir el archivo** a lo que se aplico (`git checkout <commit> -- <archivo>`; comprobar que `status` vuelve a Aplicado) y mover el cambio a un archivo nuevo. Es la salida correcta casi siempre. |
| El archivo editado **solo corrio en la BD local/Desarrollo** (nunca salio de la rama: sin merge, sin pipeline) y conviene conservar la version corregida | Se puede dejar editado. En la BD donde ya corrio hay dos opciones, ambas a mano y con confirmacion: (a) si el script es **idempotente** → borrar su fila de `_db_migrations` (`WHERE ScriptName = '<carpeta>/<archivo>'`) y `migrate up` para re-ejecutarlo; (b) si el efecto nuevo ya esta en la BD (se corrio a mano) → `UPDATE _db_migrations SET Checksum = '<nuevo>'` con el valor "Actual" que imprime `status`. En Testing/Staging/Prod ese archivo nunca corrio, asi que ahi corre la version nueva sin problema. |
| El archivo editado **ya corrio en Testing/Staging/Prod** (ya se mergeo/desplego) | **No** borrar ni cambiar checksum: revertir el archivo y crear uno nuevo con el cambio. Es la unica forma de que el cambio llegue a esos ambientes. |
| Script **failed** (FinishedAt NULL) | Leer el log en `migrations/logs/`. Corregir el archivo (aca si se puede editar: nunca termino), borrar su fila de `_db_migrations` (vuelve a pending) y `migrate up`. `up` y `push` bloquean hasta resolverlo; es lo que la propia herramienta indica. Si el efecto ya se aplico por fuera, en vez de borrar, marcarlo terminado a mano (`FinishedAt`). |
| BD vieja que ya tiene los cambios aplicados por fuera | `migrate baseline --upto <timestamp>` o `--latest` (por archivo). |
| Warnings "En DB existe ... pero no existe en carpeta" | Normal: son migraciones de otras ramas aplicadas en la misma BD. Ignorar. |
| `up` aborta por checksum de un archivo de **otra rama/persona** | No arreglarlo uno mismo en la tabla: avisar al usuario; usar `push up` si solo se necesita aplicar lo pendiente propio. |

## Notas LDCOM13_DOS_PINOS

- Una carpeta por BD: `NEGOCIO/Database/GENERAL` (principal), `INTEGRATIONS`, `LEALTAD`. Cada una
  con su `.env*` (git-ignorados) y su historial. Mapa y pipelines: `NEGOCIO/Database/README.md`.
- Nombre de carpeta: `yyyyMMddHHmmss__<ticket>_<Descripcion>`; archivos `01_...sql`, `02_...sql`.
- Pipeline: `Deploy WCF → Migrations (migrate db init + migrate push --force) → Site Admin`.
- Los worktrees nuevos no traen `.env`: correr desde `C:\FUENTES\DP\LDCOM13_DOS_PINOS\NEGOCIO\Database\GENERAL`
  con `--migrations-path <worktree>\NEGOCIO\Database\GENERAL\migrations`.
- Al mostrar el `.env` enmascarar `Password=`/`DB_PASSWORD`.
