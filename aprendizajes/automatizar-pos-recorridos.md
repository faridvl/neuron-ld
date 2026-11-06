# Automatizar el POS por UIA y aprender "recorridos" reutilizables

Para quien nunca vio esto: el POS de LDCOM (WinForms, 32 bits) se prueba hoy con scripts Python (pywinauto/UIA) que
no mueven el mouse ni el teclado del desarrollador. Un agente que lo maneja consultando al modelo en cada paso es
lento. La idea es que el agente explore un flujo UNA vez, lo guarde como recorrido con chequeos y luego lo ejecute
rapido, sin modelo, y solo vuelva al modelo si algo no coincide.

## 1. Metodo actual (UIA, sin tocar mouse ni teclado)

Requisitos: Python 3.12 con pywinauto, pywin32, comtypes y pillow; Docker local arriba (`rig docker` en la terminal
real); usuario de prueba `qa_auto` creado SOLO en el Docker local (la clave vive en un archivo local de pruebas,
nunca en chats ni en git); el slot de rig apuntando al worktree a probar.

Reglas para no molestar al desarrollador:
- Nada de `click_input`, `type_keys` ni `SendKeys` (mueven el mouse o roban el foco).
- Escribir con `set_edit_text` (ValuePattern o WM_SETTEXT); pulsar con `invoke()` o `BM_CLICK` por `PostMessage`.
- Capturas con `PrintWindow`: funcionan aunque la ventana este tapada.
- Abrir/cerrar el POS lo hace el desarrollador (`rig pos`); el agente solo lo maneja.

Trampas conocidas:
1. `Invoke` sobre un boton que abre una modal no regresa hasta cerrar la modal: usar hilo aparte o `BM_CLICK`.
2. UIA se cuelga (`children()`/`descendants()`) en ventanas con ciertos controles (Busqueda de Articulos) y con una
   modal abierta: usar la API Win32 (`backend="win32"`, grillas `SysListView32` con `.texts()`).
3. Correr los scripts ocultos y con tope de tiempo para no quedar colgado.
4. Enter en el cuadro de busqueda SELECCIONA el primer resultado; para buscar, pulsar la lupa.
5. La barra F1..F12 es un ToolStrip: botones con texto ("Buscar\r\nArticulo"), sin `auto_id`.
6. Los mensajes (Frm_Mensaje) se cierran solos en pocos segundos y su cuerpo no es texto de ventana: sondear cada
   0.25 s, capturar y leer la imagen. Comparten titulo con la ventana principal (la principal es la visible mas grande).
7. Preguntas tipo Si/No: dos botones sin texto (check a la izquierda, ESC a la derecha).
8. Al arrancar, el POS recupera el documento sin guardar (`Factura_Backup*.xml` en `bin\Debug\BD`): borrarlo con el POS
   cerrado antes de cada escenario.
9. Tras abrir el POS esperar ~10 s antes del login; si no, el clic de Ingresar no hace nada.
10. Parametros de caja se leen al arrancar el POS (reiniciar al cambiarlos); los de sucursal destino, en linea.
11. Guardar una preventa (F6) pide rol con permiso del tipo, vendedor distinto del "por defecto", pago en efectivo y
    pregunta de impresion. Facturar exige abrir caja (monto 0.00) antes.
12. El SQL del contenedor corre en UTC: no filtrar por `GETDATE()` el dia local.

Mapa de pantallas (auto_id): Login `Frm_Login` (`tbUsuario`, `tbContrasena`, `bConectar`); Tipo de Preventa `Frm_Lista`
(`Bn_F1`.. un boton por tipo); Principal `Frm_Facturacion` (`Text_Articulo`, `Btn_Agregar_Articulo`, `Barra`,
`ListaArt`); Busqueda de Articulos (EDIT, 3 botones sin texto: lupa, check, teclado; 3 SysListView32).

## 2. Lo aprendido en la prueba reciente (4 casos de la API de preventas)

- La barra del POS esta partida en PAGINAS: un boton puede no estar en la pagina actual; hay que pasar de pagina
  antes de buscarlo y dejar la barra en la pagina 1 al terminar.
- "Cargar Preventa" solo lista preventas en estado 0 y 1: una preventa en otro estado (ej. 4) no aparece ahi aunque
  si este en el monitor; no se puede abrir desde el monitor.
