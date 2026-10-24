# Módulo Admin (Site Admin, ASP.NET MVC + JS)

Archivos: `INTERFACE/ADMIN_LDCOM/**` (`Controllers/*.cs`, `Models/*.cs`, `Views/**/*.cshtml`,
`Shared/js/src/**`). El JS fuente se empaqueta con `npm run build` (gulp); el paquete generado no se
revisa.

## Qué leer

- `reglas-vigentes.md` (R01, R03, R04, R10, R12, R22 son las que aplican aquí).
- Del equipo: `.claude/rules/10-estilo-codigo.md` (nombres, comentarios).

## Estructura de una pantalla

`Views/<Pantalla>/Index.cshtml` (HTML con ids) → `Shared/js/src/view/<pantalla>View.js` (tablas
bootstrap, `columns: [{ field: ... }]`) → `Shared/js/src/controller/<pantalla>Controller.js` (eventos
`jq.on`, llamadas al servidor, `this.regX` con el registro) → `Controllers/<Pantalla>Controller.cs` →
`Models/<Pantalla>Model.cs` (arma el modelo desde un `TReg*` o un `DataSet` de `NEGOCIO`).

## Cómo revisar

1. **Contrato entre capas (R22), de punta a punta.** Por cada campo nuevo que se muestra:
   columna de la consulta en `NEGOCIO` → `row["X"]` o propiedad del `TReg` en el modelo `.cs` → nombre de
   la propiedad del modelo → `field:` de la tabla o `this.regX.Propiedad` en el JS → `id` en el
   `.cshtml`. Un nombre distinto en cualquier eslabón deja la columna vacía sin error. Verificar con
   `Grep` cada eslabón.
2. **Números en JS**: todo valor que viene del servidor pasa por `parseFloat(x) || 0` antes de sumar; si
   no, `"10" + 5` concatena. Decimales: la pantalla suele tener un parámetro (`NumDecimales`,
   `ValorNDecimales`); un `toFixed(2)` nuevo junto a una pantalla que usa el parámetro es `[ERROR]` R01.
3. **Eventos**: un `jq.on(...)` agregado o borrado cambia cuándo se guarda. Si se borra un handler que
   guardaba (`blur`, `change`), confirmar que el guardado quedó en el botón y que no se pierde lo
   escrito. Si se agrega, confirmar que no se registra dos veces (dentro de una función que se llama
   varias veces).
4. **Mensajes al usuario (R04)**: en español, mismo estilo que los vecinos (`alertSuccessMessage`,
   `alertErrorMessage`), un mensaje por acción, nunca el texto crudo de una excepción.
5. **C#**: `double.Parse(row["X"].ToString())` sin control falla si la columna viene vacía o `DBNull`;
   preferir el patrón del archivo vecino. Controladores: un método nuevo que modifica datos valida
   permisos igual que sus vecinos.
6. **cshtml**: textos visibles con el estándar de mayúsculas de la pantalla; ids únicos.
7. No revisar estándar automático (R03 nombres, R20 depuración, R04 guiones): ya viene del chequeo. Solo
   confirmar o descartar los candidatos que te pasan (`decimales-quemados`, `texto-magico`, ...).
