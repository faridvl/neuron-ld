# SFA15: lo que dicen las fuentes y lo que hay que preguntar (2026-10-27)

Informes completos en `sfa15\busqueda\` (`ado.md`, `confluence.md`, `local-y-correo.md`). Contrato: PDF `Documento Autorizacion_Venta_Final` (BD Consultores v1.0, 02/09/2026) y xlsx de SFA15.

## Lo que está confirmado por escrito
- URL única de Informatica (sin QA/PROD separados): `https://usw3-cai.dm-us.informaticacloud.com/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final`. Credenciales `Usuario`/`Contraseña` en el body.
- **Desembolsa:** `indAccion` constante 3 = Insertar, Aprobar y Desembolsar (xlsx línea 84; PDF "inserción, aprobación y desembolso"). No hay validación sin desembolso ni reverso en SFA15.
- **Sin reintentos:** "No se implementan reprocesos ni reintentos automáticos" (PDF).
- **Plazo en días** (xlsx línea 76: "Plazo en dias"). Confluence y ADO hablan de semanas (tasa anual / 52).
- **Rechazo bloquea:** Confluence CO-696-0024 paso 4B ("no permite realizar la factura") y ADO caso 3403. Lo contradice el caso 3272 (sigue en contingencia).
- **Monitor Integral:** el PDF dice que SFA15 no lo contempla; Confluence cierra el flujo con "notifica al Monitor 360" sin nombrar SFA15. Lo decide Farid.
- Origen de campos en el contrato: codAgencia = código de almacén; codUnidadCosto = número de finca; idExterno = número de factura Retail (15, no requerido); tipCredito = tipo de crédito numérico de 3 (ej. 201); numLinea = 0 en el flujo actual (PDF p.16); codCliente = código de asociado o codTipoId + numId.

## Preguntas para Dos Pinos / BD Consultores / Sysde
1. **Ambiente y credenciales (PRIORIDAD 1):** el usuario de integración que tenemos (integrador_agvretail_dev@dospinos.com, el de POS-12 y datos maestros) se autentica en Informatica pero responde **403 "not authorized to access service .../p_SFA15_Autorizacion_Venta_Final"** (probado 2026-10-28 desde Bruno). ¿Le dan permiso sobre ese proceso o nos pasan otro usuario? Además el `Usuario`/`Contraseña` del cuerpo. ¿Esa URL es de pruebas o de producción, y desembolsa créditos reales? (No lo sabemos.)
2. **codEmpresa:** RESUELTO con el PDF (pág. 17): "CR01" responde "La empresa CR01 no existe en el sistema". Es "001"; la constante del xlsx está mal. Solo avisarles del error del xlsx.
3. **codUsuario:** ¿`INTEGRACIONSFA` es el definitivo? El ejemplo de SFA13 usa "SYSDE".
4. **Desembolso:** si SFA15 desembolsa siempre, ¿hay forma de solo validar? ¿Existe reverso o anulación para una factura que no se completa (SFA13 solo sirve para notas de crédito)? ¿Qué pasa si LDCOM no recibe la respuesta (timeout) y el crédito ya quedó aplicado?
5. **Idempotencia:** ¿`idExterno` es único? ¿Qué pasa si llega dos veces la misma solicitud?
6. **Códigos de error:** el único documentado es SFA15-F01 (funcional) y "HTTP_400" (técnico). ¿Lista completa de códigos y tipos? ¿El usuario inválido sale como Técnico (PDF p.18) y no como Seguridad?
7. **indEstado:** ¿qué valores existen además de "A"?
8. **Timeout:** ¿cuál es el corte real de Informatica? (el "30 s" es supuesto nuestro).
9. **Plazo:** el contrato dice días, Confluence y ADO semanas. ¿LDCOM manda semanas × 7 o el número de días real del plan?
10a. **Lista de agencias (PRIORIDAD 2):** SFA valida `codAgencia` como catálogo propio por empresa ("La agencia 001 no existe en el sistema, para la empresa …", PDF pág. 17). Pedir la lista de agencias válidas con su código y a qué sucursal/almacén de Dos Pinos corresponde cada una. Contexto anterior de la duda: el contrato solo dice "Código de Almacén" y el ejemplo es "001". ¿Qué es en Sysde/SFA (agencia = oficina/sucursal de crédito)? ¿Es el código de almacén de SAP de la tienda? ¿Cuál es la lista de valores válidos por sucursal de Dos Pinos? (nuestro catálogo STORE trae nombres de hasta 13 caracteres, como AV-GUAYABO).
10b. **Finca como cliente:** ¿codUnidadCosto es el código de interfaz del cliente finca?
10. **Almacén y finca:** ¿el código de almacén es el de la sucursal en Dos Pinos? ¿De dónde sale el número de finca cuando el cliente es un asociado con varias fincas, y cuando no tiene?
11. **Timeout/caída:** ¿contingencia o bloqueo? (ADO caso 3404 lo deja abierto; US 1296 dice contingencia para caídas).
12. **Rechazo:** confirmar que bloquea la venta (Confluence 4B y caso 3403) y no va a contingencia (caso 3272).
13. **Reintentos:** la propuesta CO-696-0024 habla de reintentos automáticos por endpoint y el PDF dice que no hay; ¿qué manda para SFA15?
14. **Preventa y granel:** preventa pendiente (caso 3278); granel quedó fuera (PO 09/10).
15. **SFA10:** resultado de la prueba del 16/10 (planes de financiamiento / tipos de crédito con Sysde); no hay minuta.
