# revisar

Conocimiento de `rig revisar` (revision de ramas de LDCOM13_DOS_PINOS). El codigo vive en rig
(`comandos\revisar.ps1`, `revision\chequeos.ps1`, `revision\plantilla-reporte.html`); aqui solo lo que se sabe.

| Archivo | Que es |
|---|---|
| `revisor-ldcom.md` | Prompt del agente `revisor-ldcom`. `rig revisar` lo instala en `~/.claude/agents/`. |
| `reglas-vigentes.md` | Reglas R01-R22 con severidad y evidencia. R16-R20 las aplica el chequeo automatico. |
| `modulo-pv.md`, `modulo-negocio.md`, `modulo-admin.md`, `modulo-bd.md` | Enfoque y reglas que pesan en cada modulo. |
| `mapa-riesgo-facturacion.md` | Puntos de riesgo de facturacion; lo piden los archivos de modulo. |
| `casos-historicos.md` | Casos reales y como los detecto (o no) el revisor. |
| `propuestas-mejora.md` | Patrones viejos: solo generan PROPUESTA, nunca bloquean. |

Todo cambia por PR. Despues de mergear, `rig revisar` reinstala el agente solo la proxima vez que corre.
