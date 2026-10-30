"""Registro de flujos: nombre -> módulo. Cada módulo expone NOMBRE, PANTALLA y ejecutar(pos, **parametros)."""
from . import (agregar_articulo, buscar_articulo, cambiar_cliente, cambiar_documento, cancelar_documento,
               elegir_plan_credito, facturar, leer_mensaje, pagar_efectivo, salir)

REGISTRO = {m.NOMBRE: m for m in (agregar_articulo, buscar_articulo, cambiar_cliente, cambiar_documento,
                                   cancelar_documento, elegir_plan_credito, facturar, leer_mensaje, pagar_efectivo, salir)}
