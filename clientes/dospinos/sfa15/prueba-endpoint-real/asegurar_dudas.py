# Las dudas usaban CEDPF 000000000 como "identificacion inexistente", pero SFA la resolvio a un cliente real (001100069709).
# Para que una duda nunca pueda crear un credito se agrega una unidad de costo que no existe (99999999): SFA la reporta en la
# etapa de reglas de negocio, junto con los demas errores, y con cualquier error no inserta la solicitud.
import os, re

RAIZ = r'C:\FUENTES\DP\Postman_LDCOM13_DOSPINOS\Dos Pinos API\POS-10 Autorizar Venta Financiada (SFA15)\1 Dudas (no crean credito)'
VENENO = '"codUnidadCosto": "99999999"'


def cambiar(nombre, reemplazos, docs_nuevo=None, nombre_nuevo=None):
    ruta = os.path.join(RAIZ, nombre)
    texto = open(ruta, encoding='utf-8').read()
    for viejo, nuevo in reemplazos:
        if viejo not in texto:
            raise SystemExit(f'{nombre}: no encontre {viejo!r}')
        texto = texto.replace(viejo, nuevo)
    if docs_nuevo:
        texto = re.sub(r'docs: \|\n(  .*\n?)*', 'docs: |\n  ' + docs_nuevo.replace('\n', '\n  ') + '\n', texto)
    if nombre_nuevo:
        texto = re.sub(r'(info:\n  name: ).*', r'\g<1>' + nombre_nuevo, texto, count=1)
    open(ruta, 'w', encoding='utf-8', newline='').write(texto)
    print('ok', nombre)


SEGURIDAD = ("Lleva la unidad de costo 99999999 (no existe) a proposito: asi SFA siempre devuelve un error de negocio y no puede crear "
             "el credito. La identificacion CEDPF 000000000 NO sirve sola para eso: el 2026-10-28 SFA la resolvio al cliente 001100069709.")

cambiar('D01 Valores del PDF con identificacion inexistente.yml',
        [('"codUnidadCosto": "{{sfa15CodUnidadCosto}}"', VENENO)],
        "Empresa 001, agencia 001, plazo 24, tipo de credito 201 y monto 1 (los del PDF). Las lineas del detalle que NO hablen de "
        "estos campos significan que SFA los acepta.\n" + SEGURIDAD,
        'D01 Valores del PDF (con unidad de costo inexistente)')

cambiar('D02 Todo malo a la vez.yml',
        [('"plazoCredito": 0', '"plazoCredito": {{sfa15PlazoCredito}}'), ('"monSolicitud": 0', '"monSolicitud": {{sfa15MonSolicitud}}')],
        "Agencia 1501 (sucursal SAP AGV Guayabo) y tipo de credito 999 en la misma llamada, con plazo y monto validos.\n"
        "Con monto 0 o plazo 0, SFA corta en la primera etapa ('Mon Solicitud' must not be empty) y no revisa lo demas: por eso aqui van validos.\n"
        + SEGURIDAD,
        'D02 Agencia 1501 y tipo de credito 999 (con unidad de costo inexistente)')

cambiar('D03 Agencia 5100 (almacen SAP).yml', [('"codUnidadCosto": "{{sfa15CodUnidadCosto}}"', VENENO)])
cambiar('D04 Empresa CR01.yml', [('"codUnidadCosto": "{{sfa15CodUnidadCosto}}"', VENENO)])
