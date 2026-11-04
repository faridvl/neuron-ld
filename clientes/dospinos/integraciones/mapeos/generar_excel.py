"""Arma Mapeo-Integraciones-DosPinos.xlsx a partir de los *.json de esta carpeta.

Uso: python -I generar_excel.py
Cada integracion es un .json (ver README.md); no se edita el Excel a mano.
"""
import glob
import io
import json
import os
import re
from copy import copy

from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image
from openpyxl.formatting.rule import DataBarRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

CARPETA = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(CARPETA, "Mapeo-Integraciones-DosPinos.xlsx")
ARCHIVO_AVANCE = "avance.json"

AZUL_OSCURO = "2F4A63"
FILA_ALTERNA = "EEF2F6"
LETRA_BLANCA = Font(name="Calibri", bold=True, color="FFFFFF", size=11)
RELLENO_ENCABEZADO = PatternFill("solid", fgColor=AZUL_OSCURO)
RELLENO_ALTERNO = PatternFill("solid", fgColor=FILA_ALTERNA)
BORDE = Border(*(Side(style="thin", color="C9D2DB"),) * 4)
AJUSTE = Alignment(wrap_text=True, vertical="top")

# (relleno, letra) por estado
COLORES_ESTADO = {
    "Confirmado": ("C6EFCE", "1E6B34"),
    "Decidido por nosotros": ("CFE2F3", "1F4E79"),
    "Provisional": ("FCE4C4", "9C5700"),
    "Pregunta a Dos Pinos": ("F8CBCB", "9C0006"),
}
ESTADOS_PENDIENTES = ("Provisional", "Pregunta a Dos Pinos")
RELLENO_DUDA = PatternFill("solid", fgColor="F8CBCB")
LETRA_DUDA = "9C0006"

# Relleno de la fila entera en la hoja Avance; "Sin empezar" queda en blanco a propósito
COLORES_AVANCE = {
    "Implementada": "C6EFCE",
    "En curso": "FFF2CC",
    "Sin empezar": None,
}

COLUMNAS_CAMPOS = [
    ("Bloque", 18, "bloque"),
    ("Campo Dos Pinos", 20, "campo"),
    ("Sale de LDCOM (qué mandamos)", 46, "origen"),
    ("Por qué", 40, "porque"),
    ("Tipo / largo / obligatorio (según su documento)", 24, "doc"),
    ("Qué significa (en palabras simples)", 52, "descripcion"),
    ("Ejemplo", 30, "ejemplo"),
    ("Estado", 22, "estado"),
    ("Duda", 40, "duda"),
    ("Por qué es duda", 40, "porque_duda"),
    ("Nota", 46, "nota"),
    ("Pregunta N.º", 11, "pregunta"),
]


def nombre_hoja(codigo, usados):
    limpio = re.sub(r"[\[\]\*\?/\\:]", "-", codigo)[:31]
    base, n = limpio, 2
    while limpio.lower() in usados:
        limpio = f"{base[:28]}-{n}"
        n += 1
    usados.add(limpio.lower())
    return limpio


def encabezado_tabla(hoja, fila, titulos):
    for col, titulo in enumerate(titulos, start=1):
        celda = hoja.cell(row=fila, column=col, value=titulo)
        celda.font = LETRA_BLANCA
        celda.fill = RELLENO_ENCABEZADO
        celda.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        celda.border = BORDE
    hoja.row_dimensions[fila].height = 32


def pintar_estado(celda, estado):
    colores = COLORES_ESTADO.get(estado)
    if colores:
        celda.fill = PatternFill("solid", fgColor=colores[0])
        celda.font = Font(name="Calibri", bold=True, color=colores[1])
    celda.alignment = Alignment(wrap_text=True, vertical="top", horizontal="center")


def texto(valor):
    return "" if valor is None else str(valor)


