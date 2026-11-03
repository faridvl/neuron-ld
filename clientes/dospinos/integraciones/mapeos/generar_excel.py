"""Arma Mapeo-Integraciones-DosPinos.xlsx a partir de los *.json de esta carpeta.

Uso: python -I generar_excel.py
Cada integracion es un .json (ver README.md); no se edita el Excel a mano.
"""
import glob
import json
import os
import re

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

CARPETA = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(CARPETA, "Mapeo-Integraciones-DosPinos.xlsx")

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

COLUMNAS_CAMPOS = [
    ("Bloque", 18, "bloque"),
    ("Campo Dos Pinos", 20, "campo"),
    ("Tipo / largo / obligatorio (según su documento)", 24, "doc"),
    ("De dónde sale en LDCOM / qué mandamos", 46, "origen"),
    ("Qué significa (en palabras simples)", 52, "descripcion"),
    ("Ejemplo", 30, "ejemplo"),
    ("Estado", 22, "estado"),
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


def pendientes(integracion):
    return sum(1 for c in integracion["campos"] if c.get("estado") in ESTADOS_PENDIENTES)


def hoja_integracion(libro, integracion, nombre):
    hoja = libro.create_sheet(nombre)
    hoja.sheet_view.showGridLines = False
    for col, (_, ancho, _) in enumerate(COLUMNAS_CAMPOS, start=1):
        hoja.column_dimensions[get_column_letter(col)].width = ancho
    ultima = len(COLUMNAS_CAMPOS)

    hoja.cell(row=1, column=1, value=f"{integracion['codigo']} - {integracion['nombre']}").font = Font(
        name="Calibri", bold=True, size=16, color=AZUL_OSCURO)
    hoja.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ultima)

    metadatos = [
        ("Sentido", integracion.get("sentido")),
        ("Endpoint", integracion.get("endpoint")),
        ("Autenticación", integracion.get("autenticacion")),
        ("Qué la dispara en LDCOM", integracion.get("dispara")),
        ("Cuándo se envía", integracion.get("cuando_se_envia")),
        ("Fuente de la documentación", integracion.get("fuente_documentacion")),
        ("Estado general", integracion.get("estado_general")),
        ("Notas", integracion.get("notas_generales")),
    ]
    fila = 3
    for etiqueta, valor in metadatos:
        if not valor:
            continue
        titulo = hoja.cell(row=fila, column=1, value=etiqueta)
        titulo.font = Font(name="Calibri", bold=True, color=AZUL_OSCURO)
        titulo.alignment = AJUSTE
        titulo.fill = RELLENO_ALTERNO
        titulo.border = BORDE
        hoja.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=2)
        contenido = hoja.cell(row=fila, column=3, value=valor)
        contenido.alignment = AJUSTE
        contenido.border = BORDE
        if etiqueta == "Estado general":
            pintar_estado(contenido, valor)
            contenido.alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")
        hoja.merge_cells(start_row=fila, start_column=3, end_row=fila, end_column=ultima)
        ancho_total = sum(c[1] for c in COLUMNAS_CAMPOS[2:])
        hoja.row_dimensions[fila].height = altura_fila([valor], [ancho_total])
        fila += 1

    fila += 1
    reglas = integracion.get("reglas") or []
    if reglas:
        titulo = hoja.cell(row=fila, column=1, value="Reglas")
        titulo.font = Font(name="Calibri", bold=True, size=13, color=AZUL_OSCURO)
        fila += 1
        for col, texto_col in ((1, "Tema"), (3, "Regla")):
            celda = hoja.cell(row=fila, column=col, value=texto_col)
        for col in range(1, ultima + 1):
            celda = hoja.cell(row=fila, column=col)
            celda.fill = RELLENO_ENCABEZADO
            celda.font = LETRA_BLANCA
            celda.border = BORDE
        hoja.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=2)
        hoja.merge_cells(start_row=fila, start_column=3, end_row=fila, end_column=ultima)
        fila += 1
        ancho_regla = sum(c[1] for c in COLUMNAS_CAMPOS[2:])
        for indice, regla in enumerate(reglas):
            tema = hoja.cell(row=fila, column=1, value=regla["tema"])
            tema.font = Font(name="Calibri", bold=True)
            cuerpo = hoja.cell(row=fila, column=3, value=regla["regla"])
            for col in range(1, ultima + 1):
                celda = hoja.cell(row=fila, column=col)
                celda.alignment = AJUSTE
                celda.border = BORDE
                if indice % 2 == 1:
                    celda.fill = RELLENO_ALTERNO
            hoja.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=2)
            hoja.merge_cells(start_row=fila, start_column=3, end_row=fila, end_column=ultima)
            hoja.row_dimensions[fila].height = altura_fila([regla["regla"]], [ancho_regla])
            fila += 1
        fila += 1

    titulo = hoja.cell(row=fila, column=1, value="Campos mapeados")
    titulo.font = Font(name="Calibri", bold=True, size=13, color=AZUL_OSCURO)
    fila += 1
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
        hoja.cell(row=fila, column=9).alignment = Alignment(horizontal="center", vertical="top")
        pintar_estado(hoja.cell(row=fila, column=7), campo.get("estado"))
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


def main():
    integraciones = []
    for ruta in sorted(glob.glob(os.path.join(CARPETA, "*.json"))):
        with open(ruta, encoding="utf-8") as archivo:
            integraciones.append(json.load(archivo))
    if not integraciones:
        raise SystemExit("No hay archivos .json de integraciones en la carpeta.")

    libro = Workbook()
    usados = {"indice", "preguntas a dos pinos"}
    nombres = [nombre_hoja(i["codigo"], usados) for i in integraciones]
    hoja_indice(libro, integraciones, nombres)
    for integracion, nombre in zip(integraciones, nombres):
        hoja_integracion(libro, integracion, nombre)
    hoja_preguntas(libro, integraciones)
    libro.save(SALIDA)
    print(f"Generado {SALIDA} con {len(integraciones)} integración(es).")


if __name__ == "__main__":
    main()
