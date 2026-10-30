---
name: sheetjs-ce-no-estilos-xlsx-propio
description: El xlsx.core.min.js (SheetJS CE) del Admin LDCOM no escribe negrita ni fila congelada; para Excel con formato se escribe el .xlsx a mano y se valida con openpyxl.
metadata:
  type: reference
---

El exportador de tablas del Admin (tableExport + SheetJS CE) no escribe estilos ni paneles congelados, y convierte fechas en texto. Para encabezado en negrita, fila congelada, autofiltro, anchos y fechas reales se armo `Shared/js/src/util/xlsxMinimo.js` (ZIP sin compresion + XML), probado en node y validado cargandolo con `python -I` + openpyxl (disponible en esta PC).

**Why:** el Excel del Monitor de eventos salia con columnas desalineadas, fechas texto y sin formato.
**How to apply:** si piden formato real en otro Excel del Admin, reutilizar xlsxMinimo.js en vez de tableExport. Ojo: al buscar la clave de conexion en Web.config usar grep sin eco (la clave `password=` va en minuscula y se imprimio por error una vez).
