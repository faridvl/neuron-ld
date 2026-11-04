---
name: wcf-caja-pruebas-trampas
description: Trampas al probar WCF de caja contra Docker (token, App.config.example, artifacts-path, SP sin Tipo_Id)
metadata:
  type: feedback
---

- Sin login: sembrar token en Seg_Conexiones del Docker y ponerlo en App.config (gitignored).
- App.config.example trae `--` en un comentario (XML invalido); corregir solo en el App.config local.
- `--artifacts-path` nuevo exige build con restore la primera vez.
- Otro agente comparte `_q.sql`: usar archivo propio para consultas.
- Mov_Caja_Entrada_Salida_Aplicar_Anular no filtra por Tipo_Id: anular 3/5 anula tambien 9/5 (Mov_Id se repite por tipo).
- Archivos .vb/.cs del repo van CRLF; el Write los deja LF: convertir con sed antes de commitear.