def altura_fila(valores, anchos):
    lineas = 1
    for valor, ancho in zip(valores, anchos):
        caracteres_por_linea = max(int(ancho * 1.05), 1)
        for parte in texto(valor).split("\n"):
            lineas = max(lineas, -(-max(len(parte), 1) // caracteres_por_linea))
    return min(15 * lineas + 4, 400)


def en_duda(campo):
    return campo.get("estado") in ESTADOS_PENDIENTES or bool(campo.get("duda"))


def pintar_duda(hoja, fila, columnas):
    for col in range(1, columnas + 1):
        celda = hoja.cell(row=fila, column=col)
        celda.fill = RELLENO_DUDA
        celda.font = Font(name="Calibri", bold=celda.font.bold, color=LETRA_DUDA)


def pendientes(integracion):
    return sum(1 for c in integracion["campos"] if en_duda(c))


def hoja_integracion(libro, integracion, nombre):
    hoja = libro.create_sheet(nombre)
    hoja.sheet_view.showGridLines = False
    for col, (_, ancho, _) in enumerate(COLUMNAS_CAMPOS, start=1):
        hoja.column_dimensions[get_column_letter(col)].width = ancho
    ultima = len(COLUMNAS_CAMPOS)

    hoja.cell(row=1, column=1, value=f"{integracion['codigo']} - {integracion['nombre']}").font = Font(
        name="Calibri", bold=True, size=16, color=AZUL_OSCURO)
    hoja.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ultima)

    subtitulo = hoja.cell(row=2, column=1, value=(
        f"Mapeo de campos: {integracion.get('sentido', '')}. Endpoint, cuándo se envía y reglas: hoja Reglas."))
    subtitulo.font = Font(name="Calibri", italic=True, color="555555")
    hoja.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ultima)
    fila = 3
    fila_encabezado = fila
    encabezado_tabla(hoja, fila, [c[0] for c in COLUMNAS_CAMPOS])
    anchos = [c[1] for c in COLUMNAS_CAMPOS]
    for indice, campo in enumerate(integracion["campos"]):
        fila += 1
        valores = [texto(campo.get(clave)) for _, _, clave in COLUMNAS_CAMPOS]
        for col, valor in enumerate(valores, start=1):
            celda = hoja.cell(row=fila, column=col, value=valor)
            celda.alignment = AJUSTE
            celda.border = BORDE
            if indice % 2 == 1:
                celda.fill = RELLENO_ALTERNO
        hoja.cell(row=fila, column=2).font = Font(name="Calibri", bold=True)
        hoja.cell(row=fila, column=len(COLUMNAS_CAMPOS)).alignment = Alignment(horizontal="center", vertical="top")
        pintar_estado(hoja.cell(row=fila, column=8), campo.get("estado"))
        if en_duda(campo):
            pintar_duda(hoja, fila, ultima)
        hoja.row_dimensions[fila].height = altura_fila(valores, anchos)

    hoja.auto_filter.ref = f"A{fila_encabezado}:{get_column_letter(ultima)}{fila}"
    hoja.freeze_panes = hoja.cell(row=fila_encabezado + 1, column=3)
    hoja.sheet_properties.tabColor = AZUL_OSCURO
    hoja.page_setup.orientation = "landscape"
    hoja.page_setup.fitToWidth = 1
    hoja.page_setup.fitToHeight = 0
    hoja.sheet_properties.pageSetUpPr.fitToPage = True


def hoja_indice(libro, integraciones, nombres):
    hoja = libro.active
    hoja.title = "Indice"
    hoja.sheet_view.showGridLines = False
    titulos = ["Integración", "Nombre", "Sentido", "Cuándo se envía", "Estado general", "Campos",
               "Campos pendientes", "Preguntas a Dos Pinos"]
    anchos = [14, 44, 24, 60, 20, 10, 12, 14]
    for col, ancho in enumerate(anchos, start=1):
        hoja.column_dimensions[get_column_letter(col)].width = ancho
    hoja.cell(row=1, column=1, value="Mapeo de integraciones LDCOM -> Dos Pinos").font = Font(
        name="Calibri", bold=True, size=16, color=AZUL_OSCURO)
    hoja.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(titulos))
    hoja.cell(row=2, column=1, value="Una hoja por integración. Los campos pendientes son los que están "
                                      "como Provisional o Pregunta a Dos Pinos.").alignment = AJUSTE
    hoja.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(titulos))
    encabezado_tabla(hoja, 4, titulos)
    fila = 4
    for indice, (integracion, nombre) in enumerate(zip(integraciones, nombres)):
        fila += 1
        valores = [
            integracion["codigo"], integracion["nombre"], integracion.get("sentido"),
            integracion.get("cuando_se_envia"), integracion.get("estado_general"),
            len(integracion["campos"]), pendientes(integracion), len(integracion.get("preguntas") or []),
        ]
        for col, valor in enumerate(valores, start=1):
            celda = hoja.cell(row=fila, column=col, value=valor)
            celda.alignment = AJUSTE
            celda.border = BORDE
            if indice % 2 == 1:
                celda.fill = RELLENO_ALTERNO
        enlace = hoja.cell(row=fila, column=1)
        enlace.hyperlink = f"#'{nombre}'!A1"
        enlace.font = Font(name="Calibri", bold=True, color="0563C1", underline="single")
        pintar_estado(hoja.cell(row=fila, column=5), integracion.get("estado_general"))
        for col in (6, 7, 8):
            hoja.cell(row=fila, column=col).alignment = Alignment(horizontal="center", vertical="top")
        hoja.row_dimensions[fila].height = altura_fila(valores, anchos)
    hoja.auto_filter.ref = f"A4:{get_column_letter(len(titulos))}{fila}"
    hoja.freeze_panes = "A5"
    hoja.sheet_properties.tabColor = "1F4E79"


