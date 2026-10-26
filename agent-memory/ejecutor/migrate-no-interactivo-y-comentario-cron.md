---
name: migrate-no-interactivo-y-comentario-cron
description: migrate up pide confirmacion (falla sin TTY): usar push --force; un "*/" en el comentario de cabecera de un .sql cierra el bloque; una migracion fallida queda Fallida y se resuelve renombrando la carpeta
metadata:
  type: feedback
---

- `migrate up` falla en no interactivo ("Failed to read input"; ni `echo y |` sirve). Para aplicar desde un agente: `migrate push --force` (aplica los pending, no re-ejecuta modified).
- Los archivos de migracion llevan cabecera `/* ... */`: un ejemplo de cron con `*/30` dentro de ese comentario lo cierra antes de tiempo ("Incorrect syntax near '30'"). Evitar `*/` en la cabecera.
- Un script que falla deja su fila en `_db_migrations` como Fallido (checksum distinto al corregirlo). No tocar la tabla: renombrar la carpeta con otra marca de tiempo (el nombre viejo queda como aviso "no existe en carpeta"). Si no ha salido de la rama, se puede.
- `sqlcmd -i` y `:r` no entienden rutas `/c/...` de Git Bash: hacer `cd` a la carpeta y usar ruta relativa. Un `--` dentro de una sola linea pegada con `tr '\n' ' '` comenta el resto: quitar los comentarios antes.
**Why:** perdi tiempo en las tres. **How to apply:** al armar y aplicar migraciones con migrate desde un agente.
