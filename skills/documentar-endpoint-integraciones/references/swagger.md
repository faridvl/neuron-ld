# Convenciones del Swagger entregable (OpenAPI 3.0.3)

Modelo de referencia: `docs/api2/TERCER_ENTREGABLE_DP_LD10/swagger/01-tipos-credito.json`. Ante la
duda, imitarlo.

## Estructura

```
openapi: "3.0.3"
info:
  title: "<Nombre> · LD-xx"                 # p. ej. "Catálogo de precios · LD-04"
  version: "1.0.0"                          # subir minor si cambia el contrato (1.1.0)
  description: <markdown largo, ver abajo>
servers: [{ url: "https://dospinosdemo.ldcloud.pro/INTEGRATIONS-API", description: "Demo" }]
security: [{ EntraIdClientCredentials: [] }]
tags: [{ name: "LD-xx · <Nombre>" }]
paths: { "<ruta>": { "<método>": { tags, operationId, summary, description, parameters, requestBody, responses } } }
components:
  securitySchemes: EntraIdClientCredentials   # copiar tal cual del modelo (tenant/audiencia de Staging)
  schemas: <Request>, <items/hijos>, <Response>, ErrorResponse, ...
```

## `info.description` (markdown)

Empieza con `**Interfaz Dos Pinos:** <nombre de la interfaz POS-xx> (Dos Pinos → Retail)` y un
párrafo de qué hace. Luego secciones `##`, en este orden y solo las que apliquen:

1. `## Cómo funciona` — reglas principales, idempotencia, qué es llave.
2. `## Contrato de la respuesta` — tabla `| Código | Cuándo | Qué trae |` con cada HTTP posible.
3. `## Filtros` / `## Modo asíncrono` — lo específico del endpoint.
4. `## Validación de campos` — máximos, rangos, combinaciones inválidas, con el código de error.
5. `## Fuera de alcance` — lista con negritas.

## Parámetros y propiedades

- `description` explica **qué significa para quien integra**, no el nombre técnico. Incluir el
  default y el efecto de omitirlo.
- Tomar `maxLength`, `minimum/maximum`, `enum`, `default`, `required` **del código** (atributos del
  DTO y validaciones del servicio). Si el servicio valida algo que el DTO no declara (p. ej. rango
  1–6), ponerlo igual en el schema (`minimum`/`maximum`) y en la descripción con el código de error.
- Listas en query (`List<string>`/`List<int>`): `schema: { type: array, items: {...} }`,
  `style: form`, `explode: false` (se mandan separadas por coma: `priceIndex=1,3`). Verificar en el
  controller cómo las recibe; si es `[FromQuery] List<T>` con binder por defecto, ASP.NET acepta
  `?x=1&x=3` — documentar el formato que realmente funciona y probarlo.
- Enums en string (`B2C`, `ALL`) con `enum` y `default`.
- Fechas: `format: date-time`, ejemplo con `Z`.
- `example` en cada propiedad y `example`/`examples` en requestBody y responses, con valores
  reales coherentes entre sí.

## Respuestas

- Un bloque por cada HTTP que el endpoint realmente puede devolver (mirar `BaseSourceException`
  + `ApiErrorMessage.cs`). Si varios códigos de error comparten HTTP, usar `examples` con un ejemplo
  nombrado por caso (`itemNoEncontrado`, `indiceInvalido`), cada uno con `summary`.
- Errores usan `#/components/schemas/ErrorResponse` (copiar del modelo). El `message` del ejemplo
  es el de `ApiErrorMessage.cs`, literal.
- Si un campo de respuesta puede no venir (`JsonIgnore WhenWritingNull`), decirlo en su descripción.

## Al terminar

`scripts/validar-entregable.ps1 -Swagger <archivo> -Dto <archivo.cs>` y corregir lo que reporte.
