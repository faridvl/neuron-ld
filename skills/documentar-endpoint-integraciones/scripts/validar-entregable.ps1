<#
Valida los entregables de un endpoint contra el codigo.

  validar-entregable.ps1 -Swagger <archivo.json> [-Dto <archivo.cs> -Clases ItemPriceRequestDto,ItemPriceItemDto]
  validar-entregable.ps1 -Postman <archivo.postman_collection.json>

Swagger: JSON valido, openapi 3.0.3, todos los $ref existen, cada propiedad publica de las
clases indicadas del DTO aparece (en camelCase) como parametro o propiedad de algun schema, y
todo codigo de error en MAYUSCULAS_CON_GUION que aparezca en el swagger existe en ApiErrorCode.
Postman: schema v2.1, cada request tiene test, ningun client_secret real, una sola baseUrl.
Sale con codigo 1 si hay errores.
#>
param(
    [string]$Swagger,
    [string]$Dto,
    [string[]]$Clases,
    [string]$Postman,
    [string]$Repo = 'C:\FUENTES\DP\LDCOM13_INTEGRATIONS'
)

$ErrorActionPreference = 'Stop'
$Utf8 = New-Object System.Text.UTF8Encoding($false)
$problems = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Get-JsonRefs($node, [System.Collections.Generic.List[string]]$found) {
    if ($null -eq $node) { return }
    if ($node -is [System.Collections.IEnumerable] -and $node -isnot [string]) {
        foreach ($child in $node) { Get-JsonRefs $child $found }
        return
    }
    if ($node -is [pscustomobject]) {
        foreach ($property in $node.PSObject.Properties) {
            if ($property.Name -eq '$ref') { $found.Add([string]$property.Value) } else { Get-JsonRefs $property.Value $found }
        }
    }
}

function Get-PropertyNames($node, [System.Collections.Generic.HashSet[string]]$names) {
    if ($null -eq $node) { return }
    if ($node -is [System.Collections.IEnumerable] -and $node -isnot [string]) {
        foreach ($child in $node) { Get-PropertyNames $child $names }
        return
    }
    if ($node -is [pscustomobject]) {
        foreach ($property in $node.PSObject.Properties) {
            if ($property.Name -eq 'properties' -and $property.Value -is [pscustomobject]) {
                foreach ($schemaProperty in $property.Value.PSObject.Properties) { [void]$names.Add($schemaProperty.Name) }
            }
            if ($property.Name -eq 'parameters') {
                foreach ($parameter in @($property.Value)) { if ($parameter.name) { [void]$names.Add([string]$parameter.name) } }
            }
            Get-PropertyNames $property.Value $names
        }
    }
}