def hoja_avance(libro, avance):
    hoja = libro.create_sheet("Avance", 0)
    hoja.sheet_view.showGridLines = False
    columnas = [
        ("Carpeta", 9, "carpeta"),
        ("Interfaz", 13, "codigo"),
        ("Nombre", 34, "nombre"),
        ("Sentido", 20, "sentido"),
        ("Estado", 14, "estado"),
        ("% avance", 10, "porcentaje"),
        ("Qué está hecho", 52, "hecho"),
        ("Qué falta", 60, "falta"),
        ("Bloqueo / depende de", 34, "bloqueo"),
    ]
    anchos = [c[1] for c in columnas]
    for col, ancho in enumerate(anchos, start=1):
        hoja.column_dimensions[get_column_letter(col)].width = ancho
    ultima = len(columnas)
    columna_porcentaje = 6

    interfaces = avance["interfaces"]
    promedio = sum(i["porcentaje"] for i in interfaces) / len(interfaces)
    conteo = {estado: sum(1 for i in interfaces if i["estado"] == estado) for estado in COLORES_AVANCE}

    hoja.cell(row=1, column=1, value="Avance de interfaces LDCOM - Dos Pinos").font = Font(
        name="Calibri", bold=True, size=16, color=AZUL_OSCURO)
    hoja.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ultima)
    resumen = (f"Corte {avance['fecha_corte']}: {round(promedio)} % en total. "
               + f"{conteo['Implementada']} implementadas, {conteo['En curso']} en curso, {conteo['Sin empezar']} sin empezar"
               + ". Verde: implementada. Amarillo: en curso. Blanco: sin empezar.")
    hoja.cell(row=2, column=1, value=resumen).font = Font(name="Calibri", bold=True)
    hoja.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ultima)
    criterio = hoja.cell(row=3, column=1, value=avance.get("criterio"))
    criterio.font = Font(name="Calibri", italic=True, color="555555")
    criterio.alignment = AJUSTE
    hoja.merge_cells(start_row=3, start_column=1, end_row=3, end_column=ultima)
    hoja.row_dimensions[3].height = 30

    fila_encabezado = 5
    encabezado_tabla(hoja, fila_encabezado, [c[0] for c in columnas])
    fila = fila_encabezado
    for interfaz in interfaces:
        fila += 1
        valores = [interfaz.get(clave) for _, _, clave in columnas]
        color = COLORES_AVANCE.get(interfaz["estado"])
        for col, valor in enumerate(valores, start=1):
            celda = hoja.cell(row=fila, column=col, value=valor if valor != "" else None)
            celda.alignment = AJUSTE
            celda.border = BORDE
            if color:
                celda.fill = PatternFill("solid", fgColor=color)
        hoja.cell(row=fila, column=2).font = Font(name="Calibri", bold=True)
        hoja.cell(row=fila, column=5).font = Font(name="Calibri", bold=True)
        celda_porcentaje = hoja.cell(row=fila, column=columna_porcentaje)
        celda_porcentaje.value = interfaz["porcentaje"] / 100
        celda_porcentaje.number_format = "0%"
        celda_porcentaje.alignment = Alignment(horizontal="center", vertical="top")
        hoja.cell(row=fila, column=1).alignment = Alignment(horizontal="center", vertical="top")
        hoja.row_dimensions[fila].height = altura_fila([texto(v) for v in valores], anchos)

    fila += 1
    hoja.cell(row=fila, column=5, value="Total").font = Font(name="Calibri", bold=True)
    total = hoja.cell(row=fila, column=columna_porcentaje,
                      value=f"=AVERAGE({get_column_letter(columna_porcentaje)}{fila_encabezado + 1}:"
                            f"{get_column_letter(columna_porcentaje)}{fila - 1})")
    total.number_format = "0%"
    total.font = Font(name="Calibri", bold=True)
    total.alignment = Alignment(horizontal="center")

    letra = get_column_letter(columna_porcentaje)
    hoja.conditional_formatting.add(
        f"{letra}{fila_encabezado + 1}:{letra}{fila - 1}",
        DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color="5B9BD5"))
    hoja.auto_filter.ref = f"A{fila_encabezado}:{get_column_letter(ultima)}{fila - 1}"
    hoja.freeze_panes = hoja.cell(row=fila_encabezado + 1, column=3)
    hoja.sheet_properties.tabColor = "70AD47"
    hoja.page_setup.orientation = "landscape"
    hoja.page_setup.fitToWidth = 1
    hoja.page_setup.fitToHeight = 0
    hoja.sheet_properties.pageSetUpPr.fitToPage = True