- Los clics por mensaje (`BM_CLICK`/`PostMessage`) los ignoran algunos paneles; en ese caso probar `invoke()` de UIA
  o, como ultimo recurso, otra via del mismo control. Registrar cual funciono por pantalla.
- Una preventa de tipo no editable muestra "no permite edicion en Preventa": el POS bloquea editarla (resultado
  esperado, no un fallo de la automatizacion).
- Cuando una prueba cambia datos del Docker, dejar la lista de lo creado y su script de reversa junto a los
  resultados; el POS no tiene pantalla de traslados (se verifica por existencia del articulo).
  Los traslados se crean con la skill `automatizar-inventario-web`.

## 3. Diseno: explorar -> grabar -> ejecutar rapido -> reparar -> registrar

1. Explorar (con modelo, lento, una sola vez): el agente descubre el flujo ("preventa y facturarla") paso a paso,
   usando los scripts y la guia anteriores. Cada paso exitoso se anota.
2. Grabar el recorrido: archivo (JSON/YAML o script Python) con pasos `accion`, `control` (auto_id o texto),
   `parametros` y, por paso, un CHEQUEO de postcondicion (ventana esperada aparece, el texto del total cambia,
   la grilla tiene N filas, la captura del mensaje contiene tal texto). Los datos variables van como parametros.
3. Ejecutar rapido (sin modelo): un runner lee el recorrido y lo corre paso a paso con topes de tiempo y las reglas de
   la seccion 1. Si todos los chequeos pasan, el modelo nunca se consulta.
4. Reparar: si un chequeo falla, el runner se detiene, guarda captura y estado, y recien ahi llama al modelo con el
   paso fallido y la captura; el modelo propone el paso corregido y se continua. Un paso reparado se reescribe
   en el recorrido solo tras revision humana.
5. Registrar: cada corrida deja resultado, duracion, pasos reparados y capturas; los recorridos viven versionados
   (carpeta por flujo) con la version del POS contra la que se grabaron. Lo aprendido se publica aqui o en
   `proyectos/`, para todo el equipo.

Regla de seguridad: los recorridos solo corren contra el Docker local con el usuario de prueba; nunca bases compartidas.

## 4. Revision de UFO2 y Agent Workflow Memory

Confirmado en la documentacion (microsoft.github.io/UFO y repo, MIT, consultado 2026-10-28):
- UFO2 es el agente de escritorio Windows de UFO3 (el desarrollo activo esta en Galaxy); UFO2 esta en LTS. Python 3.10/3.11.
  Se corre con `python -m ufo --task <nombre>` tras copiar `config/ufo/agents.yaml.template` y poner la clave del modelo.
- Detecta controles por UIA (por defecto), por vision (OmniParser) o hibrido (`CONTROL_BACKEND`). La pagina no
  documenta limitaciones con modales ni WinForms.
- Multi-accion especulativa (`ACTION_SEQUENCE: true`): el modelo predice varias acciones en una llamada, cada una se
  valida contra el estado UIA antes de ejecutarse; si falla la validacion vuelve a una accion por llamada. Reduce
  "hasta 51%" las llamadas (sin condiciones de medicion). La propia guia no la recomienda para UIs muy cambiantes
  ni tareas que necesitan confirmacion entre acciones.
- Aprendizaje por experiencia (`RAG_EXPERIENCE`, apagado por defecto): al terminar con exito pregunta si guardar;
  un LLM resume la trayectoria y se guarda en una base vectorial FAISS (`vectordb/experience/`). Se reusa como
  ejemplos recuperados para que el modelo planee mejor.
- Demostraciones: se graban con el Step Recorder de Windows, un LLM las resume (YAML + FAISS). Segun la doc son
  CONTEXTO RAG para el modelo, no un replay determinista.
- Modelos Claude: `API_TYPE: claude`, paquete `anthropic` 0.37.1, ejemplos con modelos Claude 3/3.5 (la guia
  esta desactualizada respecto a modelos actuales).
- AWM (Agent Workflow Memory): induce "workflows" (subrutinas abstraidas) de experiencias pasadas, offline u online;
  evaluado en WebArena y Mind2Web (web, no escritorio). La pagina no describe el formato ni como se reusan.

