#!/usr/bin/env node
// Capacidad por ciclo de entrega de la iteracion de casos Dos Pinos. Solo lectura.
//
// Ciclo: jueves a miercoles (5 dias habiles). El miercoles es la fecha limite de entrega (DueDate)
// y el jueves siguiente es el release: nada de un ciclo se trabaja el jueves.
//
//   dias_restantes  = fraccion de hoy + dias habiles desde mañana hasta el miercoles
//   capacidad_ciclo = 32h * dias_restantes / 5
//   libre           = capacidad_ciclo - suma(RemainingWork de los tickets del ciclo)
//   maximo_ticket   = 16h * dias_restantes / 5   (un ticket lo hace un solo dev)
//
// Uso: node capacidad.mjs [--horas N] [--ciclos 3]
//   Con --horas indica en que ciclo cabe un ticket de N horas y que DueDate escribir.

import { execFileSync } from 'node:child_process';

const ORG = 'LD-Vacas';
const PROJECT = 'AV Retail Dos Pinos';
const ITERATION = 'AV Retail Dos Pinos\\Casos Dos Pinos';
const HORAS_DEV_CICLO = 16;
const DEVS = 2;
const DIAS_CICLO = 5;
const OFFSET_CR_HORAS = -6; // Costa Rica, sin horario de verano

const arg = (k, def) => { const i = process.argv.indexOf(k); return i > 0 ? Number(process.argv[i + 1]) : def; };
const horasTicket = arg('--horas', null);
const nCiclos = arg('--ciclos', 3);

function leerPat() {
  if (process.env.AZURE_DEVOPS_PAT) return process.env.AZURE_DEVOPS_PAT.trim();
  try {
    const out = execFileSync('reg', ['query', 'HKCU\\Environment', '/v', 'AZURE_DEVOPS_PAT'], { encoding: 'utf8' });
    return out.match(/AZURE_DEVOPS_PAT\s+REG_\w+\s+(\S+)/)?.[1];
  } catch { return undefined; }
}
const pat = leerPat();
if (!pat) { console.error('Falta AZURE_DEVOPS_PAT.'); process.exit(1); }
const headers = { Authorization: 'Basic ' + Buffer.from(':' + pat).toString('base64'), 'Content-Type': 'application/json' };
const base = `https://dev.azure.com/${ORG}/${encodeURIComponent(PROJECT)}/_apis/wit`;
async function api(url, body) {
  const res = await fetch(url, { method: body ? 'POST' : 'GET', headers, body: body && JSON.stringify(body) });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} en ${url.split('?')[0]}`);
  return res.json();
}

// --- Fechas (todo en dias calendario UTC que representan fechas de Costa Rica) ---
const DIA = 86400e3;
const iso = d => d.toISOString().slice(0, 10);
const addDias = (d, n) => new Date(d.getTime() + n * DIA);
const nombreDia = d => ['dom', 'lun', 'mar', 'mie', 'jue', 'vie', 'sab'][d.getUTCDay()];

// Miercoles de cierre del ciclo al que pertenece una fecha. Un DueDate en jueves (convencion vieja)
// pertenece al ciclo que cierra el dia anterior, porque ese jueves es su release.
function cierreDeCiclo(fecha) {
  const d = new Date(iso(fecha) + 'T00:00:00Z');
  const dow = d.getUTCDay();
  if (dow === 4) return addDias(d, -1);
  return addDias(d, (3 - dow + 7) % 7);
}

const ahoraCR = new Date(Date.now() + OFFSET_CR_HORAS * 3600e3);
const hoy = new Date(iso(ahoraCR) + 'T00:00:00Z');
const hora = ahoraCR.getUTCHours();
const esHabil = d => d.getUTCDay() >= 1 && d.getUTCDay() <= 5;
const fraccionHoy = !esHabil(hoy) ? 0 : hora < 12 ? 1 : hora < 15 ? 0.5 : 0;

// Hoy jueves ya pertenece al ciclo nuevo (el release de hoy cierra el anterior).
const cierreActual = hoy.getUTCDay() === 4 ? addDias(hoy, 6) : cierreDeCiclo(hoy);

function diasRestantes(cierre) {
  if (iso(cierre) !== iso(cierreActual)) return DIAS_CICLO;
  let n = fraccionHoy;
  for (let d = addDias(hoy, 1); d <= cierre; d = addDias(d, 1)) if (esHabil(d)) n++;
  return n;
}

// --- Datos del board ---
const wiql = `SELECT [System.Id] FROM WorkItems
  WHERE [System.TeamProject] = '${PROJECT}'
    AND [System.IterationPath] UNDER '${ITERATION}'
    AND [System.State] <> 'Closed'`;
const { workItems } = await api(`${base}/wiql?api-version=7.0`, { query: wiql });
const ids = workItems.map(w => w.id);
const items = [];
for (let i = 0; i < ids.length; i += 200) {
  const { value } = await api(`${base}/workitemsbatch?api-version=7.0`, {
    ids: ids.slice(i, i + 200),
    fields: ['Microsoft.VSTS.Scheduling.RemainingWork', 'Microsoft.VSTS.Scheduling.OriginalEstimate',
             'Microsoft.VSTS.Scheduling.DueDate'],
  });
  items.push(...value);
}

const porCiclo = new Map();
const sinFecha = [];
const vencidos = [];
const enJueves = [];
for (const { id, fields: f } of items) {
  const horas = f['Microsoft.VSTS.Scheduling.RemainingWork'] ?? f['Microsoft.VSTS.Scheduling.OriginalEstimate'];
  if (!horas) continue; // sin estimar o sin trabajo restante: no consume capacidad
  const due = f['Microsoft.VSTS.Scheduling.DueDate'];
  if (!due) { sinFecha.push({ id, horas }); continue; }
  const cierre = cierreDeCiclo(new Date(due));
  if (cierre < cierreActual) { vencidos.push({ id, horas, due: iso(new Date(due)) }); continue; }
  if (new Date(due).getUTCDay() === 4) enJueves.push(id);
  const k = iso(cierre);
  if (!porCiclo.has(k)) porCiclo.set(k, []);
  porCiclo.get(k).push({ id, horas });
}

// --- Salida ---
const r1 = n => Math.round(n * 10) / 10;
const suma = l => l.reduce((s, x) => s + x.horas, 0);
const detalle = l => l.map(x => `#${x.id} ${x.horas}h`).join(', ');

