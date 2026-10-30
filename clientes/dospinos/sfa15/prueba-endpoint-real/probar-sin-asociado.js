'use strict';
// Prueba contra el SFA15 REAL de Dos Pinos: una solicitud SIN asociado (sin codCliente, codTipoId ni numId) y con una finca.
// Debe ser rechazada por validación; sirve para ver que error devuelve SFA y en que formato.
// Seguridad: el SFA15 real DESEMBOLSA (indAccion 3 en el segundo paso). Este script nunca envia un cliente ni una identificacion,
// asi que no puede crear un credito; si algun dia se le agrega un cliente valido, se negara a correr.
//
// Uso (en tu terminal, las credenciales no se escriben en ningun archivo):
//   $env:SFA15_USUARIO = '<usuario>'; $env:SFA15_CLAVE = '<clave>'
//   node probar-sin-asociado.js [finca]        (finca por defecto: 2563, la del ejemplo del PDF)
// Para probar el script contra el simulador local: SFA15_URL=http://localhost:7390/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final

const DEFAULT_URL = 'https://usw3-cai.dm-us.informaticacloud.com/active-bpel/rt/p_SFA15_Autorizacion_Venta_Final';
const URL_SFA15 = process.env.SFA15_URL || DEFAULT_URL;
const USUARIO = process.env.SFA15_USUARIO;
const CLAVE = process.env.SFA15_CLAVE;
const TIMEOUT_MS = 40000;
const finca = process.argv[2] || '2563';

if (!USUARIO || !CLAVE) {
  console.error('Faltan SFA15_USUARIO y SFA15_CLAVE en el entorno de esta terminal.');
  process.exit(2);
}

const datosEntrada = {
  codEmpresa: process.env.SFA15_EMPRESA || '001',
  codAgencia: process.env.SFA15_AGENCIA || '001',
  codTipoId: '',
  numId: '',
  codCliente: '',
  fecSolicitud: new Date().toISOString().slice(0, 10),
  nomAutorizado: 'PRUEBA LDCOM SIN ASOCIADO',
  codTipoIdAu: '',
  numIdAu: '',
  indUsaLinea: 'S',
  numLinea: 0,
  idExterno: 'PRUEBA-LD-' + Date.now().toString().slice(-8),
  codUnidadCosto: finca,
  numConvenio: '',
  plazoCredito: 24,
  tipCredito: 201,
  monSolicitud: 1.0,
  observaciones: 'PRUEBA LDCOM: SOLICITUD SIN ASOCIADO, DEBE RECHAZARSE',
  codUsuario: 'INTEGRACIONSFA',
};

if (datosEntrada.codCliente || datosEntrada.numId || datosEntrada.codTipoId) {
  console.error('Este script no envia cliente ni identificacion: podria crear un credito real. Abortado.');
  process.exit(3);
}

(async () => {
  console.log('POST', URL_SFA15);
  console.log('Request (sin clave):', JSON.stringify({ Datos_Entrada: datosEntrada, Usuario: USUARIO, 'Contraseña': '***' }));
  const controlador = new AbortController();
  const temporizador = setTimeout(() => controlador.abort(), TIMEOUT_MS);
  const inicio = Date.now();
  try {
    const respuesta = await fetch(URL_SFA15, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ Datos_Entrada: datosEntrada, Usuario: USUARIO, 'Contraseña': CLAVE }),
      signal: controlador.signal,
    });
    const cuerpo = await respuesta.text();
    console.log(`HTTP ${respuesta.status} en ${Date.now() - inicio} ms`);
    console.log(cuerpo.replace(CLAVE, '***'));
  } catch (error) {
    console.log(`Sin respuesta tras ${Date.now() - inicio} ms: ${error.name === 'AbortError' ? 'timeout' : error.message}`);
  } finally {
    clearTimeout(temporizador);
  }
})();