Inferencia nuestra (no leida en las paginas):
- Ni UFO2 ni AWM entregan lo que queremos: ambos convierten la experiencia en contexto para el modelo, que sigue
  decidiendo cada paso; no hay un recorrido determinista con chequeos que corra sin modelo.
- El ahorro de la multi-accion depende de que la prediccion sea valida; con modales que se cierran solos y paneles
  que ignoran clics, esperamos validaciones rechazadas frecuentes.
- UIA de UFO2 puede colgarse igual que el nuestro con esas ventanas; no hay evidencia de que lo resuelva.
- Instalarlo suma dependencias pesadas (FAISS, HuggingFace, opcionalmente OmniParser) y claves de API en un PC de trabajo.

Practicas publicas parecidas a nuestro diseno (documentacion de proveedores, fiabilidad sin verificar): Stagehand y
Skyvern cachean las acciones/el codigo generado por el agente y reejecutan sin modelo, cayendo al modelo y
regenerando cuando falla; Browser Use "workflow-use" convierte una demostracion en un script parametrizado con
fallback al agente (declarado no listo para produccion). Es el mismo ciclo de la seccion 3, pero para web.

Recomendacion: NO adoptar UFO2 ahora; copiar sus ideas a nuestros scripts. Lo que mas aporta es (a) validar cada
accion contra el estado actual de UIA antes de ejecutarla (nuestros chequeos de postcondicion), (b) volver a modo
paso a paso ante una falla y (c) guardar trazas exitosas. Eso cubre lo nuestro sin dependencias nuevas.

## Siguiente paso

1. Convertir `facturar_contado.py` + `guardar_preventa.py` en UN recorrido "preventa y facturar" con chequeos por paso
   (ventana esperada, texto de total, captura del mensaje) y parametros (articulo, cantidad, vendedor).
2. Escribir el runner minimo: lee el recorrido, ejecuta con topes de tiempo, al primer chequeo fallido guarda captura y
   se detiene (sin llamar al modelo todavia). Medir el tiempo contra el agente paso a paso.
3. Solo si el punto 2 funciona, agregar la reparacion con modelo y el registro de corridas.
4. Opcional y barato, para comparar: probar UFO2 en una carpeta aislada (venv propio fuera del repo, clave de API
   temporal, solo contra el Docker local, `ACTION_SEQUENCE: false` primero) con una tarea de solo lectura; descartar si
   se cuelga con las modales.

## Venta a crédito con plan de financiamiento (SFA15)

Recorrido probado en la caja 019-04 del Docker, sin mover mouse ni teclado:

1. Cliente: F1 Cambiar Clientes → buscar → elegir la fila (el cliente-finca lleva al asociado).
2. Documento: botón de documento → FACTURA DE CREDITO (Crédito General).
3. Artículo y cantidad; para montos grandes, artículo de precio editable (AV02) con precio personalizado.
4. F5 (Imprimir Documento) abre "Seleccionar Tipo de Credito": elegir el plan → Simulador de Cuotas (el plazo es un
   combo cerrado) → F1 Confirmar. No hay pantalla de cobro: el crédito no registra forma de pago.
5. Diálogo "Guardar impresión como": escribir la ruta completa del PDF con `WM_SETTEXT` en el Edit de id 1001 y
   Enter. El diálogo puede repetirse por cada copia; cerrar las extras con Esc.
6. Verificar en base: `Ticket_Encabezado` (`Factura_Validacion_Credito`, solicitud, crédito, referencia),
   `CreditValidationAttempt` y `Events` en Integrations.

Trucos que funcionaron:
- Botones de diálogos sin `auto_id`: buscarlos por clase BUTTON y texto **con `strip()`** (el POS rellena con
  espacios) y mandar `BM_CLICK` con `PostMessage`, que no bloquea si el clic abre otro modal.
- Antes de cada paso, listar las ventanas visibles del proceso (título, clase, tamaño): los modales del POS
  comparten título y así se sabe cuál está al frente.
- El cierre de caja con el EMV sin datáfono lanza una excepción Win32 al imprimir: es ruido del ambiente, Aceptar
  y seguir; el cierre queda hecho en central.
- Para evidencias: capturar con `PrintWindow` en el momento del mensaje (se cierran solos) y renombrar al formato
  `caja-NN-<caso>-<qué se ve>.png` al copiarlas al repo.
