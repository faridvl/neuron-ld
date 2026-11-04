"""iniciar_sesion(): entra al POS con el usuario de prueba. No hace nada si ya hay sesión iniciada.
Credenciales por entorno (ver poslib.sesion); la clave no se imprime."""
from .. import sesion

NOMBRE = "iniciar_sesion"
PANTALLA = "Frm_Login: usuario, contraseña, Ingresar"
REQUIERE_PRINCIPAL = False  # la pantalla principal aún no existe (o cambia) mientras se hace login


def ejecutar(pos, tope=sesion.TOPE_SESION):
    return {"inicio_sesion": sesion.iniciar_sesion(pos.pid, tope)}
