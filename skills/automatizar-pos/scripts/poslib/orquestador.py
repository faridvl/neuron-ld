"""Corre un recorrido: lista de pasos [(flujo, {parametros})], midiendo cada uno y capturando si uno falla."""
import json
import os
import time
import traceback

from . import base
from .flujos import REGISTRO


def correr(pos, pasos, nombre="recorrido", seguir_si_falla=False):
    """Devuelve {'ok': bool, 'total_s': float, 'pasos': [{flujo, params, s, ok, resultado|error, captura}]}.
    Se detiene en el primer paso fallido (deja captura de la principal y de cada modal abierta)."""
    informe = {"recorrido": nombre, "ok": True, "pasos": []}
    inicio = time.time()
    if not pos.conectado:
        t0 = time.time()
        pos.conectar()
        informe["pasos"].append({"flujo": "(ubicar controles UIA)", "s": round(time.time() - t0, 2), "ok": True})
    for numero, (flujo, parametros) in enumerate(pasos, 1):
        parametros = dict(parametros or {})
        registro = {"n": numero, "flujo": flujo, "params": parametros}
        if flujo == "leer_mensaje":
            parametros.setdefault("nombre", "%s-%02d-mensaje" % (nombre, numero))
        t0 = time.time()
        try:
            registro["resultado"] = REGISTRO[flujo].ejecutar(pos, **parametros)
            registro["ok"] = True
        except Exception as e:  # se reporta y se captura
            registro["ok"] = False
            registro["error"] = "%s: %s" % (type(e).__name__, e)
            registro["traza"] = traceback.format_exc(limit=3)
            capturas = []
            try:
                capturas.append(pos.captura("%s-%02d-%s-FALLO" % (nombre, numero, flujo)))
                for i, h in enumerate(base.modales(pos.pid)):
                    capturas.append(base.capturar(h, os.path.join(pos.capturas, "%s-%02d-%s-FALLO-modal%d.png" % (nombre, numero, flujo, i))))
            except Exception:
                pass
            registro["captura"] = [c for c in capturas if c]
            informe["ok"] = False
        registro["s"] = round(time.time() - t0, 2)
        informe["pasos"].append(registro)
        if not registro["ok"] and not seguir_si_falla:
            break
    informe["total_s"] = round(time.time() - inicio, 2)
    return informe


def imprimir(informe):
    print("Recorrido %s: %s en %.1f s" % (informe["recorrido"], "OK" if informe["ok"] else "FALLÓ", informe["total_s"]))
    for p in informe["pasos"]:
        marca = "ok " if p.get("ok") else "ERR"
        extra = p.get("error") or json.dumps(p.get("resultado", ""), ensure_ascii=False, default=str)[:140]
        print("  %s %5.2f s  %s %s" % (marca, p["s"], p["flujo"], extra))
