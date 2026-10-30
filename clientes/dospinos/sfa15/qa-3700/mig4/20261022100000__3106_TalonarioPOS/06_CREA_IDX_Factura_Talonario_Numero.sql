/*
Fecha: 2026/10/23
Responsable: jmccarty@ld.co.cr
Propósito: US #2144 (07 Financiamiento, US-9 Talonarios) / Task #3106: índices para la validación
           en línea de "número de talonario ya usado" (TTalonarioRango.Consultar_Numero), que busca
           el número en Ticket_Encabezado y Factura_Encabezado de toda la empresa. Sin índice esa
           búsqueda recorre todo el histórico de facturas de la empresa y puede pasar el tiempo de
           espera del POS, que entonces solo valida contra la caja.

           Índice normal, no filtrado: un índice filtrado exige ciertas opciones SET en cada INSERT
           de estas tablas, y no todas las conexiones del sistema las garantizan.

           También deja la descripción de Factura_Encabezado.Factura_Talonario_Numero con la regla
           vigente (único por empresa) en las bases donde 02_ALT_TAB_Factura_Encabezado.sql ya se
           aplicó con la descripción anterior.
Nombre Tabla: Ticket_Encabezado, Factura_Encabezado
*/

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Ticket_Encabezado_Emp_Id_Factura_Talonario_Numero' AND object_id = OBJECT_ID('dbo.Ticket_Encabezado'))
BEGIN
    CREATE NONCLUSTERED INDEX IX_Ticket_Encabezado_Emp_Id_Factura_Talonario_Numero
        ON dbo.Ticket_Encabezado (Emp_Id, Factura_Talonario_Numero)
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_Factura_Encabezado_Emp_Id_Factura_Talonario_Numero' AND object_id = OBJECT_ID('dbo.Factura_Encabezado'))
BEGIN
    CREATE NONCLUSTERED INDEX IX_Factura_Encabezado_Emp_Id_Factura_Talonario_Numero
        ON dbo.Factura_Encabezado (Emp_Id, Factura_Talonario_Numero)
END
GO

DECLARE @Descripcion NVARCHAR(500) = N'Número de talonario con el que se emitió la factura en modo Talonario (US 2144). Es único por empresa: un número usado en cualquier sucursal no se vuelve a usar, salvo en los dos documentos de una venta separada (WI 1887), que comparten la misma boleta. 0 = la factura no es de talonario, o es anterior a este feature.'

IF EXISTS (SELECT 1 FROM sys.extended_properties
           WHERE major_id = OBJECT_ID('dbo.Factura_Encabezado')
             AND minor_id = COLUMNPROPERTY(OBJECT_ID('dbo.Factura_Encabezado'), 'Factura_Talonario_Numero', 'ColumnId')
             AND name = 'MS_Description')
BEGIN
    EXECUTE sys.sp_updateextendedproperty N'MS_Description', @Descripcion, N'SCHEMA', N'dbo', N'TABLE', N'Factura_Encabezado', N'COLUMN', N'Factura_Talonario_Numero'
END
GO
