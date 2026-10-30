---
name: reference-qa-3663-compilar-antes-despues
description: Receta QA para comparar ANTES/DESPUES de un fix de NEGOCIO contra el API de integraciones en Docker (worktree base, MSBuild, DLL, trampas)
metadata:
  type: reference
---

- ANTES = `git worktree add --detach <ruta> origin/release/X` + MSBuild (`C:\Program Files\Microsoft Visual Studio\18\Enterprise\MSBuild\Current\Bin\MSBuild.exe`) de RUTINAS\LD_RUTINAS.sln y NEGOCIO\LD_COM_Negocio.sln con `-t:Restore -p:RestorePackagesConfig=true` y luego `-p:Configuration=Debug -m`: solo ~1.5 min. Copiar ServiciosWCF\bin. Un recompilado cambia el hash de TODAS las DLL (no determinista), asi que comparar tamano y buscar simbolos con `grep -c -a Reemplazar`, y verificar la DLL cargada con `Get-Process -Id X | Select -Expand Modules`.
- API: copiar `evidencias/preventas-ld11/artifacts-regresion-final/bin/Integration.Api/debug` a una carpeta propia y copiar encima las 10 DLL LD.* (AccesoDatos, AccesoTablas, Catalogos, ControlBussness, MENSAJES, Parametros, Seguridad, BITACORASQL, Facturacion, Inventario); `dotnet Integration.Api.dll` con env Integration__* (LdcomPassword = clave de qa_auto codificada con el codec). El :6222 suele estar ocupado por otra sesion: usar 6224/6225. Script reutilizable: `evidencias/3663-preventa-confirmacion/docker/arrancar_api.ps1` y `lib3663.py`.
- sql_crudo antepone `SET NOCOUNT ON;`: un `CREATE TRIGGER` en el mismo lote falla ("must be the first statement"); crearlo con `EXEC(N'...')` y comillas dobladas, y verificar en sys.triggers antes de probar (si no, la prueba de atomicidad es falsa).
- Un trigger de falla simulada se acota a UNA preventa (tabla auxiliar con la clave emp-suc-tipodoc-id) para no romper a otras sesiones que escriben preventas en el mismo Docker.
- GRANEL (9001) exige customAttributes.deliveryDate; es no editable (el 2.o PUT da 422 PREORDER_NOT_EDITABLE).
