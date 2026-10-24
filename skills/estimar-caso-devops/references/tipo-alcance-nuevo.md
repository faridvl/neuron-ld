# Tipo: alcance nuevo disfrazado de bug

No es un bug: nunca existio en el codigo. Por eso no lleva horas de "fix". Segun la decision de
negocio vigente, termina en un rechazo bien documentado o en un estimado de **desarrollo nuevo**.

Señales: verbos como "incorporar" o "agregar", frases como "no se dispone de una opcion para", o que
el propio ticket diga que es "un ajuste conversado para incluir en tareas futuras".

## Primero: cual es la decision vigente

Armar la linea de tiempo de decisiones (ver `validacion.md`) y tomar la mas reciente con autor
identificable. Un comentario breve como "segun acordado con X se vera como un caso" ES una decision:
deja sin efecto a una anterior que lo descartaba.

## Segun la decision vigente

**Negocio aprobo tratarlo como caso** -> ESTIMAR como desarrollo nuevo.
- Buscar un **precedente**: la misma funcionalidad en una entidad hermana del dominio (ej. una
  restriccion o validacion que ya tiene una promocion y le falta a otra del mismo modulo). El
  precedente es el molde a copiar, no una prueba de que "se excluyo a proposito": esa lectura solo
  vale mientras no haya una decision posterior que lo apruebe.
- Estimar por capas, cada una contra el precedente: tabla/migracion, DTO y logica de negocio,
  pantalla de configuracion, validacion donde se aplica (ej. facturacion), carga masiva y reportes si
  el precedente los tiene. Anotar que capas del precedente NO se replican y por que.
- El comentario de negocio aclara que es desarrollo nuevo aprobado como caso, cita la decision que lo
  aprobo, y da el estimado.

**Nadie lo aprobo ni lo descarto** -> RECHAZAR como alcance nuevo.
- El comentario dice que es un pedido de alcance nuevo, da una nocion de tamaño si se decide
  construir (capas, sin numero de "estimado de caso") y pregunta si negocio lo quiere tramitar como
  caso o como cotizacion aparte.

**La decision vigente lo descarta** -> RECHAZAR citando esa decision.
- Citar la decision tal cual (fecha, autor, ticket, texto) y ligar ambos tickets con
  `System.LinkTypes.Related`.

**El usuario informa que ya esta gestionado en otro proyecto o iniciativa** -> RECHAZAR como "no
corresponde al flujo de casos".
- Es un dato que solo tiene el usuario; no se deduce del board.
- El comentario va directo a la conclusion sin repetir la investigacion tecnica: esa queda en la
  calibracion, no en lo que lee negocio.

**No se puede saber cual decision vale** -> preguntar al usuario; si tampoco lo sabe, BLOQUEAR.

## Estado del ticket

Si no queda nada que hacer del lado de soporte, se puede cerrar. Si falta un tramite de soporte/CRM
(cerrar el caso formalmente, confirmar con el cliente), el estado es `Blocked` asignado a quien hace
ese tramite — preguntarle al usuario a quien.
