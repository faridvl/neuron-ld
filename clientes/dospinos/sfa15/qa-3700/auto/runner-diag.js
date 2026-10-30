// Llama al Runner por stdin con la cadena (ya codificada) del Web.config publicado. Uso: node runner-diag.js <monto> <ref>
const { spawn } = require('child_process'); const fs = require('fs');
const wc = fs.readFileSync('C:/inetpub/wwwroot/dp/otros/ServiciosWCF/Web.config', 'utf8');
const m = wc.match(/connectionString="([^"]*)"\s+name="LD\.AccesoDatos\.My\.MySettings\.LDDPINTEGRATIONS"\s*\/>/);
const cs = m[1];
const [monto, ref] = [process.argv[2] || '1', process.argv[3] || 'DIAG' + Date.now().toString().slice(-8)];
const params = { CustomerCode: '4000010', BranchId: 19, DocumentDate: '2026-10-29T00:00:00', CustomerName: 'Diag', UsesCreditLine: true, CreditLineNumber: 0, ExternalReference: ref, FarmCode: "3664", TermInWeeks: 4, FinancingPlanExternalCode: '203', Amount: Number(monto), Notes: 'diag' };
const t0 = Date.now();
const c = spawn('C:/inetpub/wwwroot/dp/otros/ServiciosWCF/bin/Integration.Runner.exe', [], { stdio: ['pipe', 'pipe', 'pipe'] });
let so = '', se = ''; c.stdout.on('data', d => so += d); c.stderr.on('data', d => se += d);
c.on('close', code => { console.log('ms', Date.now() - t0, 'exit', code); console.log('OUT', so.slice(-1500)); console.log('ERR', se.slice(-1500)); });
c.stdin.write(JSON.stringify({ Method: 'ValidateFinancingPlan', Token: 'diag', Stage: 'TESTING', Tenant: 'DOS_PINOS', IntegrationConnectionString: cs, Params: JSON.stringify(params) }) + '\n'); c.stdin.end();
