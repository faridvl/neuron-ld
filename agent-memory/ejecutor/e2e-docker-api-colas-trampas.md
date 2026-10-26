---
name: e2e-docker-api-colas-trampas
description: Trampas al probar E2E el API de colas (Materiales/TC/CECO) contra Docker con una copia del repo - respaldo SQL, biseccion, jrows, backslashes, endpoints manuales.
metadata:
  type: feedback
---

Al correr E2E nivel 1 contra el Docker local con una copia del API (`scratchpad\e2e-cp*`, MOCK en `MocksData`):

- **Respaldo y reversion en SQL, no en JSON**: `SELECT * INTO ZZ_E2E_<tabla>` de los articulos/filas que se van a tocar, y revertir por llave con `UPDATE ... FROM` comparando con `EXISTS (SELECT t.* EXCEPT SELECT b.*)`. Hay que incluir las tablas hijas que NEGOCIO crea (p. ej. `Articulo_x_Proveedor_Agencia` cuelga de `Articulo_x_Proveedor`) o el DELETE de las filas extra falla por FK. Revertir `Articulo_x_Sucursal` articulo por articulo (el trigger de auditoria es cuadratico). Borrar las ZZ_ al final.
- **Antes de borrar algo creado por la prueba**, escanear TODAS las tablas con la columna llave (`Articulo_Id`: 294 tablas, tarda ~2 min, correr en background) para saber que filas deja una alta (`CU_Cola_Articulo` mete 168 filas por articulo nuevo).
- **Una publicacion que falla entera ("failed entirely") se aisla por biseccion** publicando mitades; pero las mitades que pasan SI aplican cambios (y crean nuevos): hacer el respaldo antes y no medir "creados" despues de una biseccion sin limpiar.
- **`dk.jrows` (FOR JSON + sqlcmd) revienta con varchar que trae caracteres cp1252 como la comilla ” (0x94)**: leer el nombre como `convert(varchar, convert(varbinary, col), 2)` y decodificar en python.
- **El Bash de la sesion colapsa `\\` en heredocs**: para escribir `\n` literal en un script usar `chr(92)` o las herramientas Write/Edit; los f-strings con rutas `C:\Users` necesitan ser `rf"""`.
- `POST /api/sync/{evento}/run` NO toma candado ni mueve `LastRunAt` (el candado vive en el planificador); los endpoints manuales (`/api/exchange-rate/sync`, `/api/items/sync`) usan `ratesOverride`/`itemsOverride` y se saltan el mapper de la cola: no validan fecha futura ni existencia por codigo.
- Un `UPDATE` que lista las columnas de una FK (Categoria_Id, SubCategoria_Id) revalida la FK aunque no cambien: una fila con par huerfano rompe todo el bulk. `LdcomResponseValidator.CheckStringErrors` traduce cualquier "FOREIGN KEY constraint" como "El Proveedor o Empresa especificado no existe".
- Variables de entorno vacias en Windows se pierden: para "vaciar" una config del tenant (`Integration__Tenants__0__X`) pasar un espacio `" "` (el mapper hace trim).
- Los esperados se escriben antes, pero se equivocan: al corregir uno (p. ej. "un material nuevo trae 19 filas de sucursal": falso, las crea el job R05) dejar la correccion anotada en el escenario.
