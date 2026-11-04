# Receta: una interfaz saliente LDCOM -> Dos Pinos sobre la base Notificar

Orden de trabajo para cada interfaz nueva (POS-xx) que sale de LDCOM hacia Dos Pinos. El diseño está en
`interfaces-salientes-dos-pinos-contratos.md` §4 y las piezas de LDCOM/Integrations en
`integrar-endpoint-pos-dos-pinos.md`. Esta receta dice **en qué orden** y **qué tiene que estar listo antes de cada
paso**, porque lo que más tiempo costó en POS-19 no fue programar sino esperar y corregir tarde.

## Por qué este orden

En POS-19 el primer envío real a Dos Pinos salió 7 h después de empezar. El código estaba, pero:

- la prueba real quedó como último paso y cada agente daba por terminado su trabajo con pruebas unitarias;
- al llegar a ella faltaban cosas que nadie revisó al arrancar (credencial vacía en Docker, migraciones del Docker
  atrasadas, el espacio de rig sin asignar, Docker con 15 h encendido que se colgó);
- un `git commit` quedó casi 3 h esperando aprobación de madrugada;
- cómo se llena cada campo (USER, CSAGR, NROEJ, GUID, LIBRO_CAJA) se decidió al final y obligó a cuatro rondas de
  corrección y republicación;
- la prueba desde el POS se intentó automatizar sin tener el flujo de esa pantalla y se fueron 3 h.

## Fase 0. Antes de programar (la sesión que reparte, con el usuario presente, ~45 min)

Nada se reparte a un agente hasta que estas tres cosas estén cerradas.

**A. Contrato real.** La carpeta de la interfaz en Bruno (`Postman_LDCOM13_DOSPINOS`) ya corrida contra el dev de Dos
Pinos, con sus respuestas guardadas: éxito, rechazo por campo faltante, duplicado y lo que acepte aunque no debería.
Si no está, eso es lo primero.

**B. Mapeo campo por campo, aprobado por el usuario.** El json de la interfaz en
`clientes/dospinos/integraciones/mapeos/POS-XX.json`, lleno **antes** de escribir el builder:

- cada campo de Dos Pinos con el dato de LDCOM que lo llena (`origen`) y la cita de la documentación (`doc`: tipo,
  largo, obligatorio, de qué documento o página de Confluence sale);
- los campos de control (GUID, consecutivos, referencia, usuario) decididos igual que en las interfaces ya hechas,
  salvo que el contrato diga otra cosa. El GUID no tiene excepción: siempre es el `TransactionId` que se guarda en el
  Monitor (ver `interfaces-salientes-dos-pinos-contratos.md` §4). Usuario = el cajero o quien dispara el
  documento, referencia y agrupación armadas con los IDs de LDCOM separados por guiones, recortadas al largo del
  contrato;
- los nombres de campo son abreviaturas de SAP (`BUKRS` = sociedad, `MATNR` = material, `WERKS` = centro...): ante la
  duda de qué lleva un campo, buscar su significado en la documentación de SAP antes de proponer. Los del bloque de
  control (`IDITZ`, `CSAGR`, `NROEJ`, `DATEE`, `HOURE`) son propios de Dos Pinos y no aparecen en internet;
- lo que no se sepa va como `Provisional` o `Pregunta a Dos Pinos`, nunca inventado;
- se regenera el Excel y el usuario lo revisa. Su aprobación es el visto bueno para programar;
- **apenas se aprueba, el json se commitea y se sube en neuron-ld**, para que la sesión de la otra PC trabaje con el
  mismo mapeo;
- **las preguntas a Dos Pinos salen ese mismo día** (hoja "Preguntas a Dos Pinos"), para que respondan mientras se
  programa. Mientras no respondan, el campo se programa con el valor provisional que dice el json.

El json es la fuente de verdad durante todo el trabajo: si en cualquier fase se decide o cambia cómo se llena un
campo, primero se actualiza el json (y se sube) y después el código.

Toda propuesta o pregunta al usuario lleva la fuente: "el documento X dice Y" o "no está documentado, propongo Z".

**C. Listo para la prueba real (checklist).** Cada punto se verifica, no se supone:

