---
name: documentar-endpoint-integraciones
description: Genera o actualiza los 3 entregables de documentación de un endpoint de la API LDCOM13_INTEGRATIONS (Dos Pinos) — el Swagger OpenAPI escrito a mano, la colección de Postman y la página de Confluence LD-xx — partiendo del código real (controller, DTOs, servicio, códigos de error), para que los tres digan lo mismo que el código. Usar siempre que se cree o cambie un endpoint LD-01…LD-10 (parámetro nuevo, filtro, campo, regla, código de error, cambio de contrato), cuando pidan "documentar el endpoint", "actualizar el swagger/postman/confluence", "armar el entregable" o "la documentación de LD-xx", o al cerrar un ticket de la API de integraciones que cambia el contrato, aunque no mencionen los tres archivos.
---

# Documentar un endpoint de LDCOM13_INTEGRATIONS

Cada endpoint que se entrega a Dos Pinos lleva tres documentos que tienen que decir **exactamente lo
mismo que el código**:

| Entregable | Dónde vive | Para quién |
|---|---|---|
| Swagger (OpenAPI 3.0.3, escrito a mano) | `docs/api2/<ENTREGABLE>/swagger/NN-<slug>.json` | Equipo técnico de Dos Pinos / Informatica |
| Colección de Postman | `docs/api2/<ENTREGABLE>/postman/LDCOM13 Integrations — <Nombre> LD-xx.postman_collection.json` | QA y Dos Pinos, para probar sin configurar nada |
| Página de Confluence `LD-xx <Nombre>` | Espacio `DP`, hija de "LDCOM: Interfaces" (id `316342273`) | Contrato funcional oficial |

El Swagger que genera la API (`AddSwaggerGen`) **no** es el entregable: no tiene descripciones ni
ejemplos. El entregable es el JSON escrito a mano.

Repo: `C:\FUENTES\DP\LDCOM13_INTEGRATIONS`. Colección Bruno del equipo (opcional, ver paso 6):
`C:\FUENTES\DP\Postman_LDCOM13_DOSPINOS`.

## Por qué existe este skill

Antes, cada cambio de contrato obligaba a revisar a mano los tres documentos y siempre quedaba algo
desalineado (un parámetro en Swagger pero no en Confluence, un código de error que ya no existe,
un `Requerido` mal marcado). La fuente de verdad es el **código**; los documentos se derivan de él y
se comparan contra él.

## Flujo

### 1. Ubicar el endpoint en el código

Leer `references/mapa-endpoints.md` para saber qué controller, DTO, servicio y página corresponden
al LD-xx. Del código sacar, sin suponer:

- **Ruta y método**: `[Route]` + `[HttpGet/Post/Put]` del controller.
- **Request**: propiedades del DTO de request (o query object en GET), con tipo, `[Required]`,
  `[MaxLength]`, `MaxElementLength`, defaults (`= true`, `= 100`) y si es nullable.
- **Response**: DTO de respuesta, incluidos `JsonIgnore(WhenWritingNull)` (campos que pueden no venir).
- **Reglas y validaciones**: el `Validate*` del servicio y cada `throw new BaseSourceException(...)`.
  Anotar código de error, condición que lo dispara y `statusCode` si lo fuerza.
- **Códigos de error y HTTP**: `src/Integration.Core/Domain/Exceptions/ApiErrorMessage.cs` tiene el
  mensaje y el status de cada `ApiErrorCode`. No inventar mensajes: copiarlos de ahí.
- **Resolución de catálogos**: qué campos pasan por `ResolveAsync`/`ResolveItemWithFallbackAsync`
  (CrossReference) y cuáles van directo a LDCOM. Eso decide si hace falta mapeo previo.

Si el cambio está en una rama sin commit, leer el working tree; si no, la rama del release.

### 2. Traer lo que ya está publicado

- Confluence: `scripts/confluence.ps1 -Accion Leer -PageId <id>` guarda el storage en
  `%TEMP%\cf\<id>.storage.xml` (UTF-8 correcto). Leer también la versión.
- Swagger y Postman: el más reciente de ese endpoint en `docs/api2/` (ver mapa).

### 3. Armar el delta y mostrarlo antes de escribir

Comparar código vs. cada documento y listar en una tabla: campo/regla/código, qué dice el código,
qué dice cada documento, acción. Mostrarle al usuario el delta **antes** de modificar archivos;
es el punto donde aparecen decisiones de negocio (p. ej. "el código rechaza X, Confluence dice que
lo acepta: ¿cuál vale?"). Nunca "corregir" el código para que calce con la documentación sin
preguntar.

### 4. Swagger

Seguir `references/swagger.md` (estructura, convenciones de texto, ejemplos, esquema de error,
seguridad Entra ID). Validar al final con `scripts/validar-entregable.ps1 -Swagger <archivo>`
(JSON válido, `$ref` resueltos, cada propiedad del DTO presente, códigos de error existentes).

### 5. Postman

Seguir `references/postman.md`: colección autocontenida (sin environment), carpeta
`00 · Autenticación`, una carpeta por endpoint con escenarios numerados y un `pm.test` por escenario.
Cada escenario nuevo del delta (filtro nuevo, error nuevo) lleva su request.

### 6. Bruno (si el usuario lo pide o el cambio es de contrato)

La colección del equipo en `Postman_LDCOM13_DOSPINOS/LogicalData API/<Carpeta>/LDxx *.yml`.
Agregar los parámetros nuevos **desactivados** (`disabled: true`), igual que los existentes.

### 7. Confluence (solo con aprobación explícita)

Seguir `references/confluence.md`: misma estructura de secciones que LD-10, fila nueva en
"Historial de cambios", tablas de campos con ✅/❌ en "Requerido", ejemplos en macro `code` json.
Generar el storage nuevo en `%TEMP%\cf\<id>.nuevo.xml`, mostrar el resumen de cambios y **publicar
solo cuando el usuario diga que sí** (`-Accion Publicar`). Confluence lo ve todo el equipo y el
cliente; un "dale" a una pregunta mixta no es permiso para publicar.

### 8. Cierre

Reportar: qué cambió en cada entregable, qué quedó pendiente de decisión, rutas de los archivos.
No commitear ni pushear sin pedido explícito.

## Reglas que no se negocian

- **El código manda.** Si un documento contradice el código, se reporta; no se adivina.
- **Texto en español, orientado a quien integra** (Dos Pinos), sin jerga interna de LDCOM salvo
  cuando ayuda a ubicar el dato (p. ej. "casilla «Venta Ecommerce» del artículo en Site Admin").
- **Sin narrativa de sesión** en los documentos ("antes fallaba…", "en la PR…"): eso va en el
  historial de cambios de Confluence, en una línea.
- **Valores reales de ejemplo**, coherentes entre los tres documentos (mismo artículo, misma
  sucursal). Preferir los de Staging/UAT que el usuario ya usó (`AV-RIO-FRIO`, `15000794`, etc.).
- **Encoding**: PowerShell 5.1 decodifica mal UTF-8 de Confluence; usar siempre el script.
- **Ediciones con tildes/emojis por script**: escribir el `.ps1` en el scratchpad y guardarlo **con
  BOM** antes de correrlo (sin BOM PS 5.1 lo lee como ANSI y `·`, `í`, `✅` no coinciden). No poner
  `\"\"` literal en la línea de comando de la herramienta (la bloquea como ruta): va dentro del script.
- **Editar el storage por fragmentos exactos**, con un script que falle si un fragmento no aparece
  exactamente una vez, y revisar al final que no quede texto que contradiga el cambio.
