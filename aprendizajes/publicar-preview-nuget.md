# Publicar una versión de prueba (preview) de un paquete NuGet

Cuándo: una rama necesita un paquete que todavía no existe oficial (Integration.SDK o LD.Libraries) para que el
build del PR lo encuentre en el feed.

## Qué es oficial y qué es de prueba
- **Oficial:** el pipeline lo sube solo. Integration.SDK sale de `cd-integrations-testing.yml` (etapa
  `Testing_PublishFeed`, solo en Testing). LD.Libraries sale de `cd-testing` de LDCOM13_DOS_PINOS (script
  `pack-ld-libraries.ps1`). Hasta que esa corrida no pase, el paquete oficial no existe.
- **De prueba (preview):** versión con sufijo prerelease, por ejemplo `13696.5.0.9124-preview.2` o
  `1.5.1-sfa15-preview.1`. NuGet no la ofrece a nadie que actualice paquetes sin pedirla, así que no se cuela.
- Un preview es temporal: antes de pasar a release hay que volver a la versión oficial en un PR chico.
  Si el código del paquete cambia, se publica el siguiente (`-preview.2`); un preview ya subido no se pisa.

## Pasos
1. Compilar la rama que lleva el cambio y armar el paquete con la versión con sufijo.
   - LD.Libraries: el script del pipeline `pack-ld-libraries.ps1` pasándole la versión, sobre la compilación de
     ServiciosWCF del worktree del PR.
   - Integration.SDK (en LDCOM13_INTEGRATIONS):
     `dotnet pack src/Integration.SDK/Integration.SDK.csproj --configuration Release -p:Version=<v> -p:PackageVersion=<v> -p:PackageOutputPath=<carpeta>`
     (el .nupkg del SDK pesa unos 60 MB porque trae el Runner).
2. Subirlo al feed con las credenciales de quien publica (lo hace el desarrollador, no Claude):
   ```
   dotnet nuget push "<ruta>\<paquete>.nupkg" --source "https://pkgs.dev.azure.com/LD-Vacas/_packaging/LDCOM13.DosPinos/nuget/v3/index.json" --api-key az --interactive
   ```
   `--api-key az` es un valor fijo que pide Azure Artifacts, no es una clave. Si el feed del paquete es otro
   (Integration.SDK usa el "Feed Integrations" del pipeline), cambiar `--source`.
3. Apuntar la rama a esa versión (`packages.config` / `.csproj`), compilar, correr las pruebas y recién ahí abrir el PR.
   Dejar en la descripción del PR que el paquete es temporal.
4. Anotar en el HANDOFF de la rama: versión subida y qué falta para pasar a la oficial.

## Estado conocido (2026-10-30)
- LD.Libraries `13696.5.0.9124-preview.1` y `-preview.2` se subieron a LDCOM13.DosPinos con este comando
  (la preview.1 quedó sin uso; se puede ocultar con Unlist en Artifacts). La oficial `13696.5.0.6608` ya la reemplazó.
- Integration.SDK `1.5.1-sfa15-preview.1` (rama de SFA15) solo existe armado en local (`C:\FUENTES\DP\_local-nuget`);
  NO se ha subido al feed. La rama 3700 de LDCOM ya apunta a esa versión, así que otra PC no compila hasta que se suba.

## Pendiente
Esto es manual a propósito por ahora. Buscar una forma sin pasos a mano (por ejemplo, que el build de la rama
publique el preview solo). Cuando se decida, actualizar este archivo.
