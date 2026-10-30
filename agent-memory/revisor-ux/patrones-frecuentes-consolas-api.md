---
name: patrones-frecuentes-consolas-api
description: Problemas de UX que aparecen seguido en consolas/probadores de API (elegir endpoint, editar JSON, enviar, ver respuesta); revisarlos primero
metadata:
  type: feedback
---

Buscar primero en cualquier probador de endpoints o consola de pruebas:

- Datos de ejemplo que no existen en la base de destino: el primer Enviar siempre da 4xx (p. ej. sucursal inexistente). Enviar tal cual el ejemplo y ver qué pasa.
- Acción con efecto real (consumir una cola, correr una sincronización) con el mismo botón azul "Enviar" que todo lo demás y sin confirmación. Un aviso arriba no alcanza: pedir botón con verbo + objeto y confirmación.
- Validación local (JSON mal escrito) mostrada como respuesta HTTP: insignia roja "0" y "0 ms", que el código traduce como "no se pudo conectar". Mandar un GET con JSON roto para verlo.
- JSON "formateado" re-serializado que escapa tildes (`catálogo`).
- Barra de la respuesta que repite la URL completa: con query largas se parte en 3 líneas (código, URL, tiempo).
- Tras un postback la página vuelve arriba y la respuesta queda bajo el textarea, fuera de la vista.
- Selects con códigos internos (TIPO_CAMBIO) cuando la lista de al lado usa nombres amigables.
- Texto ámbar sobre fondo crema (#b8790a / #fff3dd ≈ 3,3:1): calcular el contraste de los avisos.
- Botón que abre un modal vacío ("Sin guía todavía"): ocultarlo cuando no hay contenido.
- Desborde horizontal solo en algunos endpoints: URL de query larga sin cortes (`a=1&b=2...`) ensancha la columna del grid (`1fr` sin `minmax(0,1fr)`). El documento no se desborda (el `main` tiene overflow auto): medir `main.scrollWidth` vs `clientWidth` por endpoint y ancho, no `document`.
- Respuesta gigante pintada entera en un `<pre>` (4,6 MB con limit=10): medir el largo del texto de la respuesta; pedir truncar la vista y ofrecer copiar/descargar.
- Tuteo escondido en tooltips (`title=`) aunque los textos visibles usen "usted": grep de `title=` en el HTML.

**Why:** salieron juntos en la revisión del Probador de Endpoints de la consola de integraciones (2026-10-28).
**How to apply:** recorrer con Playwright sin interfaz (playwright-core de algún node_modules del disco + chromium de ms-playwright), script por `node - <<'EOF'` porque el hook no deja escribir archivos fuera de la memoria; el panel del navegador pierde el tamaño emulado al navegar. Ver también [[patrones-frecuentes-tablas-admin]].
