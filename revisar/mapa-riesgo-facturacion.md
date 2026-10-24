# Mapa de riesgo: facturación del POS

Zonas frágiles de `INTERFACE/FACTURACION/Facturacion/Frm_Facturacion.vb` (~17.5k líneas) y lo que la
rodea. El revisor carga este archivo **solo si el diff toca facturación** (`INTERFACE/FACTURACION/**`,
`NEGOCIO/FACTURACION/**`, `NEGOCIO/CATALOGOS/TBonificacionVenta.vb`, `TCombo.vb`, `TCliente.vb`).

Los métodos se citan por nombre: los números de línea cambian con cada commit. Para ubicarlos:
`grep -n "Sub Cambiar_Tipo_Documento" Frm_Facturacion.vb`.

## Por qué este archivo

Commits `fix(...)` por archivo en todo el repo (VB/SQL):

```
71  INTERFACE/FACTURACION/Facturacion/Frm_Facturacion.vb
51  NEGOCIO/CONTROL NEGOCIO/TCatalogo.vb
49  NEGOCIO/CATALOGOS/TCargaXTabla.vb
30  INTERFACE/FACTURACION/FacturacionLOCAL/TFacturacionLocal.vb
23  NEGOCIO/CATALOGOS/TBonificacionVenta.vb
18  INTERFACE/FACTURACION/FacturacionOBJ/TFacturacion.vb
17  NEGOCIO/FACTURACION/TFacturaLinea.vb
16  NEGOCIO/FACTURACION/TPreventa.vb
16  INTERFACE/FACTURACION/FacturacionLOCAL/TDatosServerToLocal.vb
13  INTERFACE/FACTURACION/FacturacionPrint/TPrintFactura.vb
```

Métodos de `Frm_Facturacion.vb` tocados por más commits de fix distintos:

```
13  Cambiar_Tipo_Documento          4  Cambiar_Cliente_Preventa
 9  Cambiar_Cliente                 3  Registrar_Bonificaciones
 5  Refrescar_Datos_Lista           3  Modificar_Cantidad
 5  Imprimir_Documento              3  Descuento_Global_Documento
 5  Evento_Enter_Articulo           3  Cargar_Preventa / Modificar_Preventa
 5  Agregar_Articulo_Linea          3  Agregar_Articulo / _Light / _Con_Bonificaciones
 4  Cargar_Documento                3  Cambiar_Precio
 4  Cambio_Cliente                  2  Verificar_Cambio_Bonificaciones
```

## Familias (métodos hermanos)

Si el diff cambia un miembro de una familia, el revisor revisa **todos** los demás (regla R05). Estas
familias explican la mayoría de las devoluciones de QA ("se arregló en un flujo y en el otro no").

| Familia | Miembros | Qué se suele olvidar |
|---|---|---|
| Cambio de cliente | `Cambio_Cliente`, `Cambiar_Cliente`, `Cambiar_Cliente_Preventa` | el camino de preventa; factura en espera (`pEsFacturaEspera`) |
| Agregar artículo | `Evento_Enter_Articulo` → `Agregar_Articulo`, `Agregar_Articulo_Light`, `Agregar_Articulo_Con_Bonificaciones`, `Agregar_Articulo_Linea` | escaneo vs favorito vs búsqueda; artículo suelto vs combo |
| Cantidad y bonificaciones | `Modificar_Cantidad` (2 sobrecargas), `Verificar_Cambio_Bonificaciones`, `Registrar_Bonificaciones`, `Eliminar_Articulos_Bonificados`, `Eliminar_Articulo` | la otra sobrecarga; líneas de combo con el mismo `Art_id` |
| Cargar documento | `Cargar_Documento` (factura en espera), `Cargar_Preventa` (2 sobrecargas), `Modificar_Preventa` (2 sobrecargas) | que la preventa revalide condiciones vigentes (2276) |
| Impresión | `Imprimir_Documento`, `Imprimir_Documento_Preventa`, `Imprimir_Tiket_Factura_Local`, `Imprimir_Proforma`, `Imprimir_Preventa`; `FacturacionPrint/TPrintFactura.vb`; `Frm_Reimpresion_Documentos.vb`, `Frm_Reimpresion_Documentos_Preventa.vb` | local, contingencia, reimpresión, contado vs crédito, tiquete vs factura electrónica (1495, 1532, 1655) |
| Formulario completo | `Frm_Facturacion.vb` y `Frm_Facturacion_Autonoma.vb` (comparten 203 métodos con el mismo nombre, incluidos todos los de arriba) | ver nota abajo |

