#!/bin/bash
# Estado de referencia: ultimos documentos suc 19, llamadas al simulador, intentos de Integrations
cd /c/Users/fvillacis/ClaudeLocalSession/sfa15
L="node qa-3700/qd.js LDCOM_DOS_PINOS_STAGING_DOCKER"
echo "-- Ticket_Encabezado"; $L "SELECT TOP 4 Factura_Id,TipoDoc_id,SubDoc_id,Caja_Id,Cliente_Id,PlanFinanciamiento_Id,Factura_Total,Factura_Validacion_Credito,Factura_Credito_SFA_Solicitud,Factura_Credito_SFA_Credito,Factura_Credito_SFA_Referencia FROM Ticket_Encabezado WHERE Suc_Id=19 ORDER BY Factura_Fecha DESC" 2>&1
echo "-- Factura_Encabezado"; $L "SELECT TOP 4 Factura_Id,Suc_Id,Caja_Id,Cliente_Id,Factura_Total,Factura_Validacion_Credito,Factura_Credito_SFA_Solicitud,Factura_Credito_SFA_Credito,Factura_Credito_SFA_Referencia FROM Factura_Encabezado WHERE Suc_Id=19 ORDER BY Factura_Id DESC" 2>&1
echo "-- Integrations"; node qa-3700/qd.js ZZ_QA3700_INTEGRATIONS "SELECT TOP 5 Id,ExternalReference,Status,RequestNumber,CreditNumber,CreatedAt FROM CreditValidationAttempt ORDER BY Id DESC" 2>&1
echo "-- evento"; node qa-3700/qd.js ZZ_QA3700_INTEGRATIONS "SELECT IsActive,EndpointUrl FROM IntegrationEvent WHERE Id=16"
echo "-- simulador"; curl -s localhost:7391/sim/sfa15 | node -e "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{const j=JSON.parse(s);console.log('llamadas',j.llamadas.length);j.llamadas.slice(0,3).forEach(l=>console.log(JSON.stringify({id:l.id,http:l.http,mon:(()=>{try{return JSON.parse(l.request.body).Datos_Entrada.monSolicitud}catch(e){}})()})))})"
