<#
Lee, busca y publica paginas de Confluence (logicaldata.atlassian.net) con la REST API y
la variable de entorno ATLASSIAN_BASIC_AUTH. Maneja UTF-8 a mano: Invoke-RestMethod de
PowerShell 5.1 decodifica las respuestas como Latin-1 y rompe tildes y emojis.

  confluence.ps1 -Accion Leer     -PageId 370016257
  confluence.ps1 -Accion Buscar   -Texto "LD-04"
  confluence.ps1 -Accion Publicar -PageId 370016257 -Archivo C:\...\370016257.nuevo.xml -Mensaje "Ticket 2241: filtros"

Leer deja <TEMP>\cf\<id>.storage.xml y <id>.version.txt. Publicar exige que la version en
Confluence siga siendo la que se leyo; si alguien publico en el medio, aborta.
#>
param(
    [Parameter(Mandatory = $true)][ValidateSet('Leer', 'Buscar', 'Publicar')][string]$Accion,
    [string]$PageId,
    [string]$Texto,
    [string]$Archivo,
    [string]$Mensaje = ''
)

$ErrorActionPreference = 'Stop'
$BaseUrl = 'https://logicaldata.atlassian.net/wiki/rest/api'
$WorkDir = Join-Path $env:TEMP 'cf'
New-Item -ItemType Directory -Force $WorkDir | Out-Null

if (-not $env:ATLASSIAN_BASIC_AUTH) {
    throw 'Falta la variable de entorno ATLASSIAN_BASIC_AUTH (Basic base64 de correo:api-token).'
}
$Headers = @{ Authorization = "Basic $env:ATLASSIAN_BASIC_AUTH"; Accept = 'application/json' }
$Utf8 = New-Object System.Text.UTF8Encoding($false)

function Invoke-Confluence([string]$Method, [string]$Url, [string]$JsonBody) {
    $parameters = @{ UseBasicParsing = $true; Method = $Method; Uri = $Url; Headers = $Headers; TimeoutSec = 90 }
    if ($JsonBody) {
        $parameters.Body = $Utf8.GetBytes($JsonBody)
        $parameters.ContentType = 'application/json; charset=utf-8'
    }
    $response = Invoke-WebRequest @parameters
    return $Utf8.GetString($response.RawContentStream.ToArray()) | ConvertFrom-Json
}

switch ($Accion) {
    'Leer' {
        if (-not $PageId) { throw 'Leer requiere -PageId.' }
        $page = Invoke-Confluence 'GET' "$BaseUrl/content/$PageId`?expand=body.storage,version,space,ancestors"
        $storagePath = Join-Path $WorkDir "$PageId.storage.xml"
        [IO.File]::WriteAllText($storagePath, $page.body.storage.value, $Utf8)
        [IO.File]::WriteAllText((Join-Path $WorkDir "$PageId.version.txt"), [string]$page.version.number, $Utf8)
        Write-Output ("Pagina : {0} (id {1}, espacio {2})" -f $page.title, $page.id, $page.space.key)
        Write-Output ("Version: {0}  ultima edicion {1} por {2}" -f $page.version.number, $page.version.when, $page.version.by.displayName)
        Write-Output ("Storage: {0} ({1} caracteres)" -f $storagePath, $page.body.storage.value.Length)
    }
    'Buscar' {
        if (-not $Texto) { throw 'Buscar requiere -Texto.' }
        $cql = [uri]::EscapeDataString("space = DP AND siteSearch ~ `"$Texto`"")
        $result = Invoke-Confluence 'GET' "$BaseUrl/search?limit=25&cql=$cql"
        foreach ($item in $result.results) {
            Write-Output ("{0} | {1} | {2}" -f $item.content.id, ($item.title -replace '@@@(end)?hl@@@', ''), $item.lastModified)
        }
    }
    'Publicar' {
        if (-not $PageId -or -not $Archivo) { throw 'Publicar requiere -PageId y -Archivo.' }
        $versionPath = Join-Path $WorkDir "$PageId.version.txt"
        if (-not (Test-Path $versionPath)) { throw "Primero hay que Leer la pagina $PageId (no existe $versionPath)." }
        $versionLeida = [int](Get-Content $versionPath -Raw)
        $actual = Invoke-Confluence 'GET' "$BaseUrl/content/$PageId`?expand=version"
        if ($actual.version.number -ne $versionLeida) {
            throw "La pagina cambio desde que se leyo (leida v$versionLeida, actual v$($actual.version.number)). Volver a Leer e integrar los cambios."
        }
        $storage = [IO.File]::ReadAllText($Archivo, $Utf8)
        $body = @{
            id      = $PageId
            type    = 'page'
            title   = $actual.title
            version = @{ number = $versionLeida + 1; message = $Mensaje }
            body    = @{ storage = @{ value = $storage; representation = 'storage' } }
        } | ConvertTo-Json -Depth 6 -Compress
        $published = Invoke-Confluence 'PUT' "$BaseUrl/content/$PageId" $body
        [IO.File]::WriteAllText($versionPath, [string]$published.version.number, $Utf8)
        Write-Output ("Publicada: {0} v{1}  https://logicaldata.atlassian.net/wiki{2}" -f $published.title, $published.version.number, $published._links.webui)
    }
}
