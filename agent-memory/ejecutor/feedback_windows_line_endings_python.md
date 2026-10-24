---
name: windows-line-endings-python
description: En Windows, reescribir un archivo con python open() cambia LF a CRLF; usar newline='' o Edit/Write
metadata:
  type: feedback
---

Al editar archivos del repo C# con un script de python en Windows, `open(p,'w')` convierte `\n` en `\r\n` y deja un diff enorme. Los archivos de `LDCOM13_INTEGRATIONS-colas` son LF (algunos con BOM, ClientDto.cs es CRLF + BOM).

**Why:** pasó al tocar ItemQueueRecordMapper.cs; hubo que revertir con `sed -i 's/\r$//'`.
**How to apply:** preferir Edit/Write; si hay que usar python, `open(..., newline='')` en lectura y escritura, y verificar con `file <ruta>` antes y después. Además, heredocs bash con `<<'E'` que contengan comillas triples mezcladas fallan: escribir con Write.
