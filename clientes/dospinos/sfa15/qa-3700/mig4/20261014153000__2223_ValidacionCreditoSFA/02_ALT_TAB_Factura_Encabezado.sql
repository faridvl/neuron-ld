/*
Fecha: 2026/10/14
Responsable: jmccarty@ld.co.cr
Propósito: US #1296 (07 Financiamiento) / Task #2223: indicador de si el crédito de la factura fue
           validado por el sistema externo de financiamiento (SFA). Mismos valores que
           Ticket_Encabezado.Factura_Validacion_Credito (01_ALT_TAB_Ticket_Encabezado.sql):
             0 = No aplica (default, cubre el histórico), 1 = Validado por el SFA, 2 = Sin validar.

           La columna de la base local de la caja se agrega en
           03_ALT_DAT_LDControlDBLocalAutomatico_Factura_Encabezado.sql.
Nombre Tabla: Factura_Encabezado
*/

IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Validacion_Credito' AND object_id = Object_id('Factura_Encabezado'))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Validacion_Credito tinyint NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Validacion_Credito DEFAULT (0)
    EXECUTE Sp_addextendedproperty N'MS_Description', N'Validación del crédito contra el sistema externo de financiamiento (SFA). 0 = no aplica (el documento no requiere validación del SFA, o es anterior a este feature), 1 = validado y autorizado por el SFA, 2 = sin validar (sin conexión con el SFA, o documento de talonario).', N'SCHEMA', N'dbo', N'TABLE', N'Factura_Encabezado', N'COLUMN', N'Factura_Validacion_Credito'
END
GO