def hoja_variables(libro, integraciones):
    hoja = libro.create_sheet("Variables")
    hoja.sheet_view.showGridLines = False
    titulos = ["Integración", "Campo Dos Pinos", "Qué manda LDCOM", "Ejemplo", "Por qué", "Estado", "Duda"]
    anchos = [12, 22, 52, 28, 60, 20, 40]
    for col, ancho in enumerate(anchos, start=1):
        hoja.column_dimensions[get_column_letter(col)].width = ancho
    encabezado_tabla(hoja, 1, titulos)
    fila = 1
    for integracion in integraciones:
        for campo in integracion["campos"]:
            fila += 1
            valores = [integracion["codigo"], campo.get("campo"), campo.get("origen"),
                       campo.get("ejemplo"), campo.get("porque"), campo.get("estado"), campo.get("duda")]
            for col, valor in enumerate(valores, start=1):
                celda = hoja.cell(row=fila, column=col, value=valor)
                celda.alignment = AJUSTE
                celda.border = BORDE
                if fila % 2 == 1:
                    celda.fill = RELLENO_ALTERNO
            hoja.cell(row=fila, column=1).font = Font(name="Calibri", bold=True)
            hoja.cell(row=fila, column=2).font = Font(name="Calibri", bold=True)
            pintar_estado(hoja.cell(row=fila, column=6), campo.get("estado"))
            if en_duda(campo):
                pintar_duda(hoja, fila, len(titulos))
            hoja.row_dimensions[fila].height = altura_fila(valores, anchos)
    hoja.auto_filter.ref = f"A1:{get_column_letter(len(titulos))}{max(fila, 2)}"
    hoja.freeze_panes = "C2"
    hoja.sheet_properties.tabColor = "548235"


def hoja_reglas(libro, integraciones):
    hoja = libro.create_sheet("Reglas")
    hoja.sheet_view.showGridLines = False
    titulos = ["Integración", "Tema", "Detalle"]
    anchos = [14, 30, 130]
    for col, ancho in enumerate(anchos, start=1):
        hoja.column_dimensions[get_column_letter(col)].width = ancho
    encabezado_tabla(hoja, 1, titulos)
    fila = 1
    for integracion in integraciones:
        filas = [
            ("Endpoint", integracion.get("endpoint")),
            ("Autenticación", integracion.get("autenticacion")),
            ("Qué la dispara en LDCOM", integracion.get("dispara")),
            ("Cuándo se envía", integracion.get("cuando_se_envia")),
            ("Fuente de la documentación", integracion.get("fuente_documentacion")),
            ("Notas", integracion.get("notas_generales")),
        ] + [(r["tema"], r["regla"]) for r in integracion.get("reglas") or []]
        for tema, detalle in filas:
            if not detalle:
                continue
            fila += 1
            valores = [integracion["codigo"], tema, detalle]
            for col, valor in enumerate(valores, start=1):
                celda = hoja.cell(row=fila, column=col, value=valor)
                celda.alignment = AJUSTE
                celda.border = BORDE
                if fila % 2 == 1:
                    celda.fill = RELLENO_ALTERNO
            hoja.cell(row=fila, column=2).font = Font(name="Calibri", bold=True)
            hoja.row_dimensions[fila].height = altura_fila(valores, anchos)
    hoja.auto_filter.ref = f"A1:C{max(fila, 2)}"
    hoja.freeze_panes = "A2"
    hoja.sheet_properties.tabColor = "7F7F7F"


