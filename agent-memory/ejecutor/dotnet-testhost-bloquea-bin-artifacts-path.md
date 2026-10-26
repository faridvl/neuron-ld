---
name: dotnet-testhost-bloquea-bin-artifacts-path
description: Si un testhost colgado (de otra sesion/agente) bloquea bin\ de Integration.Tests, compilar y probar con --artifacts-path en vez de matar procesos ajenos.
metadata:
  type: feedback
---

Con varios agentes en paralelo sobre el mismo repo .NET, un `testhost` viejo bloquea las DLL de `Integration.Tests\bin` (MSB3027/MSB3021) y `dotnet build` de la solucion falla solo en la copia, no en el codigo.

**Why:** no es mi proceso; matarlo puede cortar la corrida de otro agente.
**How to apply:** `dotnet restore <sln> --artifacts-path <scratchpad>\art --configfile <nuget.local.config>` y luego `dotnet build/test ... --artifacts-path <scratchpad>\art --no-restore`. Verificar con `Get-Process testhost*` si de verdad esta colgado (CPU quieta).

Trampa menor: un heredoc de bash con `cat > archivo <<'EOF'` que lleve apostrofes largos puede abortar con "unexpected EOF"; para archivos grandes usar la herramienta Write. Para editar archivos con CRLF/BOM mezclados usar un script python con newline='' (ver [[feedback_windows_line_endings_python]]).
