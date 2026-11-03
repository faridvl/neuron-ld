# Interfaces salientes LDCOM -> Dos Pinos: contratos reales, Bruno y diseño

Lo que respondió el ambiente de desarrollo de Dos Pinos al probar POS-11, POS-19, POS-24 y POS-26 en Bruno, y cómo
se decidió construirlas. Complementa [integrar-endpoint-pos-dos-pinos.md](integrar-endpoint-pos-dos-pinos.md)
(arquitectura LDCOM -> WCF -> NEGOCIO -> SDK -> Runner, sacada de POS-10).

## 1. Dos canales distintos en Informatica

| Canal | Host | Auth | Interfaces |
|---|---|---|---|
| CAI (procesos BPEL) | `https://usw3-cai.dm-us.informaticacloud.com/active-bpel/rt/<proceso>` | Basic | POS-10 (`p_SFA15_Autorizacion_Venta_Final`), POS-11 (`p_SFA13_NotasCredito`), POS-12 (`p_POS12_ReplicarVentas`) |
| API Gateway AGV | `https://usw3-gw.dm-us.informaticacloud.com/devapi.dospinos.com/agv/v1/<proceso>` | Bearer, token OAuth2 client_credentials de `https://dm-us.informaticacloud.com/authz-service/oauth/token` | POS-19 (`p_POS19_movimientos_de_cajas`), POS-24 (`p_POS24_PedidosRomana`), POS-26 (`p_POS26_TrasladoRomana`) |

- **Cada servicio CAI tiene su propio usuario Basic.** El de SFA15 (`integrador_agvretail_dev`) da 403 en SFA13; SFA13
  usa `integrador_sfa_dev`. Un 403 con "not authorized to access service" = credencial de otro servicio, no clave mala.
- **El SFA de pruebas se cae de noche** (visto a las 00:30): SFA15 responde `SFA15-C01 No existe comunicación con el
  servicio externo` y SFA13 `HTTP_504 Error técnico al obtener el token de SFA - Connection reset`, tras ~10 s. Las
  validaciones de formato siguen respondiendo porque las hace Informatica antes de llamar al SFA.
- Los documentos dicen "Basic" y "OAuth2/JWT" a la vez para el gateway: lo que funciona es Bearer.
- Hoy solo hay URLs de desarrollo para todas.

## 2. Lo que el contrato escrito no decía (y el servicio sí)

| Interfaz | Hallazgo real |
|---|---|
| POS-19 | `IDITZ` debe ser `POS19` (sin guion; no `FSD-19`). `CSAGR` máx. **14** (columna `LOG_INTERFACE_ENC.CONS_AGRUPA_TRANS`; el xlsx dice 20, el error es `ORA-12899`). Faltante de obligatorio = HTTP 400 del gateway `{"error":{"details":{"missing":["USER"]}}}`. Todo lo estructuralmente válido = 200 `Out_status 200 "Interface recibida satisfactoriamente"`, aunque el LIBRO_CAJA no exista, el importe sea 0/negativo o la fecha esté mal: **la validación de negocio es posterior, en SAP**. Reenvío con el mismo GUID+NROEJ+CSAGR+REFERENCIA = 500 `dato de control ya existe`; con mismo GUID pero otro CSAGR/REFERENCIA lo acepta de nuevo. |
| POS-24 / POS-26 | **No** usan el bloque de control de POS-19: body `Encabezado` (8 campos) + `Detalle[]`. Éxito = 200 `{"mensaje":"ROM03 recibido correctamente"}` (POS-24) o `ROM01` (POS-26). **Rechazo de validación = HTTP 200** con `{"mensaje":"Validacion: <campo> es requerido. "}`: el éxito se decide por el texto, no por el status. **Aceptan el reenvío idéntico** (Romana registra el pedido dos veces): la idempotencia es nuestra. Cantidad 0/negativa, material inexistente y `CANTIDAD_REG_INTEGRAR` incoherente se aceptan. Fecha inexistente o textos largos pueden dar 500 `Error tecnico al enviar ROMxx a ROMANA` (no se sabe si quedó registrado). POS-26: MATERIAL máx. 18, DESCRIPCION máx. 70, fechas `YYYYMMDD`. Dirección de POS-26: LDCOM -> Romana (aviso del traslado que entró por LD-06/LD-11). |
| POS-11 (SFA13) | `codEmpresa` = constante `001` (el xlsx dice `CR01`), `indOrigen` = `AVR`, `numReferencia` máx. **15**, `monDevolucion` máx. 14 enteros y 2 decimales, `fecSolicitud` `YYYY-MM-DD`. Sin usuario/clave en el cuerpo (a diferencia de SFA15). Rechazo = 200 con `indEstado R`, `desIndEstadoTransaccion "RECHAZADO VALIDACION"` y `observaciones` con todos los errores juntos. |

Regla: **antes de codificar una interfaz, correrla en Bruno contra dev**; el contrato escrito de Dos Pinos se equivocó
en largos, constantes y en cómo responde el rechazo en todas las que se probaron.

## 3. Bruno (colección `Postman_LDCOM13_DOSPINOS`)

