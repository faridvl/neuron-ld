/*
Fecha: 2026/10/29
Responsable: fvillacis@ld.co.cr
Propósito: Issue 3700 (POS-10, validar crédito con SFA15): registra en LDControlDBLocalAutomatico el script que
           agrega Factura_Credito_SFA_Solicitud, Factura_Credito_SFA_Credito y Factura_Credito_SFA_Referencia a la
           Factura_Encabezado de la base LOCAL de cada caja. La caja inserta la factura primero en su base local
           (TFacturacionLocal.Insertar_Factura_Encabezado) y la sincroniza leyendo esas columnas; sin ellas el
           INSERT y el SELECT fallan con "Invalid column name" y la caja no puede facturar.

           Emp_Id/Suc_Id/Caja_Id en 0 = aplica a todas las cajas. La idempotencia es por contenido del Script, no
           por Consecutivo. Mismo patrón que la task #2223 (20261014153000__2223_ValidacionCreditoSFA/03_...).

           El MS_Description embebido va sin tildes: viaja dentro de una cadena que se ejecuta en la caja.
Nombre Tabla: LDControlDBLocalAutomatico
*/

DECLARE @SQL AS NVARCHAR(MAX) = N'
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = ''Factura_Credito_SFA_Solicitud'' AND object_id = Object_id(''Factura_Encabezado''))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Credito_SFA_Solicitud bigint NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Credito_SFA_Solicitud DEFAULT (0)
    EXECUTE Sp_addextendedproperty N''MS_Description'', ''Numero de solicitud que el SFA asigno al autorizar el credito del documento. 0 = sin autorizacion del SFA.'', N''SCHEMA'', N''dbo'', N''TABLE'', N''Factura_Encabezado'', N''COLUMN'', N''Factura_Credito_SFA_Solicitud''
END
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = ''Factura_Credito_SFA_Credito'' AND object_id = Object_id(''Factura_Encabezado''))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Credito_SFA_Credito varchar(50) NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Credito_SFA_Credito DEFAULT ('''')
    EXECUTE Sp_addextendedproperty N''MS_Description'', ''Numero de credito que el SFA asigno al autorizar el documento. Vacio = sin autorizacion del SFA.'', N''SCHEMA'', N''dbo'', N''TABLE'', N''Factura_Encabezado'', N''COLUMN'', N''Factura_Credito_SFA_Credito''
END
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = ''Factura_Credito_SFA_Referencia'' AND object_id = Object_id(''Factura_Encabezado''))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Credito_SFA_Referencia varchar(15) NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Credito_SFA_Referencia DEFAULT ('''')
    EXECUTE Sp_addextendedproperty N''MS_Description'', ''Referencia con la que se pidio la validacion al SFA. Vacio = no se consulto al SFA.'', N''SCHEMA'', N''dbo'', N''TABLE'', N''Factura_Encabezado'', N''COLUMN'', N''Factura_Credito_SFA_Referencia''
END
'

DECLARE @Consecutivo int
SELECT @Consecutivo = ISNULL(MAX(Consecutivo), 0) + 1 FROM dbo.LDControlDBLocalAutomatico WITH (UPDLOCK, HOLDLOCK)

IF NOT EXISTS (SELECT 1 FROM dbo.LDControlDBLocalAutomatico WHERE Script LIKE '%Factura_Credito_SFA_Referencia%' AND Script LIKE '%Factura_Encabezado%')
BEGIN
    INSERT INTO dbo.LDControlDBLocalAutomatico
    (
         Emp_Id
        ,Suc_Id
        ,Caja_Id
        ,Consecutivo
        ,Script
        ,Fecha_Insercion
    )
    VALUES
    (
         0
        ,0
        ,0
        ,@Consecutivo
        ,@SQL
        ,GETDATE()
    )
END
GO
