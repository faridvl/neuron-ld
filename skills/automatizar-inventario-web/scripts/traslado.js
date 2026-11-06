#!/usr/bin/env node
// Crea un traslado de inventario en SITE_INVENTARIO_WEB y devuelve su Mov_Id.
// Uso: node traslado.js --origen "AV RIO FRIO" --destino "AV GUAYABO" --articulos 15000799:1,15000800:5
//      [--url <sitio>] [--capturas <carpeta>] [--headless] [--con-melaza]
const fs = require('fs');
const path = require('path');
const { entrarATraslados, URL_POR_DEFECTO } = require('./lib');

const ARTICULO_MELAZA = '19000257';
const URL_GUARDAR = 'TrasladoInventario_GuardarMovimiento';
const URL_AGREGAR = 'TrasladoInventario_AgregarArticulo';
const FILAS_CANTIDAD = 'tbody input:not([type=checkbox])';
const DESTINO =
  'xpath=//label[contains(translate(normalize-space(.),"abcdefghijklmnopqrstuvwxyzáéíóú",' +
  '"ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚ"),"SUCURSAL DESTINO")]' +
  '/following::input[starts-with(@id,"react-select")][1]';
const ESPERA_RED_MS = 5000;

function leerArgumentos(argv) {
  const args = { headless: false, conMelaza: false, url: URL_POR_DEFECTO };
  const valor = (i, nombre) => {
    if (i + 1 >= argv.length) throw new Error(`Falta el valor de ${nombre}`);
    return argv[i + 1];
  };
  for (let i = 0; i < argv.length; i++) {
    switch (argv[i]) {
      case '--origen': args.origen = valor(i++, '--origen'); break;
      case '--destino': args.destino = valor(i++, '--destino'); break;
      case '--articulos': args.articulos = valor(i++, '--articulos'); break;
      case '--url': args.url = valor(i++, '--url'); break;
      case '--capturas': args.capturas = valor(i++, '--capturas'); break;
      case '--headless': args.headless = true; break;
      case '--con-melaza': args.conMelaza = true; break;
      default: throw new Error(`Argumento desconocido: ${argv[i]}`);
    }
  }
  if (!args.origen || !args.destino || !args.articulos) {
    throw new Error('Uso: node traslado.js --origen <sucursal> --destino <texto> --articulos cod:cant[,cod:cant] [--url ..] [--capturas <carpeta>] [--headless] [--con-melaza]');
  }
  args.lineas = args.articulos.split(',').map((par) => {
    const [codigo, cantidad] = par.split(':').map((x) => x.trim());
    if (!/^\d+$/.test(codigo || '') || !/^\d+(\.\d+)?$/.test(cantidad || '')) {
      throw new Error(`Artículo inválido "${par}": use codigo:cantidad`);
    }
    return { codigo, cantidad };
  });
  if (!args.conMelaza && args.lineas.some((l) => l.codigo === ARTICULO_MELAZA)) {
    throw new Error(`El artículo ${ARTICULO_MELAZA} (melaza) dispara el aviso a Romana; use --con-melaza si es lo que se quiere`);
  }
  return args;
}

async function elegirDestino(p, destino) {
  const campo = p.locator(DESTINO);
  await campo.waitFor({ state: 'visible' });
  await p.waitForFunction((el) => el && !el.disabled, await campo.elementHandle());
  await campo.click();
  await p.keyboard.type(destino);
  const opcion = p.locator('[class*=option]').first();
  await opcion.waitFor();
  const elegida = (await opcion.innerText()).trim();
  await p.keyboard.press('Enter');
  return elegida;
}

async function agregarArticulo(p, { codigo, cantidad }) {
  await p.click('#articulo');
  await p.keyboard.type(codigo);
  const [respuesta] = await Promise.all([
    p.waitForResponse((r) => r.url().includes(URL_AGREGAR)),
    p.keyboard.press('Enter'),
  ]);
  const cuerpo = await respuesta.json();
  if (cuerpo.Error) throw new Error(`No se agregó el artículo ${codigo}: ${cuerpo.Mensaje}`);
  await p.waitForFunction(
    (cod) => document.querySelector('tbody tr')?.innerText.includes(cod),
    codigo,
  );
  // La fila nueva queda arriba de la tabla.
  // fill() no actualiza el estado de esta pantalla; hay que teclear.
  const fila = p.locator(FILAS_CANTIDAD).first();
  await fila.click();
  await p.keyboard.press('Control+A');
  await p.keyboard.type(cantidad);
  await p.keyboard.press('Tab');
  await p.waitForFunction(
    ({ selector, esperada }) => Number(document.querySelector(selector)?.value) === esperada,
    { selector: FILAS_CANTIDAD, esperada: Number(cantidad) },
  ).catch(() => {
    throw new Error(`La cantidad de ${codigo} no quedó en ${cantidad}`);
  });
  await p.waitForLoadState('networkidle', { timeout: ESPERA_RED_MS }).catch(() => {});
}

async function main() {
  const args = leerArgumentos(process.argv.slice(2));
  if (args.capturas) fs.mkdirSync(args.capturas, { recursive: true });
  const { b, p, errores } = await entrarATraslados(args.origen, {
    nuevo: true,
    url: args.url,
    headless: args.headless,
  });
  let codigoSalida = 0;
  try {
    await p.waitForFunction(() => document.querySelector('#form-sucursal-origen')?.value);
    const destino = await elegirDestino(p, args.destino);
    console.log(`Destino: ${destino}`);
    for (const linea of args.lineas) {
      await agregarArticulo(p, linea);
      console.log(`Artículo ${linea.codigo} x ${linea.cantidad}`);
    }
    if (args.capturas) await p.screenshot({ path: path.join(args.capturas, 'traslado-antes.png') });

    const [respuesta] = await Promise.all([
      p.waitForResponse((r) => r.url().includes(URL_GUARDAR)),
      p.click('a:has-text("Guardar"),button:has-text("Guardar")'),
    ]);
    const cuerpo = (await respuesta.text()).trim();
    const id = /ID:(\d+)/.exec(cuerpo);
    console.log(`Respuesta de guardar (HTTP ${respuesta.status()}): ${cuerpo}`);
    if (!id) throw new Error('El traslado no se guardó (la respuesta no trae ID)');
    await p.waitForFunction((n) => document.querySelector('#form-numero')?.value === n, id[1]);
    const aviso = p.locator('.toast-message', { hasText: 'almacenado' }).first();
    const mensaje = await aviso.waitFor({ timeout: ESPERA_RED_MS }).then(() => aviso.innerText()).catch(() => '');
    if (mensaje) console.log(`Mensaje de la pantalla: ${mensaje.trim()}`);
    console.log(`Mov_Id: ${id[1]}`);
    if (args.capturas) await p.screenshot({ path: path.join(args.capturas, `traslado-${id[1]}.png`) });
  } catch (e) {
    console.error(`ERROR: ${e.message.split('\n')[0]}`);
    if (args.capturas) await p.screenshot({ path: path.join(args.capturas, 'traslado-error.png') }).catch(() => {});
    codigoSalida = 1;
  } finally {
    if (errores.length) {
      console.log('Errores HTTP >= 400:');
      for (const e of errores) console.log(`  ${e}`);
      if (errores.some((e) => e.startsWith('5'))) codigoSalida ||= 2;
    }
    await b.close();
  }
  process.exit(codigoSalida);
}

main().catch((e) => {
  console.error(`ERROR: ${e.message}`);
  process.exit(1);
});
