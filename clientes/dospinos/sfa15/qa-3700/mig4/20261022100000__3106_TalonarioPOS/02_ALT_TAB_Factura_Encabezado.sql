/*
Fecha: 2026/10/22
Responsable: jmccarty@ld.co.cr
Propósito: US #2144 (07 Financiamiento, US-9 Talonarios) / Task #3106: número de talonario con el que
           se emitió la factura en modo Talonario. Misma semántica que
           Ticket_Encabezado.Factura_Talonario_Numero (01_ALT_TAB_Ticket_Encabezado.sql):
             0 = la factura no es de talonario (default, cubre el histórico).

           La columna de la base local de la caja se agrega en
           03_ALT_DAT_LDControlDBLocalAutomatico_Factura_Encabezado.sql.
Nombre Tabla: Factura_Encabezado
*/

IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Talonario_Numero' AND object_id = Object_id('Factura_Encabezado'))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Talonario_Numero bigint NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Talonario_Numero DEFAULT (0)
    EXECUTE Sp_addextendedproperty N'MS_Description', N'Número de talonario con el que se emitió la factura en modo Talonario (US 2144). Es único por empresa: un número usado en cualquier sucursal no se vuelve a usar, salvo en los dos documentos de una venta separada (WI 1887), que comparten la misma boleta. 0 = la factura no es de talonario, o es anterior a este feature.', N'SCHEMA', N'dbo', N'TABLE', N'Factura_Encabezado', N'COLUMN', N'Factura_Talonario_Numero'
END
GO
