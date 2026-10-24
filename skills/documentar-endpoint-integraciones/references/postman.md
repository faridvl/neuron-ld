# Convenciones de la colección de Postman entregable

Modelo: `docs/api2/TERCER_ENTREGABLE_DP_LD10/postman/LDCOM13 Integrations — Tipos de credito LD-10.postman_collection.json`
(schema Postman v2.1.0). La forma más segura de armar una colección nueva es **copiar ese archivo** y
reemplazar solo la carpeta del endpoint, la descripción y los datos de prueba: así el token, los
scripts y la autenticación quedan idénticos y probados.

## Partes fijas (copiar del modelo, no reescribir)

- `auth`: bearer con `{{accessToken}}`.
- `variable`: `accessToken` (vacía) y `tokenExpiresAt` (`0`). Ninguna otra.
- `event` de colección:
  - `prerequest`: obtiene y cachea el token de Entra ID (tenant/client de Staging quemados,
    `CLIENT_SECRET = 'PENDIENTE_CLIENT_SECRET'`). Nunca escribir un secreto real.
  - `test`: verifica que no sea `401` y loguea `code`/`message` de los errores.
- Carpeta `00 · Autenticación` con el request de token (`noauth`, `client_secret` pendiente).

## `info`

- `name`: `LDCOM13 Integrations — <Nombre> LD-xx` (o varios LD si la entrega junta varios).
- `description` (markdown), en este orden:
  1. Lista de endpoints incluidos: `- **LD-xx** · \`MÉTODO ruta\` — qué hace`.
  2. `## Cómo está armada`: sin environment, todo escrito en cada request; la única excepción es
     el `clientSecret`.
  3. `## Ambiente`: `baseUrl` = `https://dospinosdemo.ldcloud.pro/INTEGRATIONS-API`.
  4. `## Los escenarios`: tabla `| # | Escenario | Respuesta esperada |`.
  5. `## Datos de prueba`: de dónde salen los valores (`docs/datos-prueba-staging.md`), prefijo
     `ZZ_TEST_LDxx_` para lo que se crea, y el SQL para limpiarlo si el endpoint escribe.
  6. `## Sobre el token`.

## Carpeta del endpoint

`NN · <Nombre> (LD-xx)`, un request por escenario, nombre `N · <escenario> (<HTTP esperado>)`.
Por cada request:

- URL completa escrita (no `{{baseUrl}}`): `raw`, `protocol`, `host`, `path` y `query` separados.
  Parámetros opcionales que no usa el escenario van en `query` con `"disabled": true`, así quien
  prueba ve que existen.
- Header `Content-Type: application/json` y body `raw` + `options.raw.language = json` cuando hay body.
- `description`: qué prueba el escenario y por qué responde lo que responde (1–3 párrafos).
- `event` `test` con uno o más `pm.test` que verifiquen el HTTP y lo que distingue al escenario
  (código de error exacto, que el filtro realmente filtró, cantidad de elementos, etc.).

## Escenarios mínimos

Para cada cambio del delta, al menos:
- El caso feliz con el parámetro nuevo usado.
- El caso feliz sin el parámetro (comportamiento anterior intacto).
- Cada código de error nuevo, con el body/query mínimo que lo dispara.
- Combinaciones que pueden sorprender (filtro + paginación, filtro sin resultados → lista vacía,
  no "todos").

## Validar

`scripts/validar-entregable.ps1 -Postman <archivo>` revisa que sea JSON v2.1 válido, que no haya
secretos reales, que cada request tenga test y que todas las URLs apunten al mismo `baseUrl`.
