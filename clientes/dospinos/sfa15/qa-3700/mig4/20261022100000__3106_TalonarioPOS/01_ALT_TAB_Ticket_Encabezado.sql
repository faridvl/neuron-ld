/*
Fecha: 2026/10/22
Responsable: jmccarty@ld.co.cr
Propósito: US #2144 (07 Financiamiento, US-9 Talonarios) / Task #3106: número de talonario con el que
           la caja emitió el documento en modo Talonario.

           Ticket_Encabezado es el staging central: la factura de la caja llega aquí por
           WCFSincLocalToServer.Sincr_Factura -> TFactura.Insertar_Encabezado, y PV_Cerrar_Caja la
           traslada a Factura_Encabezado (04_ALT_SP_PV_Cerrar_Caja.sql de esta migración).

           0 = el documento no es de talonario (default, cubre el histórico). Un número de talonario
           es siempre mayor que 0: el POS lo valida contra el Talonario_Rango de la sucursal.
Nombre Tabla: Ticket_Encabezado
*/

IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Talonario_Numero' AND object_id = Object_id('Ticket_Encabezado'))
BEGIN
    ALTER TABLE dbo.Ticket_Encabezado ADD Factura_Talonario_Numero bigint NOT NULL CONSTRAINT DF_Ticket_Encabezado_Factura_Talonario_Numero DEFAULT (0)
    EXECUTE Sp_addextendedproperty N'MS_Description', N'Número de talonario con el que se emitió el documento en modo Talonario (US 2144). 0 = el documento no es de talonario. Staging: PV_Cerrar_Caja lo copia a Factura_Encabezado.Factura_Talonario_Numero.', N'SCHEMA', N'dbo', N'TABLE', N'Ticket_Encabezado', N'COLUMN', N'Factura_Talonario_Numero'
END
GO
