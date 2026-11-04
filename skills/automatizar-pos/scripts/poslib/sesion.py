"""Login al POS con el usuario de prueba (qa_auto, solo Docker local). La clave nunca se imprime ni se guarda en el repo.

Origen de las credenciales, en este orden:
  1. variables de entorno POS_USUARIO y POS_CLAVE;
  2. el archivo cuya ruta está en POS_CREDENCIALES, con líneas "Login: ..." y "Clave: ...".
"""
import os
import time

from . import base

VAR_USUARIO = "POS_USUARIO"
VAR_CLAVE = "POS_CLAVE"
VAR_ARCHIVO = "POS_CREDENCIALES"
ID_VENTANA_LOGIN = "Frm_Login"
ID_USUARIO = "tbUsuario"
ID_CLAVE = "tbContrasena"
ID_CONECTAR = "bConectar"
TITULO_LISTA_TIPOS = "Frm_Lista"
TOPE_SESION = 60.0
ESPERA_TRAS_CONECTAR = 8.0  # si se pulsa Ingresar muy pronto tras abrir el POS, el clic no hace nada: se reintenta


def leer_credenciales():
    usuario, clave = os.environ.get(VAR_USUARIO), os.environ.get(VAR_CLAVE)
    if usuario and clave:
        return usuario, clave
    ruta = os.environ.get(VAR_ARCHIVO)
    if ruta and os.path.isfile(ruta):
        valores = {}
        with open(ruta, encoding="utf-8") as f:
            for linea in f:
                if ":" in linea:
                    nombre, valor = linea.split(":", 1)
                    valores[nombre.strip()] = valor.strip()
        if valores.get("Login") and valores.get("Clave"):
            return valores["Login"], valores["Clave"]
    raise base.PasoFallido("Faltan credenciales: definir %s y %s, o %s apuntando a un archivo con Login: y Clave:"
                           % (VAR_USUARIO, VAR_CLAVE, VAR_ARCHIVO))


def hay_login(pid):
    """True si el login está visible (Win32, no se cuelga con modales). base.por_titulo no sirve: excluye la principal."""
    return any(ID_VENTANA_LOGIN.lower() in base.titulo(h).lower() for h in base.ventanas(pid, 0))


def _ventana_login(pid):
    """Envoltura UIA de la ventana de login (tiene pocos controles: UIA no se cuelga aquí)."""
    from pywinauto import Application
    aplicacion = Application(backend="uia").connect(process=pid)
    for ventana in aplicacion.windows():
        try:
            if ventana.element_info.automation_id == ID_VENTANA_LOGIN:
                return aplicacion.window(handle=ventana.handle)
        except Exception:
            continue
    return None


def _escribir(ventana, auto_id, texto):
    control = ventana.child_window(auto_id=auto_id).wrapper_object()
    control.set_edit_text("")
    control.set_edit_text(texto)


def iniciar_sesion(pid, tope=TOPE_SESION):
    """Escribe usuario y clave en el login y pulsa Ingresar hasta que el login desaparece.
    Si ya no hay login (sesión iniciada) no hace nada. Devuelve True si tuvo que iniciar sesión."""
    usuario, clave = leer_credenciales()
    if not base.esperar(lambda: _ventana_login(pid) or base.por_titulo(pid, TITULO_LISTA_TIPOS) or base.principal(pid), tope):
        raise base.PasoFallido("El POS no mostró pantalla de login")
    inicio_sesion = False
    limite = time.time() + tope
    while time.time() < limite:
        login = _ventana_login(pid)
        if login is None:
            return inicio_sesion
        _escribir(login, ID_USUARIO, usuario)
        _escribir(login, ID_CLAVE, clave)
        base.en_hilo(login.child_window(auto_id=ID_CONECTAR).wrapper_object().invoke)
        inicio_sesion = True
        base.esperar(lambda: _ventana_login(pid) is None, ESPERA_TRAS_CONECTAR)
    raise base.PasoFallido("El login sigue abierto tras %.0f s (¿credenciales incorrectas?)" % tope)
