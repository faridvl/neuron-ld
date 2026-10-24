# Calibracion de estimados

Leer antes de dar un numero. Al cerrar cada caso, agregar su fila a la tabla del final.

## El sesgo y como se corrige

En los primeros casos el usuario recorto sistematicamente 40-50% de lo propuesto, y hasta 70-80% cuando
ademas acoto el alcance. Desde que se aplican estas reglas, la mayoria de los estimados se aceptan sin
correccion (ver tabla). Las formas concretas en que se infla:

1. **Pasos de "diseño", "confirmar" o "preparacion" como renglones propios** cuando el diagnostico ya
   esta claro. Van dentro del bloque de implementacion.
2. **Tiempo por casos borde hipoteticos** sin evidencia de que ocurran en el flujo real del cliente.
3. **Actividades triviales a esa escala como renglon aparte** (ej. insertar 40 filas en un catalogo).
4. **Multiplicar pruebas por cada punto** cuando varios viven en el mismo archivo/bloque: se prueban
   juntos (caso 2232).
5. **Agregar un segundo verbo.** Si el fix ya existe, el trabajo es *confirmar*, no "confirmar y
   portar/desplegar": portar es una decision de release, fuera de este analisis (caso 2156).
6. **Estimar "todo lo que encontre"** en un ticket con varios escenarios, en vez de dejar que el
   usuario acote el alcance primero (caso 2155).

Lo que si mueve el numero: cuantos archivos/copias hay que tocar, si toca SQL/reportes ademas de la
UI, el volumen real de datos, y la superficie de prueba del flujo tocado. El tipo de bug en si mueve
poco. Un precedente del mismo fix en el repo baja el estimado: prueba que no hay incognitas de diseño.

## Referencias calibradas

| Trabajo | Horas |
|---|---|
| Bug de una condicion puntual, un archivo, sin duplicacion | 1-1.5 |
| Bug aplicando un patron que ya existe en 3+ lugares del repo | 1.5-2.5 |
| Mensaje/validacion visible en una rama ya existente (duplicada en 2 formularios) | 1.5-2 |
| Bug quirurgico duplicado en 2 formularios, con pruebas manuales | ~3 |
| Bug en el flujo central (ej. escaneo) con superficie de prueba amplia | 3-4 |
| Varios hallazgos en un mismo reporte/archivo | ~3 por reporte |
| Confirmar un fix que ya existe en otra rama | ~1 |
| Reponer un objeto perdido con una migracion nueva | ~1 |
| Carga de 4 Excel chicos (14-65 filas) en 3 ambientes, con Docker | ~3.5 |
| Remediacion de datos ~16k filas, una tabla plana, adaptando script existente | 2-3 |
| Solo cambiar un texto de mensaje | 0.5-1 |

Desglose tipico de carga de datos: Docker una vez (~15-20 min), cargar cada Excel (~20 min), validar
cada uno en el Docker que simula Staging (~30 min); Staging RC/UAT solo corren el script validado.

## Historial de casos

| Fecha | Ticket | Tipo | Propuesto | Aceptado | Leccion |
|---|---|---|---|---|---|
<!-- Si el bug no tiene commit de regresion identificable (ver tipo-bug.md), poner en la Leccion:
     "**Es un bug que viene de estandar.**" seguido del resto de la leccion. -->

