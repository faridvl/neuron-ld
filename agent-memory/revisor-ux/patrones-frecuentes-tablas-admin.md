---
name: patrones-frecuentes-tablas-admin
description: Problemas de UX que aparecen seguido en tablas editables de configuración (activar/inactivar, guardado masivo); revisarlos primero
metadata:
  type: feedback
---

Problemas que encontré en tablas de configuración con edición en línea. Conviene buscarlos primero:

- Estado "inactivo" que solo pone gris el texto de una celda: las cajas y los selectores siguen iguales y no se nota. Revisar también que la vista no siga mostrando "Próxima ejecución" de algo inactivo.
- Casillas de 13 px que solo responden en el cuadro, sin `<label>` ni aria-label.
- Verde/rojo de Bootstrap 3 (#5cb85c / #d9534f) en texto de 13 px: no llegan a 4,5:1. Proponer #3c763d / #a94442.
- Tablas hermanas con columnas de igual ancho (sin las clases de ancho de la tabla de referencia): la URL se parte en muchas líneas y los números quedan sueltos.
- `table-layout: fixed` + anchos en % + `th { white-space: nowrap }`: el encabezado largo ("Intentos máximos ⓘ") no se parte ni se corta, se monta encima de la columna vecina. Medir: borde derecho del texto+ícono vs borde de la celda (scrollWidth engaña por el tooltip oculto). Corrección preferida: encabezados cortos iguales a la tabla de referencia + detalle en el tooltip.
- "Clic en toda la celda" con `<label style="display:block">` dentro del td: el label solo mide el alto de una línea (22 px en celda de 72); arriba y abajo no responde. Medir el rect del label vs el del td.
- Marca "Inactivo" agregada con ::after bajo el nombre: si el nombre ya ocupa 3 líneas, la fila crece y todo lo de abajo salta ~16 px al marcar/desmarcar (clics seguidos fallan).
- Aunque la marca pase a `display:inline` "en la misma línea", en una columna angosta (142 px) con nombre de 3 líneas la palabra "Inactivo" se va sola a una 4.ª línea: medir con un script que agregue/quite la clase de inactivo en cada fila y compare alturas (sin tocar las casillas).
- Label de 44 px centrado en una celda de 61-72 px: "toda la celda" no es cierto; los ~10-14 px de arriba y abajo no responden. Probar un clic 26 px arriba, no solo 20.
- `<thead>` estático viejo en el .cshtml que el JS reemplaza al cargar: se ve un instante con encabezados antiguos. Comparar el thead del HTML servido con el renderizado.
- Nombre interno (p. ej. AJUSTE_SALDO) en una fila donde las demás tienen nombre amigable con su código LD-xx.
- Flecha de "volver" que descarta cambios sin preguntar y el botón Guardar al final de una página larga.
- Guardado masivo que reescribe UpdatedAt/UpdatedBy de todo, incluso secciones sensibles que no se tocaron (por ejemplo, conexiones). Comparar una huella de la BD antes y después; nunca SELECT * de tablas con credenciales.

Campo extra metido en la celda del nombre de una fila (revisión del tipo de tasa, 2026-10-28):
- El marcador "· Inactivo" hecho con `td:first-child::after` cae debajo del campo nuevo, solo en una línea, y parece describir al campo. Proponer el ::after sobre el span del nombre.
- `text-transform: uppercase` en la caja también pone en mayúscula el placeholder ("EJ.: P"): pedir `::placeholder { text-transform: none }`.
- Tooltip "Por defecto es X" mientras el vacío se rechaza: contradicción; el usuario borra creyendo que vuelve al valor por defecto.
- Ayuda solo en un tooltip `:hover` con `visibility:hidden` y sin `aria-describedby` ni tabindex: teclado y lector de pantalla nunca la reciben. Si es la única explicación del campo, pedir texto visible corto bajo la caja.
- "Sin definir" en `.val-sin-definir` (#bbb, cursiva, 1,9:1) cuando el vacío deja algo roto: debe verse como aviso (#a94442), no como dato opcional.
- maxlength igual al máximo de la regla: el mensaje "más de N caracteres" es inalcanzable y el pegado se corta en silencio.
- Errores solo en toast alertify (abajo a la derecha, 5 s) lejos del campo, con el nombre largo del evento: medir el texto y pedir mensaje bajo la caja.
- Arnés sin login del Admin: no carga Font Awesome (íconos de 0 px) y su guardado siempre responde éxito y escribe payload-N.json desde 1, pisando los de otra corrida. Inyectar el CSS de fontawesome por JS y avisar de los payloads. `leerConexionesEditar` bloquea el guardado si la copia no tiene clave: reemplazarlo por JS en la página para llegar a la validación que interesa.

**Why:** salieron todos juntos en la revisión de la columna Activo del Admin LDCOM (2026-10-26).
**How to apply:** en cualquier pantalla de configuración con casillas o activación, medir con JS (alto de encabezados, scrollWidth, colores calculados) y hacer el recorrido completo: alternar, salir sin guardar, guardar, F5.

Detalles del entorno: el Admin LDCOM necesita entrar por el menú (deja `menuId` en sessionStorage); si se entra directo por URL, los menús internos quedan vacíos. En el panel, la tecla Ctrl+F5 no recarga: usar `location.reload()` por JS y confirmar con `performance.now()` y el transferSize del .min.js. Las capturas del panel del navegador llegan con un paso de atraso: esperar 1 s después de hacer scroll. Para ver un estado que solo aparece guardando (p. ej. "Pausado" en vista), llamar al render de la vista desde consola con una copia JSON de los datos modificada y luego volver a renderizar con el original: no toca la BD. Un hook impide que este agente escriba fuera de su memoria: el informe se entrega en el mensaje final y lo guarda el que hizo el encargo.
