'use strict';
// Enciende o apaga el evento CREDIT_VALIDATION en el Docker local para las pruebas. Uso: node config-evento.js on|off <.env> [url]
const sql = require('C:/Users/fvillacis/ClaudeLocalSession/sfa15/simulador-pruebas/deps/node_modules/mssql');
const fs = require('fs');
const [mode, envPath, url = 'http://localhost:7391/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final'] = process.argv.slice(2);
const cs = fs.readFileSync(envPath, 'utf8').split(/\r?\n/).find(l => l.startsWith('DB_CONNECTION_STRING=')).slice(21);
const parts = Object.fromEntries(cs.split(';').filter(Boolean).map(p => { const i = p.indexOf('='); return [p.slice(0, i).trim().toLowerCase(), p.slice(i + 1)]; }));
if (parts.server !== 'localhost,1433' || parts.database !== 'LDCOM_DOS_PINOS_INTEGRATIONS_DEVELOP_DOCKER') { console.error('Conexion no permitida'); process.exit(2); }
(async () => {
  const pool = await new sql.ConnectionPool({ server: 'localhost', port: 1433, database: parts.database, user: parts['user id'], password: parts.password, options: { trustServerCertificate: true } }).connect();
  const on = mode === 'on';
  await pool.request().input('a', sql.Bit, on ? 1 : 0).input('u', sql.NVarChar, on ? url : 'https://CHANGE_ME/p_SFA15_Autorizacion_Venta_Final').query("UPDATE IntegrationEvent SET IsActive=@a, EndpointUrl=@u WHERE Name='CREDIT_VALIDATION'");
  await pool.request().input('u', sql.NVarChar, on ? 'e2e-usuario' : null).input('p', sql.NVarChar, on ? 'e2e-clave' : null).query("UPDATE IntegrationCredential SET AuthenticationUser=@u, AuthenticationPassword=@p WHERE EventCode='CREDIT_VALIDATION'");
  const state = await pool.request().query("SELECT E.IsActive, E.EndpointUrl, C.AuthenticationUser, C.AuthenticationPassword, E.Description FROM IntegrationEvent E JOIN IntegrationCredential C ON C.EventCode=E.Name WHERE E.Name='CREDIT_VALIDATION'");
  const row = state.recordset[0];
  console.log(JSON.stringify({ isActive: row.IsActive, url: row.EndpointUrl, user: row.AuthenticationUser, passwordSet: row.AuthenticationPassword !== null, description: row.Description }));
  await pool.close();
})().catch(e => { console.error(e); process.exit(1); });
