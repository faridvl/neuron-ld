import os, sys

RAIZ = r'C:\FUENTES\DP\Postman_LDCOM13_DOSPINOS\Dos Pinos API\POS-10 Autorizar Venta Financiada (SFA15)'
os.chdir(RAIZ)

DUDAS = '1 Dudas (no crean credito)'
EXITOSAS = '2 Exitosas (desembolsan - solo con OK de Dos Pinos)'


def carpeta(nombre, seq):
    os.makedirs(nombre, exist_ok=True)
    with open(os.path.join(nombre, 'folder.yml'), 'w', encoding='utf-8', newline='') as f:
        f.write(f"info:\n  name: {nombre}\n  type: folder\n  seq: {seq}\n\nrequest:\n  auth: inherit\n")


BASE = [
    ('codEmpresa', '"{{sfa15CodEmpresa}}"'), ('codAgencia', '"{{sfa15CodAgencia}}"'),
    ('codTipoId', '""'), ('numId', '""'), ('codCliente', '""'),
    ('fecSolicitud', '"{{sfa15FecSolicitud}}"'), ('nomAutorizado', '"PRUEBA LDCOM QA"'),
    ('codTipoIdAu', '""'), ('numIdAu', '""'), ('indUsaLinea', '"S"'), ('numLinea', '0'),
    ('idExterno', '""'), ('codUnidadCosto', '"{{sfa15CodUnidadCosto}}"'), ('numConvenio', '""'),
    ('plazoCredito', '{{sfa15PlazoCredito}}'), ('tipCredito', '{{sfa15TipCredito}}'),
    ('monSolicitud', '{{sfa15MonSolicitud}}'), ('observaciones', '"PRUEBA LDCOM QA"'),
    ('codUsuario', '"INTEGRACIONSFA"'),
]
INEXISTENTE = {'codTipoId': '"CEDPF"', 'numId': '"000000000"'}

RESUMEN = """const b = res.body || {};
const detalle = Array.isArray(b.DetalleTransaccion) ? b.DetalleTransaccion : [];
const errorEntrada = b.error ? `${b.error.message || ''} (${(b.error.detail && b.error.detail.code) || '-'})` : '';
const aprobada = !!(b.Respuesta && String(b.Respuesta.indEstado || '').trim().toUpperCase() === 'A');
const texto = aprobada ? `APROBADA: solicitud ${b.Respuesta.numSolicitud}, credito ${b.Respuesta.numCredito}`
  : detalle.length ? detalle.join(' | ') : errorEntrada || `HTTP ${res.status}`;"""

GUARDIA = """if (bru.getEnvVar("sfa15PermitirDesembolso") !== "SI") {
  throw new Error("Bloqueado: este escenario puede crear un credito real. Poner sfa15PermitirDesembolso = SI en el ambiente solo con el OK de Dos Pinos.");
}"""


def sangrar(texto, espacios):
    return texto.replace('\n', '\n' + ' ' * espacios)


def request(carpeta_destino, archivo, nombre, seq, cambios, docs, pruebas, con_guardia=False):
    campos = [(k, cambios.get(k, v)) for k, v in BASE]
    datos = ',\n'.join(f'    "{k}": {v}' for k, v in campos)
    cuerpo = ('{\n  "Datos_Entrada": {\n' + datos + '\n  },\n'
              '  "Usuario": "{{sfa15BodyUsername}}",\n  "Contraseña": "{{sfa15BodyPassword}}"\n}')
    scripts = ''
    if con_guardia:
        scripts += '    - type: before-request\n      code: |-\n        ' + sangrar(GUARDIA, 8) + '\n'
    scripts += '    - type: tests\n      code: |-\n        ' + sangrar(RESUMEN + '\n' + pruebas, 8) + '\n'
    contenido = (
        f'info:\n  name: {nombre}\n  type: http\n  seq: {seq}\n\n'
        'http:\n  method: POST\n  url: "{{sfa15BaseUrl}}/p_SFA15_Autorizacion_Venta_Final"\n'
        '  headers:\n    - name: Content-Type\n      value: application/json\n'
        '  body:\n    type: json\n    data: |-\n      ' + sangrar(cuerpo, 6) + '\n'
        '  auth:\n    type: basic\n    username: "{{sfa15BasicUsername}}"\n    password: "{{sfa15BasicPassword}}"\n\n'
        'runtime:\n  scripts:\n' + scripts + '\n'
        'settings:\n  encodeUrl: true\n  timeout: 40000\n  followRedirects: true\n  maxRedirects: 5\n\n'
        'docs: |\n  ' + sangrar(docs, 2) + '\n'
    )
    with open(os.path.join(carpeta_destino, archivo), 'w', encoding='utf-8', newline='') as f:
        f.write(contenido)