if ($Swagger) {
    $text = [IO.File]::ReadAllText($Swagger, $Utf8)
    try { $document = $text | ConvertFrom-Json } catch { $problems.Add("Swagger: JSON invalido: $($_.Exception.Message)") }
    if ($document) {
        if ($document.openapi -ne '3.0.3') { $warnings.Add("Swagger: openapi es '$($document.openapi)', el estandar del proyecto es 3.0.3") }
        $refs = New-Object System.Collections.Generic.List[string]
        Get-JsonRefs $document $refs
        $schemaNames = @($document.components.schemas.PSObject.Properties.Name)
        foreach ($ref in ($refs | Sort-Object -Unique)) {
            $target = $ref -replace '^#/components/schemas/', ''
            if ($ref -like '#/components/schemas/*' -and $schemaNames -notcontains $target) { $problems.Add("Swagger: `$ref roto: $ref") }
        }
        $documented = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
        Get-PropertyNames $document $documented

        if ($Dto) {
            $source = [IO.File]::ReadAllText($Dto, $Utf8)
            $classPattern = 'class\s+(\w+)[^{]*\{(?<body>(?:[^{}]|\{[^{}]*\})*)\}'
            foreach ($match in [regex]::Matches($source, $classPattern)) {
                $className = $match.Groups[1].Value
                if ($Clases -and $Clases -notcontains $className) { continue }
                foreach ($propertyMatch in [regex]::Matches($match.Groups['body'].Value, 'public\s+(?:required\s+)?[\w<>\[\]\?,\s]+?\s+(\w+)\s*\{\s*get;')) {
                    $propertyName = $propertyMatch.Groups[1].Value
                    $camel = $propertyName.Substring(0, 1).ToLower() + $propertyName.Substring(1)
                    if (-not $documented.Contains($camel)) { $problems.Add("Swagger: falta $className.$propertyName (como '$camel')") }
                }
            }
        }

        $errorFile = Join-Path $Repo 'src\Integration.Core\Domain\Exceptions\ApiErrorMessage.cs'
        if (Test-Path $errorFile) {
            $errorSource = [IO.File]::ReadAllText($errorFile, $Utf8)
            $enumBody = [regex]::Match($errorSource, 'enum\s+ApiErrorCode\s*\{(?<body>[^}]*)\}').Groups['body'].Value
            $knownCodes = @([regex]::Matches($enumBody, '\b([A-Z][A-Z0-9_]+)\b') | ForEach-Object { $_.Groups[1].Value })
            $candidateCodes = [regex]::Matches($text, '"([A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+)"') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
            foreach ($code in $candidateCodes) {
                if ($knownCodes -notcontains $code -and $code -notmatch '^(NO_BANK|SPECIFIC_CUSTOMERS|IN_STOCK|OUT_OF_STOCK|CUSTOMER_TYPE)$') {
                    $warnings.Add("Swagger: '$code' no es un ApiErrorCode (si es un valor de enum del contrato, ignorar)")
                }
            }
        }
    }
}

if ($Postman) {
    $collection = [IO.File]::ReadAllText($Postman, $Utf8) | ConvertFrom-Json
    if ($collection.info.schema -notlike '*v2.1.0*') { $problems.Add("Postman: schema no es v2.1.0 ($($collection.info.schema))") }
    $baseUrls = New-Object 'System.Collections.Generic.HashSet[string]'
    function Test-Items($items, [string]$path) {
        foreach ($item in $items) {
            if ($item.item) { Test-Items $item.item "$path/$($item.name)"; continue }
            $raw = [string]$item.request.url.raw
            if ($raw -notlike '*login.microsoftonline.com*') {
                [void]$baseUrls.Add(($raw -replace '/api/.*$', ''))
                if (-not ($item.event | Where-Object { $_.listen -eq 'test' })) { $script:problems.Add("Postman: sin test -> $path/$($item.name)") }
                if (-not $item.request.description) { $script:warnings.Add("Postman: sin descripcion -> $path/$($item.name)") }
            }
            foreach ($field in @($item.request.body.urlencoded)) {
                if ($field.key -eq 'client_secret' -and $field.value -ne 'PENDIENTE_CLIENT_SECRET') { $script:problems.Add("Postman: client_secret real en $path/$($item.name)") }
            }
        }
    }
    Test-Items $collection.item ''
    $prerequest = ($collection.event | Where-Object { $_.listen -eq 'prerequest' }).script.exec -join "`n"
    if ($prerequest -match "CLIENT_SECRET\s*=\s*'([^']+)'" -and $Matches[1] -ne 'PENDIENTE_CLIENT_SECRET') { $problems.Add('Postman: CLIENT_SECRET real en el pre-request de la coleccion') }
    if ($baseUrls.Count -gt 1) { $warnings.Add("Postman: mas de una baseUrl: $($baseUrls -join ', ')") }
}

foreach ($warning in $warnings) { Write-Output "AVISO  $warning" }
foreach ($problem in $problems) { Write-Output "ERROR  $problem" }
if ($problems.Count -eq 0) { Write-Output "OK ($($warnings.Count) avisos)"; exit 0 } else { exit 1 }
