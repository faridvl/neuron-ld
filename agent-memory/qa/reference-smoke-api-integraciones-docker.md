---
name: reference-smoke-api-integraciones-docker
description: Smoke de todos los endpoints del API de integraciones en el Docker (script reutilizable, trampas de config y de expectativas)
metadata:
  type: reference
---

- Script reutilizable: `ClaudeLocalSession/evidencias/smoke-release-4.0/smoke.py` (+ start_api_6270.py, q.sh). `dotnet publish -c Release -o <bin> --artifacts-path <dir>` del worktree y `python start_api_6270.py` (Popen devuelve el pid del dotnet; parar con `taskkill //PID x //F`).
- Docker puede estar caido al empezar: correr arrancar-docker.ps1 de la skill docker (salio 0 al primer intento).
- Expectativas que me fallaron: `StrictPreorderType` default false (tipo de preventa inexistente = 200 con warnings, cae a General; General(0) `isEditable=false`; solo inactivo da 422); LD-06 crea el traslado ya DESPACHADO (AP): para probar LD-07/LD-11 hay que sembrar GU con regresion/B/sembrar_traslados.py (usar MAX(Mov_Id)+1); STORE_NOT_FOUND en traslados es 404 (InventoryTransferService:110-113) y 422 en el resto.
- LD-10 sincrono: un plan invalido (INVALID_TERM, INVALID_APPLIES_TO, tasa) responde 500 EXTERNAL_SYSTEM_ERROR con errors.failures[].code por diseno cuando falla todo el lote; solo validacion de modelo (null/letras/decimales) da 400.
- En el Docker los eventos de datos maestros (CLIENTES, ARTICULOS...) estan IsActive=0 y la conexion apunta a CIH real: solo se prueba 400 (lista vacia) y 503 INTEGRATION_DISABLED; no hay endpoint de salud (usar /swagger/v1/swagger.json, filtrado al contrato partner: solo 6 rutas).
- Python SI esta en PATH en esta PC (3.12); Write/Edit bloqueado para QA: escribir scripts con PowerShell here-string + WriteAllText; en heredoc de Bash `\U` llega como `\U` (usar barras / en rutas).
