import os, re

RAIZ = r'C:\FUENTES\DP\Postman_LDCOM13_DOSPINOS\Dos Pinos API\POS-10 Autorizar Venta Financiada (SFA15)'
AMBIENTE = r'C:\FUENTES\DP\Postman_LDCOM13_DOSPINOS\environments\UAT Dos Pinos.yml'
os.chdir(RAIZ)

SIN_CREDITO = '3 Dudas pendientes (no crean credito)'
CON_CREDITO = '4 Dudas pendientes (crean credito de 1 colon)'

BASE = [
    ('codEmpresa', '"{{sfa15CodEmpresa}}"'), ('codAgencia', '"{{sfa15CodAgencia}}"'),
    ('codTipoId', '""'), ('numId', '""'), ('codCliente', '"{{sfa15ClienteUnaFinca}}"'),
    ('fecSolicitud', '"{{sfa15FecSolicitud}}"'), ('nomAutorizado', '"PRUEBA LDCOM QA"'),
    ('codTipoIdAu', '""'), ('numIdAu', '""'), ('indUsaLinea', '"S"'), ('numLinea', '0'),
    ('idExterno', '""'), ('codUnidadCosto', '"99999999"'), ('numConvenio', '""'),
    ('plazoCredito', '{{sfa15PlazoCredito}}'), ('tipCredito', '{{sfa15TipCredito}}'),
    ('monSolicitud', '{{sfa15MonSolicitud}}'), ('observaciones', '"PRUEBA LDCOM QA"'),
    ('codUsuario', '"INTEGRACIONSFA"'),
]

RESUMEN = """const b = res.body || {};
const detalle = Array.isArray(b.DetalleTransaccion) ? b.DetalleTransaccion : [];
const errorEntrada = b.error ? `${b.error.message || ''} (${(b.error.detail && b.error.detail.code) || '-'})` : '';
const estado = b.Respuesta ? String(b.Respuesta.indEstado || '').trim().toUpperCase() : '';
const aprobada = estado === 'A';
const texto = aprobada ? `APROBADA: solicitud ${b.Respuesta.numSolicitud}, credito ${b.Respuesta.numCredito}`
  : estado === 'R' ? `RECHAZADA (indEstado R): solicitud ${b.Respuesta.numSolicitud}`
  : detalle.length ? detalle.join(' | ') : errorEntrada || `HTTP ${res.status}`;
const menciona = (patron) => detalle.some((linea) => patron.test(linea));"""


def sangrar(texto, espacios):
    return texto.replace('\n', '\n' + ' ' * espacios)


def carpeta(nombre, seq):
    os.makedirs(nombre, exist_ok=True)
    with open(os.path.join(nombre, 'folder.yml'), 'w', encoding='utf-8', newline='') as f:
        f.write(f"info:\n  name: {nombre}\n  type: folder\n  seq: {seq}\n\nrequest:\n  auth: inherit\n")


def request(destino, archivo, nombre, seq, cambios, docs, pruebas, url_base='{{sfa15BaseUrl}}'):
    campos = [(k, cambios.get(k, v)) for k, v in BASE]
    datos = ',\n'.join(f'    "{k}": {v}' for k, v in campos)
    cuerpo = ('{\n  "Datos_Entrada": {\n' + datos + '\n  },\n'
              '  "Usuario": "{{sfa15BodyUsername}}",\n  "Contraseña": "{{sfa15BodyPassword}}"\n}')
    contenido = (
        f'info:\n  name: {nombre}\n  type: http\n  seq: {seq}\n\n'
        f'http:\n  method: POST\n  url: "{url_base}/p_SFA15_Autorizacion_Venta_Final"\n'
        '  headers:\n    - name: Content-Type\n      value: application/json\n'
        '  body:\n    type: json\n    data: |-\n      ' + sangrar(cuerpo, 6) + '\n'
        '  auth:\n    type: basic\n    username: "{{sfa15BasicUsername}}"\n    password: "{{sfa15BasicPassword}}"\n\n'
        'runtime:\n  scripts:\n    - type: tests\n      code: |-\n        ' + sangrar(RESUMEN + '\n' + pruebas, 8) + '\n\n'
        'settings:\n  encodeUrl: true\n  timeout: 40000\n  followRedirects: true\n  maxRedirects: 5\n\n'
        'docs: |\n  ' + sangrar(docs, 2) + '\n'
    )
    with open(os.path.join(destino, archivo), 'w', encoding='utf-8', newline='') as f:
        f.write(contenido)


SEGURO = ("No crea credito: lleva la unidad de costo 99999999 (no existe), asi SFA siempre devuelve un error de negocio. "
          "Usa el cliente 4000010 (real, con linea de credito) para que SFA valide todo lo demas.")
SIN = 'test("No se creo credito", () => { expect(aprobada).to.equal(false); });\ntest(`SFA respondio: ${texto}`, () => {});'

carpeta(SIN_CREDITO, 4)
request(SIN_CREDITO, 'P01 Plazo 1.yml', 'P01 Plazo 1', 1, {'plazoCredito': '1'},
        "Rango del plazo: con 24 SFA no se quejo. Si con 1 dice 'El plazo del credito no se encuentra dentro del rango configurado', "
        "el minimo esta por encima de 1.\n" + SEGURO,
        SIN + '\ntest("Plazo 1: " + (menciona(/plazo/i) ? "FUERA del rango" : "dentro del rango"), () => {});')
