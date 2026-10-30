---
name: confluence-buscar-claves-duplicadas
description: confluence.ps1 -Accion Buscar falla en PS 5.1 por claves duplicadas (subType/subtype); Leer por id si funciona. Publicar por un subagente puede ser denegado por el clasificador.
metadata:
  type: feedback
---

`confluence.ps1 -Accion Buscar` rompe con "duplicated keys 'subType' and 'subtype'" (ConvertFrom-Json de PS 5.1); usar `-Accion Leer -PageId` con el id conocido.

**Why:** el JSON de busqueda de Confluence trae claves que difieren solo en mayuscula.

**How to apply:** localizar paginas por id (mapa del skill documentar-endpoint-integraciones) y no por busqueda.

Ademas: un `-Accion Publicar` lanzado por subagente puede ser denegado por el clasificador de permisos aunque el coordinador lo haya autorizado (la primera publicacion pasó, la segunda no); no rodearlo, dejar el .nuevo.xml listo y reportar.
