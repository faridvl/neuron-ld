"""cerrar_caja(efectivo=0, ...): cierra la caja del POS de punta a punta.
Teclas reales: F5 (Caja; si no abre, F11 y F5) > F2 Cerrar Caja; luego atiende, según aparezcan, Retiro de Caja, Depósito Automático,
las preguntas de confirmación y la pantallita "Cierre de caja" (caduca a ~15 s: se sondea cada 50 ms y se pulsa
F1 real de inmediato). En Retiro de Caja sin efectivo sale con ESC. El error EMV (#32770) es inocuo en Docker y se cierra con OK. Terminó cuando el POS vuelve al login.
Idempotente: con efectivo=0 solo sale del Retiro y cierra, sin repetir retiro ni depósito. Si se corta a medias,
lo ya guardado en la base (retiro, depósito) queda; volver a correr con efectivo=0."""
import time

import win32con
import win32gui

from .. import base, fisico, modales, sesion

NOMBRE = "cerrar_caja"
PANTALLA = "Teclas F5>F2 (o F11>F5>F2); Retiro de Caja, Depósito Automático, Cierre de caja (F1); termina en login"
REQUIERE_PRINCIPAL = False

TITULOS_OPCIONES_CAJA = ("Frm_Lista", "Opciones de la Caja")
ESPERA_TRAS_TECLA_MENU = 2.0
TOPE_OPCIONES_CAJA = 3.0
SONDEO = 0.05
TOPE_CIERRE = 240.0
TOPE_DENOMINACIONES = 15.0
ESPERA_DENOMINACION = 0.8
ESPERA_TRAS_DENOMINACIONES = 1.0
ESPERA_TRAS_SALIR = 2.0
ESPERA_ANTES_GUARDAR = 0.5
VK_F1 = 0x70
VK_F2 = 0x71
VK_F5 = 0x74
VK_F11 = 0x7A
VK_ESC = 0x1B
CBN_SELCHANGE = 1
SECUENCIAS_ABRIR_OPCIONES = ([VK_F5], [VK_F11, VK_F5])  # F5 es Caja solo en la página principal de la barra; F11 la alterna
TECLAS = list("0123456789") + ["="]


def _boton(h, fragmento):
    for c, t in base.botones(h):
        if fragmento.lower() in t.lower():
            return c
    return None


def _pulsar(h_boton):
    win32gui.PostMessage(h_boton, win32con.BM_CLICK, 0, 0)


