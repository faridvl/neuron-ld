# SFA15 / POS10: búsqueda local y correo (solo lectura, 2026-10-27)

Fuentes principales (carpeta `C:\Users\fvillacis\Desktop\02_Documentacion_DosPinos\ultimos endpoints\POS10 y POS11\`):
- `SFA15 Autorización de la venta financiada.xlsx` (hoja "Formato Informatica", responsable Fabiola Delgado)
- `SFA15_Autorización de la venta financiada.docx` (diseño)
- `Documento Autorizacion_Venta_Final.pdf` (BD Consultores, v1.0, 02/09/2026)
- SFA13: `SFA13 Notas de crédito y devoluciones.xlsx`, `.docx`, `Documento Notas de CréditoSFA.pdf`
Mapa: POS10 = SFA15 (autorización venta financiada), POS11 = SFA13 (notas de crédito). Fuente: correo de Diego Arias 14/09/2026 "Documentación para LDCOM interfases POS10 Y POS11": "POS10 = SFA15 / POS11 = SFA13".

## 1) Contrato SFA15

Endpoint Informatica CAI (xlsx H14): `https://usw3-cai.dm-us.informaticacloud.com/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final` (Swagger: mismo URL + `?swagger`). Proceso `FINANZAS_SFA\02_Process\p_SFA15_Autorizacion_Venta_Final`. Sincrónico tiempo real, frecuencia "Diaria", volumen vacío (xlsx C8, C10).
Destino SFA (xlsx J14/J16): `http://20.3.142.207:44304/interface-api/v2/solicitud-creditos/insertar-solicitud` (POST /insertar-solicitud) y POST `/insertar-credito-pr`.

Envoltorio del request (PDF p.11 y p.20): `{"Datos_Entrada": {...}, "Usuario": "...", "Contraseña": "..."}`. Usuario y contraseña van en el BODY (PDF p.20 "Request: Usuario y contraseña para obtención de Bearer Token"). El docx dice "Autenticación: Básica entre informática y LDCOM"; el PDF de entrega muestra credenciales en el body. Informatica obtiene luego un Bearer Token hacia SFA (PDF p.8 "Autenticación mediante usuario y contraseña para la obtención del Bearer Token").

Campos de `Datos_Entrada` (xlsx filas 22-40; tipo/longitud/requerido):
| Campo | Tipo | Long. | Requerido | Nota del xlsx |
|---|---|---|---|---|
| codEmpresa | Varchar | 5 | Si | 'Valor constante "CR01"' (M22) |
| codAgencia | Varchar | 5 | Si | "Codigo de Almacen" |
| codTipoId | Varchar | 5 | No | "Codigo de tipo de identificacion CEDPF, Requerido si no hay CodCliente" |
| numId | Varchar | 30 | No | idem (cédula) |
| codCliente | Varchar | 15 | Si (H26) | "Requerido si no viene la identificacion" (contradice el "Si") |
| fecSolicitud | Datetime | - | Si | ejemplo "2026-08-17" |
| nomAutorizado | Varchar | 100 | Si | |
| codTipoIdAu / numIdAu | Varchar | 5 / 30 | No | |
| indUsaLinea | Varchar | 1 | (vacío) | "S = Usa línea, N = No usa línea" |
| numLinea | Numerico | 8 | (vacío) | "Requerido si se requiere validar disponible" |
| idExterno | Varchar | 15 | No | "Numero de Factura Retail" |
| codUnidadCosto | Varchar | 25 | Si | "Numero de Finca" |
| numConvenio | Varchar | 20 | No | "Numero de Convenio de pago" |
| plazoCredito | Numerico | 5 | Si | "Plazo en dias" (C36/M36) |
| tipCredito | Numerico | 3 | Si | "Tipo de Credito (plan de financiamiento)" |
| monSolicitud | Numerico | 16.2 | Si | "Monto de credito" |
| observaciones | Varchar | 1000 | No | |
| codUsuario | Varchar | 15 | Si | |
Segundo paso "Insertar Credito PR" (xlsx filas 42-45): codEmpresa ("CR01", Si), codUsuario (Si), indAccion (Numerico 2, Si) con nota 'M44: "1 = Insertar, 2 = Insertar y Aprobar, 3 = Insertar, Aprobar y Desembolsar / Valor constante "3""', numSolicitud (Numerico 8, Si).

Ejemplo request del PDF (p.11): codEmpresa "001", codAgencia "001", codTipoId "CEDJU", numId "3102012066", codCliente "", fecSolicitud "2026-08-17", indUsaLinea "S", numLinea 0, idExterno "CR-217657652-1", codUnidadCosto "2563", plazoCredito 24, tipCredito 201, monSolicitud 5000.00, observaciones "SOLIC. CRED API", codUsuario "INTEGRACIONSFA"; "Usuario": "SYSDE", "Contraseña": "123" (valor de ejemplo; no usar).

Respuesta exitosa (PDF p.11): `{"Respuesta":{"numSolicitud":147,"numCredito":"25093","indEstado":"A","inconsistencia":null,"monDisponible":170125083.62},"Mensaje":"Crédito insertado y aplicado satisfactoriamente.","HttpStatus":"200"}`. HttpStatus viene como string dentro del body.
Respuesta de error funcional (PDF p.12): mismos campos de Respuesta en null + `"CodigoError":"SFA15-F01","TipoError":"Funcional","Mensaje":"La identificación no se encuentra relacionada a un cliente válido.","DetalleTransaccion":[... tres mensajes ...],"HttpStatus":"400"`.

Unidades: el xlsx y el PDF dicen plazo EN DIAS ("Plazo en dias"; ejemplo 24). No dice nada de semanas.
indEstado: solo se ve "A" (aprobado/aplicado). No hay catálogo en los documentos (en SFA13 sí: A=APLICADO, R=RECHAZADO; ver abajo).
Códigos de error documentados: solo `SFA15-F01` (funcional; PDF pruebas #4, #5, #6). Para el error técnico dice "HTTP_400" (request vacío `{}`, JSON inválido). Clasificaciones (PDF p.12): Funcional, Técnico (JSON/HTTP 4xx/5xx), Seguridad, Timeout, Conectividad, pero NO publica códigos ni HTTP para Seguridad/Timeout/Conectividad. Tabla de pruebas (p.13): Timeout = "Error Timeout controlado"; error técnico = "Técnico HTTP 400/500 según respuesta". (Los códigos S01/TO1/C01/T01 del simulador no aparecen en ningún documento: son inventados por el simulador, README.md:140-142.)
Timeouts: ningún documento da un valor en segundos. Prueba #8: "Reducir temporalmente el tiempo configurado" => "Error Timeout controlado". El "corte de 30 s de Informatica" que usamos (README del simulador, DECISIONES.md #5, harness integration-credit-validation.md) NO está en ningún documento local ni correo: es supuesto.
Validaciones de Informatica antes de llamar a SFA (PDF p.10): `{}` => HTTP_400 técnico; debe venir codCliente o codTipoId+numId; indUsaLinea solo S o N; numLinea "cuyo valor permitido en el flujo actual es 0" (p.16); errores => SFA15-F01.
Casos de prueba del xlsx: el xlsx no trae casos de prueba, solo el formato de mapeo; los 8 casos están en el PDF p.13 (éxito, request vacío, identificación cliente, indUsaLinea, numLinea, error funcional, error técnico "InactiveUser/UserNotAssociated o JSON incompatible", timeout). Las capturas (imágenes) no se pudieron leer como texto.

## 2) Ambientes / URLs / credenciales

- URL única documentada: `https://usw3-cai.dm-us.informaticacloud.com/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final`. No distingue QA/producción. Postman Bruno (`C:\FUENTES\DP\Postman_LDCOM13_DOSPINOS\environments\*.yml`, variable `salesReplicationBaseUrl`) usa el mismo `https://usw3-cai.dm-us.informaticacloud.com/active-bpel/rt` en DEV, QA, QA Dos Pinos, UAT Dos Pinos, STAGING, etc. (no hay entorno SFA aparte ni ejemplos de respuesta SFA).
- Backend SFA interno: `http://20.3.142.207:44304/interface-api/v2/...` (IP privada, HTTP; xlsx J14).
- SFA13 PDF p.11 muestra la autenticación del proceso hacia Informatica: Basic Auth con usuario `integrador_sfa_dev@dospinos.com` "y contraseña respectiva". La contraseña de ese usuario existe en claro en `C:\Users\fvillacis\Desktop\02_Documentacion_DosPinos\02. Configuración\Publicaciones.postman_collection.json` (líneas ~19-22, auth basic de "Ejecutar publicacion_prueba"); NO copiada. Ese usuario es "integrador_sfa_dev" pero la colección es de CIH Publications, no de SFA15.
- Para SFA15 el PDF no entrega credenciales; en el ejemplo "Usuario":"SYSDE","Contraseña":"123" (ejemplo ilustrativo). En correos no hay credenciales SFA15 ni URL de QA/producción entregadas. Conclusión: NO hay evidencia de que ya se hayan entregado credenciales ni URLs de pruebas/prod para SFA15 (ESTADO.md de sfa15 también: "sin credenciales ni URL de pruebas").

## 3) Desembolso, validación sin desembolso, reverso, idempotencia, reintentos

- SFA15 desembolsa: el proceso encadena insertar-solicitud + insertar-credito-pr "para completar la inserción, aprobación y desembolso del crédito" (PDF p.5/p.9) e indAccion constante 3 = "Insertar, Aprobar y Desembolsar" (xlsx M44). La respuesta dice "Crédito insertado y aplicado satisfactoriamente".
- Validación sin desembolso: no existe en los documentos. indAccion 1 y 2 existen en SFA (insertar / insertar y aprobar) pero el proceso fija "3". No hay endpoint de solo consulta de disponible en SFA15. (SFA10/otros no cubren esto.)
- Reverso/anulación: no hay endpoint de reverso en SFA15. El flujo de anulación es SFA13 (POS11): "notas de crédito, devoluciones y anulaciones de ventas financiadas" (SFA13 docx 1.), body con numReferencia, monDevolucion, indOrigen "AVR". Respuesta SFA13: `indEstado` A/R, `tipTransaccion` P/NA ("PARCIAL"/"NO APLICA"), `monDisponibleLinea`; rechazo "60791 - El crédito relacionado a la factura o documento de referencia presenta devolución total." (SFA13 PDF p.12).
- Idempotencia/reintentos: "El proceso no realiza reprocesos ni reintentos automáticos" (SFA15 PDF p.9, p.10 punto 11, p.13). Los riesgos del docx (8) dicen "Reintentos exponenciales e idempotencia en Integration Hub" pero eso es plantilla común, contradice el PDF. Evidencia de duplicado en SFA13: "Rechazo debido a que ya se cuenta con registro asociado. Regla de negocio, no se puede aplicar la misma solicitud en la misma fecha." (SFA13 PDF p.22). Para SFA15 no hay prueba de reenvío; por analogía idExterno repetido el mismo día probablemente da rechazo funcional (no confirmado).

## 4) Origen de datos (qué dice la documentación)

- codAgencia: "Codigo de Almacen" (xlsx B23). Longitud 5. Ejemplo "001". No dice cómo se traduce desde LDCOM (sucursal). Sin acuerdo escrito.
- codUnidadCosto: "Numero de Finca" (B34), Varchar 25, requerido. Ejemplo "2563"; error de ejemplo "La unidad de costo 2563 no existe para el cliente 4000010." (PDF p.12). Coincide con finca del asociado en LDCOM.
- idExterno: "Numero de Factura Retail" (B33), Varchar 15, NO requerido (H33 "No"). Ejemplo "CR-217657652-1" (14 caracteres). En SFA13 el equivalente `numReferencia` = "Numero de Factura Retail" ejemplo "CR-217657003-1"; el registro asociado en pruebas de Dos Pinos fue "CR-217657652-13".
- codCliente: "Codigo del Cliente" Varchar 15, requerido si no viene identificación; ejemplos "4000004", "4000010" (códigos de asociado). Alternativa codTipoId (CEDPF/CEDJU) + numId.
- tipCredito: "Tipo de Credito (plan de financiamiento)" Numerico 3 (B37); ejemplo 201. No dice "código externo del plan"; el POS37/DP-05 es el catálogo de tipos de crédito (maestro) (CO-696-0024_Integracion_Interfaces_Ventas.md línea 81, 471-486).
- numLinea: Numerico 8, "Requerido si se requiere validar disponible"; PDF p.16: "valor permitido en el flujo actual es 0". Ejemplo con indUsaLinea "S" y numLinea 0.
- numConvenio, codTipoIdAu, numIdAu: vacíos en el ejemplo.

## 5) Monitor Integral

NO. PDF SFA15 p.7: "Nota sobre el Monitor Integral: La presente interfaz opera de manera sincrónica y en tiempo real, por lo que no contempla integración ni envío de información hacia el Monitor Integral (ni para transacciones exitosas ni para el registro y manejo de excepciones)". Igual en SFA13 PDF p.9. Nota: el docx de diseño SFA15 (4. Observabilidad) dice "Obligatoria, implementada con Monitor Integral" => contradicción docx vs PDF; manda el PDF de construcción (posterior, más específico). El SFA13 PDF p.11 describe un paso 4 de notificar al Monitor Integral (codEC SFA13): también se contradice con su propia nota p.9.

## 6) Fechas, responsables, acuerdos de pruebas

Correos (Outlook, últimos 120 días; solo 6 hilos humanos relevantes):
- 08/09/2026 13:58, Johnny Barrantes de la O, "RE: Datos maestros - LDCOM": lista pendientes de Dos Pinos: "Endpoint DP-04: autorización de venta para asociados (SFA) / POS10 Autorización de venta financiada / POS11 Notas de crédito de venta financiada / 14/09/2026" y "Endpoint DP-05: catálogo de tipos de crédito / POS37 Tipos de crédito / 14/09/2026" (fecha estimada de entrega de Dos Pinos, pedida en sesión del martes 08/09).
- 14/09/2026 08:19, Diego Esteban Arias Sanchez (Dos Pinos), "Documentación para LDCOM interfases POS10 Y POS11": adjunta xlsx/docx de SFA13 y SFA15 y PDFs "Documento construcción (SFA13) Notas de Crédito_SFA.pdf" y "(SFA15)_Autorizacion_Venta_Final.pdf". Cc Fabiola Delgado, Karla Monge. El texto solo dice "POS10 = SFA15 / POS11 = SFA13". Respuesta Johnny Barrantes 14/09 16:15 "Confirmamos el recibido de la documentación." Sin más acuerdos.
- 15/10/2026 17:09, Diego Arias (reenvío de Maria Fernanda Angulo Blanco, Sysde, 15/10 17:05): invitación "Sysde & Dos Pinos - Proyecto SFA - Prueba SFA10 Interfaz de planes de financiamiento (Tipo de credito)", viernes 16/10/2026 11:30-12:00, Teams. Asistentes: M. F. Angulo (Sysde), lalfaro (Sysde), Farid Villacis, Hans Araya, Diego Arias, Suamy Portillo, Fabiola Delgado (calendario de Outlook 16/10 11:30, confirma). Sin cuerpo con contenido ni resultado de la prueba. SFA10 = interfaz de planes de financiamiento (tipos de crédito), NO es el SFA15. No hay minuta ni resultado en el correo.
- 30/09/2026 Read AI "Daily: Dos Pinos": "Carlos informó que iniciaría tareas de financiamiento." (único dato; resumen parcial).
- Fechas en SFA13 PDF: prueba integral Dos Pinos 02/09/2026 con codUsuario "INTEGRACIONSFA" (SFA13 PDF p.20-21); documentos de construcción SFA15 y SFA13 con fecha 02/09/2026; xlsx "Fecha Solicitud" 46248 (serial Excel = 2026-09-02).
- Responsable en xlsx: "Fabiola Delgado" (Dos Pinos). BD Consultores prepara los PDFs. Evaluación Agente IA Dos Pinos en SFA15 PDF p.21 sin fecha (imagen).
- No hay correo que fije fecha de pruebas de SFA15 con Dos Pinos/BD Consultores/Sysde, ni entrega de ambiente QA. No se encontraron correos de BD Consultores.
- Otros hits eran ruido (ADO, CAS, Confluence). Ticket 1993/LD-10 (tipos de crédito) es el catálogo de planes en LDCOM, no SFA15.

## 7) Contradicciones / confirmaciones con lo que asumimos hoy

(Supuestos tomados de `C:\FUENTES\DP\LDCOM13_INTEGRATIONS-sfa15\.claude\harnesses\integration\integration-credit-validation.md` y `C:\Users\fvillacis\ClaudeLocalSession\sfa15\DECISIONES.md`.)
1. Rechazo funcional bloquea; timeout/conectividad/seguridad a contingencia: la documentación no dice qué hace LDCOM; solo da clasificaciones. DP-04 del análisis (CO-696-0024_Integracion_Interfaces_Ventas.md:463-468): rechazo "no permite realizar la factura" (confirma rechazo bloquea); no define comportamiento ante timeout/no disponible (ANALISIS_CO-696-0024_Ventas_v2.md:228-229 lo deja como pregunta abierta "if DP is unreachable, does LDCOM allow or block"). Riesgo de fondo: SFA15 DESEMBOLSA (indAccion 3) y no hay reverso; con timeout el crédito pudo quedar aplicado y la contingencia puede facturar sin que SFA lo sepa o duplicar (ya registrado como `PossiblyApplied`).
2. Semanas x 7: el contrato dice "Plazo en dias" (xlsx C36/M36); la conversión x 7 es nuestra. No hay documento que la confirme ni la contradiga; ejemplo plazoCredito 24 con tipCredito 201 no permite deducirla. Pendiente confirmar con Dos Pinos.
3. Empresa CR01: xlsx dice "Valor constante CR01" (B22, M22, B42), pero TODOS los ejemplos de SFA15 y SFA13 usan "001" y SFA13 PDF p.17 valida "algo diferente a "001" en codEmpresa" => rechazo. Contradicción real: el PDF construido valida "001" (SFA13); en SFA15 la prueba #6 cambia CodEmpresa por uno inexistente y falla con SFA15-F01. Probable que la constante real sea "001" y CR01 sea un error del xlsx. Confirmar.
4. Usuario INTEGRACIONSFA: aparece como codUsuario en el ejemplo SFA15 ("INTEGRACIONSFA") y en la prueba integral SFA13 (p.21 "se utiliza codUsuario como INTEGRACIONSFA"); en el ejemplo SFA13 usa "SYSDE". Parcialmente respaldado; no es una confirmación formal para SFA15.
5. numLinea 0: respaldado (PDF p.16 "valor permitido en el flujo actual es 0"), pero el xlsx dice requerido solo "si se requiere validar disponible" y el ejemplo manda indUsaLinea "S" con numLinea 0.
6. tipCredito = código externo del plan: xlsx lo llama "Tipo de Credito (plan de financiamiento)", Numerico 3 (1..999); ejemplo 201. Consistente con el POS37 catálogo de Dos Pinos (DP-05). Confirmado en espíritu; no hay documento de la relación exacta.
7. Un solo intento: respaldado (PDF p.9 "No se implementan reprocesos ni reintentos automáticos"); el docx de diseño habla de "reintentos exponenciales e idempotencia" (plantilla genérica) y se contradice.
8. Timeout de 30 s de Informatica: no documentado en nada local ni en correos; es supuesto nuestro (35 s por defecto, mínimo 31).
9. Códigos de error: solo SFA15-F01 está documentado; nuestro clasificador/simulador usa S01/TO1/C01/T01 inventados. Un error de seguridad real (InactiveUser/UserNotAssociated) llega como "Técnico" por PDF p.13/p.18 ("cambia el usuario por uno no existente y da un error técnico"), no como "Seguridad": tratarlo como Unavailable/Technical es consistente.
10. HTTP status: éxito "200", funcional "400", técnico "400/500 según respuesta", timeout controlado (SFA13: code 500). HttpStatus va como string en el body; el body trae HttpStatus también en error.
11. Monitor Integral: SFA15 no lo usa (supuesto nuestro coincide; docx contradice).
12. Autenticación: nuestro diseño envía Usuario/Contraseña en el body (coincide con el PDF); el docx dice "Básica".

## No encontrado
- Credenciales, URL de QA y producción de SFA15 (solo la URL única de Informatica); fechas de pruebas SFA15; correos de BD Consultores; qué hace LDCOM ante timeout (decisión de negocio sin documento); catálogo de indEstado de SFA15; reverso/anulación para SFA15; validación sin desembolso; resultado de la prueba SFA10 del 16/10; contenido de las imágenes (mapeo, capturas, "Evaluación Agente IA") de los PDF/docx.
- SimuladorCIH-DosPinos, LDCOM13_DOS_PINOS\DOC y .claude, y docs del repo sfa15: solo contienen nuestro propio trabajo (simulador, harness) o nada de SFA; no aportan contrato nuevo.

## Archivos auxiliares de esta búsqueda
- Cuerpos de correos leídos (solo en memoria al leer, volcados texto aquí): `C:\Users\fvillacis\ClaudeLocalSession\sfa15\busqueda\outlook\cuerpos.txt`
- Lista de 69 hits: `...\outlook\hits.csv`; calendario: `...\outlook\cal.txt`
