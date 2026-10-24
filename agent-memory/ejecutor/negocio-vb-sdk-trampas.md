---
name: negocio-vb-sdk-trampas
description: Trampas del SDK NEGOCIO (VB) de LDCOM al construir y probar bulk contra Docker - build, pack, trigger de auditoria, TBitacoraSQL, transacciones
metadata:
  type: reference
---

- MSBuild de `ServiciosWCF.vbproj` deja las DLL en `ServiciosWCF\bin` (no `bin\Debug`). `LD.Libraries.csproj` trae `NoBuild`: empaquetar con
  `dotnet pack ... -p:Version=<v> -p:DllSourcePath=<...\ServiciosWCF\bin> -o C:\FUENTES\DP\nuget-local`.
- `TR_Cliente_Audit` -> `Audit_Registrar` cuesta O(n^2) por sentencia: UPDATE de 100 clientes en una sentencia = 35 s, 1000 no termina.
  Partir el UPDATE en sentencias de 3-5 filas (lineal, ~34 ms/fila). INSERT no audita (`Auditar_Insert=0`). Mientras corre, bloquea lecturas de `Cliente` de todos.
- Un UPDATE con trigger no admite `OUTPUT ... INTO` (error 334): calcular un plan en tabla temporal y filtrar con una columna `Cambia`.
- `Acceso_Generico` no reabre bien tras `Commit/RollBack` (`_Tran` no se anula): leer resultados antes del Commit; tras RollBack llamar `BeginTransaction` otra vez.
  Tablas `#temp` creadas dentro de una transaccion desaparecen con el RollBack: crearlas antes si se necesita el respaldo individual.
- Probar capa VB sin WCF: cargar DLL con PowerShell, `Acceso_MSSQLServer(cadena, MSSQL)`; la cadena se "desencripta" salvo que contenga `Integrated Security=true`
  (truco: `Application Name='Integrated Security=true'`). `TCliente` crea `TBitacoraSQL` que lee HKLM\Software\LogicalData\Config\LDOPERACION: fijar
  `MySettings.Default.PropertyValues.Item('LDOPERACION')` por reflexion. Fijar cultura invariable (decimales).
- Tras probar en Docker: borrar tambien `Audit_Seguridad` y `Bit_Tabla_Borrar` creados y re-sembrar las identidades.
- `dotnet pack ... -o C:\ruta` desde Bash pierde las barras invertidas y crea una carpeta basura dentro del proyecto: correr el pack en PowerShell.
- Git Bash de esta PC no trae `python` ni `strings`; para empalmar texto en archivos CRLF usar `head`/`sed 's/$/\r/'` o la herramienta Edit y verificar con `file`.
- Antes de decidir "sentencias pequenas" revisar `sys.triggers`/`Audit_Config`: Proveedor NO tiene trigger de auditoria (solo de borrado), asi que un UPDATE/INSERT por conjunto es lineal (1000 filas < 1 s); Cliente si lo tiene.
- Tablas #temp con columnas varchar: declarar `COLLATE DATABASE_DEFAULT` para no chocar con la collation de tempdb.
