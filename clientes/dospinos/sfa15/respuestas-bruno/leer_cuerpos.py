import glob, json, os, re, sys
import yaml

sys.stdout.reconfigure(encoding='utf8', errors='replace')
RAIZ = r'C:\FUENTES\DP\Postman_LDCOM13_DOSPINOS\Dos Pinos API\POS-10 Autorizar Venta Financiada (SFA15)'
CAMPOS = ['codEmpresa', 'codAgencia', 'codTipoId', 'numId', 'codCliente', 'codUnidadCosto',
          'plazoCredito', 'tipCredito', 'monSolicitud', 'codUsuario']

for archivo in sorted(glob.glob(os.path.join(RAIZ, '*', 'D0*.yml')) + glob.glob(os.path.join(RAIZ, '*', 'E0*.yml'))):
    nombre = os.path.basename(archivo)[:3]
    datos = yaml.safe_load(open(archivo, encoding='utf8'))
    ejemplo = (datos.get('examples') or [{}])[-1]
    cuerpo = (ejemplo.get('request') or {}).get('body')
    texto = cuerpo.get('data') if isinstance(cuerpo, dict) else (cuerpo or '')
    texto = re.sub(r'("Contrase.a"\s*:\s*)"[^"]*"', r'\1"***"', str(texto))
    print(f'\n{nombre} enviado:')
    encontrados = {c: (re.search(rf'"{c}"\s*:\s*("[^"]*"|[^,\n]*)', texto) or [None, None])[1] for c in CAMPOS}
    print('   ', encontrados)
    usuario = re.search(r'"Usuario"\s*:\s*("[^"]*"|[^,\n]*)', texto)
    print('    Usuario del cuerpo:', usuario.group(1) if usuario else None)
    actual = datos['http']['body']['data']
    hoy = {c: (re.search(rf'"{c}"\s*:\s*("[^"]*"|[^,\n]*)', actual) or [None, None])[1] for c in ['codTipoId', 'numId', 'codCliente']}
    print('    archivo hoy:', hoy)
