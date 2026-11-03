# El Runner de Integration.SDK cifra por defecto y el Docker usa certificado propio

Cuándo: una llamada que pasa por Integration.SDK (validación de crédito SFA, MDS) cae a "Error técnico inesperado" y no deja filas en
`CreditValidationAttempt` ni en `Events`, mientras el resto del sistema conecta bien a la misma base.

## Qué pasa
- `Integration.Runner.exe` abre la cadena con Microsoft.Data.SqlClient, que cifra por defecto y rechaza certificados no confiables.
  NEGOCIO usa System.Data.SqlClient y no lo nota.
- El SQL del Docker usa un certificado propio. La auditoría `Started` falla cerrada, por eso no queda ni una fila.
- Reconocerlo: `sqlcmd -N` sin `-C` falla con "La cadena de certificación fue emitida por una entidad en la que no se confía".

## Solución
Agregar `TrustServerCertificate=True` solo a la copia de la cadena que va al SDK (`TCatalogo.IntegrationConnectionString`), en código y no en
el `Web.config`, que pisan el deploy y `rig ambiente`. `Encrypt=False` no hace falta.
