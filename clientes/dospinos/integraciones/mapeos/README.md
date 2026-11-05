# Mapeos de integraciones LDCOM - Dos Pinos

Un archivo `.json` por integración es la fuente de verdad. El script arma el Excel
`Mapeo-Integraciones-DosPinos.xlsx`: un índice, una hoja "Variables" (todos los campos de todas
las integraciones: qué manda LDCOM y por qué), una hoja por integración que es solo el mapeo de
campos (campo de Dos Pinos, de dónde sale en LDCOM, por qué, tipo, significado, ejemplo, estado),
una hoja "Reglas" con el endpoint, cuándo se envía y las reglas de cada integración, y una hoja
"Preguntas a Dos Pinos". El Excel se puede borrar y regenerar cuando se quiera.

## Hoja Avance

`avance.json` lleva el estado de todas las interfaces (una por carpeta de Documentos-DosPinos-Interfaces):
`estado` (Implementada en verde, En curso en amarillo, Sin empezar en blanco), `porcentaje`, `hecho`, `falta`
y `bloqueo`, con PRs como evidencia. `para_100` (opcional) dice qué le falta para el 100 % y sale como comentario
en la celda del porcentaje; si no está, el comentario usa `falta`. Se actualiza `fecha_corte` y la fila de la interfaz cada vez que avanza
(un PR mergeado, una prueba contra Dos Pinos) y se regenera el Excel.

## Agregar una integración

1. Copiar `POS-19.json` a `POS-XX.json` (el nombre del archivo es el código).
2. Llenar los datos generales, las reglas, las preguntas y los campos.
3. Correr, desde esta carpeta:

```
python -I generar_excel.py
```

Requiere `openpyxl` y `Pillow`. Cada sesión toca solo su propio json, así que no hay conflictos. El Excel tiene
que estar cerrado para regenerarlo.

## Imágenes y hojas agregadas a mano

En el Excel se pegan imágenes (capturas, tablas de Dos Pinos). Al regenerar, el script conserva las imágenes de
cada hoja en la misma celda y copia las hojas que no salen de los json (nombre distinto a las generadas). Lo que
se escriba a mano dentro de una hoja generada sí se pierde: va en el json. Una imagen queda anclada a su celda, así
que si se agregan campos antes de ella puede quedar al lado de otra fila; conviene pegarlas a la derecha de la tabla.

## Qué lleva cada json

- Datos generales: `codigo`, `nombre`, `sentido`, `endpoint`, `autenticacion`, `dispara`,
  `cuando_se_envia`, `fuente_documentacion`, `estado_general`, `notas_generales`.
- `reglas`: lista de `{tema, regla}` en palabras simples.
- `preguntas`: lista de `{numero, tema, pregunta, campos}`. Se agrupan las dudas por tema
  (no una por campo) y salen en la hoja "Preguntas a Dos Pinos".
- `campos`: lista con `bloque`, `campo`, `doc` (tipo, largo, obligatorio según el documento),
  `origen` (de dónde sale en LDCOM), `porque` (por qué se manda eso), `descripcion` (qué significa, para quien no programa),
  `ejemplo`, `estado`, `duda` y `porque_duda` (qué falta saber y por qué no está cerrado; vacíos si no hay duda), `nota` y `pregunta`
  (número o números de la lista de preguntas, o vacío). Un campo Provisional, Pregunta a Dos Pinos o con `duda` sale con
  toda la fila en rojo en el Excel.

## Estados permitidos

| Estado | Color | Cuándo |
|---|---|---|
| Confirmado | verde | Dos Pinos lo confirmó o se probó contra su ambiente |
| Decidido por nosotros | azul | Lo decidimos nosotros y no depende de ellos |
| Provisional | naranja | Usamos un valor de prueba hasta que Dos Pinos entregue el real |
| Pregunta a Dos Pinos | rojo | Es una suposición nuestra que hay que confirmar |

Lo que no se sepa se marca Provisional o Pregunta a Dos Pinos; no se inventa.
Los ejemplos que sean ilustrativos se dicen así en la nota.

## Filas con duda

Toda fila Provisional o Pregunta a Dos Pinos sale entera en rojo, con la columna 'Duda y por qué es duda'. Cada campo pendiente lleva su `duda` en el json: qué no sabemos y por qué (regla del usuario, 2026-11-04). Si falta, el Excel muestra la nota.
