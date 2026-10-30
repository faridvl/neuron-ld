'use strict';
// SOLO LECTURA contra el Docker local de LDCOM: columnas de Sucursal y muestra.
const sql = require('C:/Users/fvillacis/ClaudeLocalSession/sfa15/simulador-pruebas/deps/node_modules/mssql');
const cs = require('fs').readFileSync(process.argv[2], 'utf8').split(/\r?\n/).find(l => l.startsWith('DB_CONNECTION_STRING=')).slice(21);
const p = Object.fromEntries(cs.split(';').filter(Boolean).map(x => { const i = x.indexOf('='); return [x.slice(0, i).trim().toLowerCase(), x.slice(i + 1)]; }));
if (p.server !== 'localhost,1433') process.exit(2);
(async () => {
  const pool = await new sql.ConnectionPool({ server: 'localhost', port: 1433, database: 'LDCOM_DOS_PINOS_DEVELOP_DOCKER', user: p['user id'], password: p.password, options: { trustServerCertificate: true } }).connect();
  const q = async (t, text) => { console.log('== ' + t); const r = await pool.request().query(text); for (const row of r.recordset) console.log(JSON.stringify(row)); };
  await q('Sucursal Codigo_Interfaz', "SELECT Suc_Id, Suc_Nombre, Codigo_Interfaz, Suc_Activo FROM Sucursal ORDER BY Suc_Id");
  await pool.close();
})().catch(e => { console.error(e.message); process.exit(1); });
