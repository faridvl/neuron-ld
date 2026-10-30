'use strict';
// Pruebas del endpoint SFA15 del simulador. Uso: node probar-sfa15.js [urlBase]
// Requiere el simulador en SIN_SQL=1, SFA15_TIMEOUT_DELAY_MS=2000 y las credenciales de abajo.
const BASE = process.argv[2] || 'http://localhost:7391';
const RUTA = '/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final';
const USUARIO = 'usuario-prueba';
const CONTRASENA = 'clave-prueba';

const datosValidos = (monto) => ({
  codEmpresa: '1', codAgencia: '1', codTipoId: '01', numId: '123456789', codCliente: '1001', fecSolicitud: '2026-10-27',
  nomAutorizado: 'Prueba', codTipoIdAu: '01', numIdAu: '123456789', indUsaLinea: 'N', numLinea: 0, idExterno: 'X1',
  codUnidadCosto: '10', numConvenio: 0, plazoCredito: 30, tipCredito: 'C', monSolicitud: monto, observaciones: 'prueba', codUsuario: 'U1',
});
const peticion = (monto, cambios = {}) => ({ Datos_Entrada: { ...datosValidos(monto), ...cambios }, Usuario: USUARIO, 'Contraseña': CONTRASENA });
const sin = (monto, campo) => { const p = peticion(monto); delete p.Datos_Entrada[campo]; return p; };

const casos = [
  ['monto 1', peticion(1)],
  ['monto 9999.99', peticion(9999.99)],
  ['monto 10000 (limite)', peticion(10000)],
  ['monto 10000.01', peticion(10000.01)],
  ['monto 15000 (limite)', peticion(15000)],
  ['monto 15000.01 (timeout)', peticion(15000.01)],
  ['monto 20000 (limite)', peticion(20000)],
  ['monto 20000.01', peticion(20000.01)],
  ['monto 0', peticion(0)],
  ['monto "abc"', peticion('abc')],
  ['cuerpo {}', {}],
  ['sin credenciales', (() => { const p = peticion(1); delete p.Usuario; delete p['Contraseña']; return p; })()],
  ['credenciales malas', { ...peticion(1), 'Contraseña': 'mala' }],
  ['sin codCliente ni tipo/num id', (() => { const p = peticion(1); delete p.Datos_Entrada.codCliente; delete p.Datos_Entrada.codTipoId; return p; })()],
  ['codCliente solo (OK)', (() => { const p = peticion(1); delete p.Datos_Entrada.codTipoId; delete p.Datos_Entrada.numId; return p; })()],
  ['indUsaLinea X', peticion(1, { indUsaLinea: 'X' })],
  ['numLinea 5', peticion(1, { numLinea: 5 })],
  ['campos faltantes (3)', (() => { const p = sin(1, 'codEmpresa'); delete p.Datos_Entrada.nomAutorizado; p.Datos_Entrada.codUsuario = ''; return p; })()],
];

(async () => {
  for (const [nombre, cuerpo] of casos) {
    const inicio = Date.now();
    const r = await fetch(BASE + RUTA, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(cuerpo) });
    const j = await r.json().catch(() => null);
    const t = Date.now() - inicio;
    const detalle = j && j.DetalleTransaccion ? ` detalle=${JSON.stringify(j.DetalleTransaccion)}` : '';
    const ok = j && j.Respuesta && j.Respuesta.numSolicitud != null ? ` numSolicitud=${j.Respuesta.numSolicitud} numCredito=${j.Respuesta.numCredito} monDisponible=${j.Respuesta.monDisponible}` : '';
    console.log(`${nombre} -> HTTP ${r.status} | ${j ? `${j.TipoError || '-'}/${j.CodigoError || '-'}` : 'sin JSON'} | ${t} ms | HttpStatus=${j && j.HttpStatus}${ok}${detalle}`);
  }
  // Cuerpo vacio (sin nada) y JSON roto
  for (const [nombre, cuerpo] of [['cuerpo vacio', ''], ['JSON roto', '{no es json']]) {
    const r = await fetch(BASE + RUTA, { method: 'POST', headers: { 'content-type': 'application/json' }, body: cuerpo });
    const j = await r.json().catch(() => null);
    console.log(`${nombre} -> HTTP ${r.status} | ${j ? `${j.TipoError}/${j.CodigoError}` : 'sin JSON'}`);
  }
  const reg = await (await fetch(BASE + '/sim/sfa15')).json();
  console.log(`registro: ${reg.llamadas.length} llamadas; contrasena en el registro: ${JSON.stringify(reg.llamadas[0].request.body).includes(CONTRASENA) ? 'SIN ENMASCARAR' : 'enmascarada'}`);
  const raiz = await fetch(BASE + '/');
  console.log(`GET / (pagina existente) -> HTTP ${raiz.status}, ${(await raiz.text()).includes('Simulador CIH y Monitor 360') ? 'titulo igual' : 'titulo distinto'}`);
  const sub = await fetch(BASE + '/subscriptions/x/data', { method: 'POST', body: '{}' });
  console.log(`POST /subscriptions/x/data sin autenticacion -> HTTP ${sub.status}`);
})();
