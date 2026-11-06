---
name: config-a-bd-y-defaults
description: Fallas al mover configuracion de appsettings a parametros en BD (defaults 0/vacio silencioso, primer valor global por nombre de evento, sync-over-async, seeds con valores del appsettings viejo)
metadata:
  type: feedback
---

Al revisar un cambio que saca configuracion del appsettings y la lee de la base, buscar primero:

- Default que pasa de valor real a 0/vacio: consumidores que no validan (UserId=0, BodegaId=0 escritos en LDCOM sin error) y monitores que se saltan en log Debug (`IsConfiguredFor` falso = reporte apagado sin aviso).
- "Primer valor no vacio por nombre de evento, orden alfabetico" con el mismo parametro sembrado en varios eventos: editar el valor en un solo evento no tiene efecto si otro evento anterior alfabeticamente conserva el viejo.
- Un parametro invalido (UserFacingException en `ReadInt`) dentro de un getter de contexto (`Current`) rompe todo request, aunque no use ese valor.
- `.GetAwaiter().GetResult()` en el getter de un contexto scoped: sin deadlock en ASP.NET Core, pero una consulta completa sin cache por scope/SetTenant y hilos bloqueados.
- Seeds que siembran los valores del appsettings de produccion del cliente en ambientes con otros valores (insertar solo si no existe, pero el ambiente nunca los tuvo).
- Lazy / Task cacheado que guarda la excepcion durante la vida del scope.

**Why:** revision de fix/quitar-integration-stage (LDCOM13_INTEGRATIONS, 2026-11-05).
**How to apply:** en cualquier PR que mueva config a BD, listar por ambiente que parametros hay que cargar y que pasa si faltan.
