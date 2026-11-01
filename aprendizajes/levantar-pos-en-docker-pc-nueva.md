# Levantar API, Admin y POS contra el Docker local en una PC nueva

Para quien arma el ambiente de LDCOM desde cero. Cada trampa aparece solo después de resolver la anterior.

## POS: error "Referencia a objeto no establecida" después de Frm_Login

Causa: la central del Docker no tenía una columna que el código ya lee (`Caja.Caja_Modo_Talonario`, migración 2226).
Cadena: el WS `Caja_ListKey` falla en el servidor, `TCatalogo.GetCaja` traga la excepción y devuelve Nothing,
`iniciarSincronizacion` se salta la carga sin avisar, y el POS revienta después con una base local vacía.

Cómo reconocerlo:
- La base local tiene casi todas las tablas vacías.
- `Msg_Message` de la central trae `Invalid column name` reciente. Mirar ahí primero.

Solución: poner al día las migraciones de la central con `migrate`, no a mano.

## La sincronización inicial necesita dos cosas

- `<Sinc_Inicial>NO</Sinc_Inicial>` en `LD.Facturacion.LD`: solo hace que abra la pantalla de parámetros. El POS lo
  pasa a SI aunque la carga no haya corrido.
- Que `GetCaja` responda. Sin eso la carga no corre, aunque el `.LD` esté bien.
- Preventa tiene su propia llave, `Sinc_Inicial_Preventa`.

## Conexión local del POS

- El Integrated Security que deja rig no sirve con SQL en Docker Linux: "La Base de Datos Local no se instaló
  correctamente". Hay que usar login SQL.
- Parchar el `.LD` por fuera no dura: `GuardarLDConfig` reescribe `<Conexion>` desde la pestaña F5 al pulsar Aceptar.
  Se llena en F5.
- `WebServiceServExterno` vacío evita la llamada al servicio de Azure durante la validación.

## API de Integrations

- La clave SQL de `logical` no es la de su usuario de aplicación en el clon de Staging. La conexión a la base pasa,
  pero `Seg_Usuario_Login` falla y el endpoint responde 500 `INTERNAL_ERROR`; el motivo real está en el log.
  `LdcomUser` debe ser una cuenta de aplicación válida, como `qa_auto`, y la conexión SQL puede seguir con `logical`.
- Las claves van codificadas con `LegacyPasswordCodec`.
- El publish no trae `appsettings.json`: la configuración va por variables de entorno.

## Pantallas y automatización

- Un color rojo en Parámetros puede ser una validación vieja: solo se repinta al pulsar Aceptar.
- Si el POS no responde a los clics, buscar un modal abierto detrás.
- `win32gui.GetWindowText` sobre un EDIT de otro proceso devuelve texto en caché: usar UIA o `WM_GETTEXT`.

## Consola

- PowerShell 5.1 rompe las comillas en `docker exec`: escribir un `.sh` con LF y usar `docker cp`.
- En Git Bash, `MSYS_NO_PATHCONV=1` evita que convierta las rutas del contenedor.