| # | Qué | Cómo se verifica |
|---|---|---|
| 1 | Docker sano y reciente | `docker ps` con los contenedores `healthy`; si llevan más de 12 h encendidos, reiniciarlos con `rig docker` en la terminal del usuario antes de empezar |
| 2 | Migraciones del Docker al día con la rama base | `migrate status` desde una carpeta con su `.env` apuntando a Docker, en LDCOM y en Integrations: 0 pendientes |
| 3 | Credencial de la interfaz cargada en el Docker | `IntegrationCredential` de la interfaz con usuario y clave no nulos (se cargan desde el ambiente de Bruno sin mostrarlos) |
| 4 | Evento activo solo en Docker, apuntando a la URL real de dev de Dos Pinos | fila de `IntegrationEvent` con `IsActive = 1` y la URL de Bruno |
| 5 | Espacio de rig asignado al worktree y caja/usuario de prueba | `rig status` desde la terminal del usuario (la sesión ve un AppData aislado) |
| 6 | Permisos para trabajar sin esperar | commits locales en worktrees, `dotnet`, `rig`, `docker exec` y `migrate` contra Docker permitidos en la configuración; si no, el trabajo de noche se detiene en el primer diálogo |
| 7 | Cómo se va a probar desde el POS | si `skills/automatizar-pos` ya tiene el flujo de esa pantalla, se usa; si no, lo hace el usuario a mano y la automatización queda como tarea aparte |

Si falta un punto, se resuelve en la Fase 0 con el usuario presente. No se deja para la noche.

## Fase 1. Primer envío real (la primera hora de programar)

Antes del builder completo: una versión mínima del builder que arme un mensaje válido con un documento real del
Docker, enviada por el Runner directo a la URL real de dev de Dos Pinos. Terminado = HTTP y respuesta de Dos Pinos
guardados en `OutboundNotification` y mostrados al usuario (URL, código, cuerpo).

Así cualquier hueco del ambiente (credencial, URL, auth, migración) aparece en la primera hora y no al final.

## Fase 2. Completar (encargos chicos y en secuencia)

Un agente por pieza, cada uno cabe en su tope de turnos:

1. Builder completo + clasificador + una prueba por campo del mapeo (`Applies`, `BuildAsync`, `Classify`).
2. Fila del evento en `Database/seeds/04__webhooks.sql` (nace inactivo), hechos, parámetros y credencial.
3. Lado LDCOM, solo si el hecho no existe todavía: armado del documento y el `Notificar` post-commit.
4. Reenvío real del mismo caso para confirmar que el duplicado se clasifica bien.

Primera línea de cada encargo, antes que el contexto:

```
TERMINADO = <qué tiene que pasar, observable>. Para todo envío: respuesta HTTP real de <URL de dev de Dos Pinos>
guardada en OutboundNotification. Si no se logra, reportar BLOQUEO con la causa y no seguir con otra cosa.
NO TOCAR: <lo que no puede cambiar ni cerrar: cajas, cierres, datos que no se pueden revertir>.
```

El simulador CIH sirve para forzar lo que el real no da (caída, timeout), nunca como prueba de que la interfaz
funciona.

## Fase 3. Prueba desde el POS

Con el flujo de `automatizar-pos` o a mano por el usuario, según lo decidido en la Fase 0, punto 7. Se verifica en la
base de Integrations del Docker: la fila en `OutboundNotification` con `SENT`, su rastro en `Events` y la respuesta de
Dos Pinos. Un agente de prueba no cierra cajas ni aplica documentos que no estén en su encargo.

## Fase 4. Entregar

- Comparar el json con el último mensaje real enviado: cada campo dice lo que de verdad salió. Las respuestas de
  Dos Pinos que llegaron pasan sus campos a `Confirmado`.
- PR de Integrations y luego de LDCOM, con lo que se probó contra Dos Pinos real en "Qué se probó" y las preguntas
  que sigan abiertas.

## Reglas que no dependen de la PC

La memoria de Claude es de cada computadora; lo que se guarda en una no lo ve la sesión de la otra. Lo que tiene que
saber cualquier sesión que trabaje una interfaz va en este archivo o en otro de neuron-ld, no en la memoria local:

- La prueba que da por terminada una interfaz es contra la URL real de dev de Dos Pinos, con su respuesta.
- El mapeo se llena y se aprueba antes de programar, se sube a neuron-ld en ese momento y cada cambio va primero al
  json; cada interfaz tiene su json en `mapeos/`.
- Los scripts de automatización del POS van en `skills/automatizar-pos`, no sueltos.
- La sesión que reparte escribe en neuron-ld lo que el usuario decide antes de mandar el encargo, no al cerrar.
