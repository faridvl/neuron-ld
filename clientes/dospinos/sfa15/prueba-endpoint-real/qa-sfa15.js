'use strict';
// QA contra el SFA15 REAL (o el simulador). Escenarios de duda: agencia, empresa, finca, plazo, tipo de credito, monto, formato.
//
// SEGURIDAD: el SFA15 real DESEMBOLSA. Por eso:
//  - La bateria normal NUNCA lleva un cliente existente: todo caso falla en validacion de cliente y no puede crear credito.
//  - Los casos con cliente real (--tier2) van aparte, apagados por defecto, y siempre llevan un tipo de credito inexistente
//    (999) para forzar el rechazo. Eso reduce el riesgo pero no lo elimina; solo correrlos con OK de Dos Pinos.
//  - Las credenciales solo se leen del entorno de esta terminal; nunca se guardan ni se imprimen.
//
// Uso:
//   $env:SFA15_USUARIO='<usuario>'; $env:SFA15_CLAVE='<clave>'
//   node qa-sfa15.js --minimo              SOLO 3 llamadas (recomendado primero): una con varios campos malos, una con los del PDF y una sin cliente
//   node qa-sfa15.js                       bateria normal (sin cliente real), unas 40 llamadas
//   node qa-sfa15.js --auth                agrega usuario y clave invalidos (1 llamada cada uno; riesgo de bloqueo de cuenta)
//   node qa-sfa15.js --tier2 --cliente 4000054 --finca 4875   casos con cliente real (ver advertencia)
//   SFA15_URL=http://localhost:7391/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final   contra el simulador
const fs = require('fs');
const path = require('path');

// Lee .env (junto al script) sin pisar variables ya puestas en la terminal ni tomar valores vacios.
try {
  for (const linea of fs.readFileSync(path.join(__dirname, '.env'), 'utf8').split(/\r?\n/)) {
    const m = /^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/.exec(linea);
    if (m && m[2] && !(m[1] in process.env)) process.env[m[1]] = m[2];
  }
} catch { /* sin .env: se usa el entorno */ }

const DEFAULT_URL ='https://usw3-cai.dm-us.informaticacloud.com/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final';
const PROCESO_SFA15 = 'p_SFA15_Autorizacion_Venta_Final';
// Acepta la URL completa o solo la base (.../active-bpel/rt): si falta el nombre del proceso, se agrega.
const URL_SFA15 = (() => {
  const configurada = (process.env.SFA15_URL || DEFAULT_URL).trim().replace(/\/+$/, '');
  return configurada.endsWith(`/${PROCESO_SFA15}`) ? configurada : `${configurada}/${PROCESO_SFA15}`;
})();
const USUARIO = process.env.SFA15_USUARIO;
const CLAVE = process.env.SFA15_CLAVE;
const TIMEOUT_MS = 40000;
const PAUSA_ENTRE_LLAMADAS_MS = Number(process.env.SFA15_PAUSA_MS) || 3000;
const TIPO_CREDITO_INEXISTENTE = 999;
const FINCA_EJEMPLO = '2563';
// CEDPF 000000000 no garantiza un cliente inexistente (SFA lo resolvio a 001100069709): la unidad de costo inexistente asegura un error de negocio.
const UNIDAD_COSTO_INEXISTENTE = '99999999';
const args = process.argv.slice(2);
const valorDe = (bandera) => { const i = args.indexOf(bandera); return i >= 0 ? args[i + 1] : undefined; };

if (!USUARIO || !CLAVE) { console.error('Faltan SFA15_USUARIO y SFA15_CLAVE en el entorno de esta terminal.'); process.exit(2); }

const base = () => ({
  codEmpresa: '001', codAgencia: '001', codTipoId: 'CEDPF', numId: '000000000', codCliente: '',
  fecSolicitud: new Date().toISOString().slice(0, 10), nomAutorizado: 'PRUEBA LDCOM QA', codTipoIdAu: '', numIdAu: '',
  indUsaLinea: 'S', numLinea: 0, idExterno: '', codUnidadCosto: UNIDAD_COSTO_INEXISTENTE, numConvenio: '',
  plazoCredito: 24, tipCredito: 201, monSolicitud: 1.0, observaciones: 'PRUEBA LDCOM QA: DEBE RECHAZARSE', codUsuario: 'INTEGRACIONSFA',
});
const con = (cambios) => ({ ...base(), ...cambios });
const sin = (...campos) => { const d = base(); campos.forEach((c) => delete d[c]); return d; };

