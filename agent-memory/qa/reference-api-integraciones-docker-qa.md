---
name: reference-api-integraciones-docker-qa
description: Como levantar la API LDCOM13_INTEGRATIONS local contra el Docker (env vars, clave sa, usuario qa_auto) y trampas de datos
metadata:
  type: reference
---

- Clave sa: `docker exec ldcom-dospinos-staging-sql printenv MSSQL_SA_PASSWORD` (nunca imprimir). Codificar con Encode (por caracter, de atras hacia adelante: len(ascii)*2 + ascii) en PowerShell; no hace falta programa aparte.
- API: PowerShell Start-Process `dotnet run --no-build --no-launch-profile --artifacts-path <dir>` en src\Integration.Api con env Integration__EnableAuthentication=false, __Audit__ConnectionString, __Tenants__0__LdcomConnection/DefaultCashRegisterId=3/LdcomUser/LdcomPassword(codificada)/LdcomModulo=2, ASPNETCORE_URLS=http://localhost:6222. Usuario/clave de prueba en ClaudeLocalSession\pruebas-sql\preventa-sucursal-destino\credenciales-prueba.txt (qa_auto). Parar: Get-NetTCPConnection -LocalPort 6222.
- DocumentSubType externo es "TE" (no "TD01:TE"). Query de LD-09 usa `adjustmentTypeExternalIds` / `storeExternalIds` (plural); un nombre mal escrito se ignora en silencio.
- Estado de preventa vive en PV_Preventa_Encabezado.Estado (y Monitor); Preventa_Consultar_Estado devuelve -1 en error y la API lo mapea a Pending.
- Boleta_Local_ListKey (historico) hace JOIN a Orden_Local_Encabezado: boleta sembrada sin orden => EXTERNAL_SYSTEM_ERROR en todo LD-09.
- Docker: Parametro_Sucursal Comprometer_Existencia_Preventa y Parametro_Express no traen valores para sucursal 17/20; ver qa de preventas-ld11.
