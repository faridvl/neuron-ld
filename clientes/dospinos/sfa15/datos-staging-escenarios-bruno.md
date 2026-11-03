# Datos de Docker Staging para los escenarios SFA15 de Bruno (2026-10-28)

Fuente: `LDCOM_DOS_PINOS_STAGING_DOCKER` en el Docker local (solo SELECT, `sfa15\e2e\consulta-solo-lectura.js` + `datos-escenarios.sql`).
Modelo confirmado: `Cliente_Relacion` tipo 1 va de asociado (`Tipo_Id` 3, columna `Cliente_Id`) a finca (`Tipo_Id` 10, columna `Cliente_Relacion_Id`): 1.461 filas. `Codigo_Interfaz` = `Cliente_Id` en asociados y fincas.

| Escenario | Variable de Bruno | Valor | De donde sale |
|---|---|---|---|
| E01 asociado con 1 finca | `sfa15ClienteUnaFinca` / `sfa15FincaUnaFinca` | 4000010 / 3664 | MATA MERINO MANUEL EMILIO, su unica finca GANADERA MARSELLLA S.A.; es el cliente del ejemplo del PDF |
| E02 asociado con varias fincas | `sfa15ClienteVariasFincas` / `sfa15FincaVariasFincas` | 4000393 / 2540 | MARTINEZ SEGURA FLOR DE MARIA, 6 fincas activas |
| E03 asociado sin fincas | `sfa15ClienteSinFinca` | 4000054 | SALGADO ULLOA RAFAEL EDUARDO |
| E04 finca ajena | `sfa15FincaAjena` | 2563 | HACIENDA LA HOLANDA S.R.L., finca del asociado 4000004 (no del 4000010) |
| E05 sobre el disponible | `sfa15MontoSobreDisponible` | 999999999 | Monto muy por encima de cualquier disponible |

Todos activos, sin bloqueo y No Banca.

## Hallazgos
1. **`codUnidadCosto` = codigo de la finca del asociado (confirmado con datos):** el PDF de BD Consultores probo cliente 4000010 con unidad de costo 2563 y SFA respondio "La unidad de costo 2563 no existe para el cliente 4000010". En Staging, 2563 es la finca del asociado 4000004 y la del 4000010 es 3664. SFA valida que la finca pertenezca al cliente.
2. **Los planes de Staging no tienen codigos reales de SFA:** `PlanFinanciamiento_Codigo_Externo` son codigos de prueba de LD-10 (`ZZ_TEST_LD10_002`, `RGA10280228-B1`, etc.), alfanumericos. `tipCredito` de SFA15 es numerico de 3 (ej. 201). Con estos datos el mapeo de Integrations rechazaria el plan (pide un entero). En produccion los codigos vendran de SFA10; hay que confirmar que sean numericos. En Bruno se deja `sfa15TipCredito` = 201 (el del PDF).
3. **Sucursales sin `Codigo_Interfaz`:** las 20 estan vacias (AV GUAYABO = Suc_Id 4 = 1501 en SAP). La agencia sigue pendiente de la lista de Dos Pinos; en Bruno queda `sfa15CodAgencia` = 001.
4. Plazos: `Plan_Financiamiento_Plazo.PlanFinanciamiento_Plazo_Semanas` (en semanas). El contrato pide dias; en Bruno queda 24 (el del PDF).

## Resultados contra SFA15 de pruebas (2026-10-28, Bruno, ambiente UAT Dos Pinos)
- **E01 APROBADA** (12:27 aprox.): cliente 4000010, finca 3664, empresa 001, agencia 001, tipo de credito 201, plazo 24, monto 1.00,
  indUsaLinea S, numLinea 0, codUsuario INTEGRACIONSFA -> numSolicitud 279, numCredito 25213, indEstado A, monDisponible 109,949,445.00,
  "Credito insertado y aplicado satisfactoriamente". Se creo un credito real en el SFA de pruebas por 1.00 (sin reverso documentado).
