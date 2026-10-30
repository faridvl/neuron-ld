# Auditoria BD de Ticket_Encabezado y Factura_Encabezado (ticket 3700, columnas Factura_Credito_SFA_*)

Solo SELECT. Fecha: 2026-10-28. Usuario SQL no se registra.

## Bases auditadas
| Etiqueta | Servidor | Base |
|---|---|---|
| Docker-STAGING | localhost,1433 (SQL 2022 Linux) | LDCOM_DOS_PINOS_STAGING_DOCKER |
| Docker-DEVELOP | localhost,1433 | LDCOM_DOS_PINOS_DEVELOP_DOCKER |
| Testing | TESTINGSQL\SQL2022 | LDCOM_DOS_PINOS_NEW |

Docker tiene ademas LDCOM_DOS_PINOS_DOCKER, _V40, _E2E, _ESCENARIOS (no auditadas).

## 4. Las 3 columnas ya existen?
- Docker-STAGING: SI, ya estan en ambas tablas, NOT NULL con DEFAULT: Solicitud bigint DEFAULT 0, Credito varchar(50) DEFAULT '', Referencia varchar(15) DEFAULT ''. Ticket: column_id 130-132; Factura: 131-133 (son las ultimas).
- Docker-DEVELOP: NO existen.
- Testing: NO existen.

## 5. Filas, tamano y replicacion
| Base | Ticket_Encabezado | Factura_Encabezado | Cols antes de agregar | Indices |
|---|---|---|---|---|
| Docker-STAGING | 24 filas, 0.2 MB | 93 filas, 0.2 MB | 129 / 130 (hoy 132 / 133 con las 3) | solo PK nonclustered, HEAP |
| Docker-DEVELOP | 37 filas, 0.2 MB | 68 filas, 0.2 MB | 127 / 128 | solo PK nonclustered, HEAP |
| Testing | 152 filas, 0.3 MB | 53 filas, 0.3 MB | 129 / 130 | PK + IX_*_Emp_Id_Factura_Talonario_Numero, HEAP |

- Costo del ALTER: insignificante en las tres (decenas/cientos de filas, <1 MB). En SQL 2022 el ADD COLUMN NOT NULL con DEFAULT constante es solo metadato de todos modos.
- CDC: no (tablas ni base). Change tracking: no (0 tablas, 0 bases). Replicacion (publicada, merge, suscrita, schema published): no. Temporal: no. Compresion: NONE.
- Ojo: estas son bases de prueba; los volumenes de produccion Dos Pinos no se midieron aqui.
- Sin FKs que bloqueen: solo FK hacia Cliente y las FKs hijas (Detalle, Forma_Pago, Patrocinador...); agregar columnas no las afecta. Sin CHECK constraints sobre las tablas.

## 1. Triggers
- Ninguno sobre Ticket_Encabezado ni Factura_Encabezado en las tres bases.
- Ningun trigger de otras tablas menciona estas tablas.

## 2. Objetos que las referencian
Docker-STAGING y Docker-DEVELOP: 74 modulos cada uno (mismos). Testing: 78. Ninguno WITH SCHEMABINDING (is_schema_bound = 0 en todos). No hay tipos de tabla de usuario (table types) con nombre parecido. Sinonimos: 0.

Metodo: sys.sql_expression_dependencies + busqueda en sys.sql_modules y analisis de texto con regex sobre cada definicion (sin comentarios). Es heuristico: dinamico (EXEC con string) solo se ve si el texto del string contiene el nombre.

Hallazgos de riesgo real:
- INSERT INTO Ticket_Encabezado/Factura_Encabezado SIN lista de columnas: NINGUNO en las 3 bases. Todos los INSERT al encabezado traen lista de columnas, asi que no se rompen al agregar columnas (las nuevas toman el DEFAULT; si se quiere persistir el credito SFA, estos SPs hay que modificarlos).
- INSERT INTO otra_tabla SELECT * FROM encabezado: NINGUNO.
- alias.* sobre el encabezado: NINGUNO.
- SELECT * INTO #temp FROM encabezado: NINGUNO real. Unico marcado: PV_Interface_Notas_SAP (SELECT * INTO #Encabezado FROM @Encabezado) pero @Encabezado es una variable de tabla del propio SP, no la tabla real: falso positivo.
- Vistas WITH SCHEMABINDING: ninguna. Funciones/SP schemabound: ninguno.

