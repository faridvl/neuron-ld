'use strict';
// E2E 3700 NEGOCIO: Harness (TSistemaFinanciamientoSFA + IntegrationBridge/Runner real) -> Integrations Docker -> simulador 7391. Solo Docker local.
const fs = require('fs'); const { spawn } = require('child_process');
const sql = require('C:/Users/fvillacis/ClaudeLocalSession/sfa15/simulador-pruebas/deps/node_modules/mssql');
const envf = 'C:/Users/FVILLA~1/AppData/Local/Temp/claude/C--Users-fvillacis-ClaudeLocalSession/15c175d7-97e6-4dbf-802d-70c3b80d73b2/scratchpad/migrate-sfa15/.env';
const cs0 = fs.readFileSync(envf, 'utf8').split(/\r?\n/).find(l => l.startsWith('DB_CONNECTION_STRING=')).slice(21);
const P = Object.fromEntries(cs0.split(';').filter(Boolean).map(x => { const i = x.indexOf('='); return [x.slice(0, i).trim().toLowerCase(), x.slice(i + 1)]; }));
if (P.server !== 'localhost,1433') process.exit(2);
const DB_INT = 'LDCOM_INTEGRATIONS_3699_DOCKER', DB_LD = 'LDCOM_DOS_PINOS_STAGING_DOCKER';
const mk = (db) => new sql.ConnectionPool({ server: 'localhost', port: 1433, database: db, user: P['user id'], password: P.password, options: { trustServerCertificate: true } });
const enc = (plain) => [...plain].reverse().map(ch => { const c = String(ch.charCodeAt(0)); return String(c.length * 2) + c; }).join('');
const csInt = `Server=localhost,1433;Database=${DB_INT};User Id=${P['user id']};Password=${P.password};TrustServerCertificate=True;`;
const ENV = Object.assign({}, process.env, { E2E_LDCOM: `Server=localhost,1433;Database=${DB_LD};uid=${P["user id"]};password=${enc(P.password)};TrustServerCertificate=True;`, E2E_INTEGRATION: csInt.replace(/(Password=)([^;]*)/i, (a, p, v) => p + enc(v)) });
const SIM = 'http://localhost:7391', URL_OK = SIM + '/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final';
const STAMP = Date.now().toString(36).slice(-5).toUpperCase();
const ref = (t) => 'Q37' + STAMP + t;
const log = (o) => console.log(JSON.stringify(o));
const SECRETOS = ['e2e-usuario', 'e2e-clave', 'e2e-basic-usuario', 'e2e-basic-clave', P.password];
let pI, pL;
const sim = async () => { const b = await (await fetch(SIM + '/sim/sfa15')).json(); return { max: b.llamadas.length ? b.llamadas[0].id : 0, llamadas: b.llamadas }; };
const runHarness = (args) => new Promise((res) => { const t0 = Date.now(); const c = spawn('bin/Harness.exe', args.map(String), { cwd: __dirname + '/e2e-negocio', env: ENV }); let so = '', se = ''; c.stdout.on('data', d => so += d); c.stderr.on('data', d => se += d); c.on('close', () => { let r = null; try { r = JSON.parse(so.trim().split(/\r?\n/).pop()); } catch (e) { } res({ r, raw: r ? '' : so.slice(0, 400), se: se.slice(0, 300), ms: Date.now() - t0 }); }); });
async function attempt(r) { const x = await pI.request().input('r', sql.NVarChar, r).query('SELECT Status,RequestNumber,CreditNumber,Message FROM CreditValidationAttempt WHERE ExternalReference=@r'); return x.recordset[0] || null; }
async function caso(label, esperado, a) {
  const b = await sim(); const o = await runHarness(a); const s = await sim();
  const nuevas = s.llamadas.filter(l => l.id > b.max); const u = nuevas[0]; let body = null; try { body = u && JSON.parse(u.request.body); } catch (e) { }
  const d = body && body.Datos_Entrada;
  const fila = await attempt(String(a[7]));
  const txt = JSON.stringify(o.r || {});
  const fuga = SECRETOS.filter(x => x && txt.includes(x));
  log({ caso: label, esperado, res: o.r && { Estado: o.r.Estado, Razon: o.r.Razon, Autorizado: o.r.Autorizado, NumSolicitud: o.r.NumSolicitud, NumCredito: o.r.NumCredito, PosibleAplicado: o.r.PosibleAplicado, Mensaje: o.r.Mensaje && o.r.Mensaje.slice(0, 110) }, logs: o.r && o.r.logs, ms: o.ms, llamadasSim: nuevas.length,
    simVio: u ? { http: u.http, codUnidadCosto: d && d.codUnidadCosto, codAgencia: d && d.codAgencia, idExterno: d && d.idExterno, mon: d && d.monSolicitud, cuerpo: body && JSON.stringify(body).slice(0, 600) } : null,
    attempt: fila ? fila.Status + '/' + fila.RequestNumber + '/' + fila.CreditNumber : 'sin fila', fugaSecretos: fuga, raw: o.raw, se: o.se });
}
(async () => {
  pI = await mk(DB_INT).connect(); pL = await mk(DB_LD).connect();
  const q = (p, s) => p.request().query(s);
  const planes = (await q(pL, 'select PlanFinanciamiento_Id i, PlanFinanciamiento_Codigo_Externo c from Plan_Financiamiento where PlanFinanciamiento_Id in (1,2,3)')).recordset;
  log({ paso: 'respaldo-planes', planes });
  const ev0 = (await q(pI, "select IsActive,EndpointUrl from IntegrationEvent where Name='CREDIT_VALIDATION'")).recordset[0];
  const cred0 = (await q(pI, "select AuthenticationUser,AuthenticationPassword from IntegrationCredential where EventCode='CREDIT_VALIDATION'")).recordset[0];
  const par0 = (await q(pI, "select P.ParameterName n,P.ParameterValue v from IntegrationEventParameter P join IntegrationEvent E on E.Id=P.IntegrationEventId where E.Name='CREDIT_VALIDATION'")).recordset;
  const setEv = (a, u) => pI.request().input('a', sql.Bit, a).input('u', sql.NVarChar, u).query("UPDATE IntegrationEvent SET IsActive=@a, EndpointUrl=@u WHERE Name='CREDIT_VALIDATION'");
  const setCred = (u, p) => pI.request().input('u', sql.NVarChar, u).input('p', sql.NVarChar, p).query("UPDATE IntegrationCredential SET AuthenticationUser=@u, AuthenticationPassword=@p WHERE EventCode='CREDIT_VALIDATION'");
  const setPar = (n, v) => pI.request().input('n', sql.NVarChar, n).input('v', sql.NVarChar, v).query("UPDATE P SET ParameterValue=@v FROM IntegrationEventParameter P JOIN IntegrationEvent E ON E.Id=P.IntegrationEventId WHERE E.Name='CREDIT_VALIDATION' AND P.ParameterName=@n");
  try {
    await q(pL, "update Plan_Financiamiento set PlanFinanciamiento_Codigo_Externo='201' where PlanFinanciamiento_Id=1; update Plan_Financiamiento set PlanFinanciamiento_Codigo_Externo='' where PlanFinanciamiento_Id=2");
    await q(pI, "INSERT INTO CrossReference (CatalogId, ExternalId, InternalId, CompanyId) VALUES (1,'001','3',1)");
    await setEv(1, URL_OK); await setCred('e2e-basic-usuario', 'e2e-basic-clave'); await setPar('SfaUser', 'e2e-usuario'); await setPar('SfaPassword', 'e2e-clave'); await setPar('CompanyCode', '001');
    const R1 = ref('A1'), R2 = ref('B1'), R4 = ref('T1');
    const A = (monto, ref_, o = {}) => [1, o.cli || 1, o.plan || 1, o.plazo || 4, monto, o.suc === undefined ? 3 : o.suc, o.finca === undefined ? 3 : o.finca, ref_];
    await caso('1 autorizado con finca', 'Autorizado, NumSolicitud>0, NumCredito, codUnidadCosto=3', A(1, R1));
    await caso('2 rechazo funcional 12000', 'Rechazado, PosibleAplicado false', A(12000, R2));
    await caso('3 rechazo disponible 30000', 'Rechazado, NumSolicitud>0', A(30000, ref('C1')));
    await caso('4 timeout 15000.01', 'NoDisponible/TiempoAgotado, PosibleAplicado true (~36 s)', A(15000.01, R4));
    await caso('5 reintento mismo doc tras autorizado', 'Autorizado mismos numeros, 0 llamadas', A(1, R1));
    await caso('6 reintento tras rechazo', 'llama de nuevo (1), Rechazado', A(12000, R2));
    await caso('7 reintento tras timeout', 'NoDisponible/IntentoDuplicado, 0 llamadas', A(15000.01, R4));
    await caso('8 misma ref con otro monto tras autorizado', 'Rechazado, 0 llamadas', A(2, R1));
    await caso('9 sin finca (0)', 'Autorizado, codUnidadCosto vacio', A(1, ref('F0'), { finca: 0 }));
    await caso('10 asociado sin Codigo_Interfaz', 'NoDisponible/DatosIncompletos, 0 llamadas', A(1, ref('S1'), { cli: 10000001 }));
    await caso('11 finca sin Codigo_Interfaz', 'NoDisponible/DatosIncompletos, 0 llamadas', A(1, ref('S2'), { finca: 10027596 }));
    await caso('12 plan sin codigo externo', 'NoDisponible/DatosIncompletos, 0 llamadas', A(1, ref('P1'), { plan: 2 }));
    await caso('13 plan con codigo no numerico', 'NoDisponible/DatosIncompletos, 0 llamadas', A(1, ref('P2'), { plan: 3 }));
    await caso('14 plan inexistente', 'NoDisponible, 0 llamadas', A(1, ref('P3'), { plan: 99999 }));
    await caso('15 cliente inexistente', 'NoDisponible, 0 llamadas', A(1, ref('S3'), { cli: 99999999 }));
    await caso('16 sucursal sin mapeo STORE (4)', 'NoDisponible/NoConfigurado, 0 llamadas', A(1, ref('M1'), { suc: 4 }));
    await caso('17 referencia nula', 'NoDisponible/DatosIncompletos, 0 llamadas', A(1, 'NULL'));
    await caso('18 referencia 16 caracteres', 'NoDisponible/DatosIncompletos, 0 llamadas', A(1, 'ABCDEFGHIJKLMNOP'));
    await caso('19 sucursal 0', 'NoDisponible/DatosIncompletos, 0 llamadas', A(1, ref('Z1'), { suc: 0 }));
    await setCred('e2e-basic-usuario', 'basic-equivocada');
    await caso('20 Basic incorrecta', 'NoDisponible/Seguridad, PosibleAplicado false', A(1, ref('K1')));
    await setCred('', '');
    await caso('21 Basic vacia', 'NoDisponible/NoConfigurado, 0 llamadas', A(1, ref('K2')));
    await setCred('e2e-basic-usuario', 'e2e-basic-clave'); await setPar('SfaUser', '');
    await caso('22 SfaUser vacio', 'NoDisponible/NoConfigurado, 0 llamadas', A(1, ref('K3')));
    await setPar('SfaUser', 'e2e-usuario'); await setEv(0, URL_OK);
    await caso('23 evento inactivo', 'NoDisponible/NoConfigurado, 0 llamadas', A(1, ref('K4')));
    await setEv(1, URL_OK);
    await caso('24 control: autorizado tras restaurar', 'Autorizado', A(1, ref('K5')));
  } finally {
    for (const p of planes) await pL.request().input('c', sql.NVarChar, p.c).input('i', sql.Int, p.i).query('update Plan_Financiamiento set PlanFinanciamiento_Codigo_Externo=@c where PlanFinanciamiento_Id=@i');
    await q(pI, "DELETE FROM CrossReference WHERE CatalogId=1 AND ExternalId='001' AND InternalId='3' AND CompanyId=1");
    await setEv(ev0.IsActive, ev0.EndpointUrl); await setCred(cred0.AuthenticationUser, cred0.AuthenticationPassword);
    for (const x of par0) await setPar(x.n, x.v);
    log({ paso: 'restaurado', planes: (await q(pL, 'select PlanFinanciamiento_Id i, PlanFinanciamiento_Codigo_Externo c from Plan_Financiamiento where PlanFinanciamiento_Id in (1,2,3)')).recordset });
    await pI.close(); await pL.close();
  }
})().catch(e => { console.error(e); process.exit(1); });