**Nota sobre `Frm_Facturacion_Autonoma.vb`:** se abre cuando el `.LD` de la caja trae
`Facturacion_Autonoma = SI` (`Program_Inicio.vb`, `CLSArchivoLD.vb`). De 55 commits a
`Frm_Facturacion.vb`, solo 4 tocaron también la Autónoma. En Staging (réplica de lo que tiene el
cliente) hay 0 filas en `Caja_Autonoma`; en Testing hay 6. Por eso: si el diff toca un método
compartido, el revisor lo **menciona** ("¿aplica también a la Autónoma?") como `[RIESGO]` bajo, sin
bloquear.

## Invariantes de la factura

Lo que siempre debe cumplirse después de **cualquier** evento (agregar, cambiar cantidad, cambiar
cliente, cambiar tipo de documento, cargar preventa o factura en espera, eliminar). Si el diff toca uno
de esos manejadores, el revisor verifica cada invariante afectada y propone el escenario de prueba.

```
I1  La cantidad de cada línea se conserva al cambiar cliente o tipo de documento
    (no se duplica, no se pierde, no pide cantidad de nuevo)        -> 1529, 2244
I2  El total del documento = suma de las líneas; se recalcula después de
    cualquier cambio de cantidad o precio (Refrescar_Datos_Lista)   -> 1602
I3  Una línea de combo y una línea suelta del mismo artículo no comparten
    estado de bonificación: comparar por Art_id Y Combo_Id           -> 2244
I4  Al cambiar de cliente, las bonificaciones y combos se recalculan para
    el nuevo cliente, sin borrar las de otras líneas                 -> 1898, 1975, 1797
I5  El cliente que se factura es el que eligió el cajero (finca No REA
    factura al asociado; ver modelo de clientes)                    -> 2263, 2145
I6  La preventa cargada en facturación revalida condiciones vigentes
    (bonificaciones, existencias, categoría del tipo de preventa)    -> 2276, 2277, 2287
I7  Lo que se imprime coincide con lo facturado (cliente, impuestos,
    tarifa reducida), en línea y en local, en factura y reimpresión  -> 1495, 1530, 530
I8  El monto de una devolución usa el mismo redondeo que la factura
    original                                                          -> 1603
```

## Capa de catálogo del POS: tres caminos

`INTERFACE/FACTURACION/FacturacionOBJ/TCatalogo.vb` (241 métodos) decide por dónde va cada consulta:

```
Si _EstadoConexion.Es_Preventa         -> WCF (TCatalogoOnLine); en error: Return Nothing (sin log)
Si no, y Not _EstadoConexion.Forma_Local -> WCF; en error: Save_Msg, Online = False y cae a
                                           TCatalogoLocal (BD local)
Si _EstadoConexion.Forma_Local          -> TCatalogoLocal directo
```

- 84 de 241 métodos solo tienen camino en línea. Muchos son legítimos (monedero, integraciones), pero
  un método **nuevo** sin camino local debe justificar qué pasa sin conexión (R06).
- El camino de preventa traga la excepción y devuelve `Nothing`: el llamador debe verificarlo (R10).

**Servidor** (`NEGOCIO/CONTROL NEGOCIO/TCatalogo.vb`, 2,336 métodos): patrón
`Validar_Conexion` → `TXxx(_Transaccion.Conexion)` → `.Col.*` → `.Lista/.Consultar` → en error
`GenereDSError(msg)`, que devuelve un DataSet con tabla `"Errores"` y columna `"MensajeError"`;
`Finally` cierra la conexión. El cliente detecta el error con `Tables(0).TableName = "Errores"`. Un
método nuevo que devuelva error con otra forma (otra tabla u otra columna) no lo detecta el POS.
Excepción conocida: `TCatalogoHacienda.ConsultarMAG` usa otro cliente con su propio formato
(`"Error"`/`"Mensaje"`); no es el mismo contrato.

## BD local del POS (qué acompaña a un cambio de datos)

```
FacturacionLOCAL/BDLocal.dbml (+ BDLocal.designer.vb)   modelo LINQ de la BD local
FacturacionLOCAL/TDatosServerToLocal.vb                 sincronización servidor -> local
NEGOCIO/CATALOGOS/TLDControlDBLocal.vb                  scripts LDControlDBLocalAutomatico
NEGOCIO/Database/GENERAL/pos-local/LDCOM_LOCAL.sql      esquema base de la BD local
```

Una columna o tabla nueva que el POS usa sin conexión necesita las cuatro piezas; si falta una, el
bug aparece solo en local (1981, 863, 1445, 2166).
