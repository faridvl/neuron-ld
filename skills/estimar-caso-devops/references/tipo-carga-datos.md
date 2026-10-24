# Tipo: carga de datos

Leer primero el skill del repo `C:/FUENTES/DP/LDCOM13_DOS_PINOS/.claude/skills/remediacion-carga-datos/SKILL.md`:
ya codifica la disciplina (tabla real, cobertura, sandbox Docker, README). Ademas:

- **Carga masiva existente:** buscar `CX_Tabla` + `CargaMasivaController.cs` en ADMIN_LDCOM. Casi
  nunca cubre todo: mapear tabla por tabla que tiene loader y que no.
- **Volumen real del Excel:** el max `<row>` puede acercarse a ~1M por formato aplicado a toda la hoja.
  Leer `xl/sharedStrings.xml` (`count`/`uniqueCount`) y dividir entre columnas con texto, o parsear
  el XML. Estimar sobre filas reales, no sobre el peso del archivo.
- **Llave estable:** verificar si el catalogo tiene un codigo de interfaz aparte del id interno (ej.
  `CECO.Codigo_Interfaz` vs. `Ceco_Id`, que cambia entre ambientes). Upsert siempre por el codigo
  estable, aunque un script anterior haya usado el id interno.
- **Si el ticket trae el Excel corregido**, verificarlo contra los ejemplos del ticket antes de usarlo
  como fuente de la remediacion.
- **Sandbox Docker** (`NEGOCIO/Database/docker/database`) es un snapshot congelado: tablas migradas
  despues no estan. Aplicar esas migraciones a mano es preparacion de una sola vez (~15-20 min).
- Staging y Staging RC son replicas de UAT: investigar ahi equivale a investigar UAT.
- Se valida en el Docker que simula Staging; en Staging RC/UAT se corre el mismo script ya validado,
  no se vuelve a probar de cero.
