
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Credito_SFA_Solicitud' AND object_id = Object_id('Factura_Encabezado'))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Credito_SFA_Solicitud bigint NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Credito_SFA_Solicitud DEFAULT (0)
    EXECUTE Sp_addextendedproperty N'MS_Description', 'Numero de solicitud que el SFA asigno al autorizar el credito del documento. 0 = sin autorizacion del SFA.', N'SCHEMA', N'dbo', N'TABLE', N'Factura_Encabezado', N'COLUMN', N'Factura_Credito_SFA_Solicitud'
END
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Credito_SFA_Credito' AND object_id = Object_id('Factura_Encabezado'))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Credito_SFA_Credito varchar(50) NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Credito_SFA_Credito DEFAULT ('')
    EXECUTE Sp_addextendedproperty N'MS_Description', 'Numero de credito que el SFA asigno al autorizar el documento. Vacio = sin autorizacion del SFA.', N'SCHEMA', N'dbo', N'TABLE', N'Factura_Encabezado', N'COLUMN', N'Factura_Credito_SFA_Credito'
END
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = 'Factura_Credito_SFA_Referencia' AND object_id = Object_id('Factura_Encabezado'))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Credito_SFA_Referencia varchar(15) NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Credito_SFA_Referencia DEFAULT ('')
    EXECUTE Sp_addextendedproperty N'MS_Description', 'Referencia con la que se pidio la validacion al SFA. Vacio = no se consulto al SFA.', N'SCHEMA', N'dbo', N'TABLE', N'Factura_Encabezado', N'COLUMN', N'Factura_Credito_SFA_Referencia'
END
