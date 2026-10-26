---
name: revisar-corridas-previas
description: Antes de planificar un encargo grande, revisar fechas de avance-*.md, DECISIONES y archivos del repo: otra corrida pudo avanzar y el encargo puede venir desactualizado
metadata:
  type: feedback
---

Antes de repartir, comparar lo que dice el encargo con las fechas de los archivos de avance, la numeración de
DECISIONES y los archivos modificados del repo (`git status` + mtime). En datos maestros (2026-10-24) el encargo hablaba
de 62 decisiones y ya había 75, con NEGOCIO de dos interfaces hecho por una corrida de madrugada cortada por límite.

**Why:** el orquestador puede no saber lo que hizo otra corrida; además, el usuario cambió el rumbo a mitad (pausa,
"usar los flujos existentes de NEGOCIO en vez de métodos nuevos"). Lanzar agentes sobre un encargo viejo gasta tokens
y produce código que después se descarta.

**How to apply:** en encargos largos, lanzar agentes por tandas cortas (no 2-3 frentes a la vez de entrada), y
reportar pronto el estado encontrado; si aparece una orden de pausa, no lanzar nada más, dejar ESTADO/PENDIENTES al día
y responder corto.
