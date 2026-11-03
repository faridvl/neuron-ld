# Integrar un endpoint POS-xx de Dos Pinos (LDCOM ↔ Integrations ↔ CIH/Informatica)

Guía sacada de POS-10 (SFA15, autorización de venta financiada: tickets 3699 Integrations y 3700 LDCOM). Sirve para
POS-12 (SALE_NOTIFICATION, notificación de ventas) y para los POS que vengan de devoluciones y cierres de caja.

## 1. Arquitectura que no se negocia

- **LDCOM nunca habla HTTP con Integrations.** Camino: POS (`Frm_Facturacion`) → WCF (`NEGOCIO/ServiciosWCF`,
  p. ej. `WCFCatalogoAux`) → NEGOCIO (DLL) → `Integration.SDK` (`IntegrationBridge`) → `Integration.Runner.exe` como
  proceso (JSON por stdin) → HTTP solo hacia Dos Pinos (Informatica/CIH). La API de Integrations no participa.
- **NEGOCIO lee el config del proceso que lo hospeda.** En el Admin lee el Web.config del Admin; cuando el POS llama
  por WCF lee el Web.config de **ServiciosWCF**. Ese sitio necesita las mismas claves que el Admin:
  `IntegrationStage`, `IntegrationTenant` (appSettings) y la cadena `LD.AccesoDatos.My.MySettings.LDDPINTEGRATIONS`
  (`NEGOCIO/CONTROL NEGOCIO/TCatalogo.vb`). Sin el tenant no hay contexto de cliente.
- **Pipeline:** el paso "Parche Web.config — integraciones" (`pipelines/scripts/releases/sync-integration-settings.ps1`)
  existía solo con `-SiteDir "$(IIS_PATH_SITEADMIN)"`. Para que el POS integre hay que repetirlo con
  `-SiteDir "$(IIS_PATH_WCF)"` en cada CD (testing, staging, staging-rc, uat-production; este último lo tiene en dos lugares).
- **Runner en el bin del WCF:** el `.targets` del paquete SDK copia `Integration.Runner.exe` solo al proyecto que
  referencia el paquete. Verificar que llegue al sitio ServiciosWCF.
- **Timeouts encadenados:** el timeout del binding POS→WCF tiene que ser mayor que el timeout de Integrations hacia
  Dos Pinos (SFA15: 35 s) más el arranque del Runner. Si no, el POS corta antes de la respuesta.
- **Multicliente:** el evento se configura por tenant (`IntegrationEvent`, seed `Database/seeds/04__webhooks.sql`). Un
  cliente sin el evento recibe `NotConfigured`; el POS lo trata como contingencia.

## 2. Contrato hacia LDCOM: lo mínimo

LDCOM solo necesita un resultado simple: **Autorizado / Rechazado (bloquea) / No disponible (contingencia)** + mensaje.
Clasificar las respuestas de Dos Pinos es trabajo de Integrations (`Sfa15ResponseClassifier`). La auditoría completa
(request enmascarado, respuesta, estado) vive en Integrations (`Events` y la tabla propia del intento, p. ej.
`CreditValidationAttempt` por `ExternalReference`). Si además se quiere imprimir algo en ticket o reporte, se guarda en
LDCOM lo mínimo (ver §4).

## 3. Lo que aprendimos probando contra el ambiente real de Dos Pinos

- **Probar antes de preguntar.** Con Bruno (colección `Postman_LDCOM13_DOSPINOS`, ambiente `UAT Dos Pinos`) se
  resolvieron casi todas las dudas: códigos válidos, campos vacíos, montos, duplicados. Ordenar las carpetas por riesgo:
  "dudas (no crean nada)" y "exitosas (crean datos reales; solo con OK)", con doble candado en la URL de las segundas.
- **Envenenar las pruebas de dudas** con un dato que seguro falla (p. ej. unidad de costo `99999999`) para que no
  creen registros si la duda resulta válida. Un id "obviamente falso" (`000000000`) puede existir en Dos Pinos.
- **Auth de Informatica:** cabecera Basic (401/403 si falta o no tiene permiso sobre ese proceso) + a veces
  usuario/clave en el cuerpo. Un 403 "not authorized to access service" es permiso del usuario sobre ese proceso
  puntual, no credenciales malas.
- **Formatos de respuesta que hay que clasificar:** éxito; error funcional con HTTP 200 y `HttpStatus "400"` en el
  cuerpo; HTTP 500 con `{"error":{code,detail,message}}`; errores en inglés de la primera validación; rechazo de
  negocio como HTTP 200 con estado `R` y sin código de error. No fiarse del status HTTP.
- **Dos Pinos no protege contra duplicados** (el mismo idExterno dos veces se aprobó dos veces). La guardia de
  idempotencia va en Integrations: misma referencia + mismos datos → devolver el resultado guardado sin llamar; datos
  distintos → rechazar; intento en curso o incierto → `DuplicateAttempt`.
- **Mapeos:** se envían los códigos de LDCOM que Dos Pinos reconoce (Cliente_Id/Codigo_Interfaz del asociado, finca
  como unidad de costo, vacía si no hay finca); empresa `001`, no el código de sociedad SAP. Validar cada mapeo con
  una llamada real.
- **Credenciales:** nunca en git. Si hacen falta temporales en código, constantes vacías en un archivo excluido
  (`.git/info/exclude`) que se borra antes del primer commit.
- **Simulador:** el simulador CIH (repo privado `simulador-cih-dospinos`) reproduce las respuestas por rangos de
  monto; Integrations solo acepta http hacia localhost. Sirve para E2E y para probar el POS sin tocar Dos Pinos.

