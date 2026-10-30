---
name: restaurar-packagesconfig-feed-local-msbuild
description: Restaurar/compilar proyectos packages.config de LDCOM con un paquete NuGet local sin tocar nuget.config del repo
metadata:
  type: reference
---

MSBuild VS2022 con `-restore -p:RestorePackagesConfig=true -p:SolutionDir=<carpeta>\ -p:RestoreConfigFile=<nuget.config fuera del repo>` (RestoreSources no sirve: el `;` rompe el switch). SolutionDir es obligatorio. Para proyectos SDK-style de pruebas que referencian un proyecto viejo, agregar Reference directa al DLL del paquete (no fluye transitivo). Python con heredoc: `\n` en rutas Windows se interpreta, usar Edit para rutas.
