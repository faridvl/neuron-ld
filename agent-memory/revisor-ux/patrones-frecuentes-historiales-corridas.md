---
name: patrones-frecuentes-historiales-corridas
description: Problemas de UX que aparecen seguido en historiales/bitácoras de corridas o jobs (lista + detalle por pasos + JSON); revisarlos primero
metadata:
  type: feedback
---

Buscar primero en cualquier historial de corridas, jobs o sincronizaciones:

- Estado guardado ≠ texto mostrado: el filtro "Falló" no trae filas que la lista pinta rojas "Falló: …" (quedaron como WARNING), y "Con advertencias" trae filas verdes. Cruzar cada opción del filtro de estado con el color/texto de las filas que devuelve.
- Corrida terminada que sigue diciendo "Reintentando (intento 4 de 3)" en ámbar: se agotaron los intentos y nunca se escribió el paso Fin. Buscar contadores imposibles (N de M con N>M) y duraciones absurdas (101 h).
- Mismo concepto con dos nombres: "Con advertencias" (filtro) vs "Con avisos" (fila); "rechazados" vs "con error" sin explicar la diferencia.
- Pasos mezclados en inglés (mensajes del log: "Client sync started", "Partial failure…") aunque las etiquetas estén en español.
- Origen "Manual · API" o "Manual" sin usuario; nombres internos de interfaz (New traslado, Update preventa, códigos LD-xx) en las filas de otros orígenes.
- Pasos fuera de orden (Aviso antes de Lectura) por ordenar solo por hora con segundos iguales; pasos "Falló" y "Aviso" con el mismo texto duplicados.
- "y N avisos más" no desplegable.
- Badges que se parten en dos líneas (columna Origen y botón "Ver pasos" sin nowrap) cuando la tabla es auto-layout y cambia el ancho de columnas según el filtro.
- Badges ok/warn a 11,5 px con contraste < 4,5:1 (verde #1a8f5c/#e6f6ee ≈ 3,7; ámbar #b8790a/#fff3dd ≈ 3,3).
- Búsqueda por Id que solo acepta el Id exacto (parcial = 0) y estado vacío sin "Limpiar filtros".
- Bloque de "vaciar/borrar" siempre visible con nombres de tablas (dbo.Events) bajo la lista.

- Al pasar de chips a marca de color (subrayado): revisar que el paso "Falló" use err en TODAS las rutas (salió naranja en una y sin marca en otra), que el paso Fin de una fallida lleve marca, y que naranja != marrón: #8a5a00 vs rojo #b42318 da dE 2,3 en deuteranopia (indistinguibles). Simular con feColorMatrix en Playwright.
- Corrida cortada a mitad de reintentos sigue "Reintentando (intento 2 de 3)" días después: buscar corridas viejas sin Fin, no solo las de N>M.
- Detalle y JSON ocultos renderizados en el servidor: páginas de 50 llegan a 1,9 MB y 3 s.

- Ronda 3: un arreglo de color aplicado solo a un tipo de corrida (jobs) deja sin marca el paso "Falló" de otro origen (push de Dos Pinos, 111 corridas). Contar pasos por (etiqueta, clase) en TODAS las páginas, no mirar 3 ejemplos.
- Marca tardía "Corrida interrumpida" pegada a una corrida que ya tenía Fin: la fila pasa a gris y esconde rechazados. Y duración de interrumpida (<0,1 s) que no cuadra con las horas de los pasos (23 s).
- Filtro "Con avisos" que trae filas verdes sin decir cuántos avisos: agregar "· N avisos" al resultado.
- Volcar todo por fetch+DOMParser desde el Browser pane (javascript_tool, lanzar async sin await si pasa de 45 s); la última página se repite al pedir páginas de más.

**Why:** salieron juntos en la revisión de Historial > Corridas de la consola de integraciones (2026-10-28).
**How to apply:** abrir cada estado del filtro con 50 por página y comparar con lo que muestra la fila; abrir una corrida de reintentos y una fallida. Playwright por `$js | node -` desde PowerShell (Write y heredoc de bash bloqueados/rotos; usar solo ASCII en el script, \u para tildes). Ver [[patrones-frecuentes-consolas-api]].
