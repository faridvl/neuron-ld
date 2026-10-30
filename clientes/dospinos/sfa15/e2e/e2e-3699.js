'use strict';
// E2E 2a pasada SFA15 (QA ronda de correcciones): Runner real por stdin -> simulador local 7391 + mini servidor 7392. Solo Docker local.
// Uso: node e2e-final-2.js <Integration.Runner.exe> <.env>
const fs = require('fs');
const http = require('http');
const { spawn } = require('child_process');
const sql = require('C:/Users/fvillacis/ClaudeLocalSession/sfa15/simulador-pruebas/deps/node_modules/mssql');
const [runnerPath, envPath] = process.argv.slice(2);
const SIM = 'http://localhost:7391';
const cs = fs.readFileSync(envPath, 'utf8').split(/\r?\n/).find(l => l.startsWith('DB_CONNECTION_STRING=')).slice(21);
const parts = Object.fromEntries(cs.split(';').filter(Boolean).map(x => { const i = x.indexOf('='); return [x.slice(0, i).trim().toLowerCase(), x.slice(i + 1)]; }));
if (parts.server !== 'localhost,1433' || parts.database !== 'LDCOM_INTEGRATIONS_3699_DOCKER') { console.error('Conexion no permitida'); process.exit(2); }
const enc = (plain) => [...plain].reverse().map(ch => { const c = String(ch.charCodeAt(0)); return String(c.length * 2) + c; }).join('');
const runnerCs = cs.replace(/(password=)([^;]*)/i, (a, p, v) => p + enc(v));
const PATH_EVENTO = '/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final';
const URL_OK = SIM + PATH_EVENTO;
const URL_MINI = 'http://localhost:7392' + PATH_EVENTO;
const URL_SIN_SERVIDOR = 'http://localhost:7399' + PATH_EVENTO;
const PLACEHOLDER = 'https://CHANGE_ME/p_SFA15_Autorizacion_Venta_Final';
const BASIC_USER = 'e2e-basic-usuario', BASIC_PASS = 'e2e-basic-clave', SFA_USER = 'e2e-usuario', SFA_PASS = 'e2e-clave';
const VALORES_PRUEBA = ['e2e-usuario', 'e2e-clave', 'e2e-basic-usuario', 'e2e-basic-clave', 'basic-equivocada', 'sfa-equivocada'];
const STAMP = Date.now().toString(36).slice(-6).toUpperCase();
const ref = (tag) => 'E2G' + STAMP + tag;
const pool = new sql.ConnectionPool({ server: 'localhost', port: 1433, database: parts.database, user: parts['user id'], password: parts.password, options: { trustServerCertificate: true } });
const log = (o) => console.log(JSON.stringify(o));

// Mini servidor de prueba: modo contradictorio | 401 | 403 | secreto.
let miniModo = 'contradictorio'; let miniLlamadas = 0;
const mini = http.createServer((rq, rs) => {
  rq.on('data', () => {}); rq.on('end', () => {
    miniLlamadas++;
    if (miniModo === '401') { rs.writeHead(401); return rs.end(); }
    if (miniModo === '403') { rs.writeHead(403); return rs.end(); }
    rs.writeHead(200, { 'Content-Type': 'application/json' });
    if (miniModo === 'secreto') {
      const m = 'Usuario e2e-usuario o clave e2e-clave invalidos; cabecera e2e-basic-clave';
      return rs.end(JSON.stringify({ Respuesta: { numSolicitud: null, numCredito: null, indEstado: null, inconsistencia: null, monDisponible: null }, CodigoError: 'SFA15-F01', TipoError: 'Funcional', Mensaje: m, DetalleTransaccion: [m], HttpStatus: '400' }));
    }
    return rs.end('{"Respuesta":{"numSolicitud":7,"indEstado":"A"},"TipoError":"Funcional"}');
  });
});

