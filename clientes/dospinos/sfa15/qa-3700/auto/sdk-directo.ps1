# Llama IntegrationBridge.ValidateFinancingPlan en proceso (como lo haria el WCF) con la cadena del Web.config publicado.
param([decimal] $Monto = 1, [string] $Referencia = 'DIAG00000001', [string] $Cliente = '4000010')
$bin = 'C:\inetpub\wwwroot\dp\otros\ServiciosWCF\bin'
[xml] $cfg = Get-Content 'C:\inetpub\wwwroot\dp\otros\ServiciosWCF\Web.config'
$cadena = ($cfg.configuration.connectionStrings.add | Where-Object { $_.name -like '*LDDPINTEGRATIONS' } | Select-Object -First 1).connectionString
Get-ChildItem $bin -Filter *.dll | Where-Object { $_.Name -match '^(Integration|Newtonsoft)' } | ForEach-Object { try { [void][Reflection.Assembly]::LoadFrom($_.FullName) } catch {} }
$bridge = New-Object Integration.SDK.IntegrationBridge('TESTING', 'DOS_PINOS', $cadena, 'diag')
$req = New-Object Integration.SDK.Models.FinancingPlanValidationRequest
$req.CustomerCode = $Cliente; $req.BranchId = 19; $req.DocumentDate = Get-Date; $req.CustomerName = 'Diag'; $req.UsesCreditLine = $true
$req.CreditLineNumber = 0; $req.ExternalReference = $Referencia; $req.FarmCustomerId = 3664; $req.TermInWeeks = 4
$req.FinancingPlanExternalCode = '203'; $req.Amount = $Monto; $req.Notes = 'diag'
$sw = [Diagnostics.Stopwatch]::StartNew()
$resp = $bridge.ValidateFinancingPlan($req)
$sw.Stop()
Write-Host ("ms=" + $sw.ElapsedMilliseconds)
$resp | ConvertTo-Json -Depth 4
