# Informe: batería de QA SFA15 contra el simulador (2026-10-28)

Simulador en http://localhost:7390 (pestaña SFA15). Cada fila muestra la lista COMPLETA de errores que devuelve; ✔ = el error esperado aparece, ✘ = el simulador no lo valida.

## Batería normal (sin cliente real)

| Caso | HTTP | Qué pasa | Validado |
|---|---|---|---|
| S01 Sin cliente ni identificacion, con finca del ejemplo | 500 | [formato error] Debe indicar la identificación o el código del cliente. (code: -) | ✔ |
| S02 Sin cliente ni identificacion y sin finca | 500 | [formato error] Debe indicar la identificación o el código del cliente. (code: -) | ✔ |
| S03 Identificacion inexistente, finca inexistente | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| S04 Cliente inexistente 9999999 con finca | 200 | APROBADA: Crédito insertado y aplicado satisfactoriamente. (solicitud 149, crédito 25095) |  |
| S05 Identificacion inexistente CEDPF 000000000 (caso base) | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| A01 Agencia = sucursal SAP 1501 | 200 | La agencia 1501 no existe en el sistema, para la empresa 001.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| A02 Agencia = almacen SAP 5100 | 200 | La agencia 5100 no existe en el sistema, para la empresa 001.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| A03 Agencia = 001 (ejemplo PDF) | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. |  |
| A04 Agencia con 11 caracteres (AV-GUAYABO), mas de 5 | 200 | La agencia AV-GUAYABO no existe en el sistema, para la empresa 001.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| A05 Agencia vacia | 200 | El campo codAgencia es requerido.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| A06 Agencia inexistente 99999 | 200 | La agencia 99999 no existe en el sistema, para la empresa 001.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| E01 Empresa CR01 (xlsx) | 200 | La empresa CR01 no existe en el sistema.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| E02 Empresa vacia | 200 | El campo codEmpresa es requerido.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| E03 Empresa inexistente 999 | 200 | La empresa 999 no existe en el sistema.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| P01 Plazo 0 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido.<br>El plazo del crédito no se encuentra dentro del rango configurado. | ✔ |
| P02 Plazo negativo | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido.<br>El plazo del crédito no se encuentra dentro del rango configurado. | ✔ |
| P03 Plazo 99999 (maximo de 5 digitos) | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido.<br>El plazo del crédito no se encuentra dentro del rango configurado. | ✔ |
| P04 Plazo 100000 (excede longitud 5) | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido.<br>El plazo del crédito no se encuentra dentro del rango configurado. | ✔ |
| P05 Plazo decimal 3.5 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| T01 Tipo de credito inexistente 999 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| T02 Tipo de credito 0 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| T03 Tipo de credito como texto | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| M01 Monto 0 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido.<br>El monto de crédito es menor al monto mínimo permitido 0.00. | ✔ |
| M02 Monto negativo | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido.<br>El monto de crédito es menor al monto mínimo permitido 0.00. | ✔ |
| M03 Monto enorme 99999999999999.99 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| M04 Monto con 3 decimales | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| F01 Fecha con formato dd/mm/aaaa | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| F02 Fecha vacia | 200 | El campo fecSolicitud es requerido.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| F03 Sin el campo codUsuario | 200 | El campo codUsuario es requerido.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| F04 Sin el campo codUnidadCosto | 200 | El campo codUnidadCosto es requerido.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| F05 idExterno de 16 caracteres (maximo 15) | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| F06 codUnidadCosto de 26 caracteres (maximo 25) | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| F07 nomAutorizado vacio (requerido) | 200 | El campo nomAutorizado es requerido.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| F08 Texto con tildes y enie en observaciones | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. |  |
| F09 indUsaLinea = N con numLinea 0 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. |  |
| R01 Cuerpo vacio | 500 | El cuerpo de la solicitud es requerido. |  |
| R02 Cuerpo que no es JSON | 500 | El cuerpo de la solicitud es requerido. |  |
| R03 JSON sin Datos_Entrada | 500 | El cuerpo de la solicitud es requerido. |  |
| R04 Datos_Entrada vacio {} | 500 | [formato error] Debe indicar la identificación o el código del cliente. (code: -) |  |
| U01 Usuario invalido (1 llamada) | 500 | [formato error] Error técnico en la autenticación en el servicio externo. (code: HTTP_400) |  |
| U02 Clave invalida (1 llamada) | 500 | [formato error] Error técnico en la autenticación en el servicio externo. (code: HTTP_400) |  |

## Casos con cliente (--tier2; el simulador no valida tipo de crédito ni cliente salvo que se configure)

