$ms = "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\MSBuild.exe"
$wt = "C:\FUENTES\DP\LDCOM13_DOS_PINOS-3700"
$cfg = "C:\Users\fvillacis\ClaudeLocalSession\sfa15\restore-3700\nuget.config"
foreach ($p in @("NEGOCIO\CATALOGOS\Catalogos.vbproj","NEGOCIO\CONTROL NEGOCIO\ControlBusiness.vbproj","NEGOCIO\ServiciosWCF\ServiciosWCF.vbproj","NEGOCIO\CATALOGOS.Tests\CATALOGOS.Tests.vbproj","NEGOCIO\FACTURACION\Facturacion.vbproj")) {
  Write-Host "== $p"
  if (-not (Test-Path "$wt\$p")) { Write-Host "no existe"; continue }
  & $ms "$wt\$p" -restore -p:RestorePackagesConfig=true "-p:SolutionDir=$wt\NEGOCIO\\" "-p:RestoreConfigFile=$cfg" -p:Configuration=Debug -v:m -nologo -clp:ErrorsOnly
  Write-Host "exit=$LASTEXITCODE"
}
