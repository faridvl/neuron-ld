# Auditoria 3700 (en curso)
Precedente exacto: migraciones 2223 (Factura_Validacion_Credito), 3106 (Talonario_Numero), 2163 (PlanFinanciamiento_*), 481, 1495. Huella de codigo en origin/develop: TFacturacion.vb (1835,2996,6216 DataColumn), TFacturacionLocal 9042-9053 (insert local), TSincronizacionLocal 3297, TFactura 4961-4987, TRegFactura, PV_Cerrar_Caja.

## Avance 1
- Sync: Sincr_Factura recibe DataSet (no DataContract) -> sin cambio de contrato WCF. TSincronizacionLocal.Documentos_Datos_Encabezado (SELECT explicito, ~3297) debe sumar las 3 columnas; TFactura.Insertar_Encabezado (4977+) guard Columns.Contains; TFacturacionLocal.Insertar_Factura_Encabezado (8847-9060) inserta siempre -> falla si local sin columnas.
- Local script: TVersionBD.Actualizar_BD_Automatico en Program_Inicio.vb:910 (solo con conexion; si falla lanza excepcion y el POS no abre).
- Otros INSERT Ticket_Encabezado: TFactura:4977, TApartado:366, TDevolucion:1521 (central, lista explicita); SPs legacy (seed 02-schema): Fact_Verifica_Factura_Apdo_Cancelado, INV_Despacho_SubPed_Aplicar, Inv_Devolucion_Pedido, Inv_Guia_Trans_Liquidar, Pv_Factura_Rehacer: lista explicita.
- Local inserts Factura_Encabezado: TFacturacionLocal 8847 (factura), 10816 (apartado), 11525 (devolucion; NO lleva Plan/Validacion/Talonario).
- Sin SCHEMABINDING, sin triggers de tabla en seed, 3 vistas analitica con columnas explicitas, DDL trigger Audit_Table_DDL (solo auditoria).

## Hallazgos finales (base origin/develop 1cfd9c36)
A. Copias: PV_Cerrar_Caja (routines/procedures/caja/PV_Cerrar_Caja.sql, UTF-16) INSERT 277-358 / SELECT FROM Ticket_Encabezado 359; DELETE Ticket 913 => si no se copian se pierden. Pv_Factura_Rehacer (seeds/schema/02-schema.sql:143312; @Encabezado 143349/143547/143583; INSERT Ticket 143938,144117), INV_Despacho_SubPed_Aplicar (122341; 123273,123324), Inv_Devolucion_Pedido (125017), Inv_Guia_Trans_Liquidar (127981), Fact_Verifica_Factura_Apdo_Cancelado (100237). Armar_Encabezado_Separado TFacturacion.vb:4375-4380 copia TODAS las columnas por nombre a los 2 docs de la venta partida (duplica SFA en el doc de bonificados; Campos_En_Cero... no lo cubre).
B. Nada se rompe: sin SCHEMABINDING, sin triggers de tabla, sin TVP, sin bcp/fmt, sin SELECT * en SP/rdl/VB sobre estas tablas, listas explicitas. dbml no mapea las columnas de 2223/3106 (queda igual).
C. DataSet por WCF (no DataContract). Caja sin columnas locales + codigo nuevo: INSERT local (TFacturacionLocal 8847+) y SELECT sync (TSincronizacionLocal ~3297) fallan. Scripts locales solo al abrir con conexion (Program_Inicio.vb:910, TVersionBD). Releases 6.0-6.3: PV_Cerrar_Caja sin Validacion/Talonario, 2223/3106 solo en develop.
