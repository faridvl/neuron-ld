/*
Fecha: 2026/10/22
Responsable: jmccarty@ld.co.cr
Propósito: US #2144 (07 Financiamiento, US-9 Talonarios) / Task #3106: agrega Factura_Talonario_Numero
           al traslado Ticket_Encabezado -> Factura_Encabezado que hace este SP al cerrar la caja,
           para que la factura central conserve el número de talonario con el que se emitió.

           Recrea el SP completo (CREATE OR ALTER) sobre la versión de la task #3058
           (20261019210100__3058_PV_Cerrar_Caja_Cliente_Relacionado), que ya incluye
           Factura_Validacion_Credito y Cliente_Relacionado. Requiere 01_ALT_TAB_Ticket_Encabezado.sql y
           02_ALT_TAB_Factura_Encabezado.sql de esta misma migración.

           Definición versionada: NEGOCIO/Database/GENERAL/routines/procedures/caja/PV_Cerrar_Caja.sql
Nombre Objeto: PV_Cerrar_Caja (stored procedure)
*/
/****** Object:  StoredProcedure [dbo].[PV_Cerrar_Caja]    Script Date: 7/20/2026 10:35:47 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Modificado Por:  <Alejandro Mora Monge>    
-- Fecha Modificación: <2013-Jun-05>    
-- Descripción:   <Se inserta en Factura_Encabezado los campos Factura_Observacion, Factura_Devolucion_Efectivo >    
    
-- Modificado Por:  <Oscar Bravo Badilla>    
-- Fecha Modificación: <2014-01-14>    
-- Descripción:   <Se elimina condición de Operacion_id = @Operacion_id en la selección de Tickets     
--      y se inserta en Factura_encabezado el valor del parámetro @Operacion_Id>    
    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2014-May-15>    
-- Descripción:   <Se inserta en Factura_Encabezado campos nuevos (de Factura_Cliente_Telefono hasta Factura_Unidad_Simbolo)>    
-- =============================================         
-- Modificado Por:  <Jhonatan Solano>    
-- Fecha Modificación: <2014-Sep-03>    
-- Descripción:   <Se agrega el traslado de campos de servicio externo, y las tablas del servicio externo>    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2015-Feb-11>    
-- Descripción:   <Se elimina Gastos>    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2015-Dic-14>    
-- Descripción:   <En la tabla de Factura_Detalle se agrega campo nuevo de Detalle_Precio_Original>    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2016-Mar-29>    
-- Descripción:   <Al insertar las observaciones se agregan campos de GrupoObs_Id, Observ_Custom_Id y FacObs_Nombre>    
    
-- Modificado Por:  <Jonathan Solano Garita>    
-- Fecha Modificación: <2016-Set-16>    
-- Descripción:   <Se agrega el campo 'Guid' relacionado al RQ de Integración Tarjetas BNCR - Laro>    
    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2017-Nov-21>    
-- Descripción:   <Cambios CA>    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2018-Mar-14>    
-- Descripción:   <Campo nuevo de resolucion>    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2018-Mar-22>    
-- Descripción:   <Tabla nueva de aseguradora><Se agregan campos varios aseguradora>    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2018-Abr-10>    
-- Descripción:   <Tabla nueva de convenio>    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2018-May-04>    
-- Descripción:   <Campo nuevo convenio>    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2018-May-15>    
-- Descripción:   <Tabla nueva de descuento laboratorio>    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2018-JUN-18>    
-- Descripción:   <Se pasan nuevos campos a Factura_detalle_aseguradora>    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2018-JUL-06>    
-- Descripción:   <Se pasan nuevos campos a Factura_Detalle (Desc_Financiero)>    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2018-JUL-12>    
-- Descripción:   <Se pasan nuevos campos a Factura_Detalle (PV_Alerta_Id)>    
-- Modificado Por:  <Jose luis Granados>    
-- Fecha Modificación: <2018-JUL-18>    
-- Descripción:   <Se pasan nuevos campos a Factura_Encabezado (Factura_Numero_CAI)>    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2018-AGO-24>    
-- Descripción:   <Se pasan nuevos campos a Factura_Encabezado (Resolucion_Fec_Vencimiento)>    
-- Modificado Por:  <Jose Luis Granados Andrade>    
-- Fecha Modificación: <2018-OCT-04>    
-- Descripción:   <Se eliminan las tablas de aseguradoras y convenios>    
-- Modificado Por:  <Humberto Ramírez Morera>    
-- Fecha Modificación: <2018-OCT-25>    
-- Descripción:   <Se toman en cuenta las nuevas columnas de F.E>    
-- Modificado Por:  <Edgar Román Olivares>    
-- Fecha Modificación: <2019-May-12>    
-- Descripción:   <Se pasan nuevos campos a Factura_Detalle_Impuestos (Impuesto_Porc_Original, Impuesto_Porc_Exoneracion)>    
-- =============================================    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2019-MAY-20>    
-- Descripción:   <No toma en cuenta operacion_id para pasar las facturas>     
-- =============================================      
-- Modificado Por:  <Edgar Román Olivares>    
-- Fecha Modificación: <2019-Jun-06>    
-- Descripción:   <Se elimina el campo registro doc>    
-- =============================================      
-- Modificado Por:  <Edgar Román Olivares>    
-- Fecha Modificación: <2020-May-19>    
-- Descripción:   <Se agregan los campos: Impuesto_Porc_Original, Impuesto_Porc_Exoneracion a la tabla Factura_Detalle_Servicio_Impuestos y Ticket_Detalle_Impuestos RQ-Exoneraciones Servicios>    
-- ==============================================    
-- Modificado Por:  <Jonathan Solano Garita>    
-- Fecha Modificación: <2020-Jul-13>    
-- Descripción:   <Se agrega el campo: Operacion_Id a la tabla Factura_Forma_Pago Integración Credomatic WEB>    
-- ==============================================    
-- Modificado Por:  <Joselin Corrales>    
-- Fecha Modificación: <2020-Jul-24>    
-- Descripción:   <Se agrega campos Pago_Transferencia, Cuenta_Id en Factura_Forma_Pago >    
-- ==============================================    
-- Modificado Por:  <Jorge Hernández Centeno>    
-- Fecha Modificación: <07/04/2022>    
-- Descripción:   <Se agrega campos FP_GiftCard, FP_Transferencia y FP_Otra en encabezado de factura >    
-- ==============================================    
-- Modificado Por:  <Jorge Hernández Centeno>    
-- Fecha Modificación: <07/04/2022>    
-- Descripción:   <Se agrega pase de tabla Ticket_Detalle_Lote a Factura_Detalle_Lote >    
-- ==============================================    
-- Modificado Por:  <Humberto Ramirez Morera>    
-- Fecha Modificación: <10-nov-2022>    
-- Descripción:   <Se agrega pase de tabla Detalle_Cupon_Numero a Factura_Detalle_Cupon >    
-- ==============================================    
-- Modificado por:     <Cinthya Núñez Saborío>    
-- Fecha   :     <15/Nov/2022>    
-- Descripción  :     <Se agrega columna del IVA Devuelto RQ-031-0121>    
-- =============================================     
-- Modificado Por:  <Edgar Román Olivares>    
-- Fecha Modificación: <2022-Nov-23>    
-- Descripción:   <Se agrega el campo 'Detalle_Venta_Extraordinaria' en la tabla 'Ticket_Detalle' para que pase a 'Factura_Detalle' RQ_031_110>    
--=============================================    
-- Modificado Por:  <Humberto Ramirez Morera>    
-- Fecha Modificación: <2022-dic-27>    
-- Descripción:   <Se agregan los campos de Item Groups y detalle_linea_id, del RQ-031-0117 Ofertas Basadas en Item Groups>    
--=============================================    
-- Modificado Por:  <Cinthya Núñez Saborío>    
-- Fecha Modificación: <2024-may-13>    
-- Descripción:   <Se agregan campo Factura_QVet.  RQ-031-0131>    
--=============================================    
-- Modificado Por:  <Carlos A. López Díaz>    
-- Fecha Modificación: <2025-jul-10>    
-- Descripción:   <Se agregan campos FE_CodigoActividad,Factura_Exonera_Ley_Articulo, Factura_Exonera_Ley_Inciso, Factura_Exonera_Otro_Tipo,     
--      Factura_Exonera_Codigo_Institucion al INSERT INTO dbo.Factura_Encabezado>    
--=============================================    
-- Modificado Por:  <Carlos A. López Díaz>    
-- Fecha Modificación: <2025-jul-23>    
-- Descripción:   <Se agregan campo Detalle_Venta_Cruzada AL SELECT Ticket_Detalle, INSERT INTO dbo.Factura_Detalle>    
--=============================================    
-- Modificado Por: Carlos A. López Díaz, 
-- Fecha Modificación:21 noviembre 2025
-- Detail: Task 221 - POS | Comprobante con forma de pago dinámica: impresión y reimpresión, https://surl.li/ejqcbh
-- Descripción: Se agregar SubTipo_Id al insert / select de formas de pago.
--============================================= 
--Modificado Por: Carlos A. López Díaz, 12 febrero 2026
--Detail: Task 243: POS | Aplicar tarifa reducida
--Descripción: Se agrega campo Grupo_Impuesto_Id al insert select de los impuesto        
--============================================= 
--Modificado Por: Carlos A. López Díaz, 16 abril 2026
--Detail: Task 441: Site | Carga masiva de sugeridos
--Descripción: Se agrega campo Detalle_Venta_Cruzada_Id AL SELECT Ticket_Detalle, INSERT INTO dbo.Factura_Detalle
--============================================= 
--Modificado Por: Joshua Loría B, 27 abril 2026
--Detail: Task 481: POS | Sincronizar datos del transportista en la factura
--Descripción: Se agregan los campos Factura_Proveedor, Prov_Id, Prov_Codigo_Interfaz, relacionados al transportista en el SP de cierre de caja para que se sincronicen en la factura.
--=============================================
--Modificado Por: Joshua Loría B, 28 abril 2026
--Detail: Task 478: Site | Crear reporte de facturas con flete
--Descripción: Se agrega el campo Detalle_Articulo_Tipo_Flete a las tablas detalle para indicar el tipo de flete. Es necesario para el reporte y ticket de transportista para calculo de montos de flete.
--=============================================
--Modificado Por: Carlos A. López Díaz, 25 junio 2026
--Detail: Task 543: Sincronización a BD local
--Descripción: Se agrega sinc de la tabla Ticket_Detalle_Combo a Factura_Detalle_Combo
--=============================================
--Modificado Por: Carlos A. López Díaz, 25 junio 2026
--Detail: Task 543: Sincronización a BD local
--Descripción: Se agrega sinc de la tabla Ticket_Detalle_Combo a Factura_Detalle_Combo
--=============================================
-- Modificado Por:		<Jorge Hernández Centeno>    
-- Fecha Modificación:	<10/07/2026>    
-- Descripción:			<Se registra campo bonificacion_id en detalle de la factura y se verifica pase de la tabla Ticket_Detalle_Bono a Factura_Detalle_Bono >    
-- ==============================================    
--Modificado Por: Jirgort McCarty Vásquez, 20 julio 2026
--Detail: Task 1495: POS | Nombre de Datos Tributarios en tiquete
--Descripción: Se agrega el campo Factura_Cliente_Tributario al INSERT INTO dbo.Factura_Encabezado / SELECT FROM dbo.Ticket_Encabezado, para separar el nombre del receptor tributario FE (Datos_Tributarios_FE.Nombre) del nombre del cliente LDCOM (Factura_Cliente).
--=============================================
--Modificado Por: vvalverde@ld.co.cr, 22 septiembre 2026
--Detail: Task 240: POS | Aplicar exoneraciones guardadas
--Descripción: Se agrega campo Cliente_Exoneracion_Consecutivo al SELECT Ticket_Detalle, INSERT INTO dbo.Factura_Detalle, para que la Factura Electrónica reporte el documento correcto por línea.
--=============================================

--Modificado Por: Jirgort McCarty Vásquez, 27 agosto 2026
--Detail: Task 1683 (US 1386): POS | Preventa - Sucursal de Facturación
--Descripción: Se agrega el campo Suc_Id_Origen al INSERT INTO dbo.Factura_Encabezado / SELECT FROM dbo.Ticket_Encabezado, para que la factura central conserve la sucursal donde se originó la preventa cuando el Tipo de Preventa está configurado para facturar en una sucursal distinta a la de la caja. 0 = no aplica (venta directa, o preventa originada en la misma sucursal que facturó).
--=============================================

--Modificado Por: Carlos A. López Díaz, 09 septiembre 2026
--Detail: Task 1835: POS/Preventa - ventana de captura de número de receta al imprimir
--Descripción: Se agrega el pase de Ticket_Detalle_Receta a Factura_Detalle_Receta al cerrar caja (igual patrón que Series), y el borrado del detalle temporal de receta.
--=============================================

--Modificado Por: Jirgort McCarty Vasquez, 09 setiembre 2026
--Detail: Task 1829 (US 1284): POS y Preventa - Selector de Centro de Costo para Autoconsumo y Regalia
--Descripcion: Se agrega el campo Ceco_Id al INSERT INTO dbo.Factura_Encabezado, tomandolo del SELECT sobre dbo.Ticket_Encabezado, para que la factura central conserve el centro de costo exigido en los subdocumentos de Autoconsumo y Regalia. 0 = el documento no requiere centro de costo.
--=============================================

--Modificado Por: Carlos A. López Díaz, 22 septiembre 2026
--Detail: Task 1849: Reporte Descuentos Manuales
--Descripcion: Se agrega el pase de Usuario_Id_Autoriza de Ticket_Detalle_Descuento a Factura_Detalle_Descuento al cerrar caja (usuario que queda registrado como responsable del descuento manual).
--=============================================

--Modificado Por: Jirgort McCarty Vasquez, 28 setiembre 2026
--Detail: Task 1887 (US 1814): Particion de Factura por Exoneracion con Articulo Bonificado
--Descripcion: Se agrega el campo Factura_Id_Relacionada al INSERT INTO dbo.Factura_Encabezado, tomandolo del SELECT sobre dbo.Ticket_Encabezado, para que la factura central conserve el enlace entre los dos documentos que produce la particion. 0 = el documento no fue partido.
--=============================================

--Modificado Por: Joshua Loria B, 30 septiembre 2026
--Detail: Task 2163 (US 1398): POS y Preventa - Modal de Tipos de Credito
--Descripcion: Se agregan los campos PlanFinanciamiento_Id, PlanFinanciamiento_Plazo_Semanas y PlanFinanciamiento_Tasa_Interes al INSERT INTO dbo.Factura_Encabezado, tomandolos del SELECT sobre dbo.Ticket_Encabezado, para que la factura central conserve el Tipo de Credito aplicado. 0 = el documento no aplica Tipo de Credito.
--=============================================

--Modificado Por: fvillacis@ld.co.cr, 05 octubre 2026
--Detail: Issue 2261: Reporte Bonificaciones de Venta Aplicadas
--Descripción: Se agrega Detalle_Precio_Bono al pase de Ticket_Detalle_Bono a Factura_Detalle_Bono (precio del artículo regalado al momento de la venta).
--=============================================
--=============================================
--Modificado Por: Jirgort McCarty Vasquez, 22 octubre 2026
--Detail: Task 3106 (US 2144): Talonarios en el POS
--Descripcion: Se agrega el campo Factura_Talonario_Numero al INSERT INTO dbo.Factura_Encabezado, tomandolo del SELECT sobre dbo.Ticket_Encabezado, para que la factura central conserve el numero de talonario con el que se emitio. 0 = el documento no es de talonario.
--=============================================
--Modificado Por: Victor Valverde Fernández, 16 octubre 2026
--Detail: Task 3058: Site | Reporte Facturas por Tipo de Creación: Cliente y Finca vacíos
--Descripcion: Se agrega el campo Cliente_Relacionado al INSERT INTO dbo.Factura_Encabezado, tomandolo del SELECT sobre dbo.Ticket_Encabezado, para que la factura central conserve la finca (o el asociado) relacionada al cliente del documento. '' = el documento no tiene cliente relacionado.
--=============================================

--Modificado Por: Jirgort McCarty Vasquez, 14 octubre 2026
--Detail: Task 2223 (US 1296): Facturacion sin validacion del SFA
--Descripcion: Se agrega el campo Factura_Validacion_Credito al INSERT INTO dbo.Factura_Encabezado, tomandolo del SELECT sobre dbo.Ticket_Encabezado, para que la factura central conserve si el credito fue validado por el SFA. 0 = no aplica, 1 = validado, 2 = sin validar.
--=============================================
CREATE OR ALTER PROCEDURE [dbo].[PV_Cerrar_Caja]
 (@Emp_id  smallint,         
  @Suc_id  smallint,        
  @Caja_id  smallint,        
  @Operacion_id int,        
  @Cierre_id int,        
  @Deposito  varchar(50),    
  @Fecha_Cierre datetime ) AS        
BEGIN        
 BEGIN TRY        
  Declare @msg  as varchar(255)        
     
  if Exists( Select 1     
     from Ticket_Cola_Acumulados With(Nolock)    
     Where Emp_id  = @Emp_id    
     And  Suc_id  = @Suc_id    
     And  caja_id  = @Caja_id    
     And  Cierre_id = @Cierre_Id    
     )    
  Begin    
   raiserror ( 'Existen documentos en cola de acumulados de la factura, no se puede realizar el cierre.', 16,1)    
    
  End     
       
  -- =============================================        
  -- Pasa las facturas al historico        
  -- =============================================        
  --- Creacion de tabla temporal        
  Create Table #Documentos         
  (  Emp_id   smallint,         
   TipoDoc_id  smallint,        
   Suc_id   smallint,        
   Caja_id   smallint,        
   Factura_id  int, )        
        
  --- Inserta tabla temporal de trabajo        
  insert into #Documentos    
   (   Emp_id,   TipoDoc_id,   suc_id , Caja_id,  Factura_id)         
  (Select   Emp_Id,  TipoDoc_id,   Suc_Id,  Caja_Id,  Factura_Id        
   from dbo.Ticket_Encabezado With(Nolock)        
   Where Emp_id   = @Emp_id         
   and  Suc_id   = @Suc_id         
   and  Caja_id   = @Caja_id       
   --and     Operacion_id    = @Operacion_id         
   and  Cierre_id  = @Cierre_id )        
        
 --- Pasa encabezado factura        
     
  INSERT INTO dbo.Factura_Encabezado        
   ( Emp_Id,      TipoDoc_id ,     Suc_Id,             
   Caja_Id,      Factura_Id,      Tipo_Id,         
   SubDoc_id,      Bodega_Id,      Cliente_Id,      
   Afiliado_Id,     Usuario_Id,      Vendedor_Id,            
   Factura_Fecha,     Factura_Articulos,    Factura_Cliente, Factura_Cliente_Tributario,           
   Factura_Puntos,     Factura_Costo,     Factura_Costo_Dolar,            
   Factura_Exento,        Factura_Exento_Bruto,     Factura_Gravado,        
   Factura_Gravado_Bruto,   Factura_Subtotal,      Factura_Descuento,        
   Factura_Descuento_Exento,  Factura_Descuento_Gravado,  Factura_Impuesto,             
   Factura_Total_Sin_Redondeo,  Factura_Total,      Factura_Saldo,         
   Factura_Porc_Desc_Global,  Factura_AcumMonedero,     MonederoTarj_id,        
   Factura_OnLine,     Operacion_id,       Cierre_id,          
   Factura_FP_Efectivo,   Factura_FP_Tarjeta,     Factura_FP_Cheque,        
   Factura_FP_Monedero,   Factura_FP_NotaCredito,     Factura_FP_Cupon,        
   Factura_FP_Puntos,    Factura_FP_CoPago,    Factura_Redondeo,            
   Factura_Cedi,     PreFactura_id,     Factura_Servicios,       
   Factura_Costo_Bonificacion,  Asiento_id,      Factura_FP_Apartado,      
   Factura_Apartado_Id,   Factura_Gasto,     Factura_Nota_Pie,       
   Factura_Nota_Encabezado,  Contacto_Id,     CF_Tarjeta_Id,        
   Factura_Origen,     Factura_Cambio_Efectivo,  Factura_Devolucion_Efectivo,     
   Factura_Clase,     Factura_Servicio_Externo,  Factura_Cliente_Telefono,      
   Factura_Cliente_Direccion,  Factura_Cliente_Cedula,   Factura_Cliente_Plazo,       
   Factura_Cliente_Precio,   Factura_Cliente_DUI,   Factura_Vendedor,        
   Factura_Usuario,    Factura_Afiliado,    Factura_Afiliado_CodigoInterno,     
   Factura_Afiliado_Parentesco, Factura_Unidad_Simbolo,   Guid,           
   Factura_Numero,     Serie_id,      Resolucion_id,         
   Resolucion_Fecha,    Resolucion_Doc_Inicio,   Resolucion_Doc_Final,       
   Resolucion_Tipo_Comprobante_FE, Identificacion_Id,    Identificacion_Nombre,       
   Identificacion_Direccion,  Factura_Estado,     Factura_Descuento_FP,       
   Factura_Descuento_Tarjeta_FP,   Factura_Numero_CAI,    Resolucion_Fec_Vencimiento,    
   Factura_FE_IdOrigen,            SubDoc_Tipo_Consecutivo,        Factura_Num_Contingencia,    
   Factura_Folio_Electronico,      Factura_Clave_Numerica,         Factura_Formato_Extranjero,         
   Formato_id_Identificacion,      Factura_Correo,     Factura_Exonera_Tipo,       
   Factura_Exonera_NumDoc,   Factura_Exonera_Nombre,   Factura_Exonera_Fecha,       
   Factura_Exonera_Porcentaje,  Factura_FP_GiftCard,   Factura_FP_Transferencia,    
   Factura_FP_Otra,    Factura_Servicios_Impuesto_Devuelto, Factura_Impuesto_Devuelto,    
   Factura_QVet,     FE_CodigoActividad,    Factura_Exonera_Ley_Articulo,     
   Factura_Exonera_Ley_Inciso,  Factura_Exonera_Otro_Tipo,  Factura_Exonera_Codigo_Institucion,
   Factura_Proveedor, Prov_Id, Prov_Codigo_Interfaz, Suc_Id_Origen, Ceco_Id,
   Factura_Id_Relacionada, PlanFinanciamiento_Id, PlanFinanciamiento_Plazo_Semanas, PlanFinanciamiento_Tasa_Interes, Factura_Validacion_Credito, Cliente_Relacionado, Factura_Talonario_Numero)
  (Select
   Emp_Id,       TipoDoc_id ,     Suc_Id,             
   Caja_Id,      Factura_Id,      Tipo_Id,         
   SubDoc_id,      Bodega_Id,      Cliente_Id,     
   Afiliado_Id,     Usuario_Id,      Vendedor_Id,            
   Factura_Fecha,     Factura_Articulos,    Factura_Cliente, Factura_Cliente_Tributario,          
   Factura_Puntos,     Factura_Costo,     Factura_Costo_Dolar,            
   Factura_Exento,     Factura_Exento_Bruto,     Factura_Gravado,        
   Factura_Gravado_Bruto,   Factura_Subtotal,      Factura_Descuento,        
   Factura_Descuento_Exento,  Factura_Descuento_Gravado,  Factura_Impuesto,             
   Factura_Total_Sin_Redondeo,  Factura_Total,      Factura_Saldo,         
   Factura_Porc_Desc_Global,  Factura_AcumMonedero,     MonederoTarj_id,        
   Factura_OnLine,     Operacion_id,       Cierre_id,          
   Factura_FP_Efectivo,   Factura_FP_Tarjeta,     Factura_FP_Cheque,        
   Factura_FP_Monedero,   Factura_FP_NotaCredito,     Factura_FP_Cupon,        
   Factura_FP_Puntos,    Factura_FP_CoPago,    Factura_Redondeo,            
   Factura_Cedi,     PreFactura_id,     Factura_Servicios,       
   Factura_Costo_Bonificacion,  Asiento_id,      Factura_FP_Apartado,      
   Factura_Apartado_Id,   Factura_Gasto,     Factura_Nota_Pie,       
   Factura_Nota_Encabezado,  Contacto_Id,     CF_Tarjeta_Id,        
   Factura_Origen,     Factura_Cambio_Efectivo,  Factura_Devolucion_Efectivo,     
   Factura_Clase,     Factura_Servicio_Externo,  Factura_Cliente_Telefono,      
   Factura_Cliente_Direccion,  Factura_Cliente_Cedula,   Factura_Cliente_Plazo,       
   Factura_Cliente_Precio,   Factura_Cliente_DUI,   Factura_Vendedor,        
   Factura_Usuario,    Factura_Afiliado,    Factura_Afiliado_CodigoInterno,     
   Factura_Afiliado_Parentesco, Factura_Unidad_Simbolo,   Guid,           
   Factura_Numero,     Serie_id,      Resolucion_id,         
   Resolucion_Fecha,    Resolucion_Doc_Inicio,   Resolucion_Doc_Final,       
   Resolucion_Tipo_Comprobante_FE, Identificacion_Id,    Identificacion_Nombre,       
   Identificacion_Direccion,  Factura_Estado,     Factura_Descuento_FP,       
   Factura_Descuento_Tarjeta_FP,   Factura_Numero_CAI,    Resolucion_Fec_Vencimiento,    
   Factura_FE_IdOrigen,            SubDoc_Tipo_Consecutivo,        Factura_Num_Contingencia,    
   Factura_Folio_Electronico,      Factura_Clave_Numerica,         Factura_Formato_Extranjero,         
   Formato_id_Identificacion,      Factura_Correo,     Factura_Exonera_Tipo,       
   Factura_Exonera_NumDoc,   Factura_Exonera_Nombre,   Factura_Exonera_Fecha,       
   Factura_Exonera_Porcentaje,  Factura_FP_GiftCard,   Factura_FP_Transferencia,    
   Factura_FP_Otra,    Factura_Servicios_Impuesto_Devuelto, Factura_Impuesto_Devuelto,    
   Factura_QVet,     FE_CodigoActividad,    Factura_Exonera_Ley_Articulo,     
   Factura_Exonera_Ley_Inciso,  Factura_Exonera_Otro_Tipo,  Factura_Exonera_Codigo_Institucion,
   Factura_Proveedor, Prov_Id, Prov_Codigo_Interfaz, Suc_Id_Origen, Ceco_Id,
   Factura_Id_Relacionada, PlanFinanciamiento_Id, PlanFinanciamiento_Plazo_Semanas, PlanFinanciamiento_Tasa_Interes, Factura_Validacion_Credito, Cliente_Relacionado, Factura_Talonario_Numero
   from  dbo.Ticket_Encabezado With(Nolock)
  Where Emp_id   = @Emp_id         
  and   TipoDoc_id  > 0        
  and   Suc_id   = @Suc_id         
  and   Caja_id   = @Caja_id       
  --and   Operacion_id    = @Operacion_id        
  and   Cierre_id  = @Cierre_id )        
      
    
  --- Pasa detalle de factura      
  Insert into dbo.Factura_Detalle         
  ( Emp_Id,      TipoDoc_id ,    Suc_Id,           
	Caja_Id,     Factura_Id,     Detalle_Id,      
	Articulo_Id,    Bodega_Id,     Detalle_Fecha,          
	Detalle_Cantidad,   Detalle_Saldo,    Detalle_Costo_Unitario,        
	Detalle_Precio_Unitario,    Detalle_Descuento_Monto, Detalle_Descuento_Porc,        
	Detalle_Impuesto_Monto,  Detalle_Impuesto_Porc,  Detalle_Gasto_Monto,          
	Detalle_Puntaje,   Detalle_Total,    Detalle_AcumMonedero,      
	Detalle_PorcMonedero,  Detalle_Regalo,    Detalle_Costo_Unitario_Dolar,       
	Detalle_Tipo_Cambio,  Detalle_Porc_Precio_Sug, Detalle_Factor_Unidades,      
	Detalle_Tiene_Serie,  Detalle_Articulo_Nombre, Detalle_Manejo_Costo,    
	Detalle_Costo_Fact,   Detalle_Unidad_Simbolo,  Detalle_Peso_Total,    
	Detalle_Precio_Original, Detalle_Desc_Financiero_Porc, Detalle_Desc_Financiero_Monto,    
	PV_Alerta_Id,    Detalle_Venta_Extraordinaria, Promocion_Grupo_Id,    
	Promocion_Grupo_Nombre,  Promocion_Grupo_Consecutivo,    
	Grupo_Id,Detalle_Venta_Cruzada,Detalle_Venta_Cruzada_Id, Detalle_Articulo_Tipo_Flete,
	Combo_Id, Bonificacion_Id, Cliente_Exoneracion_Consecutivo
  )        
  Select       
   D.Emp_Id,     D.TipoDoc_id ,    D.Suc_Id,      
   D.Caja_Id,     D.Factura_Id,    D.Detalle_Id,      
   D.Articulo_Id,    D.Bodega_Id,    D.Detalle_Fecha,      
   D.Detalle_Cantidad,   D.Detalle_Saldo,   D.Detalle_Costo_Unitario,       
   D.Detalle_Precio_Unitario,  D.Detalle_Descuento_Monto,  D.Detalle_Descuento_Porc,       
   D.Detalle_Impuesto_Monto,   D.Detalle_Impuesto_Porc, D.Detalle_Gasto_Monto,          
   D.Detalle_Puntaje,   D.Detalle_Total,   D.Detalle_AcumMonedero,      
   D.Detalle_PorcMonedero,  D.Detalle_Regalo,   D.Detalle_Costo_Unitario_Dolar,      
   D.Detalle_Tipo_Cambio,  D.Detalle_Porc_Precio_Sug,  D.Detalle_Factor_Unidades,      
   D.Detalle_Tiene_Serie,  D.Detalle_Articulo_Nombre, D.Detalle_Manejo_Costo,    
   D.Detalle_Costo_Fact,  D.Detalle_Unidad_Simbolo, D.Detalle_Peso_Total,    
   D.Detalle_Precio_Original, D.Detalle_Desc_Financiero_Porc, D.Detalle_Desc_Financiero_Monto,    
   D.PV_Alerta_Id,    D.Detalle_Venta_Extraordinaria, D.Promocion_Grupo_Id,      
   D.Promocion_Grupo_Nombre, D.Promocion_Grupo_Consecutivo,    
   D.Grupo_Id,Detalle_Venta_Cruzada,Detalle_Venta_Cruzada_Id, D.Detalle_Articulo_Tipo_Flete,
   D.Combo_Id, D.Bonificacion_Id, D.Cliente_Exoneracion_Consecutivo
  from #Documentos T,        
    dbo.Ticket_detalle D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and  D.TipoDoc_id = T.TipoDoc_id        
   and  D.Suc_id     = T.Suc_id         
   and  D.Caja_id    = T.Caja_id        
   and  D.Factura_id = T.Factura_id      
       
  --- Pasa detalle lote de factura      
  Insert into dbo.Factura_Detalle_Lote         
  ( Emp_Id,      TipoDoc_id,     Suc_Id,    
   Caja_Id,     Factura_Id,     Articulo_Id,    
   Lote_Numero,    Detalle_Id,     Lote_Cantidad,    
   Lote_Vence,     Lote_Fecha_Vencimiento,  Usuario_Id,    
   Usuario_Id_Autoriza,  Fecha_Despacho_Vale,  Fecha_Actualizacion,    
   Detalle_Linea_Id    
  )        
  Select       
   D.Emp_Id,     D.TipoDoc_id,    D.Suc_Id,    
   D.Caja_Id,     D.Factura_Id,    D.Articulo_Id,    
   D.Lote_Numero,    D.Detalle_Id,    D.Lote_Cantidad,    
   D.Lote_Vence,    D.Lote_Fecha_Vencimiento, D.Usuario_Id,    
   D.Usuario_Id_Autoriza,  D.Fecha_Despacho_Vale,  D.Fecha_Actualizacion,    
   D.Detalle_Linea_Id    
  from #Documentos T,        
    dbo.Ticket_Detalle_Lote D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and  D.TipoDoc_id = T.TipoDoc_id        
   and  D.Suc_id     = T.Suc_id         
   and  D.Caja_id    = T.Caja_id        
   and  D.Factura_id = T.Factura_id      
        
  --- Pasa Detalle Descuentos        
     Insert into dbo.Factura_Detalle_Descuento        
  ( Emp_Id,     TipoDoc_id,    Suc_Id,     Caja_Id,          
   Factura_Id,    Detalle_Id,    Articulo_Id,   Descuento_Id,      
   Descuento_Nombre,  Descuento_Monto,  Descuento_Porcentaje, Descuento_Origen,    
   Detalle_Linea_Id,  Usuario_Id_Autoriza)        
  Select D.Emp_Id,   D.TipoDoc_id,   D.Suc_Id,    D.Caja_Id,        
   D.Factura_Id,   D.Detalle_Id,   D.Articulo_Id,   D.Descuento_Id,      
   D.Descuento_Nombre,  D.Descuento_Monto,  D.Descuento_Porcentaje, D.Descuento_Origen,    
   D.Detalle_Linea_Id,  D.Usuario_Id_Autoriza    
  from #Documentos T,        
    dbo.Ticket_Detalle_Descuento D With(Nolock)        
  Where D.Emp_id  = T.Emp_id         
   and  D.TipoDoc_id = T.TipoDoc_id        
   and  D.Suc_id  = T.Suc_id         
   and  D.Caja_id  = T.Caja_id        
   and  D.Factura_id = T.Factura_id        
        
  --- Pasa Detalle Impuestos        
  Insert into dbo.Factura_Detalle_Impuestos        
  ( Emp_Id,      TipoDoc_id,     Suc_Id,    Caja_Id,        
   Factura_Id,     Detalle_Id,     Articulo_Id,  Impuesto_Id,      
   Impuesto_Porc,    Impuesto_Cant,    Impuesto_Precio, Impuesto_Porc_Original,    
   Impuesto_Porc_Exoneracion, Impuesto_Porc_Devuelto,  Impuesto_Monto_Devuelto,     
   Detalle_Linea_Id,           Grupo_Id, Grupo_Impuesto_Id)            
  Select D.Emp_Id,    D.TipoDoc_id,    D.Suc_Id,   D.Caja_Id,        
   D.Factura_Id,    D.Detalle_Id,    D.Articulo_Id,  D.Impuesto_Id,      
   D.Impuesto_Porc,   D.Impuesto_Cant,   D.Impuesto_Precio, D.Impuesto_Porc_Original,    
   D.Impuesto_Porc_Exoneracion,D.Impuesto_Porc_Devuelto, D.Impuesto_Monto_Devuelto,    
   D.Detalle_Linea_Id ,  D.Grupo_Id,D.Grupo_Impuesto_Id    
  from #Documentos T,        
    dbo.Ticket_Detalle_Impuestos D With(Nolock)        
  Where  D.Emp_id     = T.Emp_id         
   and  D.TipoDoc_id = T.TipoDoc_id        
   and  D.Suc_id     = T.Suc_id         
   and  D.Caja_id    = T.Caja_id        
   and  D.Factura_id = T.Factura_id        
        
  --- Pasa Detalle Promociones        
  Insert into dbo.Factura_Detalle_Promocion        
  ( Emp_Id,     TipoDoc_id,     Suc_Id,     Caja_Id,        
   Factura_Id,    Detalle_Id,     Articulo_Id,   Promocion_Tipo,      
   Promocion_Id,   Promocion_Nombre,   Promocion_Precio,  Detalle_Linea_Id)        
  Select D.Emp_Id,   D.TipoDoc_id,    D.Suc_Id,    D.Caja_Id,        
   D.Factura_Id,   D.Detalle_Id,    D.Articulo_Id,   D.Promocion_Tipo,      
   D.Promocion_Id,   D.Promocion_Nombre,        
   D.Promocion_Precio,  D.Detalle_Linea_Id          
  from #Documentos T,        
    dbo.Ticket_Detalle_Promocion D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
  and  D.TipoDoc_id = T.TipoDoc_id        
  and  D.Suc_id     = T.Suc_id         
  and  D.Caja_id    = T.Caja_id        
  and  D.Factura_id = T.Factura_id        
        
  --- Pasa Detalle Formas de Pago        
  Insert Into dbo.Factura_Forma_Pago        
  (  Emp_Id,      TipoDoc_id,    Suc_Id,    
    Caja_Id,     Factura_Id,    Tipo_Id,    
    Pago_Id,        Pago_Fecha,    Pago_Numero,    
    Pago_Descripcion,   Pago_Aprovacion,  Moneda_Id,    
    Banco_Id,     MonederoTarj_Id,  Tarjeta_id,    
    Pago_Total,     Pago_Total_Moneda,   Pago_Total_Tipo_Cambio,    
    Pago_Suc_Ref,    Pago_Caj_Ref,   Pago_Fac_Ref,    
    Pago_Cupon_Automatico,  Cierre_Id,    Pago_Fecha_Vencimiento,    
    Autorizador_Id,    Pago_Anulado,   Operacion_Id,    
    Pago_Transferencia,   Cuenta_Id, SubTipo_Id     
  )        
  Select D.Emp_Id,     D.TipoDoc_id,   D.Suc_Id,    
    D.Caja_Id,     D.Ticket_Id,   D.Tipo_Id,    
    D.Pago_Id,     D.Pago_Fecha,   D.Pago_Numero,    
    D.Pago_Descripcion,   D.Pago_Aprovacion,   D.Moneda_Id,    
    D.Banco_Id,     D.MonederoTarj_Id,   D.Tarjeta_id,    
    D.Pago_Total,    D.Pago_Total_Moneda, D.Pago_Total_Tipo_Cambio,    
    D.Pago_Suc_Ref,    D.Pago_Caj_Ref,   D.Pago_Fac_Ref,    
    D.Pago_Cupon_Automatico, Cierre_Id,    D.Pago_Fecha_Vencimiento,    
    D.Autorizador_Id,   D.Pago_Anulado,   D.Operacion_Id,    
    Pago_Transferencia,   Cuenta_Id, SubTipo_Id    
  From #Documentos     T,    
    dbo.Ticket_Forma_Pago  D With(NoLock)        
  Where  D.Emp_id         = T.Emp_id         
  And    D.TipoDoc_id     = T.TipoDoc_id        
  And    D.Suc_id         = T.Suc_id         
  And    D.Caja_id        = T.Caja_id        
  And    D.Ticket_Id      = T.Factura_id        
    
  --- Servicios y sus impuestos    
  Insert into dbo.Factura_Detalle_Servicio        
  ( Emp_id,    TipoDoc_id,     Suc_id,      Caja_id,        
  Factura_id,    Servicio_id,    Detalle_Monto,    Detalle_Impuesto,      
  Detalle_Total,   Detalle_Impuesto_Monto_Devuelto)        
  Select D.Emp_id,  D.TipoDoc_id,    D.Suc_id,     D.Caja_id,        
  D.Factura_id,   D.Servicio_id,    D.Detalle_Monto,   D.Detalle_Impuesto,      
  D.Detalle_Total,  D.Detalle_Impuesto_Monto_Devuelto    
  from #Documentos T,        
    dbo.Ticket_Detalle_Servicio  D With(Nolock)        
  Where D.Emp_id  = T.Emp_id         
  and  D.TipoDoc_id = T.TipoDoc_id        
  and  D.Suc_id  = T.Suc_id         
  and  D.Caja_id  = T.Caja_id        
  and  D.Factura_Id = T.Factura_id        
    
  Insert into dbo.Factura_Detalle_Servicio_Impuesto        
  ( Emp_id,     TipoDoc_id,     Suc_id,      Caja_id,        
  Factura_id,     Servicio_id,    Impuesto_Id,    Impuesto_Porc,      
  Impuesto_Monto,    Impuesto_Porc_Original,  Impuesto_Porc_Exoneracion, Impuesto_Monto_Devuelto)        
  Select D.Emp_id,   D.TipoDoc_id,    D.Suc_id,     D.Caja_id,        
  D.Factura_id,    D.Servicio_id,    D.Impuesto_Id,    D.Impuesto_Porc,      
  D.Impuesto_Monto,   D.Impuesto_Porc_Original, D.Impuesto_Porc_Exoneracion,D.Impuesto_Monto_Devuelto    
  from #Documentos T,        
    dbo.Ticket_Detalle_Servicio_Impuesto  D With(Nolock)        
  Where D.Emp_id  = T.Emp_id         
  and  D.TipoDoc_id = T.TipoDoc_id        
  and  D.Suc_id  = T.Suc_id         
  and  D.Caja_id  = T.Caja_id        
  and  D.Factura_Id = T.Factura_id        
        
  --Pasa Bonificaciones        
  Insert into dbo.Factura_Detalle_Bono        
  ( Emp_Id,    TipoDoc_Id,     Suc_Id,     Caja_Id,       
   Factura_Id,   Detalle_Id,     Articulo_Id,   Detalle_Cant_Facturado,      
   Bonificacion_Id,    Articulo_Bono,    Detalle_Cant_Bono, Detalle_Precio_Bono)        
  Select D.Emp_Id,  D.TipoDoc_Id,    D.Suc_Id,    D.Caja_Id,       
   D.Factura_Id,  D.Detalle_Id,    D.Articulo_Id,   D.Detalle_Cant_Facturado,     
   D.Bonificacion_Id, D.Articulo_Bono,   D.Detalle_Cant_Bono, D.Detalle_Precio_Bono        
  from #Documentos T,        
    dbo.Ticket_Detalle_Bono  D With(Nolock)        
  Where D.Emp_id      = T.Emp_id         
  and  D.TipoDoc_id  = T.TipoDoc_id        
  and  D.Suc_id      = T.Suc_id         
  and  D.Caja_id     = T.Caja_id        
  and  D.Factura_Id  = T.Factura_id        
        
  --Pasa Series        
  INSERT dbo.Factura_Detalle_Serie        
   (Emp_id,    TipoDoc_id,    Suc_id,    Caja_Id,        
   Factura_id,   Articulo_id,   Detalle_ID,   Detalle_Serie,    
   Detalle_Fecha,  Detalle_DiasGarantia, Detalle_Devuelto, Detalle_Fecha_Dev,    
   Detalle_Linea_Id)        
  SELECT D.Emp_id,   D.TipoDoc_id,   D.Suc_id,   D.Caja_Id,        
   D.Factura_id,   Articulo_id,   Detalle_ID,   Detalle_Serie,    
   Detalle_Fecha,   Detalle_DiasGarantia, Detalle_Devuelto, Detalle_Fecha_Dev,    
   D.Detalle_Linea_Id        
  from #Documentos T,        
    dbo.Ticket_Detalle_Serie  D With(Nolock)        
  Where D.Emp_id      = T.Emp_id         
  and  D.TipoDoc_id  = T.TipoDoc_id        
  and  D.Suc_id      = T.Suc_id         
  and  D.Caja_id     = T.Caja_id        
  and  D.Factura_Id  = T.Factura_id        
        
  --Pasa Receta        
  INSERT dbo.Factura_Detalle_Receta        
   (Emp_id,    TipoDoc_id,    Suc_id,    Caja_Id,        
   Factura_id,   Articulo_id,   Detalle_Id,   Receta_Numero)        
  SELECT D.Emp_id,   D.TipoDoc_id,   D.Suc_id,   D.Caja_Id,        
   D.Factura_id,   Articulo_id,   Detalle_Id,   Receta_Numero        
  from #Documentos T,        
    dbo.Ticket_Detalle_Receta  D With(Nolock)        
  Where D.Emp_id      = T.Emp_id         
  and  D.TipoDoc_id  = T.TipoDoc_id        
  and  D.Suc_id      = T.Suc_id         
  and  D.Caja_id     = T.Caja_id        
  and  D.Factura_Id  = T.Factura_id        
        
  -- Pasa Observaciones.        
  INSERT INTO dbo.Factura_Detalle_Observacion     
  ( Emp_Id,    TipoDoc_Id,    Suc_Id,    Caja_Id,       
   Factura_Id,   GrupoObs_Id,   Observ_Id,   Observ_Custom_Id,    
   FacObs_Valor,  FacObs_Nombre,   FacObs_Fec_Actualizacion,    
   GrupoObs_Tipo)        
  SELECT D.Emp_Id,  D.TipoDoc_Id,   D.Suc_Id,   D.Caja_Id,     
    D.Factura_Id, D.GrupoObs_Id,   D.Observ_Id,  D.Observ_Custom_Id,     
    D.FacObs_Valor, D.FacObs_Nombre,  D.FacObs_Fec_Actualizacion,    
    D.GrupoObs_Tipo        
  FROM   #Documentos AS T        
  INNER JOIN dbo.Ticket_Detalle_Observacion AS D WITH(NOLOCK)        
  ON D.Emp_Id  = T.Emp_Id        
  AND D.TipoDoc_Id = T.TipoDoc_Id        
  AND D.Suc_Id  = T.Suc_Id        
  AND D.Caja_Id  = T.Caja_Id        
  AND D.Factura_Id = T.Factura_Id        
    
  Insert into dbo.Factura_Patrocinador        
     (Emp_Id,        TipoDoc_Id,     Suc_Id,      Caja_Id,     
   Factura_Id,       Detalle_Id,     Promocion_Id,    Promocion_Cant_Cupones,     
   Promocion_Cant_Patrocinadores,  Promocion_Limite_Cupones, Promocion_Fec_Actualizacion)        
  Select D.Emp_Id,      D.TipoDoc_Id,    D.Suc_Id,     D.Caja_Id,     
   D.Factura_Id,      D.Detalle_Id,    D.Promocion_Id,    D.Promocion_Cant_Cupones,    
   D.Promocion_Cant_Patrocinadores, D.Promocion_Limite_Cupones, D.Promocion_Fec_Actualizacion          
  from #Documentos T,        
    dbo.Ticket_Patrocinador D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
  and   D.TipoDoc_id = T.TipoDoc_id        
  and   D.Suc_id     = T.Suc_id         
  and   D.Caja_id    = T.Caja_id        
  and   D.Factura_id = T.Factura_id        
        
  --Pasa Cupones Autogenerados    
  Insert Into dbo.Factura_Detalle_Cupon    
   (Emp_Id,      TipoDoc_id,      Suc_Id,    
   Caja_Id,     Factura_Id,      Detalle_Id,    
   Articulo_Id,    Promocion_Cupon_Id,    Promocion_Nombre,    
   Promocion_Cupon_Tipo,  Promocion_Cupon_Descuento,  Promocion_Cupon_Porcentaje,    
   Promocion_Cupon_Monto,  Promocion_Cupon_Piezas_Base, Promocion_Cupon_Piezas_Nocobradas,    
   Detalle_Cupon_Monto,  Detalle_Cupon_Numero,   Detalle_Linea_Id    
  )    
  Select A.Emp_Id,     A.TipoDoc_id,     A.Suc_Id,    
      A.Caja_Id,     A.Factura_Id,     A.Detalle_Id,    
    A.Articulo_Id,    A.Promocion_Cupon_Id,   A.Promocion_Nombre,    
    A.Promocion_Cupon_Tipo,  A.Promocion_Cupon_Descuento, A.Promocion_Cupon_Porcentaje,    
    A.Promocion_Cupon_Monto, A.Promocion_Cupon_Piezas_Base, A.Promocion_Cupon_Piezas_Nocobradas,    
    A.Detalle_Cupon_Monto,  A.Detalle_Cupon_Numero,   A.Detalle_Linea_Id    
  From  #Documentos     T,        
    dbo.Ticket_Detalle_Cupon A With(NoLock)        
  Where  A.Emp_id         = T.Emp_id         
  And    A.TipoDoc_id     = T.TipoDoc_id        
  And    A.Suc_id         = T.Suc_id         
  And    A.Caja_id        = T.Caja_id        
  And    A.Factura_Id      = T.Factura_id    
  And  A.Detalle_Id    > 0    
        
  Insert into dbo.Factura_Detalle_ServExterno      
  (       Emp_Id,        TipoDoc_Id,                     Suc_Id,         
    Caja_Id,        Factura_Id,                     Servicio_Id,         
    Servicio_Nombre,      Autorizador_Id,                 FechaTransaccion,         
    Articulo_Id,       Articulo_Nombre,                pMonto,         
    pApMaterno,       pSKU,                           pTipoMensaje,         
    pTipoServicio,      rCodigoRespuesta,               Proveedor,         
    NumAutorizacion,      Mensaje,                        pReferencia,         
    Comision,        Servicio_Agencia,               Servicio_Empresa,         
    Servicio_Llave_Consulta,    Servicio_Recibo_Cliente,        Servicio_Recibo_Numero,         
    Servicio_Recibo_Periodo,    Servicio_Recibo_Vencimiento,    Servicio_Recibo_Conceptos_Informativos,         
    Servicio_Recibo_Conceptos_Pagos,      Servicio_Recibo_Consecutivo,    Servicio_Recibo_Moneda,         
    Servicio_Recibo_Estado,               Factura_Servicio_Externo,       Factura_Moneda_Tipo_Cambio         
  )         
  Select  S.Emp_Id,                             S.TipoDoc_Id,                   S.Suc_Id,         
    S.Caja_Id,                            S.Factura_Id,                   S.Servicio_Id,         
    S.Servicio_Nombre,                    S.Autorizador_Id,               S.FechaTransaccion,         
    S.Articulo_Id,                        S.Articulo_Nombre,              S.pMonto,         
    S.pApMaterno,                         S.pSKU,                         S.pTipoMensaje,         
    S.pTipoServicio,                      S.rCodigoRespuesta,             S.Proveedor,         
    S.NumAutorizacion,                    S.Mensaje,                      S.pReferencia,         
    S.Comision,                           S.Servicio_Agencia,             S.Servicio_Empresa,         
    S.Servicio_Llave_Consulta,            S.Servicio_Recibo_Cliente,      S.Servicio_Recibo_Numero,         
    S.Servicio_Recibo_Periodo,            S.Servicio_Recibo_Vencimiento,  S.Servicio_Recibo_Conceptos_Informativos,         
    S.Servicio_Recibo_Conceptos_Pagos,    S.Servicio_Recibo_Consecutivo,  S.Servicio_Recibo_Moneda,         
    S.Servicio_Recibo_Estado,             S.Factura_Servicio_Externo,     S.Factura_Moneda_Tipo_Cambio         
  From        #Documentos                                           T,             
    dbo.Ticket_Detalle_ServExterno S With(Nolock)             
  Where   S.Emp_Id     = T.Emp_Id             
  and     S.TipoDoc_Id = T.TipoDoc_Id             
  and     S.Suc_Id     = T.Suc_Id             
  and     S.Caja_Id    = T.Caja_Id             
  and     S.Factura_Id = T.Factura_Id    
    
  --- Pasa Detalle Laboratorio        
     Insert into dbo.Factura_Detalle_Laboratorio_Descuento      
  ( Emp_Id,       TipoDoc_id,    Suc_Id,       Caja_Id,          
   Factura_Id,      Laboratorio_Descuento_Venta_Id,       
   Laboratorio_Monto,    Cliente_Id,    Asiento_Id )        
  Select D.Emp_Id,     D.TipoDoc_id,   D.Suc_Id,      D.Caja_Id,          
   D.Factura_Id,     D.Laboratorio_Descuento_Venta_Id,       
   D.Laboratorio_Monto,   D.Cliente_Id,   D.Asiento_Id    
  from #Documentos T,        
    dbo.Ticket_Detalle_Laboratorio_Descuento D With(Nolock)        
  Where D.Emp_id  = T.Emp_id         
   and  D.TipoDoc_id = T.TipoDoc_id        
   and  D.Suc_id  = T.Suc_id         
   and  D.Caja_id  = T.Caja_id        
   and  D.Factura_id = T.Factura_id     
    
  --- Pasa Detalle Promociones Grupos de Artículos       
  Insert into dbo.Factura_Detalle_Promocion_Grupo       
  (  Emp_Id,      TipoDoc_id,     Suc_Id,        Caja_Id,        
    Factura_Id,     Detalle_Id,     Articulo_Id,               Promocion_Grupo_Id,      
    Promocion_Grupo_Nombre,  Promocion_Grupo_Tipo,  Promocion_Grupo_Consecutivo,  Promocion_Grupo_PorcDescuento,    
    Promocion_Grupo_Precio,  Grupo_Id,     Detalle_Linea_Id)        
  Select  D.Emp_Id,     D.TipoDoc_id,    D.Suc_Id,       D.Caja_Id,        
    D.Factura_Id,    D.Detalle_Id,    D.Articulo_Id,      D.Promocion_Grupo_Id,      
    D.Promocion_Grupo_Nombre, D.Promocion_Grupo_Tipo,     D.Promocion_Grupo_Consecutivo,  D.Promocion_Grupo_PorcDescuento,    
    D.Promocion_Grupo_Precio,   D.Grupo_Id,     D.Detalle_Linea_Id         
  from #Documentos T     
    inner join dbo.Ticket_Detalle_Promocion_Grupo D With(Nolock)        
     on D.Emp_id     = T.Emp_id         
     and  D.TipoDoc_id = T.TipoDoc_id        
     and  D.Suc_id     = T.Suc_id         
     and  D.Caja_id    = T.Caja_id        
     and  D.Factura_id = T.Factura_id       

	 --- Pasa Detalle Combos       
  INSERT INTO dbo.Factura_Detalle_Combo
(    Emp_Id, TipoDoc_id, Suc_Id, Caja_Id, Factura_Id,
    Detalle_Id, Articulo_Id, Detalle_Precio_Cobrado, Detalle_Precio_Original, Detalle_Descuento_Porc,
    Combo_Id
)
SELECT
    D.Emp_Id, D.TipoDoc_id, D.Suc_Id, D.Caja_Id, D.Factura_Id,
    D.Detalle_Id, D.Articulo_Id, D.Detalle_Precio_Cobrado, D.Detalle_Precio_Original, D.Detalle_Descuento_Porc,
    D.Combo_Id
FROM #Documentos T
INNER JOIN dbo.Ticket_Detalle_Combo D WITH(NOLOCK)
    ON  D.Emp_Id     = T.Emp_Id
    AND D.TipoDoc_id = T.TipoDoc_id
    AND D.Suc_Id     = T.Suc_Id
    AND D.Caja_Id    = T.Caja_Id
    AND D.Factura_Id = T.Factura_Id
WHERE NOT EXISTS
(
    SELECT 1
    FROM dbo.Factura_Detalle_Combo F WITH(NOLOCK)
    WHERE F.Emp_Id     = D.Emp_Id
      AND F.TipoDoc_id = D.TipoDoc_id
      AND F.Suc_Id     = D.Suc_Id
      AND F.Caja_Id    = D.Caja_Id
      AND F.Factura_Id = D.Factura_Id
      AND F.Detalle_Id = D.Detalle_Id
);  
  -- =============================================        
  --- Borra Tablas Ticket        
  -- =============================================        
  -- Borra Cupones Autogenerados        
  Delete A    
  From  #Documentos     T,        
    dbo.Ticket_Detalle_Cupon A    
  Where  A.Emp_id         = T.Emp_id         
   And    A.TipoDoc_id     = T.TipoDoc_id        
   And    A.Suc_id         = T.Suc_id         
   And    A.Caja_id        = T.Caja_id        
   And    A.Factura_Id      = T.Factura_id    
   And  A.Detalle_Id    > 0    
        
  -- Borra Observaciones.        
  DELETE D        
  FROM #Documentos AS T        
   INNER JOIN dbo.Ticket_Detalle_Observacion AS D WITH(NOLOCK)        
  ON  D.Emp_Id  = T.Emp_Id        
   AND  D.TipoDoc_Id = T.TipoDoc_Id        
   AND  D.Suc_Id  = T.Suc_Id        
   AND  D.Caja_Id  = T.Caja_Id        
   AND  D.Factura_Id = T.Factura_Id        
        
  delete dbo.Ticket_Forma_Pago        
  from #Documentos T,        
   dbo.Ticket_Forma_Pago D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and   D.TipoDoc_id = T.TipoDoc_id        
   and   D.Suc_id     = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Ticket_Id  = T.Factura_id        
        
  delete dbo.Ticket_Detalle_Promocion        
  from #Documentos T,        
   dbo.Ticket_Detalle_Promocion D With(Nolock)        
  Where D.Emp_id     = T.Emp_id        
   and   D.TipoDoc_id = T.TipoDoc_id     
   and   D.Suc_id     = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Factura_id = T.Factura_id        
        
  delete dbo.Ticket_Detalle_Impuestos        
  from #Documentos T,        
   dbo.Ticket_Detalle_Impuestos D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and   D.TipoDoc_id = T.TipoDoc_id        
   and   D.Suc_id  = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Factura_id = T.Factura_id         
        
  delete dbo.Ticket_Detalle_Descuento        
  from #Documentos T,        
   dbo.Ticket_Detalle_Descuento D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and   D.TipoDoc_id = T.TipoDoc_id        
 and   D.Suc_id     = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Factura_id = T.Factura_id        
        
  delete dbo.Ticket_Detalle_Servicio        
  from #Documentos T,        
   dbo.Ticket_Detalle_Servicio D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and   D.TipoDoc_id = T.TipoDoc_id        
   and   D.Suc_id     = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Factura_id = T.Factura_id        
    
  Delete D    
  from  #Documentos T,        
    dbo.Ticket_Detalle_Servicio_Impuesto D With(Nolock)        
  Where  D.Emp_id  = T.Emp_id         
   And  D.TipoDoc_id = T.TipoDoc_id        
   And  D.Suc_id  = T.Suc_id         
   And  D.Caja_id  = T.Caja_id        
   And  D.Factura_id = T.Factura_id        
    
  delete dbo.Ticket_Detalle_ServExterno          
  from #Documentos T,             
   dbo.Ticket_Detalle_ServExterno S With(Nolock)             
  Where S.Emp_Id     = T.Emp_Id             
   and   S.TipoDoc_Id = T.TipoDoc_Id             
   and   S.Suc_Id     = T.Suc_Id             
   and   S.Caja_Id    = T.Caja_Id             
   and   S.Factura_Id = T.Factura_Id        
    
  delete dbo.Ticket_Detalle_Lote        
  from #Documentos T,        
   dbo.Ticket_Detalle_Lote D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and   D.TipoDoc_id = T.TipoDoc_id        
   and   D.Suc_id     = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Factura_id = T.Factura_id      
    
  delete dbo.Ticket_Detalle        
  from #Documentos T,        
   dbo.Ticket_Detalle D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and   D.TipoDoc_id = T.TipoDoc_id        
   and   D.Suc_id     = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Factura_id = T.Factura_id        
        
  delete dbo.Ticket_Detalle_Bono        
  from #Documentos T,        
   dbo.Ticket_Detalle_Bono D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and   D.TipoDoc_id = T.TipoDoc_id        
   and   D.Suc_id     = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Factura_id = T.Factura_id        
        
  delete dbo.Ticket_Detalle_Serie        
  from #Documentos T,        
   dbo.Ticket_Detalle_Serie  D With(Nolock)        
  Where D.Emp_id      = T.Emp_id         
   and   D.TipoDoc_id  = T.TipoDoc_id        
   and   D.Suc_id      = T.Suc_id         
   and   D.Caja_id     = T.Caja_id        
   and   D.Factura_Id  = T.Factura_id        
        
  delete dbo.Ticket_Detalle_Receta        
  from #Documentos T,        
   dbo.Ticket_Detalle_Receta  D With(Nolock)        
  Where D.Emp_id      = T.Emp_id         
   and   D.TipoDoc_id  = T.TipoDoc_id        
   and   D.Suc_id      = T.Suc_id         
   and   D.Caja_id     = T.Caja_id        
   and   D.Factura_Id  = T.Factura_id        
        
  delete dbo.Ticket_Patrocinador       
  from #Documentos T,        
   dbo.Ticket_Patrocinador D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and   D.TipoDoc_id = T.TipoDoc_id        
   and   D.Suc_id     = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Factura_id = T.Factura_id       
    
  delete dbo.Ticket_Detalle_Laboratorio_Descuento    
  from #Documentos T,        
   dbo.Ticket_Detalle_Laboratorio_Descuento D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and   D.TipoDoc_id = T.TipoDoc_id        
   and   D.Suc_id     = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Factura_id = T.Factura_id     
    
  delete dbo.Ticket_Detalle_Promocion_Grupo        
  from #Documentos T,        
   dbo.Ticket_Detalle_Promocion_Grupo D With(Nolock)        
  Where D.Emp_id     = T.Emp_id        
   and   D.TipoDoc_id = T.TipoDoc_id     
   and   D.Suc_id     = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Factura_id = T.Factura_id        
    
  delete dbo.Ticket_Encabezado        
  from #Documentos T,        
  dbo.Ticket_Encabezado D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and   D.TipoDoc_id = T.TipoDoc_id        
   and   D.Suc_id     = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Factura_id = T.Factura_id       
   
   delete dbo.Ticket_Detalle_Combo        
  from #Documentos T,        
   dbo.Ticket_Detalle_Combo D With(Nolock)        
  Where D.Emp_id     = T.Emp_id         
   and   D.TipoDoc_id = T.TipoDoc_id        
   and   D.Suc_id     = T.Suc_id         
   and   D.Caja_id    = T.Caja_id        
   and   D.Factura_id = T.Factura_id        
    
  -- ============================================================    
  -- Pasa el monedero a Retiro por monedero para evitar faltantes.    
  -- =============================================================    
  Update dbo.Caja_Cierre    
  Set Cierre_Ret_Monedero = Cierre_FP_Monedero    
  Where Emp_id = @Emp_id    
  and Suc_id = @Suc_id    
  and Caja_id = @Caja_id    
  and Cierre_id = @Cierre_id    
    
        
  -- =============================================        
  -- Cambia el estado y la fecha de cierre        
  -- =============================================        
  Update dbo.Caja_Cierre        
  Set  Cierre_Fecha_Cierre  = @Fecha_Cierre,        
  Cierre_Estado   = 'CLOSE',        
  cierre_Deposito   = @Deposito        
  Where  Emp_id  = @Emp_id        
  and  Suc_id  = @Suc_id        
  and  Caja_id  = @Caja_id        
  and  Cierre_id = @Cierre_id         
    
  -- =============================================        
  --- Elimina Tabla Temporal        
  -- =============================================        
  drop table #Documentos        
  END TRY        
 BEGIN CATCH        
    Set @msg = ERROR_MESSAGE()        
    raiserror ( @msg, 16,1)        
    return 0        
 END CATCH        
-- =============================================        
END        
-- =============================================
GO
