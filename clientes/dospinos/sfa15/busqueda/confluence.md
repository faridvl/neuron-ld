# Confluence (logicaldata.atlassian.net, espacio DP) sobre SFA15 y venta financiada

Solo lectura via REST con ATLASSIAN_BASIC_AUTH. Cuerpos descargados en `...\busqueda\pg\<id>.txt`.

## Resultado principal
Confluence NO contiene el contrato de SFA15. Las busquedas "SFA15", "SFA13", "SFA10", "Sysde", "BD Consultores", "indEstado", "codUnidadCosto", "tipCredito", "plazoCredito", "INTEGRACIONSFA", "codAgencia" dan 0 resultados. "SFA" a secas aparece en ~15 paginas, siempre como sistema externo de financiamiento de Dos Pinos, sin nombres de servicio (SFA10/13/15). "Informatica" solo aparece en POS-12 (ventas, no financiamiento).
Las paginas son propuestas de alcance de LDCOM y CDC; el contrato lo debe dar Dos Pinos: "Dos Pinos sera responsable de definir ... el diseno del endpoint, la estructura y contratos de datos, la documentacion tecnica" (279281665).
Adjuntos y comentarios: casi todos son imagenes (.png/.jpg) que NO se abrieron. Comentarios: 2 en total (134250511 "Este se elimino de la oferta a enviar"; 13959169 sobre reportes), irrelevantes a SFA.

## Paginas relevantes (espacio DP)
- 279281665 Transaccionales: Propuesta Solucion CO-696-0024 Integracion Interfaces de Ventas (la mas importante)
- 134250511 Datos Maestros CO-696-0021 (catalogos, contingencia, plan de financiamiento)
- 13762565 "4. Tipos de Credito (Financiamiento)" y 247103489 "[CDC] 8. Financiamiento" (mismo contenido)
- 314474498 Flujos de integracion; 313950209 Integracion LDCOM Dos Pinos; 316342273 LDCOM: Interfaces; 388988929 Dos Pinos: Interfaces (vacia)
- 13959169 "1. Formas de Pago"; 333283329 "14. Adelanto de Ruta"; 30113833 "12. Obras en proceso"; 441810945 LD-10 Crear tipos de credito; 421494788 LD-GENERAL (auth/errores del API LD entrante)
- Base de datos "Interfaces AV Retail" (19922945): sin cuerpo accesible por API.

## 1) Contrato SFA15
NO ENCONTRADO: nada de SFA15-F01, indEstado, HTTP status ni timeouts de la autorizacion. Datos indirectos:
- Mapeo: DP-04 "Autorizacion de venta para asociados (SFA)" = interfaz POS-10 "Autorizacion de la venta financiada" = flujo FL-07 (279281665). Se supone que DP-04 envuelve SFA15, pero la pagina no lo dice.
- Plazo en SEMANAS: "Plazo: Numero de semanas" (134250511 ~l.397); tasa anual "dividirla entre 52 semanas" (13762565 l.9); rango "1-52 semanas" (l.200); tabla de amortizacion "plazo en semanas" (l.372). Cuota semanal.
- Datos a enviar a SFA al facturar (134250511 ~l.386-400): ID Factura (numero unico), Cliente (codigo de asociado), Plan (codigo del plan en SFA), Tasa, Plazo (semanas).
- "Los detalles de la tasa y rangos de plazo vienen del SFA, el plazo se elige en LDCOM y los calculos se realizan en LDCOM" (13762565 l.143). Banca/No banca viene del SFA.
- Tabla de reintentos/backoff por interfaz (codigo POS-xx) existe en 134250511 (~l.240-260) para sincronizaciones; sin fila visible de POS-10.

