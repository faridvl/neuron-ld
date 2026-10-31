# Reglas del equipo LD (neuron-ld)

Se cargan en las sesiones y agentes de los proyectos de esta neurona, de quien la instale. Las reglas de cada repo
(`<repo>/CLAUDE.md` y `<repo>/.claude/rules/`) mandan sobre estas cuando hablan de lo mismo.

## Ambiente: siempre con rig

- El ambiente local (POS, Admin, IIS, Docker, ambientes) se maneja con `rig` (antes `dp`; el alias sigue).
  Cómo usarlo: skill `rig`. Perfil de cada cliente: `clientes/<cliente>/rig.json`.
- **Compilar y abrir el POS o el Admin lo hace el desarrollador** con `rig pos`, `rig admin`, `rig publicar`.
  Claude no compila la carpeta principal ni abre/cierra el POS: dice qué comando correr.
- Antes de un push o de abrir un PR, sí se compila la rama que se envía (en su worktree) y se corren las pruebas.
  Si falla, no se pushea.
- Docker se levanta con `rig docker`, en la terminal real del desarrollador (no en una consola aislada de Claude).
- Antes de cada commit: `rig ambiente -Restaurar` (el Web.config del Admin no viaja apuntando a Docker o Testing).

## Bases de datos

- Staging, RC, Testing, Dev, UAT e Integrations: **solo lectura**. Un cambio ahí se entrega como script para que
  lo corra quien tiene permiso. El sandbox para escribir es el Docker local (`localhost,1433`).
- Testing = `LDCOM_DOS_PINOS_NEW` (no `..._STAGING`, que es Staging).
- **Todo script o consulta que se le entrega al desarrollador se corre antes contra el Docker local**, tal cual se
  entrega (mismo texto, misma base de destino: LDCOM o INTEGRATIONS), y solo se entrega si corrió sin error. Las
  consultas de una guía también. Si no se pudo probar, se dice explícitamente y por qué.
- Contraseñas: nunca en git, ni en esta neurona, ni en respuestas.

## Migraciones (`migrate`)

- Herramienta: `migrate` (LogicalData.DatabaseMigration.Cli, repo DatabaseMigration). Antes de crear, editar,
  borrar o reaplicar una migración, o ante un checksum distinto en `migrate status`: skill `migraciones-ldcom`.
- Un archivo de migración ya aplicado no se edita: el cambio va en un archivo nuevo, en la carpeta del mismo ticket.
- Siempre con `migrate`, nunca `sqlcmd` directo. Nunca tocar `dbo._db_migrations` sin confirmación explícita.
- Una migración que reescribe un SP se arma sobre la última versión del SP en cada rama destino.

## Tickets de Azure DevOps: leer todo antes de responder

Antes de cualquier análisis de un ticket revisar: descripción (y Repro Steps), todos los comentarios, imágenes
embebidas (descargarlas y verlas) y adjuntos. En la respuesta decir qué trajo cada fuente.
Para casos de cliente (CAS-XXXXX), buscar el ticket con `search_workitem`; nunca decir "sin ticket" sin buscar.

## Código

- Comentarios cortos y solo si aportan el porqué; nada de contexto de la sesión. Referencia a ticket solo como
  `'Issue 2369: <regla en pocas palabras>'`.
- Nombres descriptivos: nunca `Dim r` ni abreviaturas, tampoco en pruebas.
- Sin números ni códigos mágicos: constantes con nombre o configuración.
- Al copiar un fix a métodos hermanos (FACTCEDI, CEDI, INVENTARIO), verificar columnas y controles del destino.
- Validación nueva: rastrear hacia arriba quién la llama y qué transforma antes.
- `.rdl` tocado: `SecurityType None` + `ConnectString =Parameters!ConexionString`; nunca `DataSourceReference`.

## Pruebas unitarias: para romper, no para describir

Partir de la regla de negocio (si no está clara, preguntarla). Cubrir nulos y vacíos, límites (antes/en/después),
redondeo y datos raros. El esperado se calcula a mano, nunca reutilizando la lógica de la función. Si una prueba
falla se corrige la función y se explica el bug. Al entregar: la regla probada y qué casos cubren cada categoría.

## Nombre de las ramas (todos los repos de LD)

- Una corrección se llama `fix/<ticket-id>-descripcion`: el id del work item de Azure DevOps y una descripción corta
  en minúsculas, con guiones. Ejemplo: `fix/3659-limite-referencia-traslado`.
- El id va en el nombre para que la rama, el PR y el ticket se encuentren entre sí. Nada de listas de ids ni de
  números sueltos en la descripción.

## Ramas y PRs (LDCOM13_DOS_PINOS)

- La rama de un caso sale del **release vigente**: el `origin/release/*` de versión más alta (se calcula con git,
  no se escribe fijo). Confirmar con el desarrollador si el caso va a otro release.
- Commit y push solo con pedido explícito del desarrollador.
- Pregunta abierta del equipo: la regla del repo (`02-git-devops-workflow.md`) dice portar a develop con
  cherry-pick en una rama nueva; en la práctica se ha usado la misma rama con un PR a release y otro a develop.
  Hasta que se decida, preguntar en cada caso.

## Azure DevOps y Confluence: ya están conectados por MCP

- Servidores `ado` (Azure DevOps, org LD-Vacas) y `atlassian-rovo-mcp` (Confluence, cloudId `logicaldata.atlassian.net`).
- Antes de decir que no están conectados: `ToolSearch` con "ado" o "confluence". Se conectan unos segundos
  después de abrir la sesión y sus herramientas llegan diferidas.
- Solo si ToolSearch no los encuentra: `claude mcp list` y la guía de configuración del equipo.
- Nunca pedir que peguen un PAT o token en el chat.
