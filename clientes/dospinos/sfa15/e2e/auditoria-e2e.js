'use strict';
// Lista las filas de auditoria CREDIT_VALIDATION mas recientes del Docker local (solo lectura).
const sql = require('C:/Users/fvillacis/ClaudeLocalSession/sfa15/simulador-pruebas/deps/node_modules/mssql');
const cs = require('fs').readFileSync(process.argv[2], 'utf8').split(/\r?\n/).find(l => l.startsWith('DB_CONNECTION_STRING=')).slice(21);
const p = Object.fromEntries(cs.split(';').filter(Boolean).map(x => { const i = x.indexOf('='); return [x.slice(0, i).trim().toLowerCase(), x.slice(i + 1)]; }));
if (p.server !== 'localhost,1433') process.exit(2);
(async () => {
  const pool = await new sql.ConnectionPool({ server: 'localhost', port: 1433, database: p.database, user: p['user id'], password: p.password, options: { trustServerCertificate: true } }).connect();
  const r = await pool.request().query("SELECT TOP " + (process.argv[3] || 30) + " Id, TransactionId, EventId, EventCode, Type, Origin, Destination, Phase, Status, LEFT(Payload,160) AS Payload FROM Events WHERE Type='CREDIT_VALIDATION' ORDER BY Id DESC");
  for (const row of r.recordset.reverse()) console.log([row.Id, row.TransactionId.slice(0, 40), row.EventId, row.EventCode, row.Origin + '>' + row.Destination, row.Phase + '/' + row.Status, row.Payload].join(' | '));
  await pool.close();
})();
