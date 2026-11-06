# Scripts de apoyo (Dos Pinos)

## clonar-usuario-ldcom.sql + generar-clave-ldcom.ps1

Cuándo usarlo: un desarrollador necesita entrar al Admin y al POS de un ambiente (Testing = `LDCOM_DOS_PINOS_NEW`) con
su propio usuario, con los mismos permisos de otro usuario de aplicación (por ejemplo `logical`).

1. Generar la clave codificada: `powershell -NoProfile -File generar-clave-ldcom.ps1 -Clave 'MiClave1'`.
   Es AES (no se puede calcular en T-SQL); reproduce `EncriptarAES` de `NEGOCIO/SEGURIDAD/TSegUsuario.vb` y se verificó
   contra la DLL compilada del Admin.
2. Copiar `clonar-usuario-ldcom.sql`, llenar los parámetros `>>> LLENAR` (login, nombre, correo, clave codificada) y correrlo
   en la base LDCOM del ambiente. Una sola base; no toca INTEGRATIONS.
3. Es idempotente: si el login ya existe no toca su fila ni su clave y solo completa permisos faltantes. El resultado
   final compara filas origen vs. nuevo por tabla.

Qué copia y qué no está explicado en el encabezado del script. Para facturar en el POS no hace falta nada más por usuario:
`Vendedor_x_Usuario`, `Repartidor_x_Usuario`, `Cliente_x_Usuario` e `Inv_Despacho_Usuario` están vacías en Testing; el
POS valida el usuario contra `Seg_Usuario`, `Seg_Usuario_x_Rol` + `Seg_Menu_x_Rol` (acceso transaccional/administrativo),
`Seg_Menu_x_Usuario` (módulo) y `Seg_Sucursal_x_Usuario` (la sucursal de la caja).

`@DobleFactor` va en 0 por defecto (el origen `logical` lo tiene en 1 y pediría LDCODE). No guardar claves reales aquí.
