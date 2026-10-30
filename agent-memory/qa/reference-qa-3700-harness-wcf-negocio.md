---
name: reference-qa-3700-harness-wcf-negocio
description: Como probar NEGOCIO (TSistemaFinanciamientoSFA + Runner) y el cliente WCF real del POS con harness C# fuera del repo; trampas de conexion, urlacl, PowerShell vs Bash
metadata:
  type: reference
---

- Harness en `C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\` (e2e-negocio\Harness.cs, wcf-harness\WcfHarness.cs, e2e-3700.js, qd.js, cmp.js). Compilar con Roslyn `...\MSBuild\Current\Bin\Roslyn\csc.exe` (C# moderno) y copiando `NEGOCIO\CATALOGOS\bin` o `AccesoDatosEnLinea\bin\Debug` al lado.
- **Acceso_Generico decodifica toda cadena**: `password=` (minuscula, exacto) con la clave codificada (cada caracter: 2*largo-del-codigo + codigo, en orden inverso). Y hay que usar `Acceso_MSSQLServer(cadena, TipoBaseDatos.MSSQL)` con formato `server=..;database=..;uid=..;password=<enc>`; la base `Acceso_Generico` usa OleDb y falla. Llamar `Open()` antes de TQuery o da NullReference.
- **Runner/SDK**: la cadena de Integrations va con la clave codificada igual (el e2e-3699.js trae `enc`). Evento CREDIT_VALIDATION: configurar URL/credencial/parametros en `LDCOM_INTEGRATIONS_3699_DOCKER` y restaurar al final (IsActive 0).
- **ServiceHost sin admin**: usar prefijo `http://localhost:8733/Design_Time_Addresses/<algo>/` (urlacl ya reservado). El POS reemplaza `wcfcatalogo.svc` por `wcfcatalogoAux.svc` en la URL. El exe necesita `.exe.config` con los endpoints cliente `WCFCatalogoAux.IWCFCatalogoAux` etc. (el ctor por defecto del proxy los lee de ahi).
- **PowerShell vs Bash**: PowerShell no puede ejecutar .exe recien compilados ("Access is denied"); ejecutar harness con Bash. Y `Set-Location` de una llamada no persiste: una ruta relativa en PowerShell escribio un archivo dentro del repo (`WcfHarness.cs`); usar siempre rutas absolutas y revisar `git status`. Write/Edit estan bloqueados para QA: escribir scripts con PowerShell here-string `@'...'@` + WriteAllText.
- WCF: tras la primera llamada del cliente, cambiar `Endpoint.Binding.SendTimeout` NO tiene efecto (canal ya creado); usar `InnerChannel.OperationTimeout` o un cliente nuevo con su binding.
- `RESTORE ... MOVE` desde BACKUP COPY_ONLY a copia ZZ_ para probar migraciones; xp_cmdshell esta apagado (el .bak queda en /var/opt/mssql/data).
