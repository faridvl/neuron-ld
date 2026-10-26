---
name: fallas-frecuentes-revision
description: Tipos de falla que conviene buscar primero al cuestionar un cambio (defaults de servidor, banderas duplicadas, rutas hermanas sin parchear, estado que no se persiste)
metadata:
  type: feedback
---

Buscar primero, en cambios de reglas de negocio en POS/WCF (LDCOM VB.NET):

1. Defaults de servidor que parecen "dato leído": `TParametrosSucursal.Load` devuelve True con 0 filas y precarga defaults (Facturacion_Negativa=True, Bodega=1). Un cliente que usa `Nothing` como "sin dato" no ve ese caso. Comparar con cómo el servidor trata "sin fila" en otros sitios (p. ej. TPreventa.DebeComprometerExistencia).
2. Dos banderas con el mismo rótulo (caja vs sucursal): confirmar cuál leía el POS antes; la que "nunca se usó" puede tener valores sin revisar.
3. Rutas hermanas sin parchear: grep de la bandera/valor viejo (`Caja.Bodega_Factura`, `Caja.Suc_Id`) en todo el proyecto, no solo en el archivo del diff (sugeridos, lotes, datamatrix, BuscarArticulo, favoritos).
4. Estado de documento que no se persiste: factura en espera (XML/JSON) no guarda TipoPreventa; recuperar pierde el destino.
5. Formularios gemelos (Frm_Facturacion_Autonoma) con copia del mismo método: arreglos de reentrada o reglas se parchean en uno solo.
6. Pruebas unitarias con oráculo que repite la fórmula de la función (describen). Y fixes de dos temas en una sola rama.

7. Colas/consumos destructivos (integraciones): todo lo que se lee o valida DESPUÉS de consumir (config faltante lanzada desde un mapper, catálogo sin default, lectura de grupos/status/parámetros) pierde la publicación. Buscar `throw` dentro de `Map()` y lecturas previas dentro del `await foreach`; el arreglo es un chequeo previo antes del primer consumo.
8. SQL por conjunto con tablas temporales (#T): faltan `COLLATE DATABASE_DEFAULT` en columnas texto (solo falla si tempdb y la BD difieren; en Docker nunca falla). Comparar un archivo con otro del mismo cambio (uno lo trae, otro no).
9. "Arreglado" en ESTADO vs re-prueba posterior: comparar fecha de modificación del archivo y del paquete contra la hora del informe de E2E; leer el SET del UPDATE (una autoasignación de columna con FK vuelve a validar la FK).
10. Rutas manuales/override que conservan la lógica vieja (CrossReference, update completo) al lado del camino nuevo; grep de los `*Override` y quién los llama.
11. Pruebas que no prueban la regla: mutaciones solo sobre la capa con mocks mientras la regla vive en SQL de otro repo sin pruebas en CI; E2E con configuración inyectada solo en la copia probada.
12. Resultados "con observaciones" que el planificador ve como éxito (todo rechazado = verde); errores de datos que en una interfaz suman a Errors y en otra no (inconsistencia entre decisiones).

13. Cola destructiva + parseo ESTRICTO antes de guardar el id de reconsumo: si el sobre trae un tipo distinto (id numérico, data no lista) la publicación ya está consumida y no queda fila de bitácora para RECONSUME. Probar siempre sobres con tipos cambiados, no solo registros raros.
14. Recuperación/reproceso automático vs. cadena de reintentos: ¿qué transacciones excluye ("esperando su reintento") y en qué orden corre respecto a la corrida normal? Reproducible matando la conexión SQL a mitad de escritura: el dato viejo termina sobre el nuevo.
15. Planificador en serie + timeouts sin límite (CommandTimeout=0 en la capa de datos) = un candado de BD congela TODOS los eventos; con 2 nodos, la foto del evento (LastRunAt) tomada al inicio del tick provoca doble corrida de la misma ocurrencia.
16. Un error por registro clasificado como fallo de corrida (IsSuccess = Errors == 0) dispara reintentos que no pueden reintentar nada (la publicación ya se marcó aplicada) y el último intento sale verde ("cola vacía").
17. Higiene del sandbox: las colas del simulador son compartidas; cualquier corrida (y el job con horario por minuto) consume lo pendiente de otros. Reservar/aparcar antes de correr. Los scripts de restauración (.bak) quedan viejos cuando una migración nueva agrega columnas: verificar la fecha del .bak contra la última migración.
18. Secretos: buscar claves con LIKE por columnas dinámicas (sin imprimirlas) en la IntegrationDB; un "corregido" de credenciales puede dejar el usuario real en ChangeLog/.bak.

**Why:** hallazgos de la revisión de preventa-sucursal-destino (2026-10-24), donde 839 pruebas verdes no cubrían R1/R2. Los puntos 7-12 salieron de la revisión del núcleo de datos maestros CIH->LDCOM (2026-10-24); los 13-18 de los ataques reales al E2E con simulador (2026-10-26).
**How to apply:** empezar la revisión con estos 6 grep/lecturas antes de leer el diff línea por línea.

Nota operativa: el hook de este agente bloquea Write fuera de la memoria y algunos Bash (awk/pipes/git fetch); usar Grep/Read y devolver el informe por SubagentHandback.
