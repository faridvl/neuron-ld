'use strict';
// Prueba de punta a punta de SFA15: Runner.exe (por stdin, como lo lanza el SDK) -> servicio -> cliente HTTP -> simulador local.
// Solo toca el Docker local (localhost,1433) y deja la configuracion del evento como estaba al terminar.
// Uso: node e2e-sfa15.js <ruta Integration.Runner.exe> <ruta .env con DB_CONNECTION_STRING> [urlSimulador]
const path = require('path');
const { spawn } = require('child_process');
const sql = require(path.join('C:/Users/fvillacis/ClaudeLocalSession/sfa15/simulador-pruebas/deps/node_modules/mssql'));

const [runnerPath, envPath, simulatorBaseUrl = 'http://localhost:7391'] = process.argv.slice(2);
const fs = require('fs');
const connectionString = fs.readFileSync(envPath, 'utf8').split(/\r?\n/).find(line => line.startsWith('DB_CONNECTION_STRING=')).slice('DB_CONNECTION_STRING='.length);
const connectionParts = Object.fromEntries(connectionString.split(';').filter(Boolean).map(part => { const index = part.indexOf('='); return [part.slice(0, index).trim().toLowerCase(), part.slice(index + 1)]; }));

// El Runner espera la clave de la conexion con la codificacion del VB legado (la misma que llega por el SDK).
const encodeLegacyPassword = (plain) => [...plain].reverse().map(ch => { const code = String(ch.charCodeAt(0)); return String(code.length * 2) + code; }).join('');
const runnerConnectionString = connectionString.replace(/(password=)([^;]*)/i, (all, prefix, value) => prefix + encodeLegacyPassword(value));

const ALLOWED_SERVER = 'localhost,1433';
const ALLOWED_DATABASE = 'LDCOM_DOS_PINOS_INTEGRATIONS_DEVELOP_DOCKER';
if (connectionParts.server !== ALLOWED_SERVER || connectionParts.database !== ALLOWED_DATABASE) {
  console.error('Conexion no permitida: solo ' + ALLOWED_SERVER + ' / ' + ALLOWED_DATABASE);
  process.exit(2);
}

const EVENT_NAME = 'CREDIT_VALIDATION';
// Filas temporales de CrossReference (Docker local) para probar la traduccion; se borran al terminar.
const TEST_BRANCH_ID = 99, TEST_BRANCH_EXTERNAL = '001';
const TEST_FARM_CUSTOMER_ID = 99999999, TEST_FARM_EXTERNAL = '2563';
const STORE_CATALOG_ID = 1, CUSTOMER_CATALOG_ID = 7, COMPANY_ID = 1;
const SIMULATOR_PATH = '/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final';
const SIMULATOR_USER = 'e2e-usuario';
const SIMULATOR_PASSWORD = 'e2e-clave';
const PLACEHOLDER_URL = 'https://CHANGE_ME/p_SFA15_Autorizacion_Venta_Final';

const pool = new sql.ConnectionPool({
  server: 'localhost', port: 1433, database: connectionParts.database,
  user: connectionParts['user id'], password: connectionParts.password,
  options: { trustServerCertificate: true }
});

const baseRequest = (amount, changes = {}) => ({
  CustomerCode: '4000010', IdentificationTypeCode: null, IdentificationNumber: null,
  BranchId: TEST_BRANCH_ID, DocumentDate: '2026-10-27T00:00:00', CustomerName: 'Luis Mangel Alfaro Leal',
  UsesCreditLine: true, CreditLineNumber: 0, ExternalReference: 'FAC-E2E-' + Date.now().toString().slice(-6),
  FarmCustomerId: TEST_FARM_CUSTOMER_ID, TermInWeeks: 4, FinancingPlanExternalCode: '201', Amount: amount, Notes: 'prueba e2e', ...changes
});