request(SIN_CREDITO, 'P02 Plazo 168 (24 semanas x 7).yml', 'P02 Plazo 168 (24 semanas x 7)', 2, {'plazoCredito': '168'},
        "Si SFA espera dias, 24 semanas son 168 dias. Comparar con P01 y P03 para ubicar el rango configurado del tipo de credito.\n" + SEGURO,
        SIN + '\ntest("Plazo 168: " + (menciona(/plazo/i) ? "FUERA del rango" : "dentro del rango"), () => {});')
request(SIN_CREDITO, 'P03 Plazo 9999.yml', 'P03 Plazo 9999', 3, {'plazoCredito': '9999'},
        "Plazo muy alto, para confirmar que SFA si valida un maximo.\n" + SEGURO,
        SIN + '\ntest("Plazo 9999: " + (menciona(/plazo/i) ? "FUERA del rango" : "dentro del rango"), () => {});')
request(SIN_CREDITO, 'P04 Probar agencia (variable).yml', 'P04 Probar agencia (cambiar sfa15AgenciaPrueba)', 4,
        {'codAgencia': '"{{sfa15AgenciaPrueba}}"'},
        "Para descubrir agencias validas mientras llega el catalogo: cambiar sfa15AgenciaPrueba en el ambiente (002, 003, 010, 1501...) y enviar. "
        "Si el detalle NO dice 'La agencia X no existe', la agencia existe en SFA.\n" + SEGURO,
        SIN + '\ntest("Agencia " + bru.getEnvVar("sfa15AgenciaPrueba") + ": " + (menciona(/agencia/i) ? "NO existe" : "EXISTE"), () => {});')
request(SIN_CREDITO, 'P05 Probar tipo de credito (variable).yml', 'P05 Probar tipo de credito (cambiar sfa15TipCreditoPrueba)', 5,
        {'tipCredito': '{{sfa15TipCreditoPrueba}}'},
        "Para descubrir tipos de credito validos: cambiar sfa15TipCreditoPrueba (202, 101, 301...) y enviar. Si el detalle no menciona el tipo de "
        "credito, existe y tiene rubros, desembolso y plazo configurados.\n" + SEGURO,
        SIN + '\ntest("Tipo de credito " + bru.getEnvVar("sfa15TipCreditoPrueba") + ": " + (menciona(/tipo de cr.dito/i) ? "con problemas: ver detalle" : "valido"), () => {});')
request(SIN_CREDITO, 'P06 Monto con 3 decimales.yml', 'P06 Monto con 3 decimales (1.555)', 6, {'monSolicitud': '1.555'},
        "El contrato dice monto 16.2. Ver si SFA rechaza mas de 2 decimales o los redondea.\n" + SEGURO,
        SIN + '\ntest("Monto 1.555: " + (menciona(/monto/i) ? "rechazado" : "aceptado"), () => {});')

AVISO = ("CREA UN CREDITO REAL de 1 colon en el SFA de pruebas si SFA acepta la solicitud. Usa sfa15BaseUrlExitosas: "
         "vaciar esa variable para bloquearlo.")
CON = 'test(`SFA respondio: ${texto}`, () => {});'

carpeta(CON_CREDITO, 5)
request(CON_CREDITO, 'C01 Sin linea de credito, indUsaLinea N.yml', 'C01 Asociado sin linea de credito con indUsaLinea N', 1,
        {'codCliente': '"{{sfa15ClienteVariasFincas}}"', 'codUnidadCosto': '"{{sfa15FincaVariasFincas}}"', 'indUsaLinea': '"N"'},
        AVISO + "\nEl asociado 4000393 fue rechazado con indUsaLinea S por no tener linea principal (E02). Aqui se envia N: dice si un asociado "
        "sin linea puede financiar sin usarla, o si el tipo de credito obliga a tener linea.",
        CON, '{{sfa15BaseUrlExitosas}}')
request(CON_CREDITO, 'C02 idExterno primer envio.yml', 'C02 idExterno fijo: primer envio', 2,
        {'codUnidadCosto': '"{{sfa15FincaUnaFinca}}"', 'idExterno': '"{{sfa15IdExternoPrueba}}"'},
        AVISO + "\nPrimer envio con un idExterno fijo (sfa15IdExternoPrueba). Luego correr C03 con el mismo valor.",
        CON, '{{sfa15BaseUrlExitosas}}')
request(CON_CREDITO, 'C03 idExterno repetido.yml', 'C03 idExterno fijo: segundo envio (repetido)', 3,
        {'codUnidadCosto': '"{{sfa15FincaUnaFinca}}"', 'idExterno': '"{{sfa15IdExternoPrueba}}"'},
        AVISO + "\nMismo idExterno que C02. Si SFA lo rechaza por duplicado, podemos usar idExterno como proteccion contra doble envio "
        "(doble clic o reintento tras un timeout). Si lo aprueba de nuevo, SFA no protege y la guarda tiene que estar en LDCOM/Integrations.",
        CON + '\ntest("idExterno repetido: " + (aprobada ? "SFA LO ACEPTO (no protege contra duplicados)" : "SFA lo rechazo"), () => {});',
        '{{sfa15BaseUrlExitosas}}')

with open(AMBIENTE, encoding='utf-8') as f:
    ambiente = f.read()
nuevas = [('sfa15AgenciaPrueba', '002'), ('sfa15TipCreditoPrueba', '202'), ('sfa15IdExternoPrueba', 'LDQA-DUP-0001')]
agregar = ''.join(f'  - name: {n}\n    value: "{v}"\n' for n, v in nuevas if f'name: {n}\n' not in ambiente)
if agregar:
    with open(AMBIENTE, 'w', encoding='utf-8', newline='') as f:
        f.write(ambiente.rstrip('\n') + '\n' + agregar)
print('listo')
