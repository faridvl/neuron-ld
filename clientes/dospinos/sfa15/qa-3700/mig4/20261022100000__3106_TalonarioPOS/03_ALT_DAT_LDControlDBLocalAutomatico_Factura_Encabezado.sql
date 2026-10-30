/*
Fecha: 2026/10/22
Responsable: jmccarty@ld.co.cr
Propósito: US #2144 (07 Financiamiento, US-9 Talonarios) / Task #3106: registra en
           LDControlDBLocalAutomatico el script que agrega Factura_Talonario_Numero a la
           Factura_Encabezado de la base LOCAL de cada caja. La caja inserta la factura primero en su
           base local (TFacturacionLocal.Insertar_Factura_Encabezado) y revisa ahí que el número de
           talonario no esté en un documento que todavía no se sincronizó.

           Emp_Id/Suc_Id/Caja_Id en 0 = aplica a todas las cajas. La idempotencia es por el texto
           del ALTER dentro del Script, no por Consecutivo. Mismo patrón que la task #2223
           (20261014153000__2223_ValidacionCreditoSFA/03_...).

           El MS_Description embebido va sin tildes: viaja dentro de una cadena que se ejecuta en
           la caja, igual que en los precedentes #1829, #2163 y #2223.
Nombre Tabla: LDControlDBLocalAutomatico
*/

DECLARE @SQL AS NVARCHAR(MAX) = N'
IF NOT EXISTS(SELECT 1 FROM sys.columns WHERE NAME = ''Factura_Talonario_Numero'' AND object_id = Object_id(''Factura_Encabezado''))
BEGIN
    ALTER TABLE dbo.Factura_Encabezado ADD Factura_Talonario_Numero bigint NOT NULL CONSTRAINT DF_Factura_Encabezado_Factura_Talonario_Numero DEFAULT (0)
    EXECUTE Sp_addextendedproperty N''MS_Description'', ''Numero de talonario con el que se emitio la factura en modo Talonario. 0 = la factura no es de talonario.'', N''SCHEMA'', N''dbo'', N''TABLE'', N''Factura_Encabezado'', N''COLUMN'', N''Factura_Talonario_Numero''
END
'

DECLARE @Consecutivo int
SELECT @Consecutivo = ISNULL(MAX(Consecutivo), 0) + 1 FROM dbo.LDControlDBLocalAutomatico WITH (UPDLOCK, HOLDLOCK)

IF NOT EXISTS (SELECT 1 FROM dbo.LDControlDBLocalAutomatico WHERE Script LIKE '%ALTER TABLE dbo.Factura_Encabezado ADD Factura_Talonario_Numero bigint%')
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
