"""Recorridos predefinidos: funciones que devuelven la lista de pasos [(flujo, parametros)].
Los datos de prueba (cliente, artículo, cantidad) van como parámetros, no fijos. Para armar uno nuevo, copiar uno y
encadenar flujos de poslib.flujos (cada paso termina verificado antes de seguir)."""


def venta_contado(articulo, cantidad=1, cliente=None, cliente_visible=None):
    pasos = []
    if cliente:
        pasos.append(("cambiar_cliente", {"codigo": cliente, "muestra": cliente_visible}))
    pasos += [
        ("cambiar_documento", {"tipo": "contado"}),
        ("agregar_articulo", {"codigo": articulo, "cantidad": cantidad}),
        ("facturar", {}),
        ("pagar_efectivo", {}),
    ]
    return pasos


def venta_credito_financiado(cliente, articulo, cantidad=1, plan=None, mensaje_final=True, cliente_visible=None):
    """Crédito con validación del sistema de financiamiento: plan + simulador, y luego lo que muestre el POS
    (mensaje de rechazo/contingencia). Con mensaje_final=False no lee mensaje (úsese si el caso autoriza)."""
    pasos = [
        ("cambiar_cliente", {"codigo": cliente, "muestra": cliente_visible}),
        ("cambiar_documento", {"tipo": "credito"}),
        ("agregar_articulo", {"codigo": articulo, "cantidad": cantidad}),
        ("facturar", {}),
        ("elegir_plan_credito", {"plan": plan}),
    ]
    if mensaje_final:
        pasos.append(("leer_mensaje", {}))
    return pasos


def cancelar_y_salir_del_documento():
    return [("cancelar_documento", {})]


RECORRIDOS = {
    "venta_contado": venta_contado,
    "venta_credito_financiado": venta_credito_financiado,
    "cancelar_documento": cancelar_y_salir_del_documento,
}
