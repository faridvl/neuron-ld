'use strict';
// E2E final SFA15 (punto 8): Runner real por stdin -> simulador local 7391 (Basic + par SFA). Solo Docker local.
// Uso: node e2e-final.js <Integration.Runner.exe> <.env>
const fs = require('fs');
const { spawn } = require('child_process');
const sql = require('C:/Users/fvillacis/ClaudeLocalSession/sfa15/simulador-pruebas/deps/node_modules/mssql');
const [runnerPath, envPath] = process.argv.slice(2);
const SIM = 'http://localhost:7391';
const cs = fs.readFileSync(envPath, 'utf8').split(/\r?\n/).find(l => l.startsWith('DB_CONNECTION_STRING=')).slice(21);
const parts = Object.fromEntries(cs.split(';').filter(Boolean).map(x => { const i = x.indexOf('='); return [x.slice(0, i).trim().toLowerCase(), x.slice(i + 1)]; }));
if (parts.server !== 'localhost,1433' || parts.database !== 'LDCOM_DOS_PINOS_INTEGRATIONS_DEVELOP_DOCKER') { console.error('Conexion no permitida'); process.exit(2); }
const enc = (plain) => [...plain].reverse().map(ch => { const c = String(ch.charCodeAt(0)); return String(c.length * 2) + c; }).join('');
const runnerCs = cs.replace(/(password=)([^;]*)/i, (a, p, v) => p + enc(v));
const URL_OK = SIM + '/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final';
const PLACEHOLDER = 'https://CHANGE_ME/p_SFA15_Autorizacion_Venta_Final';
const BASIC_USER = 'e2e-basic-usuario', BASIC_PASS = 'e2e-basic-clave', SFA_USER = 'e2e-usuario', SFA_PASS = 'e2e-clave';
const STAMP = Date.now().toString(36).slice(-6).toUpperCase();
const ref = (tag) => 'E2F' + STAMP + tag;
const pool = new sql.ConnectionPool({ server: 'localhost', port: 1433, database: parts.database, user: parts['user id'], password: parts.password, options: { trustServerCertificate: true } });
const log = (o) => console.log(JSON.stringify(o));

const req = (amount, over = {}) => ({ CustomerCode: '4000010', IdentificationTypeCode: null, IdentificationNumber: null, BranchId: 99, DocumentDate: '2026-10-28T00:00:00', CustomerName: 'Cliente Prueba E2E', UsesCreditLine: true, CreditLineNumber: 0, ExternalReference: ref('X'), FarmCode: '2563', TermInWeeks: 4, FinancingPlanExternalCode: '201', Amount: amount, Notes: 'prueba e2e final', ...over });

function runRunner(params) {
  return new Promise((resolve) => {
    const t0 = Date.now();
    const child = spawn(runnerPath, [], { stdio: ['pipe', 'pipe', 'pipe'] });
    let so = '', se = '';
    child.stdout.on('data', c => so += c); child.stderr.on('data', c => se += c);
    child.on('close', () => { let r = null; try { r = JSON.parse(so.trim().split(/\r?\n/).pop()); } catch (e) { /* crudo */ } resolve({ ms: Date.now() - t0, r, se }); });
    child.stdin.write(JSON.stringify({ Method: 'ValidateFinancingPlan', Token: 'e2e', Stage: 'TESTING', Tenant: 'DOS_PINOS', IntegrationConnectionString: runnerCs, Params: JSON.stringify(params) }) + '\n');
    child.stdin.end();
  });
}
const sim = async () => { const b = await (await fetch(SIM + '/sim/sfa15')).json(); return { max: b.llamadas.length ? b.llamadas[0].id : 0, sol: b.config.proximaSolicitud, cre: b.config.proximoCredito, llamadas: b.llamadas }; };
async function setEvent(a, u) { await pool.request().input('a', sql.Bit, a).input('u', sql.NVarChar, u).query("UPDATE IntegrationEvent SET IsActive=@a, EndpointUrl=@u WHERE Name='CREDIT_VALIDATION'"); }
async function setCred(u, p) { await pool.request().input('u', sql.NVarChar, u).input('p', sql.NVarChar, p).query("UPDATE IntegrationCredential SET AuthenticationUser=@u, AuthenticationPassword=@p WHERE EventCode='CREDIT_VALIDATION'"); }
async function setParam(n, v) { await pool.request().input('n', sql.NVarChar, n).input('v', sql.NVarChar, v).query("UPDATE P SET ParameterValue=@v FROM IntegrationEventParameter P JOIN IntegrationEvent E ON E.Id=P.IntegrationEventId WHERE E.Name='CREDIT_VALIDATION' AND P.ParameterName=@n"); }
async function attempt(r) { const x = await pool.request().input('r', sql.NVarChar, r).query('SELECT Status,RequestNumber,CreditNumber FROM CreditValidationAttempt WHERE ExternalReference=@r'); return x.recordset[0] ? x.recordset[0].Status + '/' + x.recordset[0].RequestNumber + '/' + x.recordset[0].CreditNumber : 'sin fila'; }
async function audit(r) { const x = await pool.request().input('r', sql.NVarChar, '%' + r + '%').query("SELECT Phase,Status FROM Events WHERE Type='CREDIT_VALIDATION' AND TransactionId LIKE @r ORDER BY Id"); return x.recordset.map(w => w.Phase + '/' + w.Status).join(' > '); }
const parse = (z) => (z.r && z.r.Result ? JSON.parse(z.r.Result) : z.r);

