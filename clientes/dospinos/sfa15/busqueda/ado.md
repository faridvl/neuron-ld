# Búsqueda ADO sobre SFA (org LD-Vacas, proyecto AV Retail Dos Pinos) - 2026-10-27, solo lectura

## Cobertura
- Work items buscados: SFA, Sysde, "validar crédito", "venta financiada", "plan de financiamiento", SFA15, SFA13, tipCredito, codAgencia, DP-04, CO-696-0024, "Autorización SFA".
  Con 0 resultados: Sysde, SFA15, SFA13, tipCredito, codAgencia, "venta financiada".
- Wiki "SFA": 0 resultados. Código "SFA15": 0. Código "Validar_Credito_SFA": solo /INTERFACE/FACTURACION/Facturacion/Frm_Facturacion.vb (repo LDCOM13_DOS_PINOS).
- No existe en ADO NINGÚN texto del contrato SFA15/13/10 (campos, indEstado, plazo, URLs, credenciales, ambientes, desembolso, reverso, idempotencia, idExterno, codAgencia, codUnidadCosto, tipCredito).
- Adjuntos: 1296 no trae adjuntos ni imágenes embebidas; 2222 y 2282 sin descripción, sin comentarios, sin adjuntos; los test cases 3271-3282 sin comentarios. No hay comentarios de Dos Pinos ni de Sysde en ningún ticket revisado.

## Tickets relevantes (qué trajo cada uno)
- US 1296 "07 Financiamiento | US-8 Facturación en Contingencia sin Validación del SFA" (Resolved, asignado Jirgort McCarty; hijos 2222, 2223, 2224, 2282; padre Feature 109 CO-696-0007). Descripción, AC y 4 comentarios (todos de Hans Araya: 2026-08-25, 2026-09-17, 2026-10-16, 2026-10-22; los dos últimos son cambios automáticos de estado).
  - Desc: "sin importar la causa — LDCOM caído, Dos Pinos caído, o el SFA mismo caído... el sistema permite seguir facturando a crédito o a contado, sin ejecutar la validación de límite de crédito ni de Tipos de Crédito".
  - AC: "no autoriza la transacción con el sistema externo de financiamiento, y guarda que la factura se creó sin validar el crédito"; indicador se imprime "debajo del indicador de COPIA"; al reconectar se transmite a la BD central conservando el indicador.
  - "El valor 'C' del indicador es irrelevante para LDCOM (aclarado por el PO)". Mismo indicador que talonarios (US-9).
  - Fuera de alcance: "El envío del indicador hacia Dos Pinos al sincronizar es del proyecto de integraciones".
  - Pendiente abierto: ¿imprimir el indicador en otro comprobante/reporte además del tiquete?
- Tasks 2222 "Validación de SFA en factura", 2223 (plan y plazo en PV_Preventa_Encabezado/Ticket_Encabezado, SP PV_Cerrar_Caja), 2224 (sync local->línea), 2282 "Permitir facturas de crédito en modo local": todas Ready to QA, Derek Mora. Sin descripción ni comentarios.
- Test suites 3131/3137/3269 "US-8 Facturación en Contingencia sin Validación del SFA" (Derek, In Progress).
- Features: 109 CO-696-0007 Planes de Financiamiento (Hans); 122 CO-696-0024 Integración Interfaces Transaccionales (hijos 207 API Auth Closed, 445 API Preventas Closed, 1536 "API: Endpoints DP" New, 1542 "API: Endpoints LD" Active, 1540 Removed; sin descripción de SFA); 283 CO-696-0013 Granel.
- US 1946 "25 Ruta | Cambio 2 Adelanto de Ruta" (autor Joseph Vega): "La definición completa de la integración con SFA se contempla en el proyecto CO-696-0024".
- US 1222 "Cambios en alcance" (Closed, Johnny Barrantes): comentario sobre sesión con Dos Pinos que "incluyeron flujos nuevos camuflados que era parte de la integración con SFA"; Hans aclaró que eso "nunca ha estado dentro del alcance"; debía ir a una oferta nueva.
- Test cases POS02 Clientes 3401-3405 (Yessenia Solano, Design, creados 2026-10-22): INT-CLI-14..18; 3402-3405 dicen "No ejecutable hoy: DP-04 no implementado".

