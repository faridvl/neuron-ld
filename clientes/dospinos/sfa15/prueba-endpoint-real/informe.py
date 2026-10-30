import glob, json, re, sys, os
sys.stdout.reconfigure(encoding='utf8', errors='replace')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Error que debe aparecer en DetalleTransaccion (o en el formato error) para considerar que SFA valido ese campo.
ESPERADO = {
    'S01': 'identificación o el código del cliente', 'S02': 'identificación o el código del cliente',
    'S03': 'identificación', 'S05': 'identificación',
    'A01': 'agencia 1501', 'A02': 'agencia 5100', 'A04': 'agencia AV-GUAYABO', 'A05': 'codAgencia', 'A06': 'agencia 99999',
    'E01': 'empresa CR01', 'E02': 'codEmpresa', 'E03': 'empresa 999',
    'P01': 'plazo', 'P02': 'plazo', 'P03': 'plazo', 'P04': 'plazo', 'P05': 'plazo',
    'T01': 'tipo de crédito 999', 'T02': 'tipo de crédito 0', 'T03': 'tipo de crédito',
    'M01': 'monto', 'M02': 'monto', 'M03': 'monto', 'M04': 'monto',
    'F01': 'fecha', 'F02': 'fecSolicitud', 'F03': 'codUsuario', 'F04': 'codUnidadCosto', 'F05': 'idExterno',
    'F06': 'unidad de costo', 'F07': 'nomAutorizado',
}

def cargar():
    # el JSON mas reciente de la corrida normal (la del tier2 va aparte)
    archivos = sorted(glob.glob('resultados-*.json'), key=os.path.getmtime)
    corridas = [json.load(open(a, encoding='utf8')) for a in archivos]
    normales = [c for c in corridas if any(r['id'] == 'S01' for r in c['resultados']) and not any(r['id'].startswith('X') for r in c['resultados'])]
    tier2 = [c for c in corridas if any(r['id'].startswith('X') for r in c['resultados'])]
    return (normales[-1] if normales else None), (tier2[-1] if tier2 else None)

def lineas(r):
    try:
        j = json.loads(r['cuerpo'])
    except Exception:
        return [r['resumen']]
    if 'error' in j:
        d = j['error'].get('detail', {})
        return [f"[formato error] {d.get('reason') or j['error'].get('message')} (code: {d.get('code') or '-'})"]
    if j.get('DetalleTransaccion'):
        return j['DetalleTransaccion']
    if j.get('Respuesta', {}).get('indEstado'):
        return [f"APROBADA: {j.get('Mensaje')} (solicitud {j['Respuesta'].get('numSolicitud')}, crédito {j['Respuesta'].get('numCredito')})"]
    return [r['resumen']]

normal, tier2 = cargar()
out = ['# Informe: batería de QA SFA15 contra el simulador (2026-10-28)', '',
       'Simulador en http://localhost:7390 (pestaña SFA15). Cada fila muestra la lista COMPLETA de errores que devuelve; ✔ = el error esperado aparece, ✘ = el simulador no lo valida.', '']
fallos = []
for titulo, corrida in (('Batería normal (sin cliente real)', normal), ('Casos con cliente (--tier2; el simulador no valida tipo de crédito ni cliente salvo que se configure)', tier2)):
    if not corrida:
        continue
    out += [f'## {titulo}', '', '| Caso | HTTP | Qué pasa | Validado |', '|---|---|---|---|']
    for r in corrida['resultados']:
        txt = lineas(r)
        esp = ESPERADO.get(r['id'])
        marca = ''
        if esp:
            ok = any(esp.lower() in l.lower() for l in txt)
            marca = '✔' if ok else '✘'
            if not ok:
                fallos.append(r['id'])
        out.append(f"| {r['id']} {r['nombre']} | {r['http']} | " + '<br>'.join(l.replace('|', '/') for l in txt) + f" | {marca} |")
    out.append('')
out += ['## Casos donde el simulador no valida lo que el real sí (✘)', '', ', '.join(fallos) or 'ninguno', '']
open('informe-simulador.md', 'w', encoding='utf8').write('\n'.join(out))
print('casos ✘:', fallos)
print('filas:', sum(len(c['resultados']) for c in (normal, tier2) if c))
