"""nota_credito(numero_ticket, lineas=None): Documento -> NOTA DE CREDITO/CREDITO -> buscar el ticket por su numero de
factura (Factura_Id, columna "Factura") -> Marcar Todo (o solo `lineas`, lista de numeros de linea) -> Cargar -> F5.
Devuelve {"aparecio": titulo} con lo que salga tras F5: 'Aplicar nota credito' pide usuario y contrasena de un
autorizador; este flujo no las escribe, las debe teclear quien tenga permiso (o el llamador con otro paso).
Requiere un subdocumento del Doc 5 (Nota_Credito) visible para la sucursal (en una sucursal sin FE: no electronico)."""
import time

import win32gui
from pywinauto.controls.common_controls import ListViewWrapper

from .. import base

NOMBRE = "nota_credito"
PANTALLA = "Principal: Documento -> Tipos de Documentos -> Devolucion de Ticket -> detalle -> F5"

TIPO_NOTA_CREDITO_CREDITO = "NOTA DE CR"
TITULO_BUSCADOR = "Devoluci"
LUPA, CONFIRMAR = 0, 1


def _filas(dialogo):
    for h in base.descendientes(dialogo):
        if "SysListView32" in base.clase(h):
            vista = ListViewWrapper(h)
            if vista.item_count() > 0:
                return vista
    return None


def _campo_numero(dialogo):
    return next(h for h in base.descendientes(dialogo)
                if base.clase(h).endswith("EDIT.app.0.34f5582_r14_ad1") and win32gui.IsWindowVisible(h))


def ejecutar(pos, numero_ticket, lineas=None):
    pos.invocar("Bn_Documento")
    tipos = base.esperar_ventana(pos.pid, "Tipos de Documentos")
    if not tipos:
        raise base.PasoFallido("No abrio 'Tipos de Documentos'")
    base.clic_boton(tipos, TIPO_NOTA_CREDITO_CREDITO)
    time.sleep(1)
    base.clic_boton(tipos, "Aceptar")
    buscador = base.esperar_ventana(pos.pid, TITULO_BUSCADOR)
    if not buscador:
        raise base.PasoFallido("No abrio el buscador de tickets (falta subdocumento de Nota de Credito?)")
    base.clic_boton(buscador, "N")  # F1 Numero muestra el campo
    time.sleep(1)
    base.escribir(_campo_numero(buscador), str(numero_ticket))
    base.clic_sin_texto(buscador, LUPA)
    vista = base.esperar(lambda: _filas(buscador), 20)
    if not vista:
        raise base.PasoFallido("El ticket %s no aparecio (no es de credito o no existe)" % numero_ticket)
    vista.select(0)
    base.clic_sin_texto(buscador, CONFIRMAR)
    detalle = base.esperar(lambda: next((h for h in base.modales(pos.pid) if "Devoluci" in base.titulo(h)
                                         and any(t.startswith("Marcar") for _, t in base.botones(h))), None), 20)
    if not detalle:
        raise base.PasoFallido("No abrio el detalle de la devolucion (plazo vencido, ya devuelto o sin permiso)")
    if lineas is None:
        base.clic_boton(detalle, "Marcar Todo")
    else:
        raise base.PasoFallido("Devolucion parcial (lineas=%s) aun no automatizada" % (lineas,))
    time.sleep(1.5)
    base.clic_boton(detalle, "Cargar")
    if not base.esperar_cierre(detalle, 20):
        raise base.PasoFallido("El detalle de devolucion no se cerro tras Cargar (mensaje pendiente?)")
    pos.pulsar_barra("imprimir documento")
    resultado = base.esperar(lambda: base.modales(pos.pid) or None, 20)
    if not resultado:
        raise base.PasoFallido("F5 no abrio ninguna ventana")
    return {"aparecio": base.titulo(resultado[0]), "total": pos.total()}
