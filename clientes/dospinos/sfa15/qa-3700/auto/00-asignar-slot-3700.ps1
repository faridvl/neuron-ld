# Apunta el slot "otros" de rig al worktree de la 3700 (o lo devuelve con -Restaurar). Correr en la terminal real.
param([switch] $Restaurar)
$ruta = Join-Path $env:LOCALAPPDATA 'dp-tools\config.local.json'
$respaldo = "$ruta.antes-3700"
if ($Restaurar) {
    if (Test-Path $respaldo) { Copy-Item $respaldo $ruta -Force; Write-Host "Restaurado desde $respaldo" -ForegroundColor Green }
    else { Write-Host 'No hay respaldo' -ForegroundColor Yellow }
    return
}
if (-not (Test-Path $respaldo)) { Copy-Item $ruta $respaldo -Force }
$config = Get-Content $ruta -Raw | ConvertFrom-Json
Write-Host ("Slot otros antes: " + $config.slots.otros.worktree)
$config.slots.otros.worktree = 'C:\FUENTES\DP\LDCOM13_DOS_PINOS-3700'
$config | ConvertTo-Json -Depth 10 | Out-File -FilePath $ruta -Encoding utf8 -Force
Write-Host 'Slot otros -> worktree 3700' -ForegroundColor Green