const req = (amount, over = {}) => ({ CustomerCode: '4000010', IdentificationTypeCode: null, IdentificationNumber: null, BranchId: 99, DocumentDate: '2026-10-28T00:00:00', CustomerName: 'Cliente Prueba E2E', UsesCreditLine: true, CreditLineNumber: 0, ExternalReference: ref('X'), FarmCode: '2563', TermInWeeks: 4, FinancingPlanExternalCode: '201', Amount: amount, Notes: 'prueba e2e final 2', ...over });

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
async function attemptRow(r) { const x = await pool.request().input('r', sql.NVarChar, r).query('SELECT Status,RequestNumber,CreditNumber,AvailableAmount,Message,RequestFingerprint,CONVERT(varchar(40),UpdatedAt,126) UpdatedAt FROM CreditValidationAttempt WHERE ExternalReference=@r'); return x.recordset[0] || null; }
async function attempt(r) { const x = await attemptRow(r); return x ? x.Status + '/' + x.RequestNumber + '/' + x.CreditNumber : 'sin fila'; }
async function maxEvent() { const x = await pool.request().query('SELECT ISNULL(MAX(Id),0) m FROM Events'); return x.recordset[0].m; }
async function auditRows(r, afterId) { const x = await pool.request().input('r', sql.NVarChar, '%' + r + '%').input('i', sql.BigInt, afterId).query("SELECT Id,Phase,Status,Payload,ErrorMessage FROM Events WHERE Type='CREDIT_VALIDATION' AND TransactionId LIKE @r AND Id>@i ORDER BY Id"); return x.recordset; }
const auditTxt = (rows) => rows.map(w => w.Phase + '/' + w.Status).join(' > ');
const parse = (z) => (z.r && z.r.Result ? JSON.parse(z.r.Result) : z.r);

async function caso(label, esperado, params, extra = {}) {
  const b = await sim(); const e0 = await maxEvent(); const mini0 = miniLlamadas;
  const o = await runRunner(params);
  const a = await sim();
  const nuevas = a.llamadas.filter(l => l.id > b.max);
  const ult = nuevas[0];
  let body = null; try { body = ult && JSON.parse(ult.request.body); } catch (e) { /* sin cuerpo */ }
  const d = body && body.Datos_Entrada;
  const rows = await auditRows(params.ExternalReference || '#none#', e0);
  const fila = await attemptRow(params.ExternalReference || '#none#');
  log({ caso: label, esperado, success: o.r && o.r.Success, error: o.r && o.r.Error, res: parse(o), ms: o.ms, llamadasSim: nuevas.length, llamadasMini: miniLlamadas - mini0, simAntes: b.max, simDespues: a.max, sigSolicitud: a.sol, sigCredito: a.cre,
    simVio: ult ? { http: ult.http, auth: ult.request.headers.authorization, Usuario: body && body.Usuario, codEmpresa: d && d.codEmpresa, codAgencia: d && d.codAgencia, codUnidadCosto: d && d.codUnidadCosto, idExterno: d && d.idExterno, monSolicitud: d && d.monSolicitud, respuesta: ult.respuesta } : null,
    attempt: fila ? fila.Status + '/' + fila.RequestNumber + '/' + fila.CreditNumber : 'sin fila', attemptMessage: fila && fila.Message, auditoria: auditTxt(rows), auditoriaDetalle: extra.detalle ? rows : undefined, stderr: o.se.slice(0, 150) });
}