## 1) Contrato SFA15/13/10
NO ENCONTRADO en ADO. Lo único son nombres internos de LDCOM, no contrato:
- 3273: "TSistemaFinanciamientoSFA.Validar_Credito autoriza siempre mientras no exista la integración con el SFA" (stub).
- 3280: "GetValidacionCreditoSFA devuelve Nothing en modo local y TDecisionValidacionCreditoSFA.Resolver lo trata como Sin_Validar".
- 3278: "Validar_Credito_SFA solo se invoca en el camino de Facturación (Frm_Facturacion.vb, línea 14764)".
- Marca en BD Factura_Encabezado.Factura_Validacion_Credito: 0 = no aplica, 1 = validado, 2 = sin validar (3270/3273/3271).
- Mensaje (3272): "No se pudo validar el crédito con el sistema de financiamiento. La factura se emitirá sin validar el crédito." + "Motivo: <texto del SFA>".
- Plazo: US-4 (1400): "n es el plazo en semanas"; "i es la tasa de interés anual dividida entre 52 semanas" (decisión 2026-09-16). Única unidad del plazo definida (lado LDCOM). 1392: plazos = conjunto discreto por plan; datos del plan vienen de la "interfaz externa" (LD-10 Tipos de crédito, tests 3546/3547).
- Ambientes/URLs/credenciales/errores/indEstado: nada. Solo mención genérica "ambiente QA, token JWT vigente (Get Token)" en test cases de la API LDCOM (no SFA).

## 2) Desembolso, validación sin desembolso, reverso, idempotencia, reintentos
NO ENCONTRADO sobre SFA. Lo cercano:
- 1296 AC3: en contingencia LDCOM "no autoriza la transacción con el sistema externo" => en línea sí hay una "autorización" (no define si desembolsa).
- 3402 (INT-CLI-15): "Facturar a crédito; LDCOM consulta en línea a SFA y SFA aprueba." -> "La factura se emite." Referencia "Autorización SFA (DP-04)"; DP-04 no implementado.
- 1277 (Removed, consolidado en US-3), preventa: "No se contempla: ... Reintentos automáticos o reprocesos si la interfaz no responde. Liberación automática de crédito por devoluciones o notas de crédito."
- 1407 US-6: "LDCOM no gestiona la liberación del saldo de crédito ni el reembolso del financiamiento — es responsabilidad del SFA."
- 1419 US-5 OBP: envío de facturas y NC al SFA "con su plan, y que las notas de crédito no se compensen allá, son del proyecto de interfaces (Feature 122)".
- 109 (history): "El envío del indicador de contingencia y del consecutivo hacia SFA y SAP es de otro proyecto de integración (Supuestos 13 y 14 de la oferta)".
- 1946: LDCOM "NO aprueba crédito ni puede modificar los límites definidos por SFA"; envía fecha de cobro (próximo domingo) a SFA por interfaces.
- Reverso/anulación/idempotencia: sin referencias.

## 3) Origen de codAgencia, codUnidadCosto, idExterno, cliente, tipCredito
NO ENCONTRADO. Solo: el plan (Plan_Financiamiento) llega por LD-10 (interfaz externa) con id, descripción, tasa, plazos, vigencia, estado, clasificación (1392). Cliente finca asociada a cliente padre (REA o no REA): validación de saldo ABIERTA, "requiere al cliente" (1398); bug 3626 "las fincas no lo están heredando" (plan del asociado; In Review, sin comentarios). El documento guarda plan, plazo y tasa en Ticket/Factura_Encabezado (2223, 3276). Nada sobre tipCredito = código externo.

## 4) Comportamiento del POS
- Contingencia (US-8, 1296): LDCOM, Dos Pinos o SFA caídos => se factura a crédito o contado sin validar límite ni Tipos de Crédito; marca 2; aviso; el tiquete lleva el indicador. No bloquea.
- Inconsistencia entre casos: 3272 "SFA que no autoriza: la factura sigue en contingencia sin validar el límite" => un RECHAZO también va a contingencia (no bloquea), con "Motivo: <texto del SFA>". En cambio 3403 (INT-CLI-16): "SFA deniega" -> "No se emite; mensaje de denegación visible." (bloquea). 3404 (INT-CLI-17) SFA caído/timeout: "Comportamiento definido (bloquear o contingencia), con mensaje claro; no se pierde la venta ni queda factura a medias" (sin definir).
- 3271 [Q16]: "no está definido cómo se detecta la caída del SFA (timeout, reintentos)". 3272: "hoy no existe simulador del SFA ni integración; hace falta un doble de prueba".
- Sin conexión a LDCOM (modo local): 1398 AC "Se puede facturar documentos con Tipos de Crédito estando sin conexión"; 1392: preventas no funcionan sin conexión, solo se factura offline una preventa ya creada; 3280: modo local => aviso de contingencia, no se valida el límite, marca 2; 3279 [Q20] duda: la US-3 dice que los saldos se sincronizan para contingencia pero con contingencia SFA el bloque de saldo ya no se ejecuta. 2341: modo local de LDCOM != contingencia del SFA.
- Preventa: 3278: "hoy la preventa no pasa por la validación del SFA y la factura se valida al facturarla"; pendiente: "¿la preventa debe consultar al SFA o basta con la validación al facturar?".
- Devoluciones: 1407 estándar total o parcial; LDCOM no libera saldo (SFA). 3233: "LDCOM no libera ni reembolsa saldo". Notas de crédito: 1419 y 1277 arriba.
- Un solo punto de validación de saldo: al "Imprimir" (1398, decisión 2026-09-14, "no reabrir").
- Venta porcentual/granel (1500, 1501): PO 2026-10-09 decidió que LDCOM no consulta a SFA, control interno (cambio respecto de la oferta).
- Contado: no consulta SFA, marca 0 (3270). Crédito sin Tipo de Crédito: valida límite como antes, marca 0 (3275).

