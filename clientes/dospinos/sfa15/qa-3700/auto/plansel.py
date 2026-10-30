"""Selecciona la fila del plan por texto en Dgv_TiposCredito y Continuar. Uso: plansel.py <pid> <texto>"""
import sys, time
sys.path.insert(0, r"C:\Users\fvillacis\ClaudeLocalSession\sfa15\qa-3700\auto")
import w32, pos_ui
pid = int(sys.argv[1]); txt = sys.argv[2].upper()
h = w32.por_titulo(pid, "Seleccionar Tipo")
v = pos_ui.ventana_por_manejador(h)
ds = v.descendants()
filas = {}
for c in ds:
    n = c.window_text() or ""
    if n.startswith("Descripci") and " Row " in n:
        filas[int(n.rsplit(" ", 1)[1])] = c
for i in sorted(filas):
    try: print(i, filas[i].get_value())
    except Exception: print(i, "?")
    if txt in str(filas[i].get_value()).upper():
        print("elijo fila", i, flush=True)
        for c in ds:
            if (c.window_text() or "") == "Row %d" % i:
                try: c.select()
                except Exception: filas[i].click_input()
                break
        break
time.sleep(0.7)
w32.clic(h, "Continuar"); time.sleep(3)
for r in w32.snapshot(pid, "plan"): print(r, flush=True)
