---
name: simulador-cih-trampas-bcp-formato
description: Trampas al cargar JSON grandes a SQL Server con bcp desde Python y al imitar el formato CIH (campos nulos omitidos, claves variables, marcas internas en pools)
metadata:
  type: feedback
---

Al construir el simulador CIH (C:\FUENTES\DP\SimuladorCIH-DosPinos, base CIH_SIMULADOR en el Docker):

- **bcp de este equipo no acepta `-u`** (ODBC 170 viejo): quitarlo. Carga rapida de nvarchar(max): archivo UTF-16LE con terminadores multi-caracter (`~|~` campo, `~#~` fila) + `-w -t -r` a una tabla de paso, luego INSERT...SELECT. 5.000 registros (5 MB por publicacion) en ~6 s todo incluido.
- **sqlcmd con `-o` + FOR JSON** escribe BOM y parte lineas: leer con `utf-8-sig` y quitar solo `\r`/`\n` antes de `json.loads`. Variable de scripting `$(Set)` no definida aborta el script con -b: hacer un .sql por caso en vez de `NULLIF('$(Set)', ...)`.
- **CIH omite los campos nulos**: un registro real de materiales trae entre 76 y 98 claves segun el caso. Un validador de formato debe exigir las claves presentes en TODOS los registros reales y rechazar solo las que CIH nunca manda; no exigir un juego exacto. Al sobreescribir campos mapeados en una plantilla, no crear claves que la plantilla no tenia salvo que el valor no sea vacio.
- Los pools de "registros reales" armados por pruebas previas pueden traer marcas internas (`_pub`) que no existen en CIH: purgarlas y validar contra los sobres reales de la coleccion Bruno.
- La coleccion Bruno tiene ejemplos mal rotulados (el "example" de Consultar Materiales es una copia de proveedores): clasificar por la raiz de `data[0]`, no por el archivo.
- Heredoc en el Bash de la sesion colapsa `\\`: nada de rutas ni docstrings con backslash escritas por heredoc; usar Write/Edit o `chr(92)`.
