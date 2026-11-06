---
name: automatizar-inventario-web
description: Crea traslados de inventario en SITE_INVENTARIO_WEB (LDCOM, Dos Pinos) con Playwright y comprueba en la base el movimiento y el aviso POS-26 (melaza a Romana). Usar al probar traslados, reproducir un bug de esa pantalla o verificar que un traslado dispara (o no) el aviso. El POS no tiene pantalla de traslados.
---

# Automatizar SITE_INVENTARIO_WEB (traslados)

Scripts en `scripts\` (Node + `playwright-core`, con el Chrome del sistema). Leer `references\trampas.md` antes de
cambiar un selector o una espera.

## Requisitos
- Docker arriba y el sitio publicado (`rig`, ver skill `rig`): `http://localhost/dp/otros/SITE_INVENTARIO_WEB/`.
- Una vez: `npm install` dentro de `scripts\`.
- Variables de entorno `INV_USUARIO` y `QA_AUTO_PASSWORD`. En el Docker el usuario es `qaauto` (sin guion bajo: el
  front rechaza "_"). Nunca se imprimen ni se guardan en archivos.

## Usar
```
node scripts\traslado.js --origen "AV RIO FRIO" --destino "AV GUAYABO" --articulos 15000799:1,15000794:2 [--headless] [--capturas <carpeta>]
powershell -NoProfile -File scripts\comprobar-aviso.ps1 -MovId <n>
```
- `traslado.js` imprime `Mov_Id: <n>` y los errores HTTP >= 400; sale con 1 si falla y con 2 si hubo un 5xx.
- Rechaza el artículo 19000257 (melaza) salvo con `--con-melaza`: ese es el único que dispara el aviso POS-26.
- `comprobar-aviso.ps1` es solo lectura: muestra el movimiento y, si existe, el aviso con sus Events.
- Cada traslado queda en la base: anotar el Mov_Id para limpiarlo.
