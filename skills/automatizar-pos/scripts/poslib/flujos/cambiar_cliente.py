"""cambiar_cliente(codigo, texto=None, muestra=None): F1 Cambiar Clientes -> buscar -> elegir la fila cuyo Número sea `codigo` -> confirmar.
Terminó cuando el diálogo se cerró y el campo Cliente (lblDatos) empieza con `codigo` o con `muestra`.
`muestra`: código que se ve en pantalla cuando no coincide con el elegido (un asociado con finca muestra el código de su finca)."""
import win32gui
from pywinauto.controls.common_controls import ListViewWrapper

from .. import base

NOMBRE = "cambiar_cliente"
PANTALLA = "Cambiar Cliente (modal); abre Bn_Cliente / F1"


def _lista_con_filas(dialogo):
    for h in base.descendientes(dialogo):
        if "SysListView32" in base.clase(h):
            vista = ListViewWrapper(h)
            if vista.item_count() > 0:
                return vista
    return None


def _muestra(pos, codigos):
    actual = pos.texto("lblDatos").strip()
    return any(actual.startswith(str(c) + " ") for c in codigos)


def ejecutar(pos, codigo, texto=None, muestra=None):
    codigo = str(codigo)
    esperados = [codigo] + ([muestra] if muestra else [])
    if not muestra and _muestra(pos, esperados):
        return {"ya_estaba": True}
    pos.invocar("Bn_Cliente")
    dialogo = base.esperar_ventana(pos.pid, "Cambiar Cliente")
    if not dialogo:
        raise base.PasoFallido("No abrió 'Cambiar Cliente'")
    campos = sorted((h for h in base.descendientes(dialogo) if "EDIT" in base.clase(h).upper()),
                    key=lambda h: win32gui.GetWindowRect(h)[1])
    base.escribir(campos[0], texto or codigo)
    base.clic_sin_texto(dialogo, 0)  # lupa

    vista = base.esperar(lambda: _lista_con_filas(dialogo), 20)
    if not vista:
        raise base.PasoFallido("La búsqueda de cliente %s no devolvió filas" % codigo)
    elegida = next((i for i in range(vista.item_count()) if vista.get_item(i).text().strip() == codigo), None)
    if elegida is None:
        raise base.PasoFallido("El cliente %s no está en la lista" % codigo)
    vista.select(elegida)
    base.clic_sin_texto(dialogo, 1)  # check
    if not base.esperar_cierre(dialogo, 15) or not base.esperar(lambda: _muestra(pos, esperados), 10):
        raise base.PasoFallido("El campo Cliente no muestra %s (dice %r)" % (esperados, pos.texto("lblDatos")))
    return {"cliente": pos.texto("lblDatos")}
