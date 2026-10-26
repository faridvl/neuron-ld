---
name: limpieza-rangos-exactos
description: En scripts de limpieza de pruebas contra el Docker de LDCOM, nunca borrar por ">= N": los ids reales llegan a 10.000.000+; usar rangos exactos y probar con SELECT COUNT antes
metadata:
  type: feedback
---

Un script de limpieza con `DELETE ... WHERE Cliente_Id >= 9000000` borro 13.481 relaciones reales y agencias de proveedores del Docker (los clientes/proveedores reales usan 10000001+; el DELETE principal fallo por FK pero los hijos ya se habian borrado).

**Why:** el Docker develop es clon de Staging con datos reales; restaurar costo tiempo (se pudo desde `LDCOM_DOS_PINOS_STAGING_DOCKER`, misma instancia, con IDENTITY_INSERT y triggers deshabilitados).
**How to apply:** rangos cerrados (BETWEEN) para ids de prueba y de contador (ids nuevos = contador, p. ej. >= 10027598); correr primero el SELECT COUNT equivalente; comparar con la linea base despues. Tambien: sqlcmd trae QUOTED_IDENTIFIER OFF y falla contra tablas con indice filtrado (poner SET QUOTED_IDENTIFIER ON).
