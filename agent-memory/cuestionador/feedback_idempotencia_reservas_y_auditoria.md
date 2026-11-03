---
name: idempotencia-reservas-y-auditoria
description: Fallas recurrentes en idempotencia por reserva (finally que libera tras el efecto externo, sin dueno, replay sin comparar) y en auditorias por request sin tope
metadata:
  type: feedback
---

Buscar primero, en cambios con reserva/idempotencia o auditoria de errores:

- `finally` que libera la reserva si "no se completo" aunque el efecto externo (INSERT en el ERP) ya ocurrio: el reintento duplica. Verificar que haya bandera "ya inserto" y que exista prueba de fallo DESPUES del insert (las pruebas suelen cubrir solo fallos antes).
- Release/Complete/Refresh sin token de dueno y toma de reserva vencida por DELETE+INSERT no atomico, con vencimiento fijo desde CreatedAt.
- Replay que devuelve 200 con la respuesta vieja aunque el cuerpo sea distinto, sin marca ni hash; respuesta guardada que se queda obsoleta (estado, isEditable); referencia de un documento anulado que no se libera; tabla de reservas sin purga.
- Fallback silencioso de un tipo desconocido a "General" (pierde reglas del tipo, solo una advertencia).
- Auditoria de una fila por request (400) sin agregacion ni tope, con WaitAsync en el hilo del request; comentario "ya autenticada" que depende de una bandera de config (EnableAuthentication=false).
- Auditoria que descarta filas sin reintento, no guarda la hora real del evento, y escritura de BD del worker sin timeout.
- Comentarios con `AB#nnnn` y relato historico ("Hasta X el socio mandaba...") en lugar de `'Issue NNNN: regla'`; fechas en encabezados de migracion; mascaras de formato fijas.

**Why:** hallados en la revision del PR 1224 de LDCOM13_INTEGRATIONS (2026-11-02).
**How to apply:** al revisar idempotencia, trazar cada excepcion posible entre el efecto externo y el "completar"; al revisar auditorias, preguntar que pasa con 10 000 requests malos por minuto y con la BD lenta.
