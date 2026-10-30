<#
Apunta el evento POS-10 (CREDIT_VALIDATION) de la base Integrations del Docker local al SFA15 real de pruebas
o al simulador. Solo toca LDCOM_INTEGRATIONS_3699_DOCKER en el contenedor ldcom-dospinos-staging-sql.
  .\configurar-sfa15-docker.ps1 -Destino Real        # lee .env de esta carpeta
  .\configurar-sfa15-docker.ps1 -Destino Simulador   # valores de prueba del simulador (localhost:7390)
Nunca imprime usuarios ni claves.
#>
param([Parameter(Mandatory)][ValidateSet('Real', 'Simulador')][string]$Destino)
$ErrorActionPreference = 'Stop'
$Contenedor = 'ldcom-dospinos-staging-sql'
$Base = 'LDCOM_INTEGRATIONS_3699_DOCKER'

if ($Destino -eq 'Real') {
    $Valores = @{}
    Get-Content (Join-Path $PSScriptRoot '.env') | Where-Object { $_ -match '^\s*([A-Z0-9_]+)\s*=(.*)$' } | ForEach-Object {
        $Valores[$Matches[1]] = $Matches[2].Trim()
    }
    $Requeridas = 'SFA15_URL', 'SFA15_BASIC_USUARIO', 'SFA15_BASIC_CLAVE', 'SFA15_USUARIO', 'SFA15_CLAVE'
    $Faltantes = $Requeridas | Where-Object { -not $Valores[$_] }
    if ($Faltantes) { throw "Faltan en .env: $($Faltantes -join ', ')" }
    $Proceso = 'p_SFA15_Autorizacion_Venta_Final'
    $Url = $Valores.SFA15_URL.TrimEnd('/')
    if (-not $Url.EndsWith($Proceso)) { $Url = "$Url/$Proceso" }
    $Config = [ordered]@{
        Url = $Url; BasicUsuario = $Valores.SFA15_BASIC_USUARIO; BasicClave = $Valores.SFA15_BASIC_CLAVE
        Usuario = $Valores.SFA15_USUARIO; Clave = $Valores.SFA15_CLAVE
    }
}
else {
    $Config = [ordered]@{
        Url = 'http://localhost:7390/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final'
        BasicUsuario = 'basic-usuario-prueba'; BasicClave = 'basic-clave-prueba'
        Usuario = 'sim-sfa15'; Clave = 'sim-sfa15-clave'
    }
}

# Los valores viajan como variables de entorno del proceso de docker exec, no en el texto del SQL ni en la consola.
$Sql = @"
SET NOCOUNT ON; SET XACT_ABORT ON;
USE $Base;
DECLARE @EventoId INT = (SELECT Id FROM dbo.IntegrationEvent WHERE EventCode = N'POS-10');
IF @EventoId IS NULL THROW 50000, 'No existe el evento POS-10', 1;
BEGIN TRAN;
UPDATE dbo.IntegrationEvent SET EndpointUrl = N'`$(Url)', IsActive = 1, UpdatedAt = SYSUTCDATETIME() WHERE Id = @EventoId;
UPDATE dbo.IntegrationCredential SET AuthenticationUser = N'`$(BasicUsuario)', AuthenticationPassword = N'`$(BasicClave)', UpdatedAt = SYSUTCDATETIME()
 WHERE EventCode = N'CREDIT_VALIDATION';
IF @@ROWCOUNT = 0 THROW 50000, 'No existe la credencial de CREDIT_VALIDATION', 1;
MERGE dbo.IntegrationEventParameter AS Destino
USING (VALUES (N'SfaUser', N'`$(Usuario)'), (N'SfaPassword', N'`$(Clave)')) AS Origen (Nombre, Valor)
   ON Destino.IntegrationEventId = @EventoId AND Destino.ParameterName = Origen.Nombre
WHEN MATCHED THEN UPDATE SET ParameterValue = Origen.Valor, UpdatedAt = SYSUTCDATETIME()
WHEN NOT MATCHED THEN INSERT (IntegrationEventId, ParameterName, ParameterValue, CreatedAt) VALUES (@EventoId, Origen.Nombre, Origen.Valor, SYSUTCDATETIME());
COMMIT;
SELECT LEFT(e.EndpointUrl, 60) + '...' AS Url, e.IsActive,
       LEN(c.AuthenticationUser) AS LargoBasicUsuario, LEN(c.AuthenticationPassword) AS LargoBasicClave,
       (SELECT LEN(ParameterValue) FROM dbo.IntegrationEventParameter WHERE IntegrationEventId = @EventoId AND ParameterName = N'SfaUser') AS LargoUsuario,
       (SELECT LEN(ParameterValue) FROM dbo.IntegrationEventParameter WHERE IntegrationEventId = @EventoId AND ParameterName = N'SfaPassword') AS LargoClave
  FROM dbo.IntegrationEvent e CROSS JOIN dbo.IntegrationCredential c
 WHERE e.Id = @EventoId AND c.EventCode = N'CREDIT_VALIDATION';
"@
foreach ($Clave in $Config.Keys) {
    if ($Config[$Clave] -match "'") { throw "El valor de $Clave no puede llevar comilla simple" }
}
$ArchivoSql = Join-Path $env:TEMP 'configurar-sfa15-docker.sql'
Set-Content -Path $ArchivoSql -Value $Sql -Encoding UTF8
docker cp $ArchivoSql "${Contenedor}:/tmp/configurar-sfa15-docker.sql" | Out-Null
Remove-Item $ArchivoSql

$VariablesEntorno = foreach ($Clave in $Config.Keys) { '-e'; "SFA_$Clave=$($Config[$Clave])" }
$Comando = 'S=$(ls /opt/mssql-tools*/bin/sqlcmd | head -1); $S -C -b -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -i /tmp/configurar-sfa15-docker.sql -W ' +
    '-v Url="$SFA_Url" BasicUsuario="$SFA_BasicUsuario" BasicClave="$SFA_BasicClave" Usuario="$SFA_Usuario" Clave="$SFA_Clave"'
docker exec @VariablesEntorno $Contenedor bash -c $Comando
$Resultado = $LASTEXITCODE
docker exec -u 0 $Contenedor rm -f /tmp/configurar-sfa15-docker.sql
if ($Resultado -ne 0) { throw "Falló la actualización (código $Resultado)" }
Write-Host "POS-10 apunta ahora a: $Destino" -ForegroundColor Green