## 4. Tablas y procesos de mayor riesgo (devoluciones y cierres de caja)

Si un POS necesita guardar datos en el documento, el camino toca lo más delicado de LDCOM:

- **Ticket_Encabezado / Factura_Encabezado** son casi gemelas (~132 columnas comunes). La caja inserta primero en su
  **base local** (`TFacturacionLocal.Insertar_Factura_Encabezado`), sincroniza al servidor
  (`WCFSincLocalToServer.Sincr_Factura` → `TFactura.Insertar_Encabezado` → `Ticket_Encabezado`) y al **cerrar la caja**
  `PV_Cerrar_Caja` traslada Ticket → Factura.
- **Columnas nuevas:** con `NOT NULL DEFAULT` no rompen nada en BD. No hay triggers, schemabinding, `SELECT *` ni
  INSERT sin lista de columnas sobre estas tablas; se auditó en Docker y Testing. **El riesgo es de omisión:** los SPs
  que copian el encabezado con lista explícita no llevan la columna nueva hasta que se les agrega. Además de
  `PV_Cerrar_Caja`: `Pv_Factura_Rehacer`, `Fact_Verifica_Factura_Apdo_Cancelado`, `INV_Despacho_SubPed_Aplicar`,
  `Inv_Devolucion_Pedido`, `Inv_Guia_Trans_Liquidar`. Varios no están versionados en `routines/`: sacar la versión
  de la base y compararla entre ambientes.
- **Base local de la caja:** la columna se agrega con un script registrado en `LDControlDBLocalAutomatico`
  (Emp/Suc/Caja 0 = todas; idempotente por contenido del script; patrón de la task 2223). Si el código nuevo usa la
  columna y la caja todavía no aplicó el script, el INSERT falla y la caja no factura: probar ese orden.
- **Al terminar, verificar en la BD** (no solo en pantalla): que la sincronización llegue con los valores, que
  `Msg_Message` y `Cola_Local_Asyncronas` se procesen sin errores nuevos (compararlo con una corrida sin el cambio),
  y que el cierre de caja copie las columnas nuevas sin alterar el resto.
- `PV_Cerrar_Caja` y cualquier SP reescrito se arman sobre la última versión de **cada rama destino** y se aplican con
  `migrate`, nunca con sqlcmd.

## 5. Monitor Integral y correo

Hoy solo la sincronización de colas reporta al Monitor Integral (`ProcessMonitorReporter`, con correo de respaldo
`SendFallbackEmailAsync` si el monitor no responde). POS-10 y POS-12 no reportan. Si un POS nuevo debe reportar: hacerlo
después de responder al POS, con su propio timeout y sin bloquear nunca la venta.

## 6. Pruebas mínimas antes de dar un POS por terminado

1. Integrations: unitarias del clasificador y del mapeo (cada campo con su prueba) + E2E con el Runner real contra
   el simulador (cada formato de respuesta, 401/403, timeout, evento inactivo, reintento con la misma referencia).
2. LDCOM: compilar la rama en su worktree y correr Facturacion.Tests y CATALOGOS.Tests.
3. POS real automatizado (ver `automatizar-pos-recorridos.md`) contra Docker + Integrations local:
   cada resultado, contingencia, venta de contado, facturación local, sincronización, cierre de caja y
   devolución/NC si aplica, con evidencia en BD.
4. La prueba final de cada resultado va **desde el POS contra el endpoint real de pruebas de Informática**, sin
   redirigir el evento al simulador. El simulador sirve para desarrollar y para forzar casos que el real no da
   (caída, timeout); Bruno solo valida datos y no cuenta como cobertura. Cada autorización real crea un crédito sin
   reverso: montos pequeños (CRC 19,55).

## 7. Tropiezos que costaron horas en POS-10

- **Certificado del SQL de Integrations:** el Runner usa Microsoft.Data.SqlClient, que cifra por defecto. Sin
  `TrustServerCertificate=True` en la cadena que se le pasa, toda validación cae a "no disponible" y parece una
  contingencia normal. Ver `runner-integraciones-cifra-por-defecto.md`.
- **SDK preliminar → oficial:** se desarrolla con un paquete `-preview` del feed y, antes del PR, se cambia en
  NEGOCIO, ServiciosWCF y el Admin a la versión que publique el release de Testing de Integrations (en POS-10,
  `1.5.2.7597`). Restaurar con `restaurar-paquetes-feed-ado.md`, recompilar y **repetir una venta real** con el
  paquete oficial antes de darlo por cerrado.
- **El texto que ve el cajero es fijo de LDCOM** ("Favor comunicarse con Servicios Financieros"); el motivo real
  del rechazo solo queda en `CreditValidationAttempt`. Soporte lo busca ahí.
- **Escenarios de datos:** finca ajena (S04) se arma reasignando en Docker un cliente-finca a otro asociado, con
  script de preparación y de reversa; asociado sin finca usa un cliente que es el propio asociado.

## 8. Entregables en el repo de LDCOM

Mismo formato que FE AVD (`documentos/15 - PRDs/<nn> - <tema>/`): `PRD.md`, `Manual-<tema>.html` con la estructura
y el CSS del manual de FE, `qa/QA.md` con veredicto por prueba y la sección "Evidencias por archivo" (tablas
`| # | Caso | Doc | Resultado | Hora | Evidencia |`), `qa/trazabilidad.md` (documento, solicitud, crédito,
referencia, intento, eventos) y `qa/evidencias/` con archivos sueltos `caja-NN-…`, `pdf-NN-…`, `admin-NN-…`,
`log-NN-…`. Nada de zips. Revisar cada captura y log antes de subirlos: sin claves, tokens ni cadenas de conexión.