async function caso(label, esperado, params) {
  const b = await sim();
  const o = await runRunner(params);
  const a = await sim();
  const nuevas = a.llamadas.filter(l => l.id > b.max);
  const ult = nuevas[0];
  let body = null; try { body = ult && JSON.parse(ult.request.body); } catch (e) { /* sin cuerpo */ }
  const d = body && body.Datos_Entrada;
  log({ caso: label, esperado, success: o.r && o.r.Success, error: o.r && o.r.Error, res: parse(o), ms: o.ms, llamadasSim: nuevas.length, simAntes: b.max, simDespues: a.max, sigSolicitud: a.sol, sigCredito: a.cre,
    simVio: ult ? { http: ult.http, auth: ult.request.headers.authorization, Usuario: body && body.Usuario, codEmpresa: d && d.codEmpresa, codAgencia: d && d.codAgencia, codUnidadCosto: d && d.codUnidadCosto, idExterno: d && d.idExterno, monSolicitud: d && d.monSolicitud, respuesta: ult.respuesta } : null,
    attempt: await attempt(params.ExternalReference || ''), auditoria: await audit(params.ExternalReference || '#none#'), stderr: o.se.slice(0, 150) });
}

(async () => {
  await pool.connect();
  try {
    await pool.request().query("INSERT INTO CrossReference (CatalogId, ExternalId, InternalId, CompanyId) VALUES (1,'001','99',1)");
    await setEvent(1, URL_OK); await setCred(BASIC_USER, BASIC_PASS); await setParam('SfaUser', SFA_USER); await setParam('SfaPassword', SFA_PASS); await setParam('CompanyCode', '001');
    log({ paso: 'config', basicUser: BASIC_USER, sfaUser: SFA_USER, paresDistintos: BASIC_USER !== SFA_USER && BASIC_PASS !== SFA_PASS });
    const R1 = ref('A1'), R2 = ref('B1'), R3 = ref('C1'), R4 = ref('T1');
    await caso('1 aprobada con finca', 'Authorized + numSolicitud/numCredito; Basic e2e-basic-usuario, Usuario e2e-usuario', req(1, { ExternalReference: R1 }));
    await caso('2 rechazo funcional (12000)', 'Rejected con mensaje', req(12000, { ExternalReference: R2 }));
    await caso('3 rechazo por disponible (30000)', 'Rejected, RequestNumber, AvailableAmount, PossiblyApplied false', req(30000, { ExternalReference: R3 }));
    await caso('4 timeout (15000.01)', 'Unavailable/Timeout PossiblyApplied true (~36 s)', req(15000.01, { ExternalReference: R4 }));
    const sinFinca = req(1, { ExternalReference: ref('F1') }); delete sinFinca.FarmCode;
    await caso('5a sin finca (FarmCode ausente)', 'Authorized con codUnidadCosto vacio', sinFinca);
    await caso('5b FarmCode vacio', 'Authorized con codUnidadCosto vacio', req(1, { ExternalReference: ref('F2'), FarmCode: '' }));
    await caso('6a reintento R1 mismo monto tras aprobada', 'Authorized mismos numSolicitud/numCredito, 0 llamadas', req(1, { ExternalReference: R1 }));
    await caso('6b misma ref R1 otro monto (2)', 'Unavailable/DuplicateAttempt, 0 llamadas', req(2, { ExternalReference: R1 }));
    await caso('6c reintento tras timeout (T1)', 'Unavailable/DuplicateAttempt, 0 llamadas', req(15000.01, { ExternalReference: R4 }));
    await caso('6d reintento tras Rejected funcional (B1)', 'llama de nuevo (1 llamada), Rejected', req(12000, { ExternalReference: R2 }));
    await caso('6e reintento tras Rejected disponible (C1)', 'llama de nuevo (1 llamada), Rejected', req(30000, { ExternalReference: R3 }));
    {
      const C = ref('K1'); const b = await sim();
      const [x, y] = await Promise.all([runRunner(req(1, { ExternalReference: C })), runRunner(req(1, { ExternalReference: C }))]);
      const a = await sim();
      log({ caso: '7 dos envios concurrentes misma ref', esperado: 'un solo llamado al simulador', llamadasSim: a.llamadas.filter(l => l.id > b.max).length, simAntes: b.max, simDespues: a.max, resultados: [x, y].map(parse), attempt: await attempt(C), auditoria: await audit(C) });
    }
    {
      const b = await sim(); const x = await runRunner(req(1, { ExternalReference: null })); const y = await runRunner(req(1, { ExternalReference: null })); const a = await sim();
      log({ caso: '8 sin ExternalReference dos envios', esperado: 'dos llamadas (sin guarda)', llamadasSim: a.llamadas.filter(l => l.id > b.max).length, simAntes: b.max, simDespues: a.max, resultados: [x, y].map(parse) });
    }
    await setCred(BASIC_USER, 'basic-equivocada');
    await caso('9a cabecera Basic incorrecta', 'Unavailable/Security, sin crear credito (sigCredito igual)', req(1, { ExternalReference: ref('S1') }));
    await setCred(SFA_USER, SFA_PASS);
    await caso('9b pares cruzados (cabecera = par SFA)', 'Unavailable/Security (son pares distintos)', req(1, { ExternalReference: ref('S2') }));
    await setCred(BASIC_USER, BASIC_PASS); await setParam('SfaPassword', 'sfa-equivocada');
    await caso('9c cuerpo Contrasena SFA incorrecta, cabecera correcta', 'Unavailable/Security', req(1, { ExternalReference: ref('S3') }));
    await setParam('SfaPassword', SFA_PASS);
    await setCred(null, null); await setParam('SfaUser', null); await setParam('SfaPassword', null);
    await caso('9d todo vacio con respaldo vacio', 'Unavailable/NotConfigured, 0 llamadas', req(1, { ExternalReference: ref('N1') }));
    await setParam('SfaUser', SFA_USER); await setParam('SfaPassword', SFA_PASS);
    await caso('9e cabecera vacia, par SFA ok', 'Unavailable/NotConfigured, 0 llamadas', req(1, { ExternalReference: ref('N2') }));
    await setCred(BASIC_USER, BASIC_PASS); await setParam('SfaUser', null);
    await caso('9f cabecera ok, SfaUser vacio', 'Unavailable/NotConfigured, 0 llamadas', req(1, { ExternalReference: ref('N3') }));
    await setParam('SfaUser', SFA_USER);
    await caso('10 agencia sin mapeo STORE (BranchId 98)', 'NotConfigured con mensaje, 0 llamadas', req(1, { ExternalReference: ref('M1'), BranchId: 98 }));
    await caso('11 control: aprobada de nuevo', 'Authorized', req(1, { ExternalReference: ref('Z1') }));
    log({ paso: 'prefijo-referencias', prefijo: 'E2F' + STAMP });
  } finally {
    try {
      await setEvent(0, PLACEHOLDER); await setCred(null, null); await setParam('SfaUser', null); await setParam('SfaPassword', null); await setParam('CompanyCode', '001');
      await pool.request().query("DELETE FROM CrossReference WHERE CompanyId=1 AND CatalogId=1 AND ExternalId='001' AND InternalId='99'");
    } catch (e) { console.error('LIMPIEZA FALLO', e.message); }
    await pool.close();
  }
})().catch(e => { console.error('FALLO e2e', e); process.exit(1); });