| sep-2026 | 2051 | bug (2 formularios) | 5-6.5h | 3h | Diseño y casos borde separados inflaron |
| sep-2026 | 2036 | carga de datos | 7.5-11.5h | 3.5h | Relaciones triviales como renglon aparte |
| sep-2026 | 2000 | bug (1 linea) | 1-1.5h | 1-1.5h | Confirma la referencia de bug puntual |
| sep-2026 | 1739 | despliegue | 1h | 1h | Nota tecnica afirmaba algo no verificado |
| sep-2026 | 2155 | bug (2 escenarios) | 2.5-3.5h | 0.5-1h | Uno no era bug; el otro solo el mensaje |
| sep-2026 | 2156 | mixto (4 escenarios) | 2-3h | 1h | Fix ya existia en otra rama: confirmar |
| 2026-09-22 | 2232 | bug (reportes, 6 puntos) | 6-9h | 6h | Puntos del mismo bloque se prueban juntos |
| sep-2026 | 2233 | bug (patron existente) | 1.5-2.5h | 2h | Precedente en el repo = estimado bajo |
| 2026-09-25 | 2235 | alcance nuevo (con precedente) | 6-8.5h | 6h | Decision posterior revirtio rechazo previo del mismo ticket (Johnny/Hans citando acuerdo, sobre mi propio rechazo del dia anterior); precedente completo en Descuentos bajo el estimado; usuario recorto capas ya cubiertas por copia directa (SQL, TBonificacionVenta.vb, vista) y excluyo el ticket de la regla de capacidad por fecha ya prometida |
| sep-2026 | 2240 | carga de datos (parecia bug) | 2-3h | 2.5h | La base ya tenia el dato cruzado |
| 2026-09-23 | 2242 | bug | 1.5-2h | 2h | Fix propio del dia anterior cubria la mitad |
| 2026-09-24 | 2244 | bug (flujo central) | 3-4h | 3.5h | Causa mas amplia que el ticket; se documento acotado |
| 2026-09-24 | 1975 | bug (flujo central, PV/Preventa) | 3-4h | 2h | Precedente exacto en el mismo metodo (Verificar_Cambio_Bonificaciones) bajo la implementacion a ~1h; el usuario acoto ademas las pruebas de desarrollo a solo PV (Preventa y regresion de escaneo/cantidad/precio quedan para QA) y pidio no dejar esa razon por escrito en el comentario de negocio |
| 2026-09-24 | 2245 | bug (eliminar validacion, multi-capa) | 4.5-6h | 1.5h | Reverso exacto de commits propios conocidos (#1767) con desglose archivo:linea ya hecho en otro ticket (#2060): "eliminar" en ubicaciones ya identificadas cuesta una fraccion de "agregar". Usuario recorto en 3 pasos (2h en pruebas -> 0.5h; dev 2.5-3.5h -> 1h) hasta 0.5h por actividad. Duplicado con #2060 (Sprint 21, sin asignar): se linkeo Related y el estimado/nota tecnica quedaron en el caso CRM (#2245), con aviso corto en #2060 |
| 2026-09-25 | 2261 | bug (reportes, filtro multi-seleccion) | 1-1.5h -> 1h | 1h | **Es un bug que viene de estandar.** Diagnostico inicial (agente investigador) apuntaba a arreglar TValue.ValueMSSQL (clase compartida por todo el motor de reportes, ~1.5-2.5h con smoke test amplio); el usuario pregunto por que no se habia visto antes en otros reportes, lo que llevo a encontrar el precedente real: TConjuntoString (misma clase Data.vb) ya es el patron usado en TRepFact_VentasXCombo.vb para los mismos filtros multi-seleccion, y no tiene el bug. El fix se acoto a copiar ese patron en 3 lineas de un solo archivo en vez de tocar la clase compartida. Leccion: cuando el diagnostico inicial apunta a una clase base/compartida, buscar activamente un reporte/formulario hermano que resuelva el mismo tipo de filtro sin el sintoma antes de estimar sobre arreglar la clase base — un precedente que evita tocar codigo compartido baja el estimado y el riesgo mucho mas que "arreglar la raiz" |

| 2026-09-25 | 2276 | bug de estandar (flujo central, PV/Facturacion) | 3-4h | 2h | **Es un bug que viene de estandar.** Precedente exacto: rutina de revalidacion de bonificaciones ya existe (Verificar_Cambio_Condiciones_Bonificaciones_Precio) pero solo cableada al boton "Cambiar Precio", nunca a la carga de preventa en Facturacion; encontrar el precedente reusable bajo el dev a 2-2.5h. El usuario recorto ademas las pruebas manuales (1-1.5h -> 0.5-1h): son variaciones del mismo flujo de carga en una sola sesion POS, no se multiplican por escenario (mismo principio que 2232). Habia una US interna (#513) activa por "Acceptance tests fail" cubriendo el mismo punto, asignada a otro dev; el usuario pidio ignorar esa duplicacion y estimar 2276 igual, dejando pendiente en la nota tecnica activar los casos de prueba CP-BON-028 una vez exista el fix |
| 2026-09-25 | 2277 | bug de estandar (condicion puntual, PV/Facturacion) | 1.5-2.5h | 1h | **Es un bug que viene de estandar.** Causa raiz de una sola linea (If Not Es_Preventa envolviendo el chequeo de existencia en Agregar_Articulo_Bonificado, Frm_Facturacion.vb:5467): encaja exacto en la categoria calibrada "condicion puntual, un archivo, sin duplicacion" (1-1.5h), pero propuse con buffer extra por una duda sin cerrar (ExistenciasNegativas() en el guardado deberia atrapar el caso igual y el ticket dice que no bloquea; no se pudo confirmar en runtime) y por sumar la regresion de Proforma como paso aparte. El usuario corto directo al piso de la categoria calibrada: la duda de runtime y las regresiones se verifican en la misma sesion de pruebas, no son horas extra. Mismo par Preventa/Facturacion de bonificaciones que el 2276 (un dia antes), con la misma US #513 de fondo — se repite el criterio de estimar igual e ignorar el solape, dejando pendiente activar CP-BON-022 (#1131) |
| 2026-09-25 | 2293 | mixto (3 escenarios: 2 rechazados, 1 alcance nuevo con precedente) | 6-8.5h | 6h | Mismo caso CRM (CAS-77523-B0R8) que #2156, creado 4 dias despues repitiendo 2 de los mismos 3 puntos que yo ya habia resuelto ahi (cifras de control y dias de semana) — cruzar el CAS antes de investigar desde cero ahorra la mitad del trabajo. Cifras de control: confirme por segunda vez (grep amplio) que no existe en ningun lado, ya decidido como mejora aparte en #2156. Fechas de vigencia: el usuario dudo de mi conclusion inicial ("¿ya lo permite? me parece que no") y verificar directo en codigo (no solo el resumen del subagente) encontro validacion de negocio real (TCargaXTabla.vb:3219 Validar_EncabezadoCombo) que confirmaba que si existia — la duda del usuario fue la señal correcta de volver a verificar antes de publicar. Dias de semana: yo mismo lo habia rechazado como "gestionado en control de cambios" citando la misma razon que use en #2235 un dia antes — el usuario me corrigio con "mismo tema que el 2235 entonces", aplicando la decision posterior (Johnny/Hans, "se vera como un caso") que ya habia revertido esa razon de rechazo para Bonificaciones: una decision vigente sobre un tema cubre pedidos futuros con la misma razon de rechazo, no solo el ticket donde se dijo. Usuario corto 6-8.5h a 6h citando directamente el numero de #2235 (mismo precedente, sin desglosar). Explorando "cifras de control" a fondo aparecio una mejora de plataforma mucho mas grande (motor generico de carga masiva, ~75 sitios con Throw, 11 funciones candidatas reales) que el usuario decidio NO convertir en ticket — se documento en `handoff-carga-masiva-cifras-control.md` fuera de ADO para retomar algun dia. Leccion: cuando el usuario cuestiona una conclusion ya publicada en el chat, revalidar con evidencia de codigo directa antes de insistir — el subagente se habia equivocado en confiar en la configuracion sin la validacion de negocio real. |

Formato de fila nueva: fecha ISO, ticket, tipo, rango propuesto, lo aceptado (o "—" si no se estimo) y
la leccion en una linea. Si el usuario corrigio el enfoque y no solo el numero, la leccion es eso.
