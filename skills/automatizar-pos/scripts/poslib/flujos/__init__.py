"""Registro de flujos: nombre -> módulo. Cada módulo expone NOMBRE, PANTALLA y ejecutar(pos, **parametros)."""
from . import (agregar_articulo, autorizar, buscar_articulo, cambiar_cliente, cambiar_documento, cancelar_documento,
               cerrar_caja, elegir_plan_credito, facturar, iniciar_sesion, leer_mensaje, nota_credito, pagar_efectivo, salir)

REGISTRO = {m.NOMBRE: m for m in (agregar_articulo, autorizar, buscar_articulo, cambiar_cliente, cambiar_documento,
                                   cancelar_documento, cerrar_caja, elegir_plan_credito, facturar, iniciar_sesion,
                                   leer_mensaje, nota_credito, pagar_efectivo, salir)}
