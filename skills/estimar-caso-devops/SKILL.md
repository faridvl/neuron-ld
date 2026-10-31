---
name: estimar-caso-devops
description: Triage de tickets de Azure DevOps de Dos Pinos (board AV Retail) — valida con evidencia (código, commits, Confluence) si es bug real, carga de datos, hueco de despliegue o alcance nuevo; estima en horas, documenta en el ticket y llena Original Estimate, Remaining Work y Due Date. Usar al estimar, analizar o revisar un ticket o caso CRM (CAS-XXXXX) de Dos Pinos. No para implementar el fix.
argument-hint: "[ID del ticket o CAS-XXXXX]"
allowed-tools: Read, Grep, Glob, Agent, AskUserQuestion, Bash(node *capacidad.mjs*), mcp__ado__wit_work_item, mcp__ado__wit_query, mcp__ado__search_workitem, mcp__ado__core_get_identity_ids, mcp__ado__wit_work_item_attachment
---

# Triage y estimacion de tickets Dos Pinos

Toma un ticket, decide con evidencia si corresponde trabajarlo, lo estima sin inflar, lo deja
documentado y aprende del resultado. **No implementa el fix.**

El valor de este flujo esta en dos cosas: que ningun ticket se estime "a la palabra" del reporte
(se estima contra evidencia de que el pedido es correcto y de que nadie ya decidio lo contrario), y que
los estimados sean realistas — historicamente se sobreestimaba 40-50%, y la calibracion existe para
no volver a eso (sin irse al extremo de recortar lo que si tiene evidencia).

## Configuracion

| Dato | Valor |
|---|---|
| Proyecto ADO | `AV Retail Dos Pinos` (org `LD-Vacas`), herramientas `mcp__ado__*` |
| Iteracion de casos | `AV Retail Dos Pinos\Casos Dos Pinos` (un ticket en la raiz del proyecto NO esta en el board) |
| Repo | `C:/FUENTES/DP/LDCOM13_DOS_PINOS` (VB.NET WinForms + SQL Server + ADMIN_LDCOM ASP.NET) |
| Ciclo de entrega | jueves a miercoles (5 dias habiles). **Miercoles = fecha limite (DueDate)**, jueves = release: nada de un ciclo se trabaja el jueves |
| Capacidad | 32h por ciclo (2 devs x 16h), prorrateada por los dias habiles que quedan (ver paso 1) |
| cc en comentarios de negocio | Gerson Barboza Piedra (GUID via `core_get_identity_ids` con el nombre completo) |
| Bases de datos | credenciales de solo lectura en la memoria `bd-dos-pinos-desarrollo-testing` |

**Terminologia:** *ticket* = work item de ADO (numero como 2244). *Caso CRM* = `CAS-XXXXX` del cliente,
en el campo `Custom.CRMCaseId`. *Escenario* = cada pedido distinto dentro de un mismo ticket.

## Flujo

Copiar esta lista al empezar y marcarla al avanzar:

```
- [ ] 1. Traer ticket, adjuntos y capacidad
- [ ] 2. Separar escenarios y clasificar cada uno
- [ ] 3. Validar legitimidad (4 fuentes)
- [ ] 4. Decidir por escenario: ESTIMAR / RECHAZAR / BLOQUEAR
- [ ] 5. Investigar segun el tipo (solo lo que se va a estimar)
- [ ] 6. Estimar
- [ ] 7. Documentar, llenar campos, registrar calibracion, cerrar con resumen
```

### 1. Traer ticket, adjuntos y capacidad

- `wit_work_item` (get) con los campos necesarios, no `expand=all` completo: el JSON completo es
  enorme y casi todo es ruido. Pedir relaciones solo si hay adjuntos o links que revisar. Despues,
  los comentarios (`list_comments`): ahi suele estar el contexto que dejaron otros.
- Si dan un `CAS-XXXXX`: WIQL sobre `[Custom.CRMCaseId] CONTAINS 'CAS-XXXXX'` (un ticket puede tener
  varios CAS separados por `;`, y un CAS puede estar en un ticket viejo cerrado y en uno activo).
- **Adjuntos: descargarlos y verlos** (`wit_work_item_attachment`, luego Read). El texto casi siempre
  oculta el dato clave: el mensaje de error exacto, los montos reales, la estructura del Excel.
- **¿Ya paso por este flujo?** Buscar el numero en la tabla de `references/calibracion.md` y en los
  comentarios (una nota de analisis o una "Nota tecnica para desarrollo" previa). Si ya se analizo,
  no repetir la investigacion: partir de esa conclusion y enfocarse en **que cambio despues**
  (comentarios nuevos, reapertura, cambio de estado o severidad).
- Si hay campos incoherentes de antes (ej. `DueDate` sin `OriginalEstimate`), reportarlos y proponer
  la correccion; no corregirlos por cuenta propia.