- Conclusiones: el codCliente de SFA es el mismo Cliente_Id / Codigo_Interfaz de LDCOM (codigo SAP), y codUnidadCosto es el Cliente_Id de la finca:
  no hace falta traduccion para cliente ni finca. Empresa 001, agencia 001, tipo 201 y plazo 24 son validos en SFA de pruebas.
- Dudas (D01-D05): ver respuestas guardadas como ejemplos en cada request de Bruno. CEDPF 000000000 resolvio al cliente SFA 001100069709 (no es inexistente).
- **E02** (4000393, finca 2540): rechazo funcional "El tipo de credito require linea de credito. El cliente debe tener una linea de credito activa marcada como principal o indicar el numero de linea." -> ese asociado no tiene linea principal en SFA de pruebas (dato de SFA, no de mapeo).
- **E03 APROBADA** (4000054, sin fincas, codUnidadCosto ""): numSolicitud 281, numCredito 25214, monDisponible 32,741,196.47. **Asociado sin finca: se envia la unidad de costo vacia y SFA aprueba** (aunque el xlsx la marca requerida).
- **E04** (4000010 con finca 2563 ajena): rechazo funcional "La unidad de costo 2563 no existe para el cliente 4000010." (igual que el PDF). No crea credito.
- **E05** (4000010, monto 999999999): **HTTP 200, `Respuesta` con numSolicitud 280, numCredito null, `indEstado` "R"**, sin CodigoError, sin TipoError, sin Mensaje, HttpStatus "200". Tercera forma de respuesta: rechazo por disponible via indEstado R. Nuestro clasificador hoy lo trataria como Unavailable/Technical (contingencia) y deberia ser Rejected.
- Creditos creados en el SFA de pruebas: 25213 (solicitud 279, E01) y 25214 (solicitud 281, E03), 1.00 cada uno.

## Dudas pendientes resueltas (carpetas 3 y 4 de Bruno, 2026-10-28)
- Plazo (tipo 201, cliente 4000010): 1 y 168 aceptados; 9999 -> "El plazo no debe ser mayor al plazo maximo configurado para el tipo de credito". Hay un maximo entre 168 y 9999. No define si la unidad es dias o semanas.
- Agencia 002: no existe para la empresa 001. (Valida: 001. No validas: 002, 5100.)
- Tipo de credito 202: sin errores de tipo -> existe y esta configurado (ademas del 201).
- Monto 1.555 (3 decimales): aceptado sin error (LDCOM igual debe mandar 2 decimales).
- C01 (4000393, indUsaLinea N): mismo rechazo "requiere linea de credito" -> el tipo 201 exige linea activa principal aunque se mande N. Asociado sin linea no puede financiar con 201 (dato de SFA).
- C02/C03 mismo idExterno LDQA-DUP-0001: AMBOS aprobados (solicitudes 282 y 283, creditos 25215 y 25216). **SFA no protege contra duplicados: la guarda contra doble envio tiene que estar en LDCOM/Integrations.**
- Creditos de 1.00 creados en SFA de pruebas: 25213, 25214, 25215, 25216.
- Rareza de SFA: en los mensajes concatena un "1" al valor ("unidad de costo 999999991", "CEDPF1"); no afecta.

## Escenarios POS 3700 (S01-S07) contra el CIH real (2026-11-02)

La carpeta "5 Escenarios POS 3700" de Bruno ya no usa el simulador: todo va al SFA real con el environment UAT Dos Pinos.

| Escenario | Resultado |
|---|---|
| S01 autorizado con finca | A, credito 25228 |
| S04 rechazo funcional (finca ajena 2563) | HTTP 200, indEstado null, "La unidad de costo 2563 no existe para el cliente 4000010." Sin credito |
| S05 sin conexion | Host `.invalid`: no resuelve DNS (curl 6, ~0.1 s); no llega al SFA. Una corrida por error contra el real dio 200 (posible credito extra) |
| S06 timeout | Corte del cliente a 1 s: "timeout of 1000ms exceeded". El SFA si recibe la solicitud y puede crear el credito igual |
| S07 autorizado 2320.48, plan 42 dias tipo 203 | A, credito 25231 |

Las claves de SFA del environment son secretas en Bruno (no estan en el yml): los requests se corren desde Bruno.
