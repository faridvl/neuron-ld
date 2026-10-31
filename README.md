# neuron-ld

Lo que el equipo de LD sabe de LDCOM y de cada cliente. La usan `rig` (perfiles de cliente) y Claude
(reglas, fichas, agentes, skills, a través del motor `claude-brain`). No guarda contraseñas ni datos personales.

```
neuron-ld/
├── reglas.md                    reglas del equipo (Claude las carga en las sesiones y agentes de los proyectos de LD)
├── clientes/<cliente>/rig.json  perfil del cliente para rig: carpeta, repos, slots, ambientes, IIS, reportes
├── proyectos/<repo>.md          ficha: qué es, ramas, comandos, riesgos, dónde viven sus reglas
├── aprendizajes/                "así resolvimos X", útil en más de un caso
├── agents/                      agentes de LDCOM para Claude
├── agent-memory/                lo que aprenden los agentes
└── skills/                      skills de LD (rig, migraciones, estimar casos, ...)
```

## Cómo se usa

- Con rig: `rig setup` la ubica o la clona; `rig init` lee `clientes/<cliente>/rig.json`.
- Con Claude: `claude-brain\install.ps1 -RaizProyectos "C:\FUENTES" -Cerebros "<ruta de neuron-ld>"`.

## Cómo se cambia

Igual que el código: rama, cambio y PR. Un perfil de cliente nuevo o un servidor que cambia se sube una vez y
todo el equipo lo recibe al actualizar su copia (`git pull` en neuron-ld).
