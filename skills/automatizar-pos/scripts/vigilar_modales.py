"""Vigila las modales de un POS y guarda captura y texto de cada una (mensajes que se autocierran en segundos).
Uso: python -I vigilar_modales.py <pid> [segundos=30] [--capturas CARPETA]
No pulsa nada: solo observa. Imprime un JSON con titulo, textos y botones de cada ventana vista."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from poslib import modales  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pid", type=int)
    ap.add_argument("segundos", type=float, nargs="?", default=30)
    ap.add_argument("--capturas", default=os.path.join(os.getcwd(), "capturas"))
    a = ap.parse_args()
    print(json.dumps(modales.vigilar(a.pid, a.segundos, a.capturas), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
