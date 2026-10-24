# Tipo: bug

1. Delegar la causa raiz a `investigador-ldcom` con el escenario completo: pasos, montos, mensaje de
   error exacto, sucursal/caja si el ticket la trae.
2. Verificar el hallazgo leyendo el codigo real (Read con offset/limit). Si los numeros del ticket
   calzan exacto con el mecanismo encontrado (ej. 50+50=100 en el 2244), la confianza es alta sin
   correr la app.
3. **Grep del patron en todo el repo.** La logica de facturacion/caja esta duplicada por copy-paste
   entre formularios paralelos. Confirmar cuales copias comparten el defecto; no asumir que todas.
4. Revisar si el fix toca SQL/reportes o si esos solo consumen lo que la UI calcula mal. Tocar SQL +
   reportes sube bastante el estimado.
5. Si el sintoma es "un campo muestra el valor de otro", consultar primero la base: puede que el dato
   ya este cruzado ahi y el caso sea de datos, no de codigo (caso 2240).
6. En reportes con datos raros, revisar tambien el **formulario de captura**: una opcion de UI oculta
   por un fix anterior puede dejar una rama del backend inalcanzable (caso 2232).
7. Si un patron aparece en un ambiente y no en otro, triangular contra 2-3 ambientes antes de decidir
   si es dato sucio de pruebas o un bug real poco frecuente.

Un mensaje de error secundario en las capturas no se descarta por no ser el foco obvio: en el 2156
era la causa real de otro escenario del mismo ticket.

## Bug de estandar (sin commit identificable)

`git log --all --oneline -- <archivo>` puede no mostrar ningun commit que "introdujo" el defecto,
porque el codigo defectuoso existe desde el commit original del modulo (o desde antes del alcance del
historial). Esto es distinto de un bug que se rompio por un cambio reciente: aqui nunca estuvo bien.

Cuando el analisis de codigo confirma la causa raiz pero no hay un commit de regresion que la
explique, se marca explicitamente — no se deja como si fuera una regresion mas:

- En la nota tecnica (`references/plantillas.md`), agregar en negrita: **Es un bug que viene de
  estandar.** seguido de la evidencia (`git log --all` sin resultados relacionados, o el commit mas
  viejo que toca el archivo ya lo trae asi).
- En la fila de `references/calibracion.md`, anotarlo tambien: cambia como se explica el estimado
  (no hay "que se rompio" que contar, es "siempre estuvo mal") y ayuda a que un caso futuro con el
  mismo sintoma se reconozca mas rapido.

No cambia el tipo de caso (sigue siendo bug, se estima igual) ni el estimado en si — es una etiqueta
de origen, para que quien lo lea despues no asuma que hay una regresion que buscar en otro lado.

## De quien fue el commit que introdujo el bug (solo para el usuario, nunca para el ticket)

Una vez confirmada la causa raiz linea por linea, identificar el commit que la introdujo:

```
git blame -L <linea>,<linea> -- <archivo>       # ultimo commit que toco esa linea exacta
git show -s --format="%H %ai %an" <hash>        # id completo, fecha, autor
```

Si `git blame` no encuentra nada (el bug es de estandar, ver arriba), decirlo asi en vez de forzar un
commit que no aplica.

**Esto se reporta solo al usuario en el chat/resumen, nunca en el comentario de negocio ni en la nota
tecnica** (`references/plantillas.md`) — esos documentos son para resolver el ticket, no para señalar
quien lo causo. Formato al reportarlo en el chat:

```
Commit que introdujo esto: <hash corto> · <fecha> · <autor>
```