function runRunner(params) {
  return new Promise((resolve) => {
    const startedAt = Date.now();
    const child = spawn(runnerPath, [], { stdio: ['pipe', 'pipe', 'pipe'] });
    let standardOutput = ''; let standardError = '';
    child.stdout.on('data', chunk => standardOutput += chunk);
    child.stderr.on('data', chunk => standardError += chunk);
    child.on('close', () => {
      let response = null;
      try { response = JSON.parse(standardOutput.trim().split(/\r?\n/).pop()); } catch (error) { /* se reporta crudo */ }
      resolve({ elapsedMs: Date.now() - startedAt, response, standardOutput, standardError });
    });
    const command = { Method: 'ValidateFinancingPlan', Token: 'e2e', Stage: 'TESTING', Tenant: 'DOS_PINOS', IntegrationConnectionString: runnerConnectionString, Params: JSON.stringify(params) };
    child.stdin.write(JSON.stringify(command) + '\n');
    child.stdin.end();
  });
}

async function simulatorCallCount() {
  const response = await fetch(simulatorBaseUrl + '/sim/sfa15');
  const body = await response.json();
  const list = Array.isArray(body) ? body : (body.llamadas || body.calls || body.items || []);
  return list.length;
}

async function setEvent(isActive, endpointUrl) {
  await pool.request().input('isActive', sql.Bit, isActive).input('url', sql.NVarChar, endpointUrl).input('name', sql.NVarChar, EVENT_NAME)
    .query('UPDATE IntegrationEvent SET IsActive=@isActive, EndpointUrl=@url WHERE Name=@name');
}
async function setCredential(user, password) {
  await pool.request().input('user', sql.NVarChar, user).input('password', sql.NVarChar, password).input('name', sql.NVarChar, EVENT_NAME)
    .query('UPDATE IntegrationCredential SET AuthenticationUser=@user, AuthenticationPassword=@password WHERE EventCode=@name');
}
async function setParameter(name, value) {
  await pool.request().input('parameterName', sql.NVarChar, name).input('value', sql.NVarChar, value).input('eventName', sql.NVarChar, EVENT_NAME)
    .query('UPDATE P SET ParameterValue=@value FROM IntegrationEventParameter P JOIN IntegrationEvent E ON E.Id=P.IntegrationEventId WHERE E.Name=@eventName AND P.ParameterName=@parameterName');
}
async function auditRowsFor(reference) {
  const result = await pool.request().input('reference', sql.NVarChar, '%' + reference + '%')
    .query("SELECT TOP 10 Phase, Status, LEFT(Payload, 300) AS Payload FROM Events WHERE TransactionId LIKE '%' + @reference + '%' ORDER BY Id");
  return result.recordset;
}

