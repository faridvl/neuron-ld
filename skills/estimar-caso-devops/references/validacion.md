# Validar legitimidad: las 4 fuentes

Objetivo: que ningun escenario se estime sin evidencia de que el pedido es correcto **y** de que nadie
ya decidio lo contrario. Revisar las cuatro fuentes; si una no se puede consultar, decirlo como bloqueo,
no como ausencia de evidencia.

## 1. Board historico (la que mas decide)

- `search_workitem` con las palabras clave del tema, **sin filtro de estado**. Complementar con WIQL
  `[System.TeamProject] = 'AV Retail Dos Pinos' AND [System.Title] CONTAINS '<tema>'`, tambien sin
  filtrar por estado ni iteracion.
- Tickets con `Custom.CRMCaseId` vacio no aparecen buscando por CAS: por eso ademas se busca por tema.
- Si aparece un ticket relacionado **Closed**, leer sus comentarios completos (`list_comments`). Ahi
  puede estar la decision de negocio que resuelve el caso sin mirar codigo (ej. un ticket cerrado
  que dice "no se va a realizar, el diseño no lo contempla").
- Armar una **linea de tiempo** con todas las decisiones encontradas (este ticket y los relacionados):
  fecha, autor, que se decidio. La decision vigente es la mas reciente con autor identificable.

## 2. Commits

- `git log --all -i --grep="<tema>"` y `git log --all --oneline -- <ruta de la tabla/formulario>`.
- Distingue "existio y se rompio" (bug) de "nunca existio" (alcance nuevo).
- Revisar tambien fixes muy recientes del propio equipo sobre el mismo codigo, aunque el ticket diga
  que son casos independientes: quien reporta no sabe si la causa vive en la misma funcion (caso 2242).

## 3. Codigo

- Confirmar en tabla, DTO y UI si el campo o la logica pedida existe hoy.
- Revisar si el mismo patron existe en una entidad hermana del dominio (ej. Combos vs. Bonificaciones):
  que exista alla y no aca puede ser una exclusion **a proposito**, no un olvido.
- Confirmar que se esta leyendo la rama correcta: `git branch --show-current` y
  `git merge-base --is-ancestor HEAD origin/release/X.Y` contra la rama del ambiente reportado.

## 4. Confluence

- `mcp__atlassian-rovo-mcp__*` para buscar la spec que respalde el pedido (ej. un codigo tipo
  `RET-UT-DC-####` citado en el ticket). `cloudId` = `logicaldata.atlassian.net` — usar siempre este
  valor, nunca adivinar con `ld.co.cr` (el dominio de correo no es el del sitio y da un error
  distinto, "No cloud ID found for hostname").
- Si el conector responde sin permiso o no esta conectado, reportarlo como **bloqueo de acceso** y
  seguir con las otras tres fuentes. "No pude consultarlo" no es "no hay nada".

## Como decidir

| Evidencia | Decision |
|---|---|
| Existio y algo lo rompio, o la spec lo exige y el codigo no lo cumple | ESTIMAR (bug) |
| Nunca existio y nadie lo descarto ni lo aprobo | RECHAZAR como alcance nuevo (proponer tramitarlo aparte) |
| Nunca existio, pero la decision vigente es tratarlo como caso | ESTIMAR como desarrollo nuevo, sobre un precedente si existe |
| Nunca existio y la decision vigente lo descarta | RECHAZAR citando esa decision y ligando los tickets |
| No se puede saber cual decision vale | Preguntar al usuario; si tampoco lo sabe, BLOQUEAR |
| El usuario informa que ya esta gestionado en otro proyecto | RECHAZAR como "no corresponde al flujo de casos" |
| El comportamiento es el esperado, o es error del usuario | RECHAZAR, con la evidencia que lo muestra |

Antes de concluir "bug", descartar activamente error del usuario con evidencia directa: abrir el
archivo real que subio, consultar el dato real en la base. Sin eso queda como suposicion.