def hoja_preguntas(libro, integraciones):
    hoja = libro.create_sheet("Preguntas a Dos Pinos")
    hoja.sheet_view.showGridLines = False
    titulos = ["Integración", "N.º", "Tema", "Pregunta", "Campos que afecta", "Respuesta de Dos Pinos"]
    anchos = [14, 6, 34, 80, 34, 40]
    for col, ancho in enumerate(anchos, start=1):
        hoja.column_dimensions[get_column_letter(col)].width = ancho
    encabezado_tabla(hoja, 1, titulos)
    fila = 1
    for integracion in integraciones:
        for pregunta in integracion.get("preguntas") or []:
            fila += 1
            valores = [integracion["codigo"], pregunta.get("numero"), pregunta.get("tema"),
                       pregunta.get("pregunta"), pregunta.get("campos"), pregunta.get("respuesta", "")]
            for col, valor in enumerate(valores, start=1):
                celda = hoja.cell(row=fila, column=col, value=valor)
                celda.alignment = AJUSTE
                celda.border = BORDE
                if fila % 2 == 1:
                    celda.fill = RELLENO_ALTERNO
            hoja.cell(row=fila, column=1).font = Font(name="Calibri", bold=True)
            hoja.cell(row=fila, column=2).alignment = Alignment(horizontal="center", vertical="top")
            hoja.row_dimensions[fila].height = altura_fila(valores, anchos)
    hoja.auto_filter.ref = f"A1:{get_column_letter(len(titulos))}{max(fila, 2)}"
    hoja.freeze_panes = "A2"
    hoja.sheet_properties.tabColor = "C00000"


def leer_agregado_a_mano(nombres_generados):
    """Imágenes de cada hoja y hojas enteras que la gente agregó al Excel: el json no las tiene."""
    if not os.path.exists(SALIDA):
        return {}, []
    anterior = load_workbook(SALIDA)
    imagenes = {hoja.title: list(hoja._images) for hoja in anterior.worksheets if hoja._images}
    hojas_propias = [hoja for hoja in anterior.worksheets if hoja.title.lower() not in nombres_generados]
    return imagenes, hojas_propias


def pegar_imagenes(hoja, imagenes):
    for original in imagenes:
        nueva = Image(io.BytesIO(original._data()))
        nueva.anchor = original.anchor
        nueva.width, nueva.height = original.width, original.height
        hoja.add_image(nueva)


def copiar_hoja_propia(libro, origen):
    destino = libro.create_sheet(origen.title)
    for fila in origen.iter_rows():
        for celda in fila:
            if celda.value is None and not celda.has_style:
                continue
            nueva = destino.cell(row=celda.row, column=celda.column, value=celda.value)
            if celda.has_style:
                nueva.font, nueva.fill, nueva.border = copy(celda.font), copy(celda.fill), copy(celda.border)
                nueva.alignment, nueva.number_format = copy(celda.alignment), celda.number_format
    for letra, dimension in origen.column_dimensions.items():
        destino.column_dimensions[letra].width = dimension.width
    for numero, dimension in origen.row_dimensions.items():
        destino.row_dimensions[numero].height = dimension.height
    for rango in origen.merged_cells.ranges:
        destino.merge_cells(str(rango))


def main():
    integraciones = []
    for ruta in sorted(glob.glob(os.path.join(CARPETA, "*.json"))):
        if os.path.basename(ruta) == ARCHIVO_AVANCE:
            continue
        with open(ruta, encoding="utf-8") as archivo:
            integraciones.append(json.load(archivo))
    if not integraciones:
        raise SystemExit("No hay archivos .json de integraciones en la carpeta.")

    libro = Workbook()
    usados = {"avance", "indice", "variables", "reglas", "preguntas a dos pinos"}
    nombres = [nombre_hoja(i["codigo"], usados) for i in integraciones]
    imagenes, hojas_propias = leer_agregado_a_mano(usados)
    hoja_indice(libro, integraciones, nombres)
    hoja_variables(libro, integraciones)
    for integracion, nombre in zip(integraciones, nombres):
        hoja_integracion(libro, integracion, nombre)
    hoja_reglas(libro, integraciones)
    hoja_preguntas(libro, integraciones)
    ruta_avance = os.path.join(CARPETA, ARCHIVO_AVANCE)
    if os.path.exists(ruta_avance):
        with open(ruta_avance, encoding="utf-8") as archivo:
            hoja_avance(libro, json.load(archivo))
    for hoja in hojas_propias:
        copiar_hoja_propia(libro, hoja)
    for nombre, imagenes_hoja in imagenes.items():
        if nombre in libro.sheetnames:
            pegar_imagenes(libro[nombre], imagenes_hoja)
        else:
            print(f"Aviso: la hoja '{nombre}' ya no existe; sus {len(imagenes_hoja)} imagen(es) no se conservaron.")
    try:
        libro.save(SALIDA)
    except PermissionError:
        raise SystemExit(f"No se pudo guardar {SALIDA}: ciérrelo en Excel y vuelva a correr el script.")
    print(f"Generado {SALIDA} con {len(integraciones)} integración(es).")


if __name__ == "__main__":
    main()