(async () => {
  await new Promise(r => mini.listen(7392, r));
  await pool.connect();
  const eventoBase = await maxEvent();
  const inicio = new Date().toISOString();
  log({ paso: 'inicio', eventoBase, inicio });
  try {
    await pool.request().query("INSERT INTO CrossReference (CatalogId, ExternalId, InternalId, CompanyId) VALUES (1,'001','99',1)");
    await setEvent(1, URL_OK); await setCred(BASIC_USER, BASIC_PASS); await setParam('SfaUser', SFA_USER); await setParam('SfaPassword', SFA_PASS); await setParam('CompanyCode', '001');
    log({ paso: 'config', basicUser: BASIC_USER, sfaUser: SFA_USER, paresDistintos: BASIC_USER !== SFA_USER && BASIC_PASS !== SFA_PASS });
    const R1 = ref('A1'), R2 = ref('B1'), R3 = ref('C1'), R4 = ref('T1');
    await caso('1 aprobada con finca', 'Authorized + numSolicitud/numCredito; Basic e2e-basic-usuario, Usuario e2e-usuario', req(1, { ExternalReference: R1 }), { detalle: true });
    await caso('2 rechazo funcional (12000)', 'Rejected con mensaje', req(12000, { ExternalReference: R2 }));
    await caso('3 rechazo por disponible (30000)', 'Rejected, RequestNumber, AvailableAmount, PossiblyApplied false', req(30000, { ExternalReference: R3 }));
    await caso('4 timeout (15000.01)', 'Unavailable/Timeout PossiblyApplied true (~36 s), UNCERTAIN', req(15000.01, { ExternalReference: R4 }));
    const sinFinca = req(1, { ExternalReference: ref('F1') }); delete sinFinca.FarmCode;
    await caso('5a sin finca (FarmCode ausente)', 'Authorized con codUnidadCosto vacio', sinFinca);
    await caso('5b FarmCode vacio', 'Authorized con codUnidadCosto vacio', req(1, { ExternalReference: ref('F2'), FarmCode: '' }));
    await caso('6a reintento R1 mismo monto tras aprobada', 'Authorized mismos numSolicitud/numCredito, 0 llamadas', req(1, { ExternalReference: R1 }), { detalle: true });
    const antes13 = await attemptRow(R1);
    await caso('6b/13 misma ref R1 ya Authorized con otro monto (2)', 'Rejected (no DuplicateAttempt), PossiblyApplied false, 0 llamadas, fila AUTHORIZED intacta', req(2, { ExternalReference: R1 }), { detalle: true });
    const despues13 = await attemptRow(R1);
    log({ caso: '13 fila AUTHORIZED antes/despues', esperado: 'identicas (mismo numSolicitud/numCredito, Fingerprint, UpdatedAt)', antes: antes13, despues: despues13, identicas: JSON.stringify(antes13) === JSON.stringify(despues13) });
    await caso('6c reintento tras timeout (T1)', 'Unavailable/DuplicateAttempt, 0 llamadas', req(15000.01, { ExternalReference: R4 }), { detalle: true });
    await caso('6d reintento tras Rejected funcional (B1)', 'llama de nuevo (1 llamada), Rejected', req(12000, { ExternalReference: R2 }));
    await caso('6e reintento tras Rejected disponible (C1)', 'llama de nuevo (1 llamada), Rejected', req(30000, { ExternalReference: R3 }));
    {
      const C = ref('K1'); const b = await sim();
      const [x, y] = await Promise.all([runRunner(req(1, { ExternalReference: C })), runRunner(req(1, { ExternalReference: C }))]);
      const a = await sim();
      log({ caso: '7 dos envios concurrentes misma ref', esperado: 'un solo llamado al simulador', llamadasSim: a.llamadas.filter(l => l.id > b.max).length, simAntes: b.max, simDespues: a.max, resultados: [x, y].map(parse), attempt: await attempt(C), auditoria: auditTxt(await auditRows(C, eventoBase)) });
    }
    {
      const b = await sim(); const x = await runRunner(req(1, { ExternalReference: null })); const y = await runRunner(req(1, { ExternalReference: null })); const a = await sim();
      log({ caso: '8 sin ExternalReference dos envios', esperado: 'dos llamadas (sin guarda)', llamadasSim: a.llamadas.filter(l => l.id > b.max).length, simAntes: b.max, simDespues: a.max, resultados: [x, y].map(parse) });
    }
    const S1 = ref('S1');
    await setCred(BASIC_USER, 'basic-equivocada');
    await caso('9a cabecera Basic incorrecta', 'Unavailable/Security, PossiblyApplied false, simulador 401 sin crear credito, NOT_SENT', req(1, { ExternalReference: S1 }), { detalle: true });
    await setCred(SFA_USER, SFA_PASS);
    await caso('9b pares cruzados (cabecera = par SFA)', 'Unavailable/Security, PossiblyApplied false, NOT_SENT', req(1, { ExternalReference: ref('S2') }));
    await setCred(BASIC_USER, BASIC_PASS); await setParam('SfaPassword', 'sfa-equivocada');
    await caso('9c cabecera correcta, SfaPassword incorrecta (simulador 500 autenticacion)', 'Unavailable/Security, PossiblyApplied false, NOT_SENT', req(1, { ExternalReference: ref('S3') }));
    await setParam('SfaPassword', SFA_PASS);
    await caso('9g reintento con la MISMA referencia de 9a tras corregir la credencial', 'llama de nuevo (1 llamada) y Authorized', req(1, { ExternalReference: S1 }), { detalle: true });
    await setCred(null, null); await setParam('SfaUser', null); await setParam('SfaPassword', null);
    await caso('9d todo vacio con respaldo vacio', 'Unavailable/NotConfigured, 0 llamadas', req(1, { ExternalReference: ref('N1') }));
    await setParam('SfaUser', SFA_USER); await setParam('SfaPassword', SFA_PASS);
    await caso('9e cabecera vacia, par SFA ok', 'Unavailable/NotConfigured, 0 llamadas', req(1, { ExternalReference: ref('N2') }));
    await setCred(BASIC_USER, BASIC_PASS); await setParam('SfaUser', null);
    await caso('9f cabecera ok, SfaUser vacio', 'Unavailable/NotConfigured, 0 llamadas', req(1, { ExternalReference: ref('N3') }));
    await setParam('SfaUser', SFA_USER);
    await caso('10 agencia sin mapeo STORE (BranchId 98)', 'NotConfigured con mensaje, 0 llamadas', req(1, { ExternalReference: ref('M1'), BranchId: 98 }));
    await caso('11 control: aprobada de nuevo', 'Authorized', req(1, { ExternalReference: ref('Z1') }));

    await setEvent(1, URL_MINI); miniModo = 'contradictorio';
    const A12 = ref('W1');
    await caso('12 A + TipoError Funcional (mini servidor)', 'Unavailable/Technical, PossiblyApplied true, UNCERTAIN', req(1, { ExternalReference: A12 }), { detalle: true });
    await caso('12b reintento misma ref tras 12', 'Unavailable/DuplicateAttempt, 0 llamadas al mini servidor', req(1, { ExternalReference: A12 }), { detalle: true });
    miniModo = '401';
    await caso('12c HTTP 401 cuerpo vacio (mini)', 'Unavailable/Security, PossiblyApplied false, NOT_SENT', req(1, { ExternalReference: ref('W2') }));
    miniModo = '403';
    await caso('12d HTTP 403 cuerpo vacio (mini)', 'Unavailable/Security, PossiblyApplied false, NOT_SENT', req(1, { ExternalReference: ref('W3') }));
    miniModo = 'secreto';
    await caso('12e rechazo funcional con secretos de prueba dentro de Mensaje (mini)', 'Rejected; Message, Events y CreditValidationAttempt.Message con *** y sin e2e-usuario/e2e-clave/e2e-basic-clave', req(1, { ExternalReference: ref('W4') }), { detalle: true });

    await setEvent(1, URL_SIN_SERVIDOR);
    const C14 = ref('D1');
    await caso('14 conexion rechazada (puerto 7399 sin servidor)', 'Unavailable/Connectivity, PossiblyApplied false, NOT_SENT', req(1, { ExternalReference: C14 }), { detalle: true });
    await setEvent(1, URL_OK);
    await caso('14b reintento misma ref apuntando de vuelta al simulador', 'llama (1 llamada) y Authorized', req(1, { ExternalReference: C14 }));

    await pool.request().query("INSERT INTO CrossReference (CatalogId, ExternalId, InternalId, CompanyId) VALUES (1,'ABCDEF','97',1)");
    try {
      await caso('15 agencia con codigo externo de 6 caracteres (BranchId 97)', 'NotConfigured, 0 llamadas', req(1, { ExternalReference: ref('G1'), BranchId: 97 }));
    } finally {
      await pool.request().query("DELETE FROM CrossReference WHERE CompanyId=1 AND CatalogId=1 AND ExternalId='ABCDEF' AND InternalId='97'");
      log({ paso: 'cross-reference-temporal-borrada', quedan: (await pool.request().query("SELECT COUNT(*) n FROM CrossReference WHERE ExternalId='ABCDEF' AND InternalId='97'")).recordset[0].n });
    }

    const cond = VALORES_PRUEBA.map(v => "Payload LIKE '%" + v + "%' OR ErrorMessage LIKE '%" + v + "%'").join(' OR ');
    const fuga = await pool.request().input('i', sql.BigInt, eventoBase).query("SELECT Id,Phase,Status,LEFT(Payload,200) Payload,LEFT(ErrorMessage,200) ErrorMessage FROM Events WHERE EventCode='POS-10' AND Id>@i AND (" + cond + ')');
    const total = await pool.request().input('i', sql.BigInt, eventoBase).query("SELECT COUNT(*) n, MIN(Id) minId, MAX(Id) maxId FROM Events WHERE EventCode='POS-10' AND Id>@i");
    log({ paso: 'fuga-valores-prueba', esperado: '0 filas', eventosPOS10: total.recordset[0], filasConValores: fuga.recordset.length, filas: fuga.recordset });
    const fugaAttempt = await pool.request().query("SELECT ExternalReference,Message FROM CreditValidationAttempt WHERE ExternalReference LIKE 'E2G" + STAMP + "%' AND (" + VALORES_PRUEBA.map(v => "Message LIKE '%" + v + "%'").join(' OR ') + ')');
    log({ paso: 'fuga-valores-en-CreditValidationAttempt.Message', esperado: '0 filas', filas: fugaAttempt.recordset.length, detalle: fugaAttempt.recordset });
    log({ paso: 'prefijo-referencias', prefijo: 'E2G' + STAMP, inicio, eventoBase });
  } finally {
    try {
      await setEvent(0, PLACEHOLDER); await setCred(null, null); await setParam('SfaUser', null); await setParam('SfaPassword', null); await setParam('CompanyCode', '001');
      await pool.request().query("DELETE FROM CrossReference WHERE CompanyId=1 AND CatalogId=1 AND ExternalId='001' AND InternalId='99'");
      await pool.request().query("DELETE FROM CrossReference WHERE CompanyId=1 AND CatalogId=1 AND ExternalId='ABCDEF' AND InternalId='97'");
    } catch (e) { console.error('LIMPIEZA FALLO', e.message); }
    await pool.close(); mini.close();
  }
})().catch(e => { console.error('FALLO e2e', e); process.exit(1); });