const escenarios = [
  // Sin asociado: la pregunta original
  // Sin identificacion ni cliente, SFA solo responde "Debe indicar la identificacion o el codigo del cliente" (formato error, HTTP 500).
  ['S01', 'Sin cliente ni identificacion, con finca del ejemplo', con({ codTipoId: '', numId: '' })],
  ['S02', 'Sin cliente ni identificacion y sin finca', con({ codTipoId: '', numId: '', codUnidadCosto: '' })],
  // Con una identificacion que no existe, SFA valida el resto y devuelve todos los errores juntos (pag. 17 del PDF).
  ['S03', 'Identificacion inexistente, finca inexistente', con({ codUnidadCosto: '99999999' })],
  ['S04', 'Cliente inexistente 9999999 con finca', con({ codCliente: '9999999' })],
  ['S05', 'Identificacion inexistente CEDPF 000000000 (caso base)', con({})],
  // Modo --minimo: SFA devuelve todos los errores juntos, asi que una llamada con varios campos malos prueba varias reglas.
  ['Z01', 'Todo malo a la vez (agencia 1501, tipo de credito 999, plazo 0, monto 0, finca 99999999)', con({ codAgencia: '1501', tipCredito: 999, plazoCredito: 0, monSolicitud: 0, codUnidadCosto: '99999999' })],
  ['Z02', 'Valores del ejemplo del PDF con identificacion inexistente', con({})],
  // Agencia: que es y que valida
  ['A01', 'Agencia = sucursal SAP 1501', con({ codAgencia: '1501' })],
  ['A02', 'Agencia = almacen SAP 5100', con({ codAgencia: '5100' })],
  ['A03', 'Agencia = 001 (ejemplo PDF)', con({ codAgencia: '001' })],
  ['A04', 'Agencia con 11 caracteres (AV-GUAYABO), mas de 5', con({ codAgencia: 'AV-GUAYABO' })],
  ['A05', 'Agencia vacia', con({ codAgencia: '' })],
  ['A06', 'Agencia inexistente 99999', con({ codAgencia: '99999' })],
  // Empresa
  ['E01', 'Empresa CR01 (xlsx)', con({ codEmpresa: 'CR01' })],
  ['E02', 'Empresa vacia', con({ codEmpresa: '' })],
  ['E03', 'Empresa inexistente 999', con({ codEmpresa: '999' })],
  // Plazo
  ['P01', 'Plazo 0', con({ plazoCredito: 0 })],
  ['P02', 'Plazo negativo', con({ plazoCredito: -1 })],
  ['P03', 'Plazo 99999 (maximo de 5 digitos)', con({ plazoCredito: 99999 })],
  ['P04', 'Plazo 100000 (excede longitud 5)', con({ plazoCredito: 100000 })],
  ['P05', 'Plazo decimal 3.5', con({ plazoCredito: 3.5 })],
  // Tipo de credito y monto
  ['T01', 'Tipo de credito inexistente 999', con({ tipCredito: 999 })],
  ['T02', 'Tipo de credito 0', con({ tipCredito: 0 })],
  ['T03', 'Tipo de credito como texto', con({ tipCredito: 'ABC' })],
  ['M01', 'Monto 0', con({ monSolicitud: 0 })],
  ['M02', 'Monto negativo', con({ monSolicitud: -5 })],
  ['M03', 'Monto enorme 99999999999999.99', con({ monSolicitud: 99999999999999.99 })],
  ['M04', 'Monto con 3 decimales', con({ monSolicitud: 1.234 })],
  // Formato y campos obligatorios
  ['F01', 'Fecha con formato dd/mm/aaaa', con({ fecSolicitud: '14/08/2026' })],
  ['F02', 'Fecha vacia', con({ fecSolicitud: '' })],
  ['F03', 'Sin el campo codUsuario', sin('codUsuario')],
  ['F04', 'Sin el campo codUnidadCosto', sin('codUnidadCosto')],
  ['F05', 'idExterno de 16 caracteres (maximo 15)', con({ idExterno: '1234567890123456' })],
  ['F06', 'codUnidadCosto de 26 caracteres (maximo 25)', con({ codUnidadCosto: 'X'.repeat(26) })],
  ['F07', 'nomAutorizado vacio (requerido)', con({ nomAutorizado: '' })],
  ['F08', 'Texto con tildes y enie en observaciones', con({ observaciones: 'Prueba ñandú ÁÉÍÓÚ' })],
  ['F09', 'indUsaLinea = N con numLinea 0', con({ indUsaLinea: 'N' })],
];

const crudos = [
  ['R01', 'Cuerpo vacio', () => ''],
  ['R02', 'Cuerpo que no es JSON', () => 'esto no es json'],
  ['R03', 'JSON sin Datos_Entrada', () => JSON.stringify({ Usuario: USUARIO, 'Contraseña': CLAVE })],
  ['R04', 'Datos_Entrada vacio {}', () => JSON.stringify({ Datos_Entrada: {}, Usuario: USUARIO, 'Contraseña': CLAVE })],
];