## 5) Casos de prueba (todos en Design; US-8 "Ejecuta: Derek" Mora; los INT-* asignados a Yessenia Solano)
- 3270 contado: no consulta SFA, marca 0.
- 3271 SFA no responde con LDCOM en línea: aviso, emite, marca 2. Requiere simulador SFA (FIN-823). Duda Q16.
- 3272 SFA no autoriza: aviso + "Motivo: <texto del SFA>", no se detiene, marca 2. Requiere simulador SFA (FIN-822). Duda Q16.
- 3273 crédito con Tipo de Crédito y SFA autoriza: marca 1, sin aviso; "ejecutable hoy" porque el stub autoriza siempre (FIN-821).
- 3274 Imprimir abortado no arrastra marca al siguiente doc (0) (FIN-826).
- 3275 crédito sin Tipo de Crédito: valida como antes, marca 0 (FIN-825).
- 3276 PV_Cerrar_Caja conserva marca/plan/plazo/tasa en Factura_Encabezado (FIN-827).
- 3277 indicador impreso debajo de COPIA, original y reimpresión; Manual; ninguna de las 4 tareas lo cubre; ningún TPrint* lo referencia (FIN-828).
- 3278 preventa no consulta SFA ni se marca (definición pendiente) (FIN-829).
- 3279 caja local saldo insuficiente se emite igual [Q20]; 3280 caja local sin conexión, crédito con plan sin validar, marca 2 (FIN-830); 3281 sync a central con marca 2, sin duplicar (FIN-832); 3282 crédito sin Tipo de Crédito en local como antes (FIN-833).
- POS02 Clientes: 3401 sync de clientes no pisa el crédito de SFA; 3402 aprobado; 3403 denegado; 3404 sin respuesta; 3405 monto exacto contra el disponible (disponible, +0.01, -0.01); 3402-3405 "No ejecutable hoy: DP-04 no implementado".
- LD-10 Tipos de crédito: 3546 modo asíncrono (202, received=10); 3547 cola asíncrona con reinicio ("Validar diseño").
- Relacionados: 3198, 3178, 3259, 3261, 3262, 3579 "Punta a punta | Financiamiento".

## 6) Decisiones de usuarios y contradicciones con lo que asumimos
Decisiones (Hans Araya / PO / equipo):
- Hans, 2026-09-17 (1296): US-8 es concepto nuevo, paralelo; no confundir con contingencia de LDCOM.
- PO: valor 'C' irrelevante, solo importa si el crédito fue validado.
- Equipo 2026-09-14: un solo punto de validación al Imprimir. 2026-09-16: devoluciones estándar; plazo en semanas, tasa/52.
- PO 2026-10-09: sin consulta a SFA en granel/venta porcentual.

Contradicciones/hallazgos vs. lo asumido:
1. "Rechazo funcional bloquea": en ADO NO está definido; 3272 dice lo contrario (rechazo => sigue en contingencia, marca 2, mensaje con Motivo del SFA) y 3403 dice que bloquea. 3404 deja "bloquear o contingencia" abierto. La US-8 (1296) habla solo de "no se puede validar" (caídas), no de rechazos.
2. "Timeout/conectividad/seguridad a contingencia": consistente con 1296 (caídas => contingencia), pero la detección (timeout, reintentos) está marcada indefinida (3271 Q16); 1277 excluye reintentos.
3. "Semanas x 7": ADO solo define plazo en semanas (n semanas, tasa/52); nada sobre días ni x7.
4. Empresa CR01, usuario INTEGRACIONSFA, numLinea 0, tipCredito = código externo del plan, codAgencia/codUnidadCosto/idExterno: sin mención en ADO.
5. 1296 AC3: en contingencia "no autoriza la transacción"; si SFA15 desembolsa, un desembolso ya hecho no se revierte desde el POS: reverso/anulación no definido y 1407 deja el reembolso al SFA.
6. Preventa: hoy sin consulta a SFA (3278); sin decisión de si debe consultar.
7. Feature 283 aún lista "integración con SFA" para granel, pero 1500/1501 (PO 2026-10-09) la descartaron.
8. Indicador impreso en tiquete (3277) no implementado ni cubierto por tareas.
9. La integración real con SFA (DP-04, Feature 122 / CO-696-0024) figura "no implementada"; las US de Financiamiento (CO-696-0007) tratan al SFA como externo a LDCOM.
No hay en ADO respuestas de Sysde/Dos Pinos sobre el contrato: hay que pedirlo fuera (oferta CO-696-0007 Supuestos 1-5, 8, 13, 14, citados pero no incluidos en ADO; Confluence; correo).
