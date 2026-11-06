<#
Codifica una clave de LDCOM (Seg_Usuario.Usuario_Password) igual que el Admin y el POS.
Reproduce EncriptarAES de NEGOCIO/SEGURIDAD/TSegUsuario.vb (y TManagerTable.vb): Rijndael-256 bits de llave, ECB, PKCS7, bloque 128,
llave = MD5(llave fija ASCII) copiada en los bytes 0-15 y otra vez desde el byte 15 (queda el byte 31 en cero), texto ASCII, salida Base64.

Uso:  .\generar-clave-ldcom.ps1 -Clave 'MiClave1'
Salida: el texto Base64 que va en Usuario_Password (con Usuario_Password_AES = 1).
La clave se escribe en la consola; no se guarda en ningun archivo.
#>
param(
    [Parameter(Mandatory = $true)][string]$Clave
)

$ErrorActionPreference = 'Stop'
# Llave fija del codigo fuente (TSegUsuario.vb Valor_Llave_AES). No es un secreto del usuario.
$LlaveFijaLdcom = '123456789ohsfdflkjhasdfdasfdaspi'
$BytesMd5 = 16
$BytesLlaveAes = 32
$DesplazamientoSegundaCopia = 15

$md5 = [System.Security.Cryptography.MD5]::Create()
$resumenLlave = $md5.ComputeHash([System.Text.Encoding]::ASCII.GetBytes($LlaveFijaLdcom))
$llave = New-Object byte[] $BytesLlaveAes
[Array]::Copy($resumenLlave, 0, $llave, 0, $BytesMd5)
[Array]::Copy($resumenLlave, 0, $llave, $DesplazamientoSegundaCopia, $BytesMd5)

$aes = New-Object System.Security.Cryptography.RijndaelManaged
$aes.BlockSize = 128
$aes.KeySize = 256
$aes.Mode = [System.Security.Cryptography.CipherMode]::ECB
$aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7
$aes.Key = $llave

$bytesClave = [System.Text.Encoding]::ASCII.GetBytes($Clave)
$cifrado = $aes.CreateEncryptor().TransformFinalBlock($bytesClave, 0, $bytesClave.Length)
[Convert]::ToBase64String($cifrado)
