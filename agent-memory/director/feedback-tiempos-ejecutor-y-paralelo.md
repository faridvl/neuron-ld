---
name: tiempos-ejecutor-y-paralelo
description: En encargos con tope de horas, un ejecutor de etapa grande tardó ~2 h; las etapas que no comparten archivos sí se pueden correr en paralelo con --artifacts-path separados
metadata:
  type: feedback
---

Con tope de 4 h, la etapa 1 de LDCOM13_INTEGRATIONS (preventas, 3 capas + 160 pruebas) tomó ~115 min en un solo ejecutor; las etapas 2 y 3 (otros archivos) tomaron ~12 min cada una en paralelo con topes de 50 min en el brief.

**Why:** el reloj se consume por el ejecutor más largo; sin tope en el brief una etapa se come el presupuesto.

**How to apply:** poner siempre "TOPE: N minutos" y partir la etapa grande en dos tandas (código/contrato primero, matriz de pruebas después); correr en paralelo etapas con archivos disjuntos usando `dotnet --artifacts-path` distinto por agente y avisar qué archivos compartidos solo admiten Edit puntual. Lanzar qa, cuestionador y docs juntos (3) al cerrar y reservar ~30 min para una ronda de correcciones.