- Carpeta por interfaz en `Dos Pinos API/` con `00 Obtener token`, `1 Validaciones`, `2 Casos por evento`, `3 Escenarios
  POS` (datos reales de Staging, la llave en `docs:` para repetirlos desde el POS). Las respuestas reales quedan como
  `examples:` en cada request.
- CLI: `@usebruno/cli` necesita Node 20+ (con Node 18 falla con `crypto.subtle`). Se corre desde la raíz de la colección
  (`You can run only at the root of a collection`) y el token **primero**, listándolo antes que las carpetas (el orden
  por `seq` lo deja al final). Ejemplo:
  `node bru.js run "<carpeta>/00 Obtener token.yml" "<carpeta>/1 Validaciones" ... --env "UAT Dos Pinos" --reporter-json out.json`
- **Las variables `secret: true` no están en el `.yml`** (Bruno las guarda en la app): el CLI las recibe con
  `--env-var nombre=valor`, tomadas de un `.env` fuera de git, sin imprimirlas. El JSON del reporte trae la cabecera
  Authorization y los cuerpos con clave: enmascarar antes de guardar y borrar el crudo.
- Los tests de validación deben fallar ante 401/403 ("llegó al servicio"); si no, un error de autenticación pasa como
  "rechazo esperado".
- Escenarios que crean datos reales (créditos SFA, pedidos en Romana) se marcan REAL en el nombre y se guardan detrás
  de una variable de URL propia (`...BaseUrlExitosas`, `...BaseUrlReversas`) que se vacía para bloquearlos.

## 4. Diseño acordado para las salientes (decisiones del desarrollador)

**Un solo método en LDCOM: `Notificar(hecho, documento)`.**

- **LDCOM no conoce POS-xx ni a Dos Pinos.** Avisa hechos propios con un enum fijo (`HechoLdcom`: CierreCaja,
  MovimientoCaja, PreventaCreada, TrasladoCreado, Venta, NotaCredito; viaja como `CIERRE_CAJA`...).
- **El documento va completo en el `Notificar`**, en el modelo propio de LDCOM (`DocumentoLdcom` y uno por hecho:
  sucursal, caja, montos, líneas y los `Codigo_Interfaz` que LDCOM ya tiene). Su `Referencia` es la llave única y
  estable: notificar dos veces el mismo documento no duplica. Los modelos viven en el SDK (contrato compartido).
- **Integrations no lee la BD de LDCOM.** Arma cada mensaje con el documento + parámetros del evento
  (`IntegrationEventParameter`: IDITZ, MANDANTE, sociedad) + mapeos (`CrossReference`).
- **Un hecho puede alimentar varias interfaces:** tabla `IntegrationEventFact (IntegrationEventId, FactName)`.
  `IntegrationEvent.Name` es único por integración, así que NO se usa como nombre del hecho: cada interfaz conserva su
  propio evento (nombre, intentos, monitor, código POS-xx en `EventCode`).
- **Lo único propio de cada interfaz** es un builder (`IOutboundNotificationBuilder`): `Applies` (su regla, p. ej.
  POS-24 solo preventas de tipo romana, comparado contra un parámetro del evento), `BuildAsync` (arma el mensaje) y
  `Classify` (Sent / AlreadySent / Rejected / Transient). Se registran solos por reflexión. Si el hecho ya existe en
  LDCOM, una interfaz nueva no toca LDCOM.
- **Envío:** `Notificar` vuelve en cuanto Integrations guardó el pendiente (`OutboundNotification`, con la foto del
  documento) y **nunca lanza**. El envío sale al instante en segundo plano (el cajero no espera al Runner ni a Dos
  Pinos); un job reintenta solo lo pendiente. Los reintentos reenvían el mismo mensaje armado en el primer intento.
- **Reintentos e intervalo salen de la tabla del evento** (`IntegrationEvent.RetryMax` y `BackoffSeconds`), igual que
  en datos maestros. `RetryMax` es el total de intentos: 1 = sin reintentos; 0 no se acepta (Admin y API, rango 1-10).
- Sin reintento ciego donde el destino no es idempotente: SFA (mueve crédito) fijo en 1; POS-24/26 aceptan duplicados,
  así que un timeout o un 500 de Romana no se reintenta sin saber si llegó. POS-19 sí se puede reintentar: el duplicado
  vuelve como "dato de control ya existe" y se toma como enviado (`AlreadySent`).
- **Dónde queda el rastro:** todo en Integrations (`OutboundNotification` + `Events` + Monitor 360, y correo si falla
  el monitor). **LDCOM no guarda nada** salvo un error al comunicarse con Integrations (`Recibido = false`), que va al
  log de NEGOCIO con el hecho y la referencia; **nunca detiene ni revierte** la venta, el cierre o la preventa.
- **Excepción:** POS-10 (y POS-11) siguen síncronos porque el POS necesita la respuesta del SFA para facturar.
- Nombres genéricos: lo común (Notificar, pendientes, despacho, suscripción) no lleva nombre de interfaz ni de
  cliente; solo los builders llevan POS19, POS24...
