# Restaurar paquetes ya publicados en los feeds de ADO (sin preguntarle al usuario)

Cuándo: un `packages.config` apunta a una versión que ya está en un feed de LD-Vacas (Integration.SDK oficial,
LD.Libraries, previews subidas) y MSBuild/NuGet responde **401 Unauthorized** o se queda colgado.

## Por qué falla
- Esta PC no tiene el Azure Artifacts Credential Provider ni Azure CLI. MSBuild desde consola no usa la sesión de
  Visual Studio.
- Con `-p:NuGetInteractive=true` y el proveedor de VS, NuGet espera un inicio de sesión con código de dispositivo
  y queda colgado sin mostrar nada. No usarlo.

## Cómo se hace
El token vive en la variable de entorno de usuario `AZURE_DEVOPS_PAT` (la misma del MCP de ADO). Se usa un
nuget.config **fuera del repo** que la referencia con `%AZURE_DEVOPS_PAT%` (NuGet expande variables), así el token
nunca se escribe en disco ni se imprime:

```xml
<configuration>
  <packageSources>
    <clear />
    <add key="LogicalData.Tools" value="https://pkgs.dev.azure.com/LD-Vacas/_packaging/LogicalData.Tools/nuget/v3/index.json" />
    <add key="LDCOM13.DosPinos" value="https://pkgs.dev.azure.com/LD-Vacas/_packaging/LDCOM13.DosPinos/nuget/v3/index.json" />
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" protocolVersion="3" />
  </packageSources>
  <packageSourceCredentials>
    <LogicalData.Tools>
      <add key="Username" value="az" />
      <add key="ClearTextPassword" value="%AZURE_DEVOPS_PAT%" />
    </LogicalData.Tools>
    <LDCOM13.DosPinos>
      <add key="Username" value="az" />
      <add key="ClearTextPassword" value="%AZURE_DEVOPS_PAT%" />
    </LDCOM13.DosPinos>
  </packageSourceCredentials>
</configuration>
```

En la consola (la variable de usuario no siempre llega al proceso; cargarla explícita):

```powershell
$env:AZURE_DEVOPS_PAT = [Environment]::GetEnvironmentVariable('AZURE_DEVOPS_PAT','User')
& "<MSBuild de VS 2022>" <proyecto> -t:Restore -p:RestorePackagesConfig=true "-p:SolutionDir=<carpeta de la solución>\" "-p:RestoreConfigFile=<nuget.config temporal>" -p:NuGetInteractive=false -v:m -nologo
```

- Si `AZURE_DEVOPS_PAT` no existe en la PC, se agrega como variable de entorno de usuario (el token lo genera el
  desarrollador en ADO con permiso Packaging Read). No se pregunta "cómo restaurar": se agrega y se sigue.
- La versión oficial de Integration.SDK es `<Version del .csproj>.<BuildId del CI>` (ej.: 1.5.2.7597, el BuildId es
  el número del artifact `integrations-api-build/1.0.0.<BuildId>` que consume `cd-integrations-testing`).
- Funcionó el 2026-11-02 restaurando Integration.SDK 1.5.2.7597 de LDCOM13.DosPinos para la rama 3700.

Relacionado: `publicar-preview-nuget.md` (subir un preview) y la receta de compilación de NEGOCIO en
`clientes/dospinos/sfa15/ESTADO.md`.