SPs que ESCRIBEN (INSERT con lista de columnas) en los encabezados. No se rompen, pero son los candidatos a tocar si el feature debe guardar los datos SFA:
- Pv_Factura_Rehacer
- PV_Cerrar_Caja (inserta en Factura_Encabezado leyendo Ticket_Encabezado, 10 INSERT)
- Fact_Verifica_Factura_Apdo_Cancelado
- INV_Despacho_SubPed_Aplicar
- Inv_Devolucion_Pedido
- Inv_Guia_Trans_Liquidar
(PV_Cerrar_Caja inserta en Factura_Encabezado con lista explicita de columnas: las 3 columnas nuevas NO viajaran a Factura_Encabezado salvo que se agreguen al INSERT/SELECT. Es el principal punto de "quedar sin las columnas".)

Otros objetos (solo leen, no se rompen): funciones FN_FacturaTicket_FormaPago / FormaPagoOtras (inline TVF), reportes Rep_*, SP_Reporte_*, PV_FacturacionAcum_*, PV_Interface_* (Facturas/Notas CxC/SAP), Con_Asientos_Generar_*, Genera_Estadistica_*, Comi_Comisiones_*, Inv_Prefactura_*, Rep_Trazabilidad, CORTAR_BD, Corte_Historico_Prefactura_Cedi, etc. (lista completa en las dependencias de cada base).

Vistas: Docker 1 (View_Descuentos_x_Articulo, no usa columnas nuevas); Testing 2 (View_Descuentos_x_Articulo y View_Analitica_Ventas, esta ultima con CTE de columnas explicitas, sin SELECT *, sin schemabinding).

## 3. Tablas espejo / de estructura parecida
- Ticket_Encabezado y Factura_Encabezado son casi gemelas (132 columnas en comun). En las tres bases Factura tiene 1 columna mas que Ticket.
- Apartado_Encabezado (77 cols en comun, 0-2 filas): estructura parecida, no recibe las columnas nuevas; ningun SP la llena con SELECT * desde los encabezados.
- PV_Preventa_Encabezado / PV_Preventa_Encabezado_Histo (28-31 cols en comun): historico de preventas, no es copia de los encabezados.
- PV_Prefactura_Encabezado / _Historico, SAP_Factura_Encabezado (interfaz SAP, el SP PV_Interface_Notas_SAP la llena con lista explicita), PV_Format_Ticket_Encabezado: no son espejos por SELECT *.
- No hay *_Hist / *_Anulada del encabezado. No se encontro INSERT ... SELECT sin lista de columnas desde los encabezados hacia ninguna tabla.

## 6. Diferencias entre bases
- Columnas SFA: solo Docker-STAGING las tiene (probablemente por una corrida previa del 3700). Develop y Testing no.
- Docker-DEVELOP tiene 2 columnas menos que Testing/Docker-STAGING en ambas tablas: Factura_Validacion_Credito y Factura_Talonario_Numero (y por lo mismo no tiene el indice IX_*_Emp_Id_Factura_Talonario_Numero). Docker-STAGING y Testing son iguales salvo las 3 SFA.
- Testing tiene 6 modulos distintos respecto a Docker que refieren los encabezados: FN_FacturaTicket_PagosSinpe, SP_Reporte_VentasContingencia, SP_Reporte_VentasPorTipoCredito, FE_Consecutivo_Sembrar, View_Analitica_Ventas y fn_FacturaTicket_FormaPago (en Docker es FN_FacturaTicket_FormaPago: mismo nombre con otra capitalizacion). Docker tiene SP_ReporteFormasPagoTransaccion_Prueba2232 que Testing no.
  Ninguno de los extra de Testing tiene patrones de riesgo.
- Docker-STAGING tiene 74 modulos, Develop 74 (identicos en lista); Testing 78.
- Versiones: Docker SQL 2022 CU23 en Linux, Testing SQL 2022 RTM-GDR (16.0.1175), compat 160 en Docker.

## Resumen de riesgo
Bajo. Ningun objeto se rompe al agregar las 3 columnas (sin triggers, sin schemabinding, sin INSERT sin lista de columnas, sin SELECT * hacia otras tablas, sin CDC/replicacion/change tracking). El riesgo es de omision: los 6 SPs de escritura (sobre todo PV_Cerrar_Caja, Pv_Factura_Rehacer y Fact_Verifica_Factura_Apdo_Cancelado, que copian Ticket->Factura) no copiaran las columnas nuevas hasta que se les agreguen. Las instancias de POS/Admin (LINQ/dbml) no se auditaron aqui (solo BD).
