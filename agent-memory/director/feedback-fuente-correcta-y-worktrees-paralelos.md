---
name: fuente-correcta-y-worktrees-paralelos
description: Antes de portar trabajo sin commit de un worktree, listar los demás worktrees (git worktree list) y comparar fechas: puede haber una versión más nueva; y el coordinador puede cambiar fuente y alcance a mitad
metadata:
  type: feedback
---

En el port del Admin de Integraciones (2026-10-28) el encargo apuntaba a `e2e-admin-interfaces`, pero existía `admin-interfaces-63` con un superconjunto (rediseño Figma) más nuevo; el coordinador luego confirmó que esa era la fuente. Se rehízo la rama y se gastó ~1 h con agentes sobre la versión equivocada.

**Why:** el encargo nombra una fuente, pero otras sesiones dejan worktrees con trabajo más reciente sin commit.
**How to apply:** al empezar, `git worktree list` + mtime/`git status` de worktrees con nombre parecido; reportar de inmediato la duda al llamador antes de lanzar revisores. Tomar una copia de seguridad en rama local (`backup/...`) antes de rehacer commits. Para portar un worktree con base vieja usar `git diff HEAD | git apply --3way` y, si hay conflictos porque la base no tenía un commit ya mergeado, copiar el archivo completo si su diff contra la base release coincide con lo esperado. Revisores (revisor-ldcom/qa/cuestionador) tardaron 15-28 min cada uno: con prisa, solo revisor-ldcom.