## 2) Ambientes
NO ENCONTRADO para SFA/DP-04. Solo la tabla de AVD (30081065) con "Usuario/Password: Secreto. Solicitar a ..." y la URL de INTEGRATIONS de LD en LD-GENERAL (http://testing-iis/BETA/DOS_PINOS_STAGING/INTEGRATIONS; auth Entra ID client credentials, para el API LD entrante). Para llamadas a Dos Pinos, la URL se configura en el mantenimiento de APIs de LDCOM (279281665); no hay URL en el texto.

## 3) Comportamiento
- DP-04: "solicitar al API Dos Pinos autorizacion para realizar una venta financiada (SFA)"; periodicidad "Tiempo real"; disparador "Antes de imprimir una factura de credito con plan de financiamiento". FL-07 paso 4(A) autorizada -> permite la factura; 4(B) "recibe el rechazo, lo muestra al cajero y no permite realizar la factura". Confirma que un rechazo bloquea.
- Desembolso: NO se dice. Tampoco validacion sin desembolso, reverso/anulacion, idempotencia ni que pasa si la factura no se completa. Solo: "Las ventas financiadas se reflejan como creditos separados en SFA y SIAG" (13762565 l.112); POS-11 "Notas de credito de ventas financiadas ... parte del flujo SFA (directo)".
- Contingencia: "En contingencia se podrian enviar datos al SFA/Dos Pinos obsoletos ... Se deberia bloquear la venta? R/ Sin bloquear nada; enviar un indicador de que la factura se hizo en contingencia" (134250511 l.253-254); indicador pedido: "que sea un C" (l.409); se abordaria en una "sesion de contingencia" (sin pagina).
- Reintentos: el API LDCOM hace "reintentos automaticos y reporte de eventos al Monitor Integral 360" (279281665 l.23); por endpoint se parametriza maximo de reintentos y backoff; "En caso de indisponibilidad temporal ... LDCOM aplicara las politicas de reintentos configuradas por interfaz. Los eventos pendientes seran reenviados".
- "LDCOM NO aprueba credito ni puede modificar los limites definidos por SFA" (333283329 l.137); "Si el SFA lo permite, se puede facturar" (134250511 l.149).

## 4) Origen de codAgencia, codUnidadCosto, idExterno, codCliente, tipCredito, numLinea, plazoCredito
NO ENCONTRADO como tales. Lo mas cercano: Cliente = codigo de asociado; Plan = codigo del plan en SFA; ID Factura = numero unico de la factura; plazo = semanas elegidas en LDCOM. Catalogo de homologacion de IDs externo/LDCOM: 134250511 Cambio 3. Nada sobre almacen->agencia ni finca->unidad de costo. LD-10 (441810945) y DP-05/POS-37 tratan el catalogo de tipos de credito.

## 5) Monitor Integral
Si en general: "Todos los eventos enviados al API Dos Pinos seran monitoreados y registrados en el Monitor Integral 360, tanto en escenarios exitosos como fallidos segun la configuracion" (279281665); FL-07/DP-04 cierra con el patron "registra el resultado del evento y lo notifica al Monitor 360". Politica configurable por interfaz; retencion 90 dias. Ninguna pagina nombra SFA15.

## 6) Escenarios de prueba, QA, mocks
NO ENCONTRADO. Los informes QA (457736193, 437223427, etc.) no mencionan financiamiento/SFA/POS-10. Sin mocks ni simuladores.

## 7) Contradicciones o matices con lo asumido
- Rechazo bloquea la venta: CONFIRMADO (FL-07 4B).
- Timeout/conectividad -> contingencia: respaldado en general (sin bloquear + indicador C), pero la politica detallada quedo para otra sesion; seguridad (401/403) no se menciona.
- Semanas x 7: Confluence solo habla de semanas (1-52, cuota semanal); nada de dias. La conversion a dias es supuesto nuestro.
- Un solo intento sin reintentos: POSIBLE CONTRADICCION; 0024 define reintentos y backoff configurables por endpoint y reenvio de pendientes, sin aclarar si aplica a DP-04 sincrono.
- Empresa CR01, usuario INTEGRACIONSFA, numLinea 0, tipCredito = codigo externo del plan: sin mencion. "Plan: Codigo del plan en SFA" apoya lo del codigo externo.
- Matiz: LDCOM solo simula cuotas; los calculos reales los hace SFA y las diferencias se revisan administrativamente (13762565 l.508).
