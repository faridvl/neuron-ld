'use strict';
// SOLO LECTURA contra el Docker local (localhost,1433). Uso: node consulta-solo-lectura.js <.env con DB_CONNECTION_STRING> <base> <archivo.sql>
// El .sql trae consultas separadas por lineas "-- ##"; se rechaza cualquier cosa que no sea SELECT.
const fs = require('fs');
const sql = require('C:/Users/fvillacis/ClaudeLocalSession/sfa15/simulador-pruebas/deps/node_modules/mssql');
const [archivoEnv, base, archivoSql] = process.argv.slice(2);
const cs = fs.readFileSync(archivoEnv, 'utf8').split(/\r?\n/).find((l) => l.startsWith('DB_CONNECTION_STRING=')).slice(21);
const p = Object.fromEntries(cs.split(';').filter(Boolean).map((x) => { const i = x.indexOf('='); return [x.slice(0, i).trim().toLowerCase(), x.slice(i + 1)]; }));
if (String(p.server).toLowerCase() !== 'localhost,1433') { console.error('Solo se permite localhost,1433'); process.exit(2); }
const bloques = fs.readFileSync(archivoSql, 'utf8').split(/^-- ##/m).map((b) => b.trim()).filter(Boolean);
const PROHIBIDO = /\b(insert|update|delete|merge|exec|execute|drop|alter|create|truncate|grant|revoke|into)\b/i;
(async () => {
  const pool = await new sql.ConnectionPool({ server: 'localhost', port: 1433, database: base, user: p['user id'], password: p.password,
    options: { trustServerCertificate: true }, requestTimeout: 60000 }).connect();
  for (const bloque of bloques) {
    const [titulo, ...resto] = bloque.split(/\r?\n/);
    const consulta = resto.join('\n');
    if (PROHIBIDO.test(consulta.replace(/--.*$/gm, ''))) { console.log(`== ${titulo}: RECHAZADA (no es solo SELECT)`); continue; }
    console.log(`== ${titulo}`);
    try {
      const r = await pool.request().query(consulta);
      for (const fila of r.recordset || []) console.log(JSON.stringify(fila));
    } catch (e) { console.log('   ERROR: ' + e.message); }
  }
  await pool.close();
})().catch((e) => { console.error(e.message); process.exit(1); });
