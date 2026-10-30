'use strict';
// Consulta de solo lectura/escritura acotada al Docker local. Uso: node q.js <.env> "<SQL>"
const sql = require('C:/Users/fvillacis/ClaudeLocalSession/sfa15/simulador-pruebas/deps/node_modules/mssql');
const cs = require('fs').readFileSync(process.argv[2], 'utf8').split(/\r?\n/).find(l => l.startsWith('DB_CONNECTION_STRING=')).slice(21);
const p = Object.fromEntries(cs.split(';').filter(Boolean).map(x => { const i = x.indexOf('='); return [x.slice(0, i).trim().toLowerCase(), x.slice(i + 1)]; }));
if (p.server !== 'localhost,1433' || p.database !== 'LDCOM_DOS_PINOS_INTEGRATIONS_DEVELOP_DOCKER') { console.error('no permitido'); process.exit(2); }
(async () => {
  const pool = await new sql.ConnectionPool({ server: 'localhost', port: 1433, database: p.database, user: p['user id'], password: p.password, options: { trustServerCertificate: true } }).connect();
  const r = await pool.request().query(process.argv[3]);
  for (const s of (r.recordsets || [])) for (const row of s) console.log(JSON.stringify(row));
  await pool.close();
})().catch(e => { console.error(e.message); process.exit(1); });
