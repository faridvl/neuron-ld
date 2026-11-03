# Acentos dañados entre un sitio IIS y un proceso hijo por stdin

## Cómo se reconoce

- Un sitio .NET Framework bajo IIS lanza un ejecutable (`Process.Start`, `RedirectStandardInput`, `CreateNoWindow = true`)
  y le pasa texto por stdin.
- En el servidor salen `φ ≤ Θ` donde iban `í ó é` (OEM 437), o `¾` en una PC con OEM 850. En la base el dato está bien
  (`varchar` cp1252 con `ED/F3/E9`).
- En la PC del desarrollador con IIS Express (que sí tiene consola) todo sale bien.

## Por qué pasa

- El padre en w3wp no tiene consola: `GetConsoleCP()` da 0 y .NET Framework escribe el stdin del hijo en ANSI (1252).
- El hijo con `CREATE_NO_WINDOW` recibe una consola oculta con el código OEM del equipo (437/850) y `Console.In`
  decodifica con ese: `0xF3` (ó en 1252) se lee como `≤`.
- La salida suele estar bien si el hijo responde JSON con `System.Text.Json` (escapa todo lo no ASCII).

## Cómo se resolvió (LDCOM13_INTEGRATIONS, Admin → Integration.Runner)

- El padre serializa el comando con Newtonsoft `StringEscapeHandling.EscapeNonAscii`: el stdin viaja en ASCII puro y
  deja de importar el código de página de cada lado. No hubo que tocar el hijo.
- `ProcessStartInfo.StandardInputEncoding` no sirve en net462 (no existe ahí).

## Cómo reproducirlo sin el servidor

- Lanzar IIS Express desacoplado (sin consola), igual que w3wp:
  `Invoke-CimMethod Win32_Process Create` con `Win32_ProcessStartup.CreateFlags = 8` (`DETACHED_PROCESS`).
- O emular el padre en PowerShell 5.1 (.NET Framework) con `FreeConsole()` antes de `Process.Start` y un hijo net8 que
  imprima los `U+XXXX` que recibió.
- Probar con `chcp`/OEM 437 no basta: el problema es que padre e hijo usen tablas distintas.
