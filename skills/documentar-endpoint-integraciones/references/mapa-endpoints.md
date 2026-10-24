# Mapa de endpoints LDCOM13_INTEGRATIONS

Rutas relativas a `C:\FUENTES\DP\LDCOM13_INTEGRATIONS`. Verificado contra `release/3.1.0` (2026-10-08).
Si algo no calza (archivo movido, endpoint nuevo), confirmar con
`git grep -n -E '\[Route\(|\[Http(Get|Post|Put)' -- src/Integration.Api/Controllers` y actualizar
esta tabla.

| LD | Endpoint | Controller | DTO (src/Integration.Core/Domain/Dtos) | Servicio (src/Integration.Core/Services) | Confluence (id) |
|---|---|---|---|---|---|
| LD-01 | `POST /api/preorders` | `CreatePreorder.cs` | `PreorderDto.cs` (`CreatePreorderRequest`) | `Preorder/PreorderService.cs` | 344195073 |
| LD-02 | `PUT /api/preorders/{preorderId}` | `CreatePreorder.cs` | `UpdatePreorderDto.cs`, `PreorderSnapshotDto.cs` | `Preorder/PreorderService.cs` | 349569028 |
| LD-03 | `POST /api/customers/account-balance` | `AccountBalanceController.cs` | `AccountBalanceDto.cs` | `AccountBalance/AccountBalanceService.cs` | 366280705 |
| LD-04 | `GET /api/items/prices` | `ItemsController.cs` | `ItemPriceDtos.cs` | `Items/ItemPriceService.cs` | 370016257 |
| LD-05 | `GET /api/items/stock` | `ItemsController.cs` | `ItemStockDtos.cs` | `Items/ItemStockService.cs` | 376242208 |
| LD-06 | `POST /api/inventory/transfers` | `InventoryTransfersController.cs` | `InventoryTransferDto.cs` | `InventoryTransfers/InventoryTransferService.cs` | 351404033 |
| LD-07 | `PUT /api/inventory/transfers/{transferId}` | `InventoryTransfersController.cs` | `InventoryTransferDto.cs` | `InventoryTransfers/InventoryTransferService.cs` | 365428738 |
| LD-08 | `POST /api/purchase-orders` | `PurchaseOrdersController.cs` | `PurchaseOrderDto.cs` | `PurchaseOrders/PurchaseOrderService.cs` | 364249089 |
| LD-09 | `GET /api/inventory/movements` | `InventoryMovementsController.cs` | `InventoryMovementDtos.cs` | `InventoryMovements/InventoryMovementService.cs` | 376242177 |
| LD-10 | `POST /api/credit-types` | `CreditTypesController.cs` | `CreditTypeDto.cs` | `CreditTypes/CreditTypeService.cs` | 441810945 |

Otras páginas de Confluence del mismo árbol:
- `421494788` — LD-GENERAL Autenticación y manejo de errores (envelope de error, 401/403, Entra ID).
- `364380164` — Campos excluidos por endpoint.

Repositorio LDCOM (Gateway → NEGOCIO): `src/Integration.Gateway/Repositories/LD/<Area>/Ldcom*Repository.cs`
y `LdcomLibraryWrapper.cs` (qué método de NEGOCIO llama cada operación).

Códigos de error: `src/Integration.Core/Domain/Exceptions/ApiErrorMessage.cs` (mensaje + HTTP status por
`ApiErrorCode`). Catálogos: `src/Integration.Core/Domain/Constants/CatalogName.cs`.

## Último entregable conocido por endpoint (docs/api2)

| LD | Swagger | Postman |
|---|---|---|
| LD-01 | `ENTREGA-SWAGGER-ENDPOINTS/01-crear-preventa.json` | no hay de entregable; ver `docs/testing/*/` |
| LD-02 | `CUARTO_ENTREGABLE_DP_LD02/swagger/01-editar-preventa.json` | `CUARTO_ENTREGABLE_DP_LD02/postman/LDCOM13 Integrations — Editar preventa LD-02.postman_collection.json` |
| LD-03 | `ENTREGA-SWAGGER-ENDPOINTS/03-ajustar-saldo-cliente.json` | no hay de entregable; ver `docs/testing/*/` |
| LD-04 | `ENTREGA-SWAGGER-ENDPOINTS-V2/01-catalogo-precios.json` | `SEGUNDO_ENTREGABLE_DP_LD04_LD_05_LD09/postman/LDCOM13 Integrations — Catálogos LD-04 - LD-05 - LD-09.postman_collection.json` |
| LD-05 | `ENTREGA-SWAGGER-ENDPOINTS-V2/02-catalogo-inventario.json` | idem LD-04 |
| LD-06 | `ENTREGA-SWAGGER-ENDPOINTS/04-crear-traslado.json` | no hay de entregable |
| LD-07 | `ENTREGA-SWAGGER-ENDPOINTS/05-modificar-traslado.json` | no hay de entregable |
| LD-08 | `ENTREGA-SWAGGER-ENDPOINTS/06-crear-orden-compra.json` | no hay de entregable |
| LD-09 | `ENTREGA-SWAGGER-ENDPOINTS-V2/03-catalogo-movimientos.json` | idem LD-04 |
| LD-10 | `TERCER_ENTREGABLE_DP_LD10/swagger/01-tipos-credito.json` | `TERCER_ENTREGABLE_DP_LD10/postman/LDCOM13 Integrations — Tipos de credito LD-10.postman_collection.json` |

`docs/api/POS-*.json` son la generación anterior (por código POS de Dos Pinos); no usarlos como base.

## Dónde dejar un entregable nuevo

Carpeta nueva por entrega: `docs/api2/<N>_ENTREGABLE_DP_<LDs>/` con `swagger/` y `postman/`
(p. ej. `QUINTO_ENTREGABLE_DP_LD04_LD05_LD08/`). Preguntar el nombre si no es obvio. Se copia el
último swagger del endpoint y se modifica; no se edita el de una entrega ya enviada.

## Bruno (colección de trabajo del equipo)

`C:\FUENTES\DP\Postman_LDCOM13_DOSPINOS\LogicalData API\` — carpetas `Preorders`, `AccountBalance`,
`Items` (LD04, LD05), `Inventario` (LD06, LD07, LD09), `PurchaseOrders` (LD08), `CreditTypes` (LD10).
Environments en `environments\*.yml` (QA Dos Pinos, UAT Dos Pinos…). Es un repo git aparte.
