"""buscar_articulo(texto): escribe el texto y pulsa la lupa (Enter SELECCIONA el primer resultado; la lupa busca).
Terminó cuando se abre 'Búsqueda de Artículos'. Devuelve el handle de la ventana para seguir con ella."""
from .. import base

NOMBRE = "buscar_articulo"
PANTALLA = "Principal: Text_Articulo + lupa; modal 'Busqueda de Articulos' (EDIT, 3 botones sin texto, 3 SysListView32)"


def ejecutar(pos, texto):
    base.escribir(pos._hwnd["Text_Articulo"], str(texto))
    pos.invocar("Btn_Agregar_Articulo")
    ventana = base.esperar_ventana(pos.pid, "squeda", 15)
    if not ventana:
        raise base.PasoFallido("No abrió la búsqueda de artículos")
    return {"ventana": ventana, "titulo": base.titulo(ventana)}