- Si el ticket no esta asignado a la identidad del token (`@Me`), avisar antes de seguir (ver
  *Puntos de consulta*).
- Correr `node scripts/capacidad.mjs` (ruta relativa al directorio base de esta skill, que se muestra
  al cargarla) y darle al usuario de entrada la linea del ciclo actual ("el ciclo que cierra el mie
  30/09 tiene 1.1h libres; lo nuevo va al 07/10"). Es contexto para todo lo que sigue.

  La capacidad depende de la fecha en que se estima, no solo de la semana: un martes quedan 2 de los
  5 dias del ciclo. El script aplica:

  ```
  dias_restantes  = fraccion de hoy (1 antes de 12:00, 0.5 hasta 15:00, 0 despues)
                    + dias habiles desde mañana hasta el miercoles
  capacidad_ciclo = 32h x dias_restantes / 5
  libre           = capacidad_ciclo - suma de RemainingWork del ciclo
  maximo_ticket   = 16h x dias_restantes / 5      (un ticket lo hace un solo dev)
  cabe si: estimado <= libre  y  estimado <= maximo_ticket;  si no, ciclo siguiente
  ```

  Si el usuario menciona feriados o ausencias, descontarlos a mano: el script no los conoce.

### 2. Separar escenarios y clasificar

Un ticket puede empaquetar pedidos de naturaleza muy distinta (el 2156 traia un bug real, un feature
que nunca existio, una confusion de plantillas y un punto fuera de alcance). Listar los escenarios y
clasificar cada uno:

| Tipo | Como se reconoce | Referencia |
|---|---|---|
| Bug | Algo que existe se comporta mal y se puede reproducir | [references/tipo-bug.md](references/tipo-bug.md) |
| Carga de datos | Pide cargar/reemplazar datos, trae Excel | [references/tipo-carga-datos.md](references/tipo-carga-datos.md) |
| Despliegue | "Funciona en un ambiente y en otro no" | [references/tipo-despliegue.md](references/tipo-despliegue.md) |
| Alcance nuevo | "Incorporar", "agregar", "no se dispone de una opcion para" algo que nunca existio | [references/tipo-alcance-nuevo.md](references/tipo-alcance-nuevo.md) |

Antes de investigar logica, descartar lo barato: `git log --all --oneline --grep=<numero>` y buscar
una migracion con el numero del ticket en el nombre. A veces el fix ya existe en otra rama.

### 3. Validar legitimidad

Para todo escenario, no solo los que suenan a feature: cruzar el pedido contra Confluence, el board
historico (todos los estados), los commits y el codigo. Detalle y criterios de decision en
[references/validacion.md](references/validacion.md). La fuente que mas pesa suele ser un ticket
**Closed** con una decision de negocio en sus comentarios — por eso la busqueda no se filtra por estado.

### 4. Decidir por escenario

| Decision | Cuando | Que sigue |
|---|---|---|
| **ESTIMAR** | Bug real, carga o despliegue legitimo; o alcance nuevo que negocio ya aprobo tratar como caso | Pasos 5 y 6 |
| **RECHAZAR** | Alcance nuevo sin aprobacion, comportamiento esperado, error de usuario, o ya gestionado en otro proyecto | Sin horas; comentario de rechazo ([plantillas](references/plantillas.md)) |
| **BLOQUEAR** | Ambiguedad de negocio que el usuario tampoco puede resolver | Sin horas; `Blocked`, asignar a quien responde |

**Las decisiones de negocio se leen en orden cronologico.** Una decision posterior, con autor
identificable, deja sin efecto a una anterior sobre el mismo tema — aunque sea un comentario breve
como "segun acordado con X se vera como un caso". Una contradiccion entre dos decisiones de fechas
distintas no es ambiguedad: manda la mas reciente. Solo hay ambiguedad si no se puede saber cual
vale (misma epoca, autores sin relacion, o la reciente es vaga sobre que se aprobo).

Antes de proponer BLOQUEAR, preguntarle al usuario: muchas veces tiene el contexto que falta y el
ticket se puede estimar o rechazar sin frenar a nadie.

"Bug vs. diseño aceptado" lo define negocio, no la evidencia tecnica: una causa raiz solida no
significa que el comportamiento este mal. Si hay duda, se muestra el analisis y el usuario acota el
alcance antes de estimar.

### 5. Investigar segun el tipo

Leer solo la referencia del tipo que toca. Reglas comunes:

- La busqueda de causa raiz se delega al agente `investigador-ldcom` con el escenario completo
  (montos, pasos, mensaje exacto), no con palabras clave. Asi la lectura masiva de archivos queda en
  su contexto y no en esta conversacion. Pasarle tambien lo que ya se sabe (rutas encontradas,
  precedente a comparar, que NO hace falta revisar) y la pregunta concreta a responder: un encargo
  acotado cuesta una fraccion de uno abierto.
- Lo que reporte el agente se verifica leyendo el codigo real antes de estimar sobre eso. Si el agente
  deja una pista sin cerrar, seguirla 1-2 niveles a mano antes de rendirse (caso 2244).
- Buscar precedentes: si el mismo problema ya se resolvio en otro lugar del repo, el fix es copiar
  ese patron y el estimado baja. Conocimiento del repo acumulado en
  [references/conocimiento-repo.md](references/conocimiento-repo.md).
- En un bug (no en carga de datos/despliegue/alcance nuevo), identificar el commit que lo introdujo
  (`git blame` sobre la linea exacta) y decirselo al usuario en el chat: commit, fecha, autor — ver
  [references/tipo-bug.md](references/tipo-bug.md). **Esto es solo para que el usuario lo sepa: nunca
  va en el comentario de negocio ni en la nota tecnica.**

**Regla de parada:** si tras leer codigo y bases no aparece la causa, parar y reportar que falta
(dato, acceso o decision). Esto es estimar, no hacer forense.

### 6. Estimar

Leer [references/calibracion.md](references/calibracion.md) antes de dar el numero. Formato: tabla
actividad -> rango de horas, total en rango, nunca un numero falso-preciso. Las pruebas son manuales
(correr la app de escritorio); no hay suite automatizada para POS/caja.

Si el usuario cuestiona el numero, dar una opinion tecnica honesta con riesgos concretos — ni validar
por validar ni objetar en generico.

### 7. Documentar, campos, calibracion y cierre

1. **Comentarios** con las plantillas de [references/plantillas.md](references/plantillas.md): comentario
   de negocio y despues nota tecnica (o comentario de rechazo/bloqueo). Revisar cada borrador contra
   la lista de verificacion de ese archivo, mostrarlo al usuario y publicar solo con su OK
   (`wit_work_item_comment_write`, `format: Html`).
2. **Campos** (`wit_work_item_write`):
   - `Microsoft.VSTS.Scheduling.OriginalEstimate` y `RemainingWork`: el mismo numero si no se empezo.
     Solo para decisiones ESTIMAR; en RECHAZAR/BLOQUEAR quedan vacios, porque un numero implicaria
     que el trabajo ya se acepto.
   - `Microsoft.VSTS.Scheduling.DueDate`: el **miercoles** del ciclo donde cabe
     (`node scripts/capacidad.mjs --horas <estimado>` lo calcula), solo con confirmacion del usuario.
     Formato `YYYY-MM-DDT06:00:00Z`: con `T00:00:00Z` la UI muestra el dia anterior (Costa Rica es
     UTC-6). Los tickets viejos con DueDate en jueves pertenecen al ciclo del miercoles anterior; no
     se corrigen sin que el usuario lo pida.
   - Estados del proyecto: `New`, `Active`, `Blocked`, `In Review`, `Ready to QA`, `Closed`.
3. **Si el hallazgo afecta otro ticket:** comentario corto alla remitiendo a este, mas un link
   `System.LinkTypes.Related` (`wit_work_item_link_write`). No copiar la nota tecnica: la copia queda
   obsoleta cuando se resuelve el original.
4. **Calibracion:** agregar la fila del caso a la tabla de [references/calibracion.md](references/calibracion.md),
   y la leccion si el usuario corrigio el numero o el enfoque. Si aparecio conocimiento reutilizable
   del repo, agregarlo a `conocimiento-repo.md`.
5. **Cerrar** con el resumen final de [references/plantillas.md](references/plantillas.md).

## Puntos de consulta (siempre se detiene y pregunta)

1. El ticket no esta asignado al usuario: reasignar, solo comentar o solo poner fecha.
2. No se puede saber que decision de negocio esta vigente, o hay una ambiguedad de "que es lo
   correcto" (antes de proponer BLOQUEAR).
3. La investigacion revela un alcance mayor al que pide el ticket: documentarlo amplio o acotado
   (caso 2244: el usuario eligio acotado, y es una decision valida).
4. Antes de publicar cada comentario y antes de escribir `DueDate`.
5. Un ticket que queda `Blocked`: a quien asignarlo.

## Limites

- Bases reales: solo lectura. Cualquier escritura se pide aparte mostrando server/base/usuario reales,
  no el nombre amigable del ambiente.
- Algo que nunca existio en el codigo no se estima como "fix": o se rechaza como alcance nuevo, o, si
  negocio ya lo aprobo como caso, se estima como desarrollo nuevo (ver `references/tipo-alcance-nuevo.md`).
- Las escrituras en ADO piden aprobacion por configuracion; no intentar esquivarla.
