/*
Fecha: 2026/10/29
Responsable: fvillacis@ld.co.cr
Propósito: Issue 3700 (POS-10, validar crédito con SFA15): guarda en el staging central la autorización que el
           SFA dio al documento y la referencia con la que se pidió. Prueba de Dos Pinos RET-UT-FAC-0051.

           Ticket_Encabezado es el staging central: la factura de la caja llega aquí por
           WCFSincLocalToServer.Sincr_Factura -> TFactura.Insertar_Encabezado, y PV_Cerrar_Caja la
           traslada a Factura_Encabezado (04_ALT_SP_PV_Cerrar_Caja.sql de esta migración).

           Columnas (las tres con DEFAULT, así el código anterior que no las envía sigue insertando):
             Factura_Credito_SFA_Solicitud  bigint       0  = sin autorización del SFA.
             Factura_Credito_SFA_Credito    varchar(50)  '' = sin autorización del SFA. El contrato de
                                                         Integrations no fija el largo de numCredito (llega
                                                         como texto), por eso el margen.
             Factura_Credito_SFA_Referencia varchar(15)  '' = no se consultó al SFA. 15 es el máximo de
                                                         idExterno (TGeneradorReferenciaCreditoSFA).
Nombre Tabla: Ticket_Encabezado
*/

IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Credito_SFA_Solicitud' AND object_id = Object_id('Ticket_Encabezado'))
BEGIN
    ALTER TABLE dbo.Ticket_Encabezado ADD Factura_Credito_SFA_Solicitud bigint NOT NULL CONSTRAINT DF_Ticket_Encabezado_Factura_Credito_SFA_Solicitud DEFAULT (0)
    EXECUTE Sp_addextendedproperty N'MS_Description', N'Número de solicitud que el SFA asignó al autorizar el crédito del documento. 0 = el documento no tuvo autorización del SFA (sin crédito, rechazado, o sin conexión). Staging: PV_Cerrar_Caja lo copia a Factura_Encabezado.Factura_Credito_SFA_Solicitud.', N'SCHEMA', N'dbo', N'TABLE', N'Ticket_Encabezado', N'COLUMN', N'Factura_Credito_SFA_Solicitud'
END
GO

IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Credito_SFA_Credito' AND object_id = Object_id('Ticket_Encabezado'))
BEGIN
    ALTER TABLE dbo.Ticket_Encabezado ADD Factura_Credito_SFA_Credito varchar(50) NOT NULL CONSTRAINT DF_Ticket_Encabezado_Factura_Credito_SFA_Credito DEFAULT ('')
    EXECUTE Sp_addextendedproperty N'MS_Description', N'Número de crédito que el SFA asignó al autorizar el documento. Vacío = el documento no tuvo autorización del SFA. Staging: PV_Cerrar_Caja lo copia a Factura_Encabezado.Factura_Credito_SFA_Credito.', N'SCHEMA', N'dbo', N'TABLE', N'Ticket_Encabezado', N'COLUMN', N'Factura_Credito_SFA_Credito'
END
GO

IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Credito_SFA_Referencia' AND object_id = Object_id('Ticket_Encabezado'))
BEGIN
    ALTER TABLE dbo.Ticket_Encabezado ADD Factura_Credito_SFA_Referencia varchar(15) NOT NULL CONSTRAINT DF_Ticket_Encabezado_Factura_Credito_SFA_Referencia DEFAULT ('')
    EXECUTE Sp_addextendedproperty N'MS_Description', N'Referencia estable (idExterno, hasta 15 caracteres) con la que se pidió la validación al SFA. Se guarda siempre que se haya llamado al SFA, incluso sin conexión, para conciliar con Dos Pinos. Vacío = no se consultó al SFA. Staging: PV_Cerrar_Caja lo copia a Factura_Encabezado.Factura_Credito_SFA_Referencia.', N'SCHEMA', N'dbo', N'TABLE', N'Ticket_Encabezado', N'COLUMN', N'Factura_Credito_SFA_Referencia'
END
GO
