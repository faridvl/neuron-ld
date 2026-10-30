"""Selecciona fila de una lista por texto y pulsa un boton, luego snapshot. Uso: listsel.py <pid> <titulo> <texto_fila> <boton> [espera]"""
import sys, time
sys.path.insert(0, r"C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\auto")
import w32
from pywinauto import Application
pid = int(sys.argv[1]); tit = sys.argv[2]; fila = sys.argv[3].upper(); btn = sys.argv[4]; espera = float(sys.argv[5]) if len(sys.argv) > 5 else 3
h = w32.por_titulo(pid, tit)
w = Application(backend="win32").connect(process=pid).window(handle=h)
lv = [c for c in w.children() if "SysListView32" in c.class_name()][0]
textos = lv.texts()[1:]
idx = next(i for i, t in enumerate(textos) if fila in (t or "").upper())
print("fila", idx, repr(textos[idx]), flush=True)
lv.select(idx); time.sleep(0.5)
w32.clic(h, btn); time.sleep(espera)
for r in w32.snapshot(pid, "ls"): print(r, flush=True)