carpeta(DUDAS, 2)
carpeta(EXITOSAS, 3)

NO_CREDITO = ('test("No se creo credito", () => { expect(aprobada).to.equal(false); });\n'
              'test(`SFA respondio: ${texto}`, () => {});')

request(DUDAS, 'D01 Valores del PDF con identificacion inexistente.yml', 'D01 Valores del PDF con identificacion inexistente', 1,
        dict(INEXISTENTE),
        "Empresa, agencia, finca, plazo, tipo de credito y monto del ejemplo del PDF, con una identificacion que no existe "
        "(CEDPF 000000000). SFA valida todo y devuelve los errores juntos: lo que NO aparezca en el detalle es un valor que SFA acepta.\n"
        "Si responde 'Error tecnico en la autenticacion', el Usuario/Contraseña del cuerpo no son validos.",
        NO_CREDITO + '\ntest("SFA llego a validar las reglas (hay DetalleTransaccion)", () => { expect(detalle.length).to.be.above(0); });')

request(DUDAS, 'D02 Todo malo a la vez.yml', 'D02 Todo malo a la vez (agencia 1501, tipo 999, plazo 0, monto 0, finca 99999999)', 2,
        dict(INEXISTENTE, codAgencia='"1501"', tipCredito='999', plazoCredito='0', monSolicitud='0', codUnidadCosto='"99999999"'),
        "Varios campos malos en una sola llamada: cada linea del detalle nombra el campo que fallo. La agencia 1501 es la sucursal SAP AGV Guayabo.",
        NO_CREDITO
        + '\ntest("Agencia 1501 (sucursal SAP): " + (detalle.some(l => /agencia 1501/i.test(l)) ? "NO existe en SFA" : "EXISTE en SFA"), () => {});'
        + '\ntest("Tipo de credito 999: " + (detalle.some(l => /tipo de cr.dito 999/i.test(l)) ? "rechazado" : "no se valido"), () => {});')

request(DUDAS, 'D03 Agencia 5100 (almacen SAP).yml', 'D03 Agencia 5100 (almacen SAP)', 3,
        dict(INEXISTENTE, codAgencia='"5100"'),
        "Prueba si el codigo de almacen SAP (5100, Alm. AGV General) es una agencia valida en SFA.",
        NO_CREDITO + '\ntest("Agencia 5100: " + (detalle.some(l => /agencia 5100/i.test(l)) ? "NO existe en SFA" : "EXISTE en SFA"), () => {});')

request(DUDAS, 'D04 Empresa CR01.yml', 'D04 Empresa CR01 (constante del xlsx)', 4,
        dict(INEXISTENTE, codEmpresa='"CR01"'),
        "El xlsx dice codEmpresa constante CR01; el PDF muestra que se rechaza. Confirma con el servicio real.",
        NO_CREDITO + '\ntest("Empresa CR01: " + (detalle.some(l => /empresa CR01/i.test(l)) ? "NO existe (usar 001)" : "EXISTE"), () => {});')

request(DUDAS, 'D05 Sin cliente ni identificacion.yml', 'D05 Sin cliente ni identificacion', 5, {},
        "Sin codCliente, codTipoId ni numId: el filtro de entrada responde HTTP 500 'Debe indicar la identificacion o el codigo del cliente' "
        "antes de autenticar contra SFA.",
        NO_CREDITO + '\ntest("Responde el filtro de entrada", () => { expect(errorEntrada).to.match(/identificaci/i); });')

AVISO = ("PUEDE CREAR UN CREDITO REAL (SFA15 inserta, aprueba y desembolsa). Bloqueado mientras sfa15PermitirDesembolso no sea SI.\n"
         "Datos de Docker Staging (ver ClaudeLocalSession\\sfa15\\datos-staging-escenarios-bruno.md).")
