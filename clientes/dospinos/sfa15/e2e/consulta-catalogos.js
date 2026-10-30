'use strict';
// SOLO LECTURA contra el Docker local de Integrations: catalogos y CrossReference de STORE, CUSTOMER, COST_CENTER, WAREHOUSE.
const sql = require('C:/Users/fvillacis/ClaudeLocalSession/sfa15/simulador-pruebas/deps/node_modules/mssql');
const cs = require('fs').readFileSync(process.argv[2], 'utf8').split(/\r?\n/).find(l => l.startsWith('DB_CONNECTION_STRING=')).slice(21);
const p = Object.fromEntries(cs.split(';').filter(Boolean).map(x => { const i = x.indexOf('='); return [x.slice(0, i).trim().toLowerCase(), x.slice(i + 1)]; }));
if (p.server !== 'localhost,1433') process.exit(2);
(async () => {
  const pool = await new sql.ConnectionPool({ server: 'localhost', port: 1433, database: p.database, user: p['user id'], password: p.password, options: { trustServerCertificate: true } }).connect();
  const q = async (title, text) => { console.log('== ' + title); const r = await pool.request().query(text); for (const row of r.recordset) console.log(JSON.stringify(row)); };
  await q('Catalog', "SELECT Id, Name, Description, Type, HasDefault, DefaultValue, LdcomTableName, LdcomIdColumn, LdcomDescColumn FROM Catalog WHERE Id IN (1,7,8,9) ORDER BY Id");
  await q('CrossReference por catalogo/empresa', "SELECT CatalogId, CompanyId, COUNT(*) AS Filas, SUM(CASE WHEN ExternalId=InternalId THEN 1 ELSE 0 END) AS Identidad FROM CrossReference WHERE CatalogId IN (1,7,8,9) GROUP BY CatalogId, CompanyId ORDER BY CatalogId, CompanyId");
  await q('STORE muestra', "SELECT TOP 25 ExternalId, InternalId, CompanyId FROM CrossReference WHERE CatalogId=1 ORDER BY TRY_CAST(InternalId AS INT), ExternalId");
  await q('COST_CENTER muestra', "SELECT TOP 8 ExternalId, InternalId, CompanyId FROM CrossReference WHERE CatalogId=8 ORDER BY Id");
  await q('CUSTOMER muestra', "SELECT TOP 8 ExternalId, InternalId, CompanyId FROM CrossReference WHERE CatalogId=7 ORDER BY Id");
  await q('STORE: una misma sucursal con varias filas', "SELECT TOP 10 InternalId, COUNT(*) AS Filas, MIN(ExternalId) AS Min, MAX(ExternalId) AS Max FROM CrossReference WHERE CatalogId=1 GROUP BY InternalId HAVING COUNT(*)>1");
  await pool.close();
})().catch(e => { console.error(e.message); process.exit(1); });
