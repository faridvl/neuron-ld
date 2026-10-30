# Revisión del módulo de facturación (POS) frente a SFA15 (2026-10-28)

Fuente: `origin/develop` de LDCOM13_DOS_PINOS, leído sin checkout. Verificado a mano: `TRegRespuestaValidacionCreditoSFA` solo tiene `Autorizado`/`Mensaje`; `TValidacionCredito` = No_Aplica 0 / Validado 1 / Sin_Validar 2 con mensaje de contingencia; la validación (Frm_Facturacion.vb:15155) corre antes de `Cargar` (15207) y `GuardarLocal` (15212).

## Qué tiene el POS al validar y qué falta
| Dato SFA15 | ¿Lo tiene el POS? | Dónde | Falta |
|---|---|---|---|
| Cliente (asociado) | Sí | `Facturacion.Cliente` (Cliente_Id; `TRegCliente.Codigo_Interfaz`) | Hoy viaja `Cliente_Id`; en SFA de pruebas es el mismo código |
| Sucursal (→ agencia) | Sí | `_Sucursal.Sucursal.Suc_Id` (15218); `EstadoConexion.Suc_Id_Factura` | No viaja: agregar al contrato WCF |
| Finca | Sí | `Facturacion.Cliente_Relacionado` (Nothing si no tiene fincas) | No viaja: mandar su Cliente_Id o vacío |
| Código externo del plan | En línea sí, local no | `TRegPlanFinanciamiento.Codigo_Externo`; al facturar solo se guarda `PlanFinanciamiento_Id` | Resolver el código en el servidor por Id |
| Plazo | Sí, en semanas | `Facturacion.PlanFinanciamiento_Plazo_Semanas` | Confirmar días o semanas |
| Monto | Sí | `MontoTotal` | — |
| Número de factura (`idExterno`) | No | Se asigna en `Cargar`, después de validar | Dejar vacío (opcional) o mover la validación |
| Línea de crédito (`indUsaLinea`/`numLinea`) | No existe el concepto | Solo `Credito_Limite`/`Credito_Saldo` | Decisión de negocio |
| Identificación, nombre, fecha | Sí | `TRegCliente` | Opcionales |

## Hallazgos
1. **Contrato WCF** `SFA_Validar_Credito(pConexion, pEmp_Id, pCliente_Id, pPlanFinanciamiento_Id, pPlazo_Semanas, pMonto)` y respuesta `Autorizado`/`Mensaje`: no distingue rechazado de no disponible, ni trae numSolicitud/numCredito.
2. **NEGOCIO** `TSistemaFinanciamientoSFA.Validar_Credito` es un stub que autoriza siempre.
3. **Rechazo = contingencia hoy**: `Autorizado=False` → `Sin_Validar` (2) y la factura se emite con el aviso "No se pudo validar el crédito...". Contradice FAC-0053 (rechazo bloquea con "Favor comunicarse con Servicios Financieros" y registra el intento).
4. **Número de autorización**: no hay columna para numSolicitud/numCredito (FAC-0051). Existe `Factura_Validacion_Credito` (migración 20261014153000__2223_ValidacionCreditoSFA).
5. **Preventa** no valida SFA; al facturarla en el POS entra por el flujo de factura. Notas de crédito (SFA13) no existen.
6. **Doble llamada**: un reintento tras cancelar serie/receta/datos fiscales vuelve a llamar a SFA con el mismo documento (la validación va antes de esos pasos). Si `GuardarLocal` falla después de autorizar, no hay reversa.
7. **Offline**: `GetValidacionCreditoSFA` devuelve Nothing → `Sin_Validar` (contingencia), coherente con FAC-0106/0107. La llamada es síncrona: un timeout largo congela la caja.

## Cambios necesarios en LDCOM (priorizados)
1. Contrato WCF nuevo: entrada con Suc_Id, finca, (referencia); respuesta con estado Autorizado / Rechazado / No disponible, NumSolicitud, NumCredito, Mensaje, PossiblyApplied. Regenerar Reference.vb.
2. Implementar `TSistemaFinanciamientoSFA.Validar_Credito` con `IntegrationBridge.ValidateFinancingPlan` (código externo del plan por Id, cliente por Codigo_Interfaz, plazo según lo que confirme SFA).
3. `TDecisionValidacionCreditoSFA` con 3 ramas: Rechazado bloquea con "Favor comunicarse con Servicios Financieros" y registra el intento; No disponible = contingencia. Pruebas unitarias.
4. Pasar la finca (`Cliente_Relacionado`) o vacío.
5. Migración + BD local + objetos para guardar numSolicitud/numCredito (FAC-0051).
6. No volver a llamar a SFA para el mismo documento si ya hay autorización (cache por documento) y definir qué hacer si falla el guardado después de autorizar.
7. Decisiones abiertas: línea de crédito, referencia de factura, SFA13 para NC, días o semanas.

## Sin confirmar
Cómo se imprime la marca de contingencia; si `Codigo_Interfaz` llega poblado en el cliente local; carpetas de Preventa separadas.