APROBADA = ('test(`SFA respondio: ${texto}`, () => {});\n'
            'test("Credito aprobado", () => { expect(aprobada).to.equal(true); });')
RECHAZO = ('test(`SFA respondio: ${texto}`, () => {});\n'
           'test("Rechazo funcional (no aprobada)", () => { expect(aprobada).to.equal(false); expect(String(b.TipoError || "")).to.match(/funcional/i); });')

request(EXITOSAS, 'E01 Asociado con una finca.yml', 'E01 Asociado con una finca', 1,
        {'codCliente': '"{{sfa15ClienteUnaFinca}}"', 'codUnidadCosto': '"{{sfa15FincaUnaFinca}}"'},
        AVISO + "\nAsociado con exactamente una finca, enviando su finca. Esperado: aprobada con numSolicitud y numCredito.",
        APROBADA, True)
request(EXITOSAS, 'E02 Asociado con varias fincas.yml', 'E02 Asociado con varias fincas (una elegida)', 2,
        {'codCliente': '"{{sfa15ClienteVariasFincas}}"', 'codUnidadCosto': '"{{sfa15FincaVariasFincas}}"'},
        AVISO + "\nAsociado con 2 o mas fincas; se envia una (la que elegiria el cajero). Esperado: aprobada.",
        APROBADA, True)
request(EXITOSAS, 'E03 Asociado sin fincas.yml', 'E03 Asociado sin fincas (unidad de costo vacia)', 3,
        {'codCliente': '"{{sfa15ClienteSinFinca}}"', 'codUnidadCosto': '""'},
        AVISO + "\nEl caso de cerca del 80% de los asociados: dice si SFA aprueba con la unidad de costo vacia o que error devuelve.",
        'test(`SFA respondio: ${texto}`, () => {});', True)
request(EXITOSAS, 'E04 Asociado con finca ajena.yml', 'E04 Asociado con finca de otro asociado', 4,
        {'codCliente': '"{{sfa15ClienteUnaFinca}}"', 'codUnidadCosto': '"{{sfa15FincaAjena}}"'},
        AVISO + "\nFinca que pertenece a otro asociado. Esperado: rechazo 'La unidad de costo X no existe para el cliente Y'.",
        RECHAZO, True)
request(EXITOSAS, 'E05 Monto sobre el disponible.yml', 'E05 Monto sobre el disponible', 5,
        {'codCliente': '"{{sfa15ClienteUnaFinca}}"', 'codUnidadCosto': '"{{sfa15FincaUnaFinca}}"', 'monSolicitud': '{{sfa15MontoSobreDisponible}}'},
        AVISO + "\nMonto muy superior al disponible. Esperado: rechazo funcional 'no tiene disponible' "
        "(prueba FAC-0053: el POS debe mostrar 'Favor comunicarse con Servicios Financieros').",
        RECHAZO, True)

for viejo in ['SFA15 Sin asociado (debe rechazarse).yml', 'SFA15 Identificacion inexistente (errores acumulados).yml']:
    if os.path.exists(viejo):
        os.remove(viejo)

# Variables nuevas del ambiente (vacias; los datos de Staging se llenan despues)
AMBIENTE = r'C:\FUENTES\DP\Postman_LDCOM13_DOSPINOS\environments\UAT Dos Pinos.yml'
with open(AMBIENTE, encoding='utf-8') as f:
    ambiente = f.read()
nuevas = [('sfa15PermitirDesembolso', 'NO'), ('sfa15ClienteUnaFinca', ''), ('sfa15FincaUnaFinca', ''),
          ('sfa15ClienteVariasFincas', ''), ('sfa15FincaVariasFincas', ''), ('sfa15ClienteSinFinca', ''),
          ('sfa15FincaAjena', ''), ('sfa15MontoSobreDisponible', '999999999')]
agregar = ''.join(f'  - name: {n}\n    value: "{v}"\n' for n, v in nuevas if f'name: {n}\n' not in ambiente)
if agregar:
    if not ambiente.endswith('\n'):
        ambiente += '\n'
    with open(AMBIENTE, 'w', encoding='utf-8', newline='') as f:
        f.write(ambiente + agregar)
print('listo')