console.log(`Hoy ${iso(hoy)} ${nombreDia(hoy)} ${String(hora).padStart(2, '0')}h (cuenta ${fraccionHoy} dia). Ciclo jue-mie, DueDate = miercoles.`);
const ciclos = [];
for (let i = 0; i < nCiclos; i++) {
  const cierre = addDias(cierreActual, 7 * i);
  const dias = diasRestantes(cierre);
  const cap = r1(HORAS_DEV_CICLO * DEVS * dias / DIAS_CICLO);
  const maxTicket = r1(HORAS_DEV_CICLO * dias / DIAS_CICLO);
  const l = porCiclo.get(iso(cierre)) ?? [];
  const libre = r1(cap - suma(l));
  ciclos.push({ cierre, libre, maxTicket });
  console.log(`Cierra mie ${iso(cierre)}: quedan ${dias} dias -> ${cap}h, comprometido ${r1(suma(l))}h, libre ${libre}h, max por ticket ${maxTicket}h${l.length ? `  (${detalle(l)})` : ''}`);
}
if (enJueves.length) console.log(`DueDate en jueves (convencion vieja, contados en el ciclo del miercoles anterior): ${enJueves.map(x => '#' + x).join(', ')}`);
if (vencidos.length) console.log(`Con DueDate ya pasado y trabajo restante: ${vencidos.map(x => `#${x.id} ${x.horas}h (${x.due})`).join(', ')}`);
if (sinFecha.length) console.log(`Sin DueDate: ${sinFecha.length} tickets, ${r1(suma(sinFecha))}h  (${detalle(sinFecha)})`);

if (horasTicket != null) {
  const c = ciclos.find(c => horasTicket <= c.libre && horasTicket <= c.maxTicket);
  console.log(c
    ? `Ticket de ${horasTicket}h: cabe en el ciclo que cierra ${iso(c.cierre)} -> DueDate ${iso(c.cierre)}T06:00:00Z`
    : `Ticket de ${horasTicket}h: no cabe en los proximos ${nCiclos} ciclos; revisar con el usuario.`);
}
