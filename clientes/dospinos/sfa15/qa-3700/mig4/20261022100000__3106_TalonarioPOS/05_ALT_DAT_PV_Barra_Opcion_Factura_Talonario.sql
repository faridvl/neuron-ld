/*
Fecha: 2026/10/22
Responsable: jmccarty@ld.co.cr
Propósito: US #2144 (07 Financiamiento, US-9 Talonarios) / Task #3106: agrega el botón
           "Factura Talonario" a la barra de LD Facturación (Barra 4, F4). El botón activa el modo
           Talonario para el documento en curso; si la caja no tiene Caja_Modo_Talonario, el POS
           muestra una alerta y no hace nada más.

           El Nombre 'Factura_Talonario' tiene que coincidir exacto con el miembro del enum
           TTipo_Function de INTERFACE/FACTURACION/Facturacion/TBarra.vb: la fila de esta tabla y el
           enum se relacionan por nombre, no por posición.

           El texto va en dos palabras, como el resto de la barra: el botón parte el texto en una
           línea por palabra y con tres empuja y corta el ícono de la tecla.
           Re-ejecutable: si el botón ya existe solo se corrige el texto. Si otro botón ya ocupa F4 en
           la Barra 4 de este ambiente, no se sobreescribe: se informa y el botón se ubica a mano.
Nombre Tabla: PV_Barra_Opcion
*/

IF EXISTS (SELECT 1 FROM dbo.PV_Barra_Opcion WHERE Nombre = 'Factura_Talonario')
BEGIN
    UPDATE dbo.PV_Barra_Opcion
    SET    Texto = 'Factura Talonario', BO_Fec_Actualizacion = GETDATE()
    WHERE  Nombre = 'Factura_Talonario' AND Texto <> 'Factura Talonario'

    PRINT 'La opción de barra Factura_Talonario ya estaba registrada. Solo se asegura su texto.'
END
ELSE IF EXISTS (SELECT 1 FROM dbo.PV_Barra_Opcion WHERE FX = 'F4' AND Barra = '4')
BEGIN
    PRINT '*** AVISO: F4 de la Barra 4 ya está ocupado por otro botón en este ambiente. No se agregó Factura_Talonario.'
END
ELSE
BEGIN
    INSERT INTO dbo.PV_Barra_Opcion (Nombre, FX, Barra, Texto, ImageIndex, ToolTip, BO_Fec_Actualizacion, Enabled, BO_Padre)
    VALUES ('Factura_Talonario', 'F4', '4', 'Factura Talonario', '0', 'Activa el modo Talonario para este documento', GETDATE(), 'CA', '')

    PRINT 'Se agregó la opción de barra Factura_Talonario'
END
GO
