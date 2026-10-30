import glob, json, os, re, sys
import yaml

sys.stdout.reconfigure(encoding='utf8', errors='replace')
RAIZ = r'C:\FUENTES\DP\Postman_LDCOM13_DOSPINOS\Dos Pinos API\POS-10 Autorizar Venta Financiada (SFA15)'

for archivo in sorted(glob.glob(os.path.join(RAIZ, '*', '[DE]0*.yml'))):
    datos = yaml.safe_load(open(archivo, encoding='utf8'))
    ejemplos = datos.get('examples') or []
    print(f'\n## {os.path.basename(archivo)[:-4]}  (ejemplos guardados: {len(ejemplos)}, archivo modificado {os.path.getmtime(archivo):.0f})')
    for i, ejemplo in enumerate(ejemplos):
        respuesta = ejemplo.get('response') or {}
        cuerpo = respuesta.get('body')
        texto = cuerpo.get('data') if isinstance(cuerpo, dict) else cuerpo
        try:
            j = json.loads(texto) if texto else {}
        except Exception:
            j = None
        nombre = ejemplo.get('name', '')
        print(f'  [{i}] {nombre} -> HTTP {respuesta.get("status")} {respuesta.get("statusText", "")}')
        if j is None:
            print('     ', re.sub(r'\s+', ' ', str(texto))[:400])
        elif 'error' in j:
            print('      [formato error]', json.dumps(j['error'], ensure_ascii=False)[:400])
        elif j:
            r = j.get('Respuesta') or {}
            if str(r.get('indEstado') or '').strip().upper() == 'A':
                print('      APROBADA', json.dumps(r, ensure_ascii=False), '|', j.get('Mensaje'))
            else:
                print('     ', j.get('CodigoError'), j.get('TipoError'), '| HttpStatus', j.get('HttpStatus'))
                for linea in j.get('DetalleTransaccion') or [j.get('Mensaje')]:
                    print('       -', linea)
