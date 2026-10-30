---
name: trampas-entorno-qa
description: Trampas de entorno al probar en esta PC (Bash heredocs, Docker SQL, reseed, Write bloqueado, API en copia)
metadata:
  type: reference
---

- **Write/Edit sobre codigo esta bloqueado para QA** (hook: solo memoria). Los scripts de prueba fuera del repo se escriben con `cat > archivo <<'EOF'` en Bash.
- **Heredocs en Bash**: una comilla simple desbalanceada en el cuerpo rompe TODO el comando ("unexpected EOF while looking for matching '"), aunque el delimitador este entrecomillado. Y los backslashes se pierden: `\11` se vuelve tabulador, `\r` salto de linea, `\a` campana, `\b` retroceso. Solucion: usar solo comillas dobles y `chr(39)` para SQL, `chr(92)` para backslash, o un marcador (`@`) que Python reemplaza al instalar el archivo. Revisar siempre con regex `[\x00-\x08\x0b-\x1f]` los .md escritos.
- **Docker SQL**: `localhost,1433` (contenedor ldcom-dospinos-staging-sql) tiene las bases `..._DEVELOP_DOCKER`, `..._STAGING_DOCKER` (copia local de Staging, util para reconstruir filas) e `..._INTEGRATIONS_DEVELOP_DOCKER`. Cualquier UPDATE que liste Categoria_Id/SubCategoria_Id de un articulo con par huerfano (1,31) falla por FK aunque no cambie el valor: restaurar sin esas columnas.
- **Antes de correr una publicacion que escribe: respaldo de filas** (no solo checksum). Con solo checksum hay que reconstruir desde evidencias anteriores y verificar con BINARY_CHECKSUM.
- Borrar relaciones/clientes por SQL genera filas en `Bit_Tabla_Borrar` (por trigger) despues de calcular lo "nuevo": recalcular la lista antes de borrarlas. Reseed: derivarlo de las llaves borradas (cola del identity), nunca valor fijo.
- API de prueba: copia `scratchpad/e2e-cpN` con `dotnet restore --configfile nuget.local.config --artifacts-path <dir>` (restore tambien necesita el artifacts-path); `scratchpad/api4.sh start|stop` levanta/mata el :6222. Variable de entorno vacia (`Integration__Tenants__0__X=`) pisa el appsettings para simular config faltante.
- Para "no se consumio" en cola: IntegrationEvent.SourceType=2 + EndpointUrl a un servidor falso local (`e2e/mat/fake_cola.py`, :7391) que cuenta POSTs; restaurar la fila con checksum.
- `dotnet build` del repo real con `--artifacts-path` propio no ensucia el `git status`.
- **PowerShell here-string `@'...'@` + `[IO.File]::WriteAllText(ruta, texto -replace "`r`n","`n", UTF8 sin BOM)`** es la forma fiable de escribir scripts .sh/.py/.sql desde QA (el heredoc de Bash pierde backslashes y rompe con comillas). Ojo: un .md con CRLF (BUGS.md) se agrega con CRLF.
- **Sandbox E2E compartido entre varios QA**: el simulador solo tiene Estado Pendiente/Consumida; los scripts de apartar/restaurar de otro QA devuelven a Pendiente lo que tu cargaste. Cargar aparcado (Consumida) y activar con un script que aparte las demas. Restaurar la LDCOM E2E tira la sesion del Admin de otro QA y deja mapeos de trazabilidad huerfanos en la IntegrationDB.
- **sqlcmd con tablas ZZ_ con guion** falla; `BINARY_CHECKSUM(t.*)` no es valido (subconsulta con `BINARY_CHECKSUM(*)`). Python lee SQL grande con `sqlcmd -y 0` + `FOR JSON PATH` a archivo (q4sql.py); la clave sale de q.sh evaluando bash con PATH de Git. PowerShell: cultura invariante para CSV (decimales con coma).
- **Matar el API y reiniciarlo** dispara solo el SyncSchedulerJob sobre ActiveTransactionId abierto y consume toda la cola de esa interfaz.
- **Oraculo campo por campo**: correrlo justo tras la 1.a corrida; contra decisiones vigentes (DECISIONES.md: 136 correo, 39 inactivar por AxS, 60 nombre comercial), no contra la primera version de la regla.

- **Sin Python en PATH** (alias de Microsoft Store): analizar HTML con scripts .ps1 escritos a archivo (`param($d)`; rutas completas, `[IO.File]::ReadAllText` no resuelve relativas). En bash dentro de la herramienta `"$W\$f"` llego literal: pasar rutas desde PowerShell.
- **API :6232 del sandbox corre una copia vieja**: sus filas JOB siguen con Type vacio y Phase NULL; el codigo nuevo del API solo se verifica con pruebas unitarias hasta que la copia se actualice.

- **Escenarios de monitor (2026-10)**: copias ESCENARIOS por BACKUP COPY_ONLY/RESTORE en el Docker (MOVE a /var/opt/mssql/data/, con MSYS_NO_PATHCONV=1 para rutas del contenedor). Pero ese mismo MSYS_NO_PATHCONV rompe scripts que usan rutas /c/... (python no las ve) y `taskkill //F` se vuelve `/F`: lanzar los .sh con `env -u MSYS_NO_PATHCONV`. Una corrida manual (API) drena TODAS las publicaciones pendientes de la suscripcion (1 por llamada, hasta vaciar): para dosificar, marcar Estado en CIH_SIMULADOR.dbo.Publicacion y restaurar al final. Reintentos solo en corridas programadas (IsSchedulable=1 + cron `M * * * ? *`, tick 30 s); manual = 1 intento. Corrida "con usuario": Runner.exe por stdin (TriggerSync, UserName) con appsettings.json junto al exe. Capturas a archivo: Chrome headless + cdp.py del scratchpad (el panel Browser no guarda PNG).

- **Consola :6243** (correr-consola-historial.sh) apunta a LDCOM_DOS_PINOS_INTEGRATIONS_E2E (1.540 corridas sin TRACE). Total de la pantalla = "N corridas encontradas"; PageSize fuera de [10,15,25,50] vuelve a 15. sqlcmd con `{texto}` literal en -Q/-i devuelve vacio sin error (no sirve para probar SQL roto): verificar por la pagina. ESCENARIOS (2026-10-28 02:33) aun tenia la generacion previa (TriggeredBy DOS_PINOS, sin 'Programador').
