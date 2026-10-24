# Convenciones de la página de Confluence LD-xx

- Sitio `https://logicaldata.atlassian.net`, espacio `DP`, padre "LDCOM: Interfaces" (`316342273`).
- Título `LD-xx <Nombre>` (ver ids en `mapa-endpoints.md`). Modelo completo: LD-10 (`441810945`).
- Acceso: el MCP de Atlassian pide OAuth; usar la REST API con la variable de usuario
  `ATLASSIAN_BASIC_AUTH` mediante `scripts/confluence.ps1` (maneja UTF-8; PowerShell 5.1 sin el
  script rompe tildes y emojis).

## Estructura de secciones (igual que LD-10)

```
<p><code>MÉTODO /ruta</code></p>
h2 Historial de cambios        tabla Fecha | Descripción | Autor (fila nueva al final, orden cronológico)
h2 Descripción
h2 Contexto de uso
   h3 Trigger
h2 Reglas y validaciones
   h3 Reglas de negocio        lista
   h3 <una h3 por tema>         (Filtros, Modo asíncrono, Resolución de artículos, Idempotencia…)
h2 Funcionalidades excluidas
h2 Códigos de error            tabla Código | Descripción
h2 Request
   h3 Query parameters         tabla Parámetro | Tipo | Requerido | Descripción
   h3 Body                     h4 por ejemplo + macro code json
   h3 Descripción de campos    h4 por objeto, tabla Campo | Tipo | Longitud | Requerido | Descripción
h2 Response
   h3 <HTTP> <texto>           una por cada respuesta, con macro code json
   h3 Campos del response      tabla Campo | Descripción
h2 Notas de implementación     lista
```

Las páginas de catálogo (GET) no tienen Body: Query parameters + Response.

## Formato (storage XHTML)

- Historial de cambios en orden **cronológico: la fila nueva va al final** (así están LD-04 y LD-10).
  Fecha `9/Octubre/2026`, autor el correo del usuario (`fvillacis@ld.co.cr`), descripción en una
  línea con qué cambió en el contrato.
- Si hay un comportamiento que va a cambiar pronto (p. ej. un bug que se corrige en la próxima
  entrega), preguntar si se documenta: el usuario prefirió **no mencionarlo** y que pregunten, para
  no reeditar la página a los pocos días. Documentar solo lo que seguirá siendo cierto.
- Columna Requerido: emoji literal `✅` / `❌` dentro de `<p>`.
- Columna Longitud: **siempre un valor concreto** para parámetros y campos nuevos, aunque la página
  tenga `N/A` en otros: enum = largo del valor más largo (`itemType` → `3`), lista de enteros =
  dígitos por elemento (`priceIndex` 1–6 → `1 (por elemento)`), string = su `MaxLength`. El usuario
  lo pidió explícitamente.
- Nombres de campos, valores y rutas en `<code>`.
- Ejemplos JSON:
  ```xml
  <ac:structured-macro ac:name="code" ac:schema-version="1">
    <ac:parameter ac:name="language">json</ac:parameter>
    <ac:parameter ac:name="breakoutMode">wide</ac:parameter>
    <ac:parameter ac:name="breakoutWidth">760</ac:parameter>
    <ac:plain-text-body><![CDATA[ ...json... ]]></ac:plain-text-body>
  </ac:structured-macro>
  ```
- Notas destacadas: macro `info` (dato útil) o `warning` (algo que puede salir mal), con
  `<ac:rich-text-body><p>…</p></ac:rich-text-body>`.
- Tablas: `<table data-table-width="760" data-layout="default">`.
- Los atributos `local-id` / `ac:local-id` / `ac:macro-id` existentes se pueden conservar o
  omitir en los bloques nuevos; Confluence los regenera.

## Cómo editar sin romper la página

1. `confluence.ps1 -Accion Leer -PageId <id>` → `%TEMP%\cf\<id>.storage.xml` y la versión.
2. Editar **sobre ese storage** (insertar filas/secciones), no regenerar la página entera: así no
   se pierde lo que otros editaron a mano (comentarios inline, ajustes de formato).
3. Guardar en `%TEMP%\cf\<id>.nuevo.xml` y mostrar al usuario un resumen de las diferencias.
4. Solo con un "sí, publicá" explícito: `confluence.ps1 -Accion Publicar -PageId <id>
   -Archivo <nuevo.xml> -Mensaje "<ticket>: <resumen>"`. El script vuelve a leer la versión y
   aborta si alguien publicó en el medio.