if (args.includes('--auth')) {
  crudos.push(['U01', 'Usuario invalido (1 llamada)', () => JSON.stringify({ Datos_Entrada: base(), Usuario: 'USUARIO_INEXISTENTE_QA', 'Contraseña': CLAVE })]);
  crudos.push(['U02', 'Clave invalida (1 llamada)', () => JSON.stringify({ Datos_Entrada: base(), Usuario: USUARIO, 'Contraseña': 'clave-incorrecta-qa' })]);
}

if (args.includes('--tier2')) {
  const cliente = valorDe('--cliente'); const finca = valorDe('--finca');
  if (!cliente) { console.error('--tier2 exige --cliente <codigo de asociado real>.'); process.exit(3); }
  // El tipo de credito inexistente fuerza el rechazo aunque el cliente exista; aun asi, solo con OK de Dos Pinos.
  escenarios.push(['X01', 'CLIENTE REAL sin finca (asociado sin fincas), tipo credito inexistente', con({ codCliente: cliente, codUnidadCosto: '', tipCredito: TIPO_CREDITO_INEXISTENTE })]);
  escenarios.push(['X02', 'CLIENTE REAL con finca del ejemplo (ajena), tipo credito inexistente', con({ codCliente: cliente, tipCredito: TIPO_CREDITO_INEXISTENTE })]);
  if (finca) escenarios.push(['X03', 'CLIENTE REAL con su finca propia, tipo credito inexistente', con({ codCliente: cliente, codUnidadCosto: finca, tipCredito: TIPO_CREDITO_INEXISTENTE })]);
}

// --agencias 001,002,010-020 : prueba cada codigo de agencia con una identificacion inexistente (no puede crear credito) y
// lista las que SFA no marca como inexistentes. Es la forma de descubrir las agencias validas sin que nos pasen la lista.
function codigosDeAgencia(texto) {
  const codigos = [];
  for (const parte of texto.split(',')) {
    const rango = /^(\d+)-(\d+)$/.exec(parte.trim());
    if (rango) {
      const ancho = rango[1].length;
      for (let n = Number(rango[1]); n <= Number(rango[2]); n++) codigos.push(String(n).padStart(ancho, '0'));
    } else if (parte.trim()) codigos.push(parte.trim());
  }
  return codigos;
}

// Un 401/403 se repetiria en cada caso y varios intentos fallidos pueden bloquear la cuenta de integracion: se detiene todo.
function paradaPorAcceso(r, donde) {
  console.error(`${donde}: HTTP ${r.http}. ${r.http === 401 ? 'Credenciales Basic invalidas o ausentes.' : 'El usuario no tiene permiso sobre el proceso.'} Detenido tras 1 intento para no bloquear la cuenta.`);
  console.error(ocultarClave(String(r.cuerpo)).slice(0, 300));
  const archivo = path.join(__dirname, `resultados-${new Date().toISOString().replace(/[:.]/g, '-')}-detenido.json`);
  fs.writeFileSync(archivo, JSON.stringify({ url: URL_SFA15, fecha: new Date().toISOString(), detenido: donde, http: r.http,
    cuerpo: ocultarClave(String(r.cuerpo)).slice(0, 2000) }, null, 2), 'utf8');
  console.error('Detalle guardado en', archivo);
  process.exit(5);
}

const sinClienteReal = (datos) => !datos.codCliente || datos.codCliente === '9999999';
const esperaMs = (ms) => new Promise((r) => setTimeout(r, ms));

async function llamar(cuerpo) {
  const controlador = new AbortController();
  const temporizador = setTimeout(() => controlador.abort(), TIMEOUT_MS);
  const inicio = Date.now();
  try {
    const cabeceras = { 'Content-Type': 'application/json' };
    // Informatica (IICS) pide autenticacion Basic en la puerta (401 con realm "IICS Application Integration Security Realm").
    if (process.env.SFA15_BASIC_USUARIO) {
      cabeceras.Authorization = 'Basic ' + Buffer.from(`${process.env.SFA15_BASIC_USUARIO}:${process.env.SFA15_BASIC_CLAVE || ''}`).toString('base64');
    }
    const respuesta = await fetch(URL_SFA15, { method: 'POST', headers: cabeceras, body: cuerpo, signal: controlador.signal });
    const texto = await respuesta.text();
    return { http: respuesta.status, ms: Date.now() - inicio, cuerpo: texto };
  } catch (error) {
    return { http: 0, ms: Date.now() - inicio, cuerpo: '', error: error.name === 'AbortError' ? 'timeout' : error.message };
  } finally { clearTimeout(temporizador); }
}

