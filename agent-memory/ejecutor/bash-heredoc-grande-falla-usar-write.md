---
name: bash-heredoc-grande-falla-usar-write
description: En el Bash de esta PC, heredocs grandes con comillas/acentos fallan con "unexpected EOF"; escribir el script con Write y ejecutarlo.
metadata:
  type: feedback
---

Un `cat > archivo <<'E'` o `python - <<'E'` con cuerpo largo (muchas comillas, acentos, comillas triples) fallo dos veces con "unexpected EOF while looking for matching" y no escribio nada.

**Why:** el parser del tool Bash revisa comillas del comando completo aunque el heredoc sea literal.

**How to apply:** para editar varios archivos o reemplazos grandes, crear el `.py` en el scratchpad con Write y correrlo con `python <ruta>`; para archivos nuevos, Write directo. Verificar siempre que el archivo cambio (git status/diff) antes de seguir. Para reemplazos que conservan CRLF/BOM: leer en bytes, detectar BOM/CRLF, reemplazar con `assert count == 1`, escribir en bytes.
