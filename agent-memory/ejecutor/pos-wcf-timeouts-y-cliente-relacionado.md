---
name: pos-wcf-timeouts-y-cliente-relacionado
description: POS Dos Pinos (LDCOM13): el timeout de las llamadas WCF sale de codigo y parametros, no del App.config; Cliente_Relacionado no siempre es una finca
metadata:
  type: reference
---

- En el POS (INTERFACE\FACTURACION) `TCatalogoOnLine` crea su propio BasicHttpBinding en el constructor y lo asigna a todos los clientes WCF; el binding del App.config (sendTimeout 01:30:00) nunca se usa. El timeout de cada llamada lo fija `WebServ_TimeOutTime(Minimum/Medium/Maximum)` con `WS_Timeout_min/med/max` de Parametros Generales (10 s si min = 0).
- `Facturacion.Cliente_Relacionado` puede ser la finca (Tipo_Comportamiento = Pertenece_Otro_Cliente) o el corporativo padre de un distribuidor hijo. Para "finca" filtrar por Tipo_Comportamiento.
- Los archivos nuevos escritos con Write quedan en LF; el repo es CRLF: convertir con sed 's/$/\r/' y verificar con `file`. Un docstring `'''` dentro de un heredoc python con `'''` rompe: usar Write a un archivo temporal y empalmar.
- Reference.vb del POS (WCF) se edita a mano en este repo (commits b0a2cd45 y 2222), solo ese archivo.
