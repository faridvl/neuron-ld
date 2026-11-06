<#
Muestra, solo lectura, un traslado de inventario y el aviso POS-26 (MOLASSES_TRANSFER, IntegrationEvent 4009)
que salió de él, en el Docker local de LDCOM.
Uso: powershell -NoProfile -File comprobar-aviso.ps1 -MovId 9816
#>
param(
    [Parameter(Mandatory)][ValidateRange(1, 2147483647)][int]$MovId,
    [string]$BaseCentral = 'LDCOM_DOS_PINOS_STAGING_DOCKER',
    [string]$BaseIntegraciones = 'LDCOM_DOS_PINOS_INTEGRATIONS_STAGING_DOCKER',
    [string]$Servidor = 'localhost,1433',
    [string]$ComunRig = 'E:\Proyectos\LD\rig\lib\comun.ps1'
)

. $ComunRig
$env:SQLCMDPASSWORD = Get-ClaveSaDocker

function Consultar([string]$Base, [string]$Sql) {
    sqlcmd -S $Servidor -U sa -d $Base -C -W -s '|' -Q "SET NOCOUNT ON; $Sql"
}

Write-Host "== Movimiento $MovId en $BaseCentral"
Consultar $BaseCentral @"
SELECT Emp_Id, Suc_Id, Bodega_Id, Mov_Id, Suc_Destino, Bodega_Destino, Mov_Estado,
       Mov_Estado_Interfaz, Mov_Fecha, Mov_Comentario
FROM Mov_Inventario_Encabezado WHERE Mov_Id = $MovId
"@
Write-Host '-- Lineas'
Consultar $BaseCentral @"
SELECT Suc_Id, Detalle_Id, Articulo_Id, Detalle_Cantidad, Detalle_Estado
FROM Mov_Inventario_Detalle WHERE Mov_Id = $MovId ORDER BY Suc_Id, Detalle_Id
"@

Write-Host ''
Write-Host "== Aviso (OutboundNotification, evento 4009) en $BaseIntegraciones"
$avisos = Consultar $BaseIntegraciones @"
SELECT Id, FactName, DocumentReference, Status, Attempts, LastHttpStatus,
       LEFT(LastResponse, 120) AS LastResponse, LEFT(LastError, 160) AS LastError,
       CreatedAt, SentAt, TransactionId
FROM OutboundNotification
WHERE IntegrationEventId = 4009 AND ISJSON(DocumentJson) = 1
  AND JSON_VALUE(DocumentJson, '`$.MovimientoId') = '$MovId'
ORDER BY Id
"@
if (($avisos | Measure-Object).Count -le 2) {
    Write-Host "Sin aviso para el movimiento $MovId."
    return
}
$avisos

Write-Host ''
Write-Host '== Events del aviso'
Consultar $BaseIntegraciones @"
SELECT e.Id, e.EventCode, e.Type, e.Phase, e.Status, e.CreatedAt, LEFT(e.ErrorMessage, 160) AS ErrorMessage
FROM Events e
WHERE e.TransactionId IN (
    SELECT CONVERT(nvarchar(50), n.TransactionId) FROM OutboundNotification n
    WHERE n.IntegrationEventId = 4009 AND ISJSON(n.DocumentJson) = 1
      AND JSON_VALUE(n.DocumentJson, '`$.MovimientoId') = '$MovId')
ORDER BY e.Id
"@
