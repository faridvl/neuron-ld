# SFA15 (POS-10) — validación de crédito: trabajo y pruebas

Tickets: 3699 (API de integraciones, repo LDCOM13_INTEGRATIONS) y 3700 (facturación/NEGOCIO, repo LDCOM13_DOS_PINOS).
Estado vivo: `ESTADO.md`. Decisiones: `DECISIONES.md`. Requisitos: `trazabilidad-requisitos-3700.md`.

## Carpetas
- `simulador-pruebas/`, `e2e/`: pruebas contra el simulador CIH y el Runner real.
- `qa-3700/`: recorrido del POS/NEGOCIO (scripts `auto/`, `e2e-3700.js`, `AVANCE.md`).
- `prueba-endpoint-real/`: pruebas contra el endpoint real (necesitan credenciales y URL de Dos Pinos).
- `config-docker/`: `configurar-sfa15-docker.ps1` (Real|Simulador).
- `referencia/`, `descargas-nuevas/`, `pdf-imagenes/`, `busqueda/`: documentos de Dos Pinos y hallazgos.

## Lo que NO viaja y hay que recrear en cada PC
- `config-docker/.env` (credenciales SFA de pruebas; ver `.env.example`).
- `node_modules` / `deps`: `npm install` donde haga falta (mssql, etc.); en `simulador-pruebas/deps` van sus dependencias.
- Binarios (`*.dll`, `*.pdb`, `wcf-harness/`, `sdk-host/bin`) y logs: se regeneran compilando.
- Las rutas de los scripts apuntan a `C:\FUENTES\DP\...`; ajustar a la raíz de repos de cada PC.
- El correo de Outlook usado en la búsqueda inicial no se subió (es privado).
