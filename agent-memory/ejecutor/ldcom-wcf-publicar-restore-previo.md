---
name: ldcom-wcf-publicar-restore-previo
description: Al reapuntar el SDK en un worktree LDCOM, publicar-wcf falla por NuGet faltante hasta restaurar ServiciosWCF con RestoreConfigFile; publicar cambia el Web.config
metadata:
  type: reference
---

Tras cambiar la version del paquete en packages.config, `publicar-wcf.ps1` falla con "references NuGet package(s) that are missing". Primero: MSBuild ServiciosWCF.vbproj -restore -p:RestorePackagesConfig=true -p:RestoreConfigFile=<nuget-local.config fuera del repo> -p:SolutionDir=<wt>\NEGOCIO\ -t:Restore. La publicacion reemplaza el Web.config (hash cambia): restaurar del respaldo. Un LD.Facturacion.exe abierto desde el worktree bloquea la compilacion del POS (MSB3027) y matarlo puede ser denegado por el clasificador: dejarlo como bloqueo y avisar.
