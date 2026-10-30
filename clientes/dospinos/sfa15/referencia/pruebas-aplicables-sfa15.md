# Listado Maestro de Pruebas de Dos Pinos (12-09-2026): qué aplica a SFA15 (2026-10-28)

Copia: `sfa15\referencia\Listado_Maestro_Pruebas_2026-09-12.xlsx` (volcado de texto: `listado-maestro-pruebas-volcado.txt`). Hojas: Financiamiento (20 pruebas RET-UT-FIN), Integraciones, Facturación (120), Adelanto de Rutas, etc. La versión del 23-10-2026 (copia `Listado_Maestro_Pruebas_2026-10-23.xlsx`) se comparó el 2026-10-28: las hojas Financiamiento, Integraciones, Adelanto de Rutas y Obras en Proceso no cambiaron, y las pruebas FAC-0047/0051/0053/0098/0106/0107 y MET-0028 son idénticas. Lo que cambió está en otras hojas (Facturación, Dinámicas, etc.) y no toca SFA15. Este análisis sigue vigente.

Las columnas "Resultado/Observaciones" marcan "Requiere integración con el SFA" en las pruebas que dependen de SFA15. Ninguna prueba nombra SFA15, POS10 ni sus campos: se refieren al comportamiento de negocio.

## Pruebas que deben pasar cuando SFA15 esté conectado
| Prueba | Qué exige | Cómo queda hoy |
|---|---|---|
| RET-UT-FAC-0051 | Factura a crédito de asociado: consulta a SFA; sin disponible bloquea; con disponible **recibe número de autorización, permite facturar y lo registra en la factura** | Integrations devuelve `numSolicitud` y `numCredito`. NEGOCIO/POS solo guardan `Factura_Validacion_Credito`; **falta persistir el número de autorización**. |
| RET-UT-FAC-0053 | SFA responde "No tiene disponible": **bloqueo + mensaje "Favor comunicarse con Servicios Financieros" + registra el intento** | Requiere el tercer estado "rechazado" en `TRegRespuestaValidacionCreditoSFA` (hoy todo no-autorizado = contingencia). Mensaje fijo de LDCOM, no el de Dos Pinos. Registrar el intento = auditoría (ya existe del lado de Integrations). |
| RET-UT-FAC-0106 / 0107, RET-UT-FIN-0009, RET-UT-AR-0006, RET-UT-AR-0014 | Sin conexión o SFA caído: factura sin validaciones financieras, marca "C", el indicador se guarda, imprime y viaja; mensaje controlado | Cubierto por el diseño (Unavailable → contingencia `Factura_Validacion_Credito` 2). Probar con el simulador (timeout y conectividad) y con el SFA real. |
| RET-UT-FIN-0019 / 0020 | Facturar bajo y sobre el límite, y con límite condicionado; **piden a Dos Pinos la lista de asociados para esta prueba** | Pedir a Dos Pinos asociados de prueba con disponible alto, bajo y condicionado. |
| RET-UT-FAC-0098 | NC de asociado envía a SFA: fecha, factura relacionada, NC, monto, plazo, tasa, autorizado y **sucursal** | Es SFA13 (notas de crédito), no SFA15. Pista: los campos de SFA13 no traen otra cosa que `codAgencia` para la sucursal; refuerza que **agencia = sucursal** (en el código propio de SFA). |
| RET-UT-FIN-0006 | Un plazo fuera del conjunto del plan no se puede usar | Relaciona con la duda días/semanas: el plazo que llega a SFA debe ser uno del conjunto del plan. |

## Reglas de negocio que confirman decisiones
- Integraciones, fila POS02 (Clientes): "cada vez que se requiere generar una factura, LDCOM debe hacer la consulta en línea a SFA con el propósito de obtener una **aprobación, caso contrario una denegación**". Respalda que el rechazo funcional bloquea la venta (Confluence 4B, ADO 3403) frente al caso 3272.
- RET-UT-FAC-0047: no se puede mezclar crédito/financiamiento con otros métodos de pago (regla de LDCOM, ya existente).

## Relacionadas pero de otra interfaz o fuera de alcance
- Financiamiento FIN-0001/0007/0008/0010 (mantenimiento y sincronización de tipos de crédito): SFA10 / LD-10, no SFA15. FIN-0013/0014/0015/0018 (selección de plan, artículo no autorizado, banca/no banca, dos tipos de crédito): del POS, sirven de regresión.
- Adelanto de Rutas AR-0002 ("validar crédito en línea contra SFA") y AR-0005 (estado de cuenta): pueden ser otra interfaz (disponible de crédito, POS-09); confirmar antes de asumirlas.
- GRS-0026 (preventa de granel reserva disponible), OBP-0010 (OBP con SFA): granel y OBP quedaron fuera.
- MET-0028 y FLE-0006: dicen que requieren integración con SAP, no con SFA.
- FAC-0098 y OBP-0010 describen notas de crédito hacia SFA (SFA13).

## Qué hacer cuando se desarrolle
1. Persistir `numSolicitud`/`numCredito` en la factura (FAC-0051).
2. Agregar el estado "rechazado" y el mensaje fijo "Favor comunicarse con Servicios Financieros" (FAC-0053).
3. Pruebas con el simulador de las 3 situaciones: autorizado, rechazado y caída/timeout (FAC-0106/0107, FIN-0009).
4. Pedir a Dos Pinos la lista de asociados de prueba (FIN-0019/0020).