const ocultarClave = (texto) => String(texto).split(CLAVE).join('***');

function resumir(r) {
  let resumen = r.error ? `SIN RESPUESTA (${r.error})` : '';
  let esExito = false;
  try {
    const j = JSON.parse(r.cuerpo);
    const mensajes = [].concat(j.Mensajes || j.Mensaje || j.errores || []).filter(Boolean);
    resumen = [j.CodigoError, j.TipoError, ...mensajes.map(String)].filter(Boolean).join(' | ') || JSON.stringify(j).slice(0, 220);
    esExito = !!(j.Respuesta && (j.Respuesta.numSolicitud || j.Respuesta.indEstado));
  } catch { if (!r.error) resumen = r.cuerpo.slice(0, 220); }
  return { resumen: ocultarClave(resumen), esExito };
}

async function enumerarAgencias(texto) {
  const validas = []; const inexistentes = []; const dudosas = [];
  for (const codigo of codigosDeAgencia(texto)) {
    const datos = con({ codAgencia: codigo });
    const r = await llamar(JSON.stringify({ Datos_Entrada: datos, Usuario: USUARIO, 'Contraseña': CLAVE }));
    if (r.http === 401 || r.http === 403) paradaPorAcceso(r, 'agencia ' + codigo);
    const detalle = (() => { try { return [].concat(JSON.parse(r.cuerpo).DetalleTransaccion || []); } catch { return null; } })();
    const marcaInexistente = detalle && detalle.some((linea) => /agencia/i.test(linea) && /no existe/i.test(linea));
    if (!detalle) dudosas.push(codigo); else if (marcaInexistente) inexistentes.push(codigo); else validas.push(codigo);
    console.log(`agencia ${codigo}: ${!detalle ? 'respuesta sin DetalleTransaccion (' + (r.error || 'HTTP ' + r.http) + ')' : marcaInexistente ? 'no existe' : 'NO marcada como inexistente (probable valida)'}`);
    await esperaMs(PAUSA_ENTRE_LLAMADAS_MS);
  }
  console.log(`Probables validas: ${validas.join(', ') || 'ninguna'} | inexistentes: ${inexistentes.length} | sin interpretar: ${dudosas.join(', ') || 'ninguna'}`);
}

(async () => {
  if (valorDe('--agencias')) { await enumerarAgencias(valorDe('--agencias')); return; }
  const fila = [];
  const lista = [
    ...escenarios.map(([id, nombre, datos]) => ({ id, nombre, datos, cuerpo: JSON.stringify({ Datos_Entrada: datos, Usuario: USUARIO, 'Contraseña': CLAVE }) })),
    ...crudos.map(([id, nombre, armar]) => ({ id, nombre, datos: null, cuerpo: armar() })),
  ];
  if (args.includes('--minimo')) {
    const orden = ['Z02', 'Z01', 'S01'];
    lista.splice(0, lista.length, ...orden.map((id) => lista.find((c) => c.id === id)).filter(Boolean));
  }
  console.log(`QA SFA15 -> ${URL_SFA15}  (${lista.length} casos, pausa ${PAUSA_ENTRE_LLAMADAS_MS} ms)`);
  for (const caso of lista) {
    if (caso.datos && !args.includes('--tier2') && !sinClienteReal(caso.datos)) { console.error(`${caso.id}: lleva cliente real fuera de --tier2. Abortado.`); process.exit(4); }
    const r = await llamar(caso.cuerpo);
    if (r.http === 401 || r.http === 403) { paradaPorAcceso(r, caso.id); }
    const { resumen, esExito } = resumir(r);
    const linea = { id: caso.id, nombre: caso.nombre, http: r.http, ms: r.ms, resumen, EXITO_INESPERADO: esExito, cuerpo: ocultarClave(r.cuerpo).slice(0, 2000) };
    fila.push(linea);
    console.log(`${esExito ? '!!! EXITO INESPERADO ' : ''}${caso.id} HTTP ${r.http} ${r.ms}ms  ${caso.nombre}\n     -> ${resumen}`);
    // --simulador: el simulador no conoce clientes y aprueba cualquier codCliente; solo con esa bandera se sigue de largo.
    if (esExito && !args.includes('--simulador')) { console.error('El SFA acepto una solicitud que debia rechazarse: puede haberse creado un credito. Detenido.'); break; }
    await esperaMs(PAUSA_ENTRE_LLAMADAS_MS);
  }
  const archivo = path.join(__dirname, `resultados-${new Date().toISOString().replace(/[:.]/g, '-')}.json`);
  fs.writeFileSync(archivo, JSON.stringify({ url: URL_SFA15, fecha: new Date().toISOString(), resultados: fila }, null, 2), 'utf8');
  console.log('Resultados guardados en', archivo);
})();