def _armar_efectivo(h_dialogo, monto):
    """Pulsa cada denominación (de mayor a menor) y teclea la cantidad en el teclado numérico (clic físico)."""
    denominaciones = []
    for c, t in base.botones(h_dialogo):
        texto = t.replace(",", "")
        if "." in texto and texto.replace(".", "", 1).isdigit():
            denominaciones.append((float(texto), c))
    denominaciones.sort(reverse=True)
    teclas = {win32gui.GetWindowText(c): c for c in base.descendientes(h_dialogo)
              if win32gui.GetWindowText(c) in TECLAS and win32gui.IsWindowVisible(c)}
    resto = round(monto, 2)
    for valor, boton in denominaciones:
        cantidad = int(resto // valor)
        if cantidad <= 0:
            continue
        _pulsar(boton)
        time.sleep(ESPERA_DENOMINACION)
        for digito in str(cantidad):
            fisico.clic_en_control(h_dialogo, teclas[digito])
        fisico.clic_en_control(h_dialogo, teclas["="])
        resto = round(resto - cantidad * valor, 2)
    if resto > 0.001:
        raise base.PasoFallido("No se pudo armar el efectivo con las denominaciones; faltaron %.2f" % resto)


def _retiro(pos, h, efectivo):
    if efectivo > 0:
        fisico.pulsar_por_id(h, "BN_F4")  # F4 Efectivo abre Denominaciones
        dialogo = base.esperar_ventana(pos.pid, "Denominaciones", TOPE_DENOMINACIONES)
        if not dialogo:
            raise base.PasoFallido("No abrió Denominaciones")
        time.sleep(ESPERA_TRAS_DENOMINACIONES)
        _armar_efectivo(dialogo, efectivo)
        _pulsar(_boton(dialogo, "Salir"))
        time.sleep(ESPERA_TRAS_SALIR)
        _pulsar(_boton(h, "Retirar"))
    else:
        fisico.pulsar_tecla(h, VK_ESC)


def _deposito(h, numero, banco, encargado):
    from pywinauto.controls.hwndwrapper import HwndWrapper
    campos = [c for c in base.descendientes(h) if "EDIT" in base.clase(c).upper()]
    HwndWrapper(campos[0]).set_edit_text(numero)  # WM_SETTEXT directo no actualiza el control del POS
    combos = sorted((c for c in base.descendientes(h) if "COMBOBOX" in base.clase(c).upper()),
                    key=lambda c: win32gui.GetWindowRect(c)[1])
    for combo, indice in zip(combos, (banco, encargado)):
        win32gui.SendMessage(combo, win32con.CB_SETCURSEL, indice, 0)
        identificador = win32gui.GetDlgCtrlID(combo) & 0xFFFF
        win32gui.SendMessage(win32gui.GetParent(combo), win32con.WM_COMMAND, (CBN_SELCHANGE << 16) | identificador, combo)
    time.sleep(ESPERA_ANTES_GUARDAR)
    _pulsar(_boton(h, "Guardar"))


def _cierre_de_caja(h):
    fisico.pulsar_tecla(h, VK_F1, espera=0)


def _opciones_de_caja(pid):
    return next((h for h in base.modales(pid) if base.titulo(h) in TITULOS_OPCIONES_CAJA), None)


def abrir_opciones_de_caja(pid):
    """Abre la ventana de opciones de la caja con teclas reales desde la principal; devuelve su handle."""
    pantalla_principal = base.principal(pid)
    for secuencia in SECUENCIAS_ABRIR_OPCIONES:
        for codigo in secuencia:
            fisico.pulsar_tecla(pantalla_principal, codigo, espera=ESPERA_TRAS_TECLA_MENU)
        opciones = base.esperar(lambda: _opciones_de_caja(pid), TOPE_OPCIONES_CAJA)
        if opciones:
            return opciones
    raise base.PasoFallido("No abrió la ventana de opciones de la caja (F5 ni F11+F5)")


def ejecutar(pos, efectivo=0, banco=0, encargado=0, numero_deposito="QA0001", tope=TOPE_CIERRE):
    fisico.pulsar_tecla(abrir_opciones_de_caja(pos.pid), VK_F2, espera=0)
    hecho = {"retiro": False, "deposito": False, "cierre": False, "confirmaciones": 0}
    vistas = set()
    limite = time.time() + tope
    while time.time() < limite:
        modales.cerrar_errores_dotnet(pos.pid)
        for h in base.modales(pos.pid):
            if h in vistas:
                continue
            titulo = base.titulo(h)
            if "Cierre de caja" in titulo:
                _cierre_de_caja(h)
                hecho["cierre"] = True
            elif "Retiro de Caja" in titulo:
                _retiro(pos, h, efectivo if not hecho["retiro"] else 0)
                hecho["retiro"] = hecho["retiro"] or efectivo > 0
            elif "sito Autom" in titulo:
                _deposito(h, numero_deposito, banco, encargado)
                hecho["deposito"] = True
            elif "Confirmaci" in titulo:
                if modales.responder_pregunta(h):
                    hecho["confirmaciones"] += 1
            else:
                continue
            vistas.add(h)
        if sesion.hay_login(pos.pid):
            return hecho
        time.sleep(SONDEO)
    raise base.PasoFallido("La caja no terminó de cerrar en %.0f s (hecho: %s)" % (tope, hecho))
