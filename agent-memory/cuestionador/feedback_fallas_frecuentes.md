---
name: fallas-frecuentes-revision
description: Tipos de falla que conviene buscar primero al cuestionar un cambio (defaults de servidor, banderas duplicadas, rutas hermanas sin parchear, estado que no se persiste)
metadata:
  type: feedback
---

Buscar primero, en cambios de reglas de negocio en POS/WCF (LDCOM VB.NET):

1. Defaults de servidor que parecen "dato leído": `TParametrosSucursal.Load` devuelve True con 0 filas y precarga defaults (Facturacion_Negativa=True, Bodega=1). Un cliente que usa `Nothing` como "sin dato" no ve ese caso. Comparar con cómo el servidor trata "sin fila" en otros sitios (p. ej. TPreventa.DebeComprometerExistencia).
2. Dos banderas con el mismo rótulo (caja vs sucursal): confirmar cuál leía el POS antes; la que "nunca se usó" puede tener valores sin revisar.
3. Rutas hermanas sin parchear: grep de la bandera/valor viejo (`Caja.Bodega_Factura`, `Caja.Suc_Id`) en todo el proyecto, no solo en el archivo del diff (sugeridos, lotes, datamatrix, BuscarArticulo, favoritos).
4. Estado de documento que no se persiste: factura en espera (XML/JSON) no guarda TipoPreventa; recuperar pierde el destino.
5. Formularios gemelos (Frm_Facturacion_Autonoma) con copia del mismo método: arreglos de reentrada o reglas se parchean en uno solo.
6. Pruebas unitarias con oráculo que repite la fórmula de la función (describen). Y fixes de dos temas en una sola rama.

**Why:** hallazgos de la revisión de preventa-sucursal-destino (2026-10-24), donde 839 pruebas verdes no cubrían R1/R2.
**How to apply:** empezar la revisión con estos 6 grep/lecturas antes de leer el diff línea por línea.

Nota operativa: el hook de este agente bloquea Write fuera de la memoria y algunos Bash (awk/pipes/git fetch); usar Grep/Read y devolver el informe por SubagentHandback.
