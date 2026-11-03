"""Corre un recorrido del POS. Uso:
  python -I correr.py <pid> <recorrido> [--params JSON] [--capturas CARPETA]
  python -I correr.py --listar
  python -I correr.py <pid> --pasos '[["cambiar_cliente",{"codigo":"4000010"}],["facturar",{}]]'
Recorridos predefinidos en recorridos.py. Sale con código 1 si un paso falla."""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from poslib import base, orquestador  # noqa: E402
from poslib.flujos import REGISTRO  # noqa: E402
from recorridos import RECORRIDOS  # noqa: E402


def listar():
    print("Recorridos:")
    for nombre, funcion in RECORRIDOS.items():
        print("  %-26s %s" % (nombre, (funcion.__doc__ or "").strip().split(chr(10))[0]))
    print("Flujos:")
    for nombre, modulo in REGISTRO.items():
        print("  %-26s %s" % (nombre, modulo.PANTALLA))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pid", type=int, nargs="?")
    ap.add_argument("--listar", action="store_true", help="lista recorridos y flujos y sale (no toca el POS)")
    ap.add_argument("recorrido", nargs="?")
    ap.add_argument("--params", default="{}")
    ap.add_argument("--pasos")
    ap.add_argument("--capturas", default=os.path.join(os.getcwd(), "capturas"))
    ap.add_argument("--json", help="archivo donde guardar el informe")
    a = ap.parse_args()
    if a.listar:
        listar()
        return
    if a.pid is None:
        ap.error("falta el pid del POS (o --listar)")
    pasos = json.loads(a.pasos) if a.pasos else RECORRIDOS[a.recorrido](**json.loads(a.params))
    pos = base.Pos(a.pid, a.capturas)
    informe = orquestador.correr(pos, pasos, a.recorrido or "pasos")
    orquestador.imprimir(informe)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(informe, f, ensure_ascii=False, indent=1, default=str)
    sys.exit(0 if informe["ok"] else 1)


if __name__ == "__main__":
    main()
