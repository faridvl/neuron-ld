// Entrada a SITE_INVENTARIO_WEB (LDCOM) con Playwright y el Chrome del sistema.
const { chromium } = require('playwright-core');

const URL_POR_DEFECTO = 'http://localhost/dp/otros/SITE_INVENTARIO_WEB/';
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const ESPERA_MS = 30000;
const PAUSA_VISIBLE_MS = 150;

function leerCredenciales() {
  const usuario = process.env.INV_USUARIO;
  const clave = process.env.QA_AUTO_PASSWORD;
  if (!usuario || !clave) {
    throw new Error('Faltan las variables de entorno INV_USUARIO y QA_AUTO_PASSWORD');
  }
  return { usuario, clave };
}

// Devuelve { b, p, errores }: navegador, página y lista de respuestas HTTP >= 400.
async function abrir({ url = URL_POR_DEFECTO, headless = false } = {}) {
  const { usuario, clave } = leerCredenciales();
  const b = await chromium.launch({
    executablePath: CHROME,
    headless,
    slowMo: headless ? 0 : PAUSA_VISIBLE_MS,
  });
  const p = await (await b.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
  p.setDefaultTimeout(ESPERA_MS);
  const errores = [];
  p.on('response', (r) => {
    if (r.status() >= 400) errores.push(`${r.status()} ${r.url()}`);
  });
  try {
    await p.goto(url);
    await p.fill('input[placeholder=Usuario]', usuario);
    await p.fill('input[placeholder=Contraseña]', clave);
    await p.click('button:has-text("Iniciar Sesión")');
    await p.locator('#cb_Sucursal').waitFor({ state: 'visible' });
  } catch (e) {
    await b.close();
    throw new Error(`No se pudo iniciar sesión (${e.message.split('\n')[0]}). Errores HTTP: ${errores.join(' | ') || 'ninguno'}`);
  }
  return { b, p, errores };
}

// Sucursal -> Utilizar parámetros -> Movimientos -> Traslados de Inventario [-> Nuevo].
async function entrarATraslados(sucursal, { nuevo = false, ...opciones } = {}) {
  const sesion = await abrir(opciones);
  const { b, p } = sesion;
  try {
    await p.selectOption('#cb_Sucursal', { label: sucursal });
    await p.click('text=Utilizar parámetros');
    await p.locator('a:has-text("Movimientos")').first().click();
    await p.locator('a:has-text("Traslados de Inventario")').first().click();
    const botonNuevo = p.locator('text=Nuevo Traslado de Inventario');
    await botonNuevo.waitFor({ state: 'visible' });
    if (nuevo) {
      await botonNuevo.click();
      await p.locator('#articulo').waitFor({ state: 'visible' });
    }
  } catch (e) {
    await b.close();
    throw e;
  }
  return sesion;
}

module.exports = { abrir, entrarATraslados, URL_POR_DEFECTO, ESPERA_MS };