| Caso | HTTP | Qué pasa | Validado |
|---|---|---|---|
| S01 Sin cliente ni identificacion, con finca del ejemplo | 500 | [formato error] Debe indicar la identificación o el código del cliente. (code: -) | ✔ |
| S02 Sin cliente ni identificacion y sin finca | 500 | [formato error] Debe indicar la identificación o el código del cliente. (code: -) | ✔ |
| S03 Identificacion inexistente, finca inexistente | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| S04 Cliente inexistente 9999999 con finca | 200 | APROBADA: Crédito insertado y aplicado satisfactoriamente. (solicitud 150, crédito 25096) |  |
| S05 Identificacion inexistente CEDPF 000000000 (caso base) | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| A01 Agencia = sucursal SAP 1501 | 200 | La agencia 1501 no existe en el sistema, para la empresa 001.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| A02 Agencia = almacen SAP 5100 | 200 | La agencia 5100 no existe en el sistema, para la empresa 001.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| A03 Agencia = 001 (ejemplo PDF) | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. |  |
| A04 Agencia con 11 caracteres (AV-GUAYABO), mas de 5 | 200 | La agencia AV-GUAYABO no existe en el sistema, para la empresa 001.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| A05 Agencia vacia | 200 | El campo codAgencia es requerido.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| A06 Agencia inexistente 99999 | 200 | La agencia 99999 no existe en el sistema, para la empresa 001.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| E01 Empresa CR01 (xlsx) | 200 | La empresa CR01 no existe en el sistema.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| E02 Empresa vacia | 200 | El campo codEmpresa es requerido.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| E03 Empresa inexistente 999 | 200 | La empresa 999 no existe en el sistema.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| P01 Plazo 0 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido.<br>El plazo del crédito no se encuentra dentro del rango configurado. | ✔ |
| P02 Plazo negativo | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido.<br>El plazo del crédito no se encuentra dentro del rango configurado. | ✔ |
| P03 Plazo 99999 (maximo de 5 digitos) | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido.<br>El plazo del crédito no se encuentra dentro del rango configurado. | ✔ |
| P04 Plazo 100000 (excede longitud 5) | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido.<br>El plazo del crédito no se encuentra dentro del rango configurado. | ✔ |
| P05 Plazo decimal 3.5 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| T01 Tipo de credito inexistente 999 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| T02 Tipo de credito 0 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| T03 Tipo de credito como texto | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| M01 Monto 0 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido.<br>El monto de crédito es menor al monto mínimo permitido 0.00. | ✔ |
| M02 Monto negativo | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido.<br>El monto de crédito es menor al monto mínimo permitido 0.00. | ✔ |
| M03 Monto enorme 99999999999999.99 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| M04 Monto con 3 decimales | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| F01 Fecha con formato dd/mm/aaaa | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| F02 Fecha vacia | 200 | El campo fecSolicitud es requerido.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| F03 Sin el campo codUsuario | 200 | El campo codUsuario es requerido.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| F04 Sin el campo codUnidadCosto | 200 | El campo codUnidadCosto es requerido.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| F05 idExterno de 16 caracteres (maximo 15) | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| F06 codUnidadCosto de 26 caracteres (maximo 25) | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✘ |
| F07 nomAutorizado vacio (requerido) | 200 | El campo nomAutorizado es requerido.<br>El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. | ✔ |
| F08 Texto con tildes y enie en observaciones | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. |  |
| F09 indUsaLinea = N con numLinea 0 | 200 | El código de tipo de identificación CEDPF no existe en el sistema.<br>La identificación no se encuentra relacionada a un cliente válido. |  |
| X01 CLIENTE REAL sin finca (asociado sin fincas), tipo credito inexistente | 200 | El campo codUnidadCosto es requerido. |  |
| X02 CLIENTE REAL con finca del ejemplo (ajena), tipo credito inexistente | 200 | APROBADA: Crédito insertado y aplicado satisfactoriamente. (solicitud 151, crédito 25097) |  |
| X03 CLIENTE REAL con su finca propia, tipo credito inexistente | 200 | APROBADA: Crédito insertado y aplicado satisfactoriamente. (solicitud 152, crédito 25098) |  |
| R01 Cuerpo vacio | 500 | El cuerpo de la solicitud es requerido. |  |
| R02 Cuerpo que no es JSON | 500 | El cuerpo de la solicitud es requerido. |  |
| R03 JSON sin Datos_Entrada | 500 | El cuerpo de la solicitud es requerido. |  |
| R04 Datos_Entrada vacio {} | 500 | [formato error] Debe indicar la identificación o el código del cliente. (code: -) |  |

## Casos donde el simulador no valida lo que el real sí (✘)

P05, T01, T02, T03, M03, M04, F01, F05, F06, P05, T01, T02, T03, M03, M04, F01, F05, F06
