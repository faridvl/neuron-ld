'use strict';
// Consulta al Docker local (localhost,1433). Uso: node qd.js <base> "<SQL>"
const sql = require('C:/Users/fvillacis/ClaudeLocalSession/sfa15/simulador-pruebas/deps/node_modules/mssql');
const envf = 'C:/Users/FVILLA~1/AppData/Local/Temp/claude/C--Users-fvillacis-ClaudeLocalSession/15c175d7-97e6-4dbf-802d-70c3b80d73b2/scratchpad/migrate-sfa15/.env';
const cs = require('fs').readFileSync(envf, 'utf8').split(/\r?\n/).find(l => l.startsWith('DB_CONNECTION_STRING=')).slice(21);
const p = Object.fromEntries(cs.split(';').filter(Boolean).map(x => { const i = x.indexOf('='); return [x.slice(0, i).trim().toLowerCase(), x.slice(i + 1)]; }));
if (p.server !== 'localhost,1433') { console.error('no permitido'); process.exit(2); }
(async () => {
  const pool = await new sql.ConnectionPool({ server: 'localhost', port: 1433, database: process.argv[2], user: p['user id'], password: p.password, options: { trustServerCertificate: true }, requestTimeout: 120000 }).connect();
  const r = await pool.request().query(process.argv[3]);
  for (const s of (r.recordsets || [])) for (const row of s) console.log(JSON.stringify(row));
  await pool.close();
})().catch(e => { console.error(e.message); process.exit(1); });