(async () => {
  await pool.connect();
  const rows = [];
  const simulatorUrl = simulatorBaseUrl + SIMULATOR_PATH;
  try {
    await pool.request().query("INSERT INTO CrossReference (CatalogId, ExternalId, InternalId, CompanyId) VALUES (1,'001','99',1),(7,'2563','99999999',1)");
    await setEvent(1, simulatorUrl);
    await setCredential(SIMULATOR_USER, SIMULATOR_PASSWORD);

    const scenarios = [
      ['monto 1 (OK)', 1, {}],
      ['monto 10000 (limite OK)', 10000, {}],
      ['monto 10000.01 (rechazo funcional)', 10000.01, {}],
      ['monto 15000 (limite rechazo)', 15000, {}],
      ['monto 15000.01 (timeout: simulador 40 s > 35 s)', 15000.01, {}],
      ['monto 20000.01 (conectividad)', 20000.01, {}],
      ['idExterno de 16 caracteres (solicitud invalida)', 1, { ExternalReference: 'ABCDEFGHIJKLMNOP' }],
      ['sin identificacion del cliente (solicitud invalida)', 1, { CustomerCode: null }],
      ['monto 0 (solicitud invalida)', 0, {}],
      ['sucursal real Suc_Id 4 -> AV-GUAYABO (10 car. > 5 de codAgencia)', 1, { BranchId: 4 }],
      ['sucursal sin mapeo (Suc_Id 98)', 1, { BranchId: 98 }],
      ['finca sin mapeo (Cliente 98)', 1, { FarmCustomerId: 98 }],
      ['sucursal y finca sin mapeo', 1, { BranchId: 98, FarmCustomerId: 98 }],
    ];
    for (const [label, amount, changes] of scenarios) {
      const before = await simulatorCallCount();
      const request = baseRequest(amount, changes);
      const outcome = await runRunner(request);
      const after = await simulatorCallCount();
      const lastCall = (await (await fetch(simulatorBaseUrl + '/sim/sfa15')).json()).llamadas[0];
      const sentBody = after > before && lastCall ? JSON.parse(lastCall.request.body).Datos_Entrada : null;
      rows.push({ label, amount, sentCodAgencia: sentBody && sentBody.codAgencia, sentCodUnidadCosto: sentBody && sentBody.codUnidadCosto, runnerSuccess: outcome.response && outcome.response.Success, result: outcome.response && outcome.response.Result ? JSON.parse(outcome.response.Result) : null, error: outcome.response && outcome.response.Error, elapsedMs: outcome.elapsedMs, simulatorCalls: after - before, stderr: outcome.standardError.slice(0, 200), audit: (await auditRowsFor(request.ExternalReference)).map(row => row.Phase + '/' + row.Status) });
    }

    await setCredential(SIMULATOR_USER, 'clave-equivocada');
    {
      const before = await simulatorCallCount();
      const request = baseRequest(1);
      const outcome = await runRunner(request);
      rows.push({ label: 'credenciales malas (seguridad)', amount: 1, runnerSuccess: outcome.response && outcome.response.Success, result: outcome.response && outcome.response.Result ? JSON.parse(outcome.response.Result) : null, elapsedMs: outcome.elapsedMs, simulatorCalls: (await simulatorCallCount()) - before });
    }
    await setCredential(SIMULATOR_USER, SIMULATOR_PASSWORD);

    await setEvent(0, simulatorUrl);
    {
      const before = await simulatorCallCount();
      const outcome = await runRunner(baseRequest(1));
      rows.push({ label: 'evento inactivo', amount: 1, result: outcome.response && outcome.response.Result ? JSON.parse(outcome.response.Result) : null, elapsedMs: outcome.elapsedMs, simulatorCalls: (await simulatorCallCount()) - before });
    }
    await setEvent(1, PLACEHOLDER_URL);
    {
      const before = await simulatorCallCount();
      const outcome = await runRunner(baseRequest(1));
      rows.push({ label: 'URL CHANGE_ME', amount: 1, result: outcome.response && outcome.response.Result ? JSON.parse(outcome.response.Result) : null, elapsedMs: outcome.elapsedMs, simulatorCalls: (await simulatorCallCount()) - before });
    }
    await setEvent(1, 'http://example.invalid/p_SFA15');
    {
      const before = await simulatorCallCount();
      const outcome = await runRunner(baseRequest(1));
      rows.push({ label: 'http a host que no es localhost', amount: 1, result: outcome.response && outcome.response.Result ? JSON.parse(outcome.response.Result) : null, elapsedMs: outcome.elapsedMs, simulatorCalls: (await simulatorCallCount()) - before });
    }
    await setEvent(1, 'http://localhost:7399/p_SFA15');
    {
      const outcome = await runRunner(baseRequest(1));
      rows.push({ label: 'nadie escucha (conectividad real)', amount: 1, result: outcome.response && outcome.response.Result ? JSON.parse(outcome.response.Result) : null, elapsedMs: outcome.elapsedMs });
    }
  } finally {
    await setEvent(0, PLACEHOLDER_URL);
    await setCredential(null, null);
    await pool.request().query("DELETE FROM CrossReference WHERE CompanyId=1 AND ((CatalogId=1 AND ExternalId='001' AND InternalId='99') OR (CatalogId=7 AND ExternalId='2563' AND InternalId='99999999'))");
    await pool.close();
  }
  for (const row of rows) console.log(JSON.stringify(row));
})().catch(error => { console.error('FALLO e2e:', error); process.exit(1); });
