/*
Fecha: 2026/10/14
Responsable: jmccarty@ld.co.cr
Propósito: US #1296 (07 Financiamiento) / Task #2223: registra en LDControlDBLocalAutomatico el
           script que agrega Factura_Validacion_Credito a la Factura_Encabezado de la base LOCAL de
           cada caja. La caja inserta la factura primero en su base local
           (TFacturacionLocal.Insertar_Factura_Encabezado); sin la columna, ese INSERT falla con
           "Invalid column name" y la caja no puede facturar.

           Emp_Id/Suc_Id/Caja_Id en 0 = aplica a todas las cajas. La idempotencia es por contenido
           del Script, no por Consecutivo. Mismo patrón que la task #2163
           (20260930120000__2163_Modal_Tipos_Credito/05_...).

           El MS_Description embebido va sin tildes: viaja dentro de una cadena que se ejecuta en
           la caja, igual que en los precedentes #1829 y #2163.
Nombre Tabla: LDControlDBLocalAutomatico
*/

DECLARE @SQL AS NVARCHAR(MAX) = N'
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = ''Factura_Validacion_Credito'' AND object_id = Object_id(''Factura_Encabezado''))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Validacion_Credito tinyint NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Validacion_Credito DEFAULT (0)
    EXECUTE Sp_addextendedproperty N''MS_Description'', ''Validacion del credito contra el sistema externo de financiamiento (SFA). 0 = no aplica, 1 = validado y autorizado por el SFA, 2 = sin validar (sin conexion con el SFA, o documento de talonario).'', N''SCHEMA'', N''dbo'', N''TABLE'', N''Factura_Encabezado'', N''COLUMN'', N''Factura_Validacion_Credito''
END
'

DECLARE @Consecutivo int
SELECT @Consecutivo = ISNULL(MAX(Consecutivo), 0) + 1 FROM dbo.LDControlDBLocalAutomatico WITH (UPDLOCK, HOLDLOCK)

IF NOT EXISTS (SELECT 1 FROM dbo.LDControlDBLocalAutomatico WHERE Script LIKE '%Factura_Validacion_Credito%' AND Script LIKE '%Factura_Encabezado%')
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
