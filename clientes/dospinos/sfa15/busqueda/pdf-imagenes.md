# SFA15: lo que muestran las imágenes del PDF de BD Consultores (2026-10-28)

Fuente: `Documento Autorizacion_Venta_Final.pdf`, capturas de Postman de las pruebas (págs. 14-19). Imágenes extraídas en `sfa15\pdf-imagenes\` (baja resolución; las amplificadas se llaman `ampl_*`). La pág. 21 es un recorte vacío, sin contenido.

## Hallazgos
1. **codEmpresa "CR01" se rechaza** (pág. 17): HTTP 200, `CodigoError` SFA15-F01, `TipoError` Funcional, `Mensaje` "La empresa CR01 no existe en el sistema.". El valor correcto es "001" (todos los ejemplos del PDF); la constante "CR01" del xlsx está mal.
2. **La agencia es un catálogo de SFA por empresa**: "La agencia 001 no existe en el sistema, para la empresa CR01." No es solo un campo libre: SFA la valida contra su propia lista, ligada a la empresa.
3. **SFA acumula los errores**: una sola respuesta trae todas las reglas incumplidas en `DetalleTransaccion` (empresa, agencia, tipo de identificación, cliente, unidad de costo "no existe en el sistema" y "no existe para el cliente", plazo fuera de rango configurado, tipo de crédito inexistente, monto menor al mínimo, usuario INTEGRACIONSFA inexistente, cliente inactivo). Sirve para el QA: un caso sin cliente igual muestra si valida agencia/empresa/plazo/tipo de crédito.
4. **El status HTTP del transporte no es el del error**: los errores funcionales vienen con HTTP 200 y `HttpStatus: "400"` dentro del cuerpo (pág. 17 y 18). La clasificación debe mandar por el cuerpo (`CodigoError`/`TipoError`), no por el HTTP.
5. **Hay un segundo formato de error**, con HTTP 500 y la forma `{"error":{"code":500,"detail":{"reason","code","details"},"message"}}`, sin `CodigoError`/`TipoError` de primer nivel. Se ve en: falta cliente/identificación ("Debe indicar la identificación o el código del cliente.", pág. 15), indUsaLinea distinto de S/N, numLinea distinto de 0 (págs. 16, con code SFA15-F0x dentro de `detail`), usuario/clave inválidos (pág. 18) y timeout del token de SFA ("HTTP_408", "Timeout al obtener el token de SFA15", pág. 19).
6. **Éxito** (pág. 14): HTTP 200, `Respuesta` con numSolicitud 147, numCredito "25093", indEstado "A", monDisponible; `Mensaje` "Crédito insertado y aplicado satisfactoriamente."; `HttpStatus` "200". Request de la prueba: codAgencia "001", codTipoId CEDJU, numId 3102012066, codUnidadCosto "2563", plazo 24, tipCredito 201, monto 5000.
7. **Cuerpo vacío {}** (pág. 14): `CodigoError` HTTP_400, `TipoError` Técnico, "El cuerpo de la solicitud es requerido."
8. **Unidad de costo** (pág. 18): "La unidad de costo 2563 no existe para el cliente 4000010." además de "no existe en el sistema": es un catálogo de SFA ligado al cliente.

## Efecto en nuestro código (pendiente de aplicar)
- `Sfa15ResponseClassifier` ya da prioridad al cuerpo sobre el HTTP (caso 4 cubierto). No lee el formato `error` del punto 5: hoy lo trata como Técnico con el mensaje genérico "respondió HTTP 500".
- Semilla `CREDIT_VALIDATION`: `CompanyCode` debe ser `001`, no `CR01`.
- Simulador: devuelve 400 para lo funcional; la realidad es 200 con `HttpStatus` en el cuerpo y 500 con el formato `error` para entradas inválidas.
