"""autorizar(): llena USUARIO y CONTRASENA del dialogo de autorizacion abierto ('Aplicar nota credito.' u otro con
los mismos campos) con las credenciales de prueba (sesion.leer_credenciales) y pulsa Aceptar.
Devuelve {"aparecio": titulo} de lo que quede abierto tras aceptar (o None si no queda ventana modal)."""
import time

import win32gui

from .. import base, sesion

NOMBRE = "autorizar"
PANTALLA = "Dialogo modal de autorizador (usuario y contrasena) tras F5 en nota de credito"

ETIQUETA_USUARIO = "USUARIO"
CLASE_CAMPO = "EDIT"


def _dialogo(pid):
    return next((h for h in base.modales(pid)
                 if any(t.upper().startswith(ETIQUETA_USUARIO) for t in base.textos(h))
                 and any(CLASE_CAMPO in base.clase(c) for c in base.descendientes(h))), None)


def ejecutar(pos):
    dialogo = base.esperar(lambda: _dialogo(pos.pid), 20)
    if not dialogo:
        raise base.PasoFallido("No hay dialogo de autorizacion abierto")
    usuario, clave = sesion.leer_credenciales()
    campos = sorted((c for c in base.descendientes(dialogo)
                     if CLASE_CAMPO in base.clase(c) and win32gui.IsWindowVisible(c)),
                    key=lambda c: win32gui.GetWindowRect(c)[1])
    if len(campos) < 2:
        raise base.PasoFallido("El dialogo de autorizacion no tiene dos campos")
    base.escribir(campos[0], usuario)
    base.escribir(campos[1], clave)
    base.clic_boton(dialogo, "Aceptar")
    time.sleep(3)
    restantes = base.modales(pos.pid)
    return {"aparecio": base.titulo(restantes[0]) if restantes else None}
