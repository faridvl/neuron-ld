/*
Fecha: 2026/10/14
Responsable: jmccarty@ld.co.cr
Propósito: US #1296 (07 Financiamiento) / Task #2223: indicador de si el crédito del documento fue
           validado por el sistema externo de financiamiento (SFA).

           Ticket_Encabezado es el staging central: la factura de la caja llega aquí por
           WCFSincLocalToServer.Sincr_Factura -> TFactura.Insertar_Encabezado, y PV_Cerrar_Caja la
           traslada a Factura_Encabezado (04_ALT_SP_PV_Cerrar_Caja.sql de esta migración).

           Valores:
             0 = No aplica: el documento no requiere validación del SFA (default, cubre el histórico).
             1 = Validado y autorizado por el SFA.
             2 = Sin validar: no hubo conexión con el SFA al emitir (o, en US-9, documento de talonario).

           El nombre no usa "Contingencia" a propósito: Factura_Num_Contingencia ya es la
           contingencia de factura electrónica (Hacienda), un concepto distinto.
Nombre Tabla: Ticket_Encabezado
*/

IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Validacion_Credito' AND object_id = Object_id('Ticket_Encabezado'))
BEGIN
    ALTER TABLE dbo.Ticket_Encabezado ADD Factura_Validacion_Credito tinyint NOT NULL CONSTRAINT DF_Ticket_Encabezado_Factura_Validacion_Credito DEFAULT (0)
    EXECUTE Sp_addextendedproperty N'MS_Description', N'Validación del crédito contra el sistema externo de financiamiento (SFA). 0 = no aplica (el documento no requiere validación del SFA), 1 = validado y autorizado por el SFA, 2 = sin validar (sin conexión con el SFA, o documento de talonario). Staging: PV_Cerrar_Caja lo copia a Factura_Encabezado.Factura_Validacion_Credito.', N'SCHEMA', N'dbo', N'TABLE', N'Ticket_Encabezado', N'COLUMN', N'Factura_Validacion_Credito'
END
GO
