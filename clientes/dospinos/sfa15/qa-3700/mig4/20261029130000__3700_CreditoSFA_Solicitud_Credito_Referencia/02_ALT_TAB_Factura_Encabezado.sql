/*
Fecha: 2026/10/29
Responsable: fvillacis@ld.co.cr
Propósito: Issue 3700 (POS-10, validar crédito con SFA15): guarda en la factura central la autorización del SFA
           (solicitud y crédito) y la referencia con la que se pidió la validación. Mismas columnas y
           significado que Ticket_Encabezado (01_ALT_TAB_Ticket_Encabezado.sql).

           La columna de la base local de la caja se agrega en
           03_ALT_DAT_LDControlDBLocalAutomatico_Factura_Encabezado.sql.
Nombre Tabla: Factura_Encabezado
*/

IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Credito_SFA_Solicitud' AND object_id = Object_id('Factura_Encabezado'))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Credito_SFA_Solicitud bigint NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Credito_SFA_Solicitud DEFAULT (0)
    EXECUTE Sp_addextendedproperty N'MS_Description', N'Número de solicitud que el SFA asignó al autorizar el crédito del documento. 0 = el documento no tuvo autorización del SFA (sin crédito, rechazado, o sin conexión).', N'SCHEMA', N'dbo', N'TABLE', N'Factura_Encabezado', N'COLUMN', N'Factura_Credito_SFA_Solicitud'
END
GO

IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Credito_SFA_Credito' AND object_id = Object_id('Factura_Encabezado'))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Credito_SFA_Credito varchar(50) NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Credito_SFA_Credito DEFAULT ('')
    EXECUTE Sp_addextendedproperty N'MS_Description', N'Número de crédito que el SFA asignó al autorizar el documento. Vacío = el documento no tuvo autorización del SFA.', N'SCHEMA', N'dbo', N'TABLE', N'Factura_Encabezado', N'COLUMN', N'Factura_Credito_SFA_Credito'
END
GO

IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Credito_SFA_Referencia' AND object_id = Object_id('Factura_Encabezado'))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Credito_SFA_Referencia varchar(15) NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Credito_SFA_Referencia DEFAULT ('')
    EXECUTE Sp_addextendedproperty N'MS_Description', N'Referencia estable (idExterno, hasta 15 caracteres) con la que se pidió la validación al SFA. Se guarda siempre que se haya llamado al SFA, incluso sin conexión, para conciliar con Dos Pinos. Vacío = no se consultó al SFA.', N'SCHEMA', N'dbo', N'TABLE', N'Factura_Encabezado', N'COLUMN', N'Factura_Credito_SFA_Referencia'
END
GO
