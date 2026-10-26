---
name: paridad-clientes-contador-control-residuo
description: Tras correr paridad-clientes.ps1 contra Docker, Contador_Cadena_Control y Contador_Cadena CLIENTE quedan movidos; la siguiente corrida falla en Admin-Alta con "Problemas al obtener el consecutivo".
metadata:
  type: feedback
---

El camino del Admin (`Admin-Alta`) gasta el contador de clientes: sube `Contador_Cadena` (CLIENTE) e inserta filas en `Contador_Cadena_Control`. Una herramienta de limpieza por llave que solo borra clientes/relaciones NO las devuelve; la siguiente corrida de `paridad-clientes.ps1` revienta por PK repetida en Control.

**Why:** pasó en la ronda de decisiones 136-144 (2026-10-25); el Docker tenía Contador 27598 y Control con máximo 27597 como estado base.

**How to apply:** después de cada corrida de paridad, borrar con conteo exacto las filas de Control con `Valor >` el máximo base (leerlo ANTES de correr) y devolver `Contador_Cadena` a su valor base. Tomar la línea base antes y verificar `limpieza_dinamica.py` (no cubre esas dos tablas: solo avisa "no se toca"). Los scripts largos con Python embebido en heredoc de Bash fallan con comillas: usar Write + `python -I <ruta>`.
