# Inventario de los scripts de origen y su destino

Los scripts sueltos vivían en cuatro carpetas de trabajo (`auto\` de la sesión, `fix-3791\auto\`,
`preventa-sucursal-destino\auto\` y `qa-3700\auto\` de SFA15). Esta tabla dice qué pasó con cada grupo. Los originales no
se borraron: son evidencia de sus casos. Lo nuevo se hace siempre con `scripts\correr.py` y `poslib`.

Decisiones: **migrado** = ya vive en `poslib` (o en un recorrido); **cubierto** = `poslib` ya lo hacía, el script es
redundante; **referencia** = útil para diagnosticar, se consulta pero no se migra; **descartado** = específico de un
caso resuelto o de una sola corrida.

| Script(s) | Qué hace | ¿Duplica poslib? | ¿Probado? | Decisión |
|---|---|---|---|---|
| `modales.py`, `confirmar_pregunta.py`, `cerrar_dialogo.py`, `cerrar_dialogo_ok.py`, `leer_msg.py` | Vigilar mensajes que se cierran solos, responder la pregunta (check/ESC), cerrar errores .NET | `base.py` tenía lo básico, no la vigilancia ni los errores .NET | Sí (preventa 3791, cierre de caja) | Migrado a `poslib\modales.py` (`vigilar`, `responder_pregunta`, `cerrar_errores_dotnet`) y `scripts\vigilar_modales.py` |
| `entrar.py`, `entrar_facturacion.py`, `login_y_tipos.py`, `login2.py`, `prueba_captura_login.py` | Login con qa_auto y espera de pantalla | No: `poslib` no tenía login | Sí | Migrado a `poslib\sesion.py` y flujo `iniciar_sesion` (clave por variable de entorno, nunca en el repo) |
| `cerrar_caja.py`, `cerrar_caja_f1.py`, `f1_rapido.py`, `clic_dialogo.py` | Cierre de caja punta a punta (retiro, depósito, F1 en la pantallita de 15 s) | No | Sí (Docker, 3791 y 3722) | Migrado a flujo `cerrar_caja` y recorrido `cerrar_caja` |
| `clic_rel.py`, `clic_abs.py`, `clic_en_control.py`, `pulsar_id.py` | Clic físico por coordenadas de captura y UIA invoke por `auto_id` | Parcial (`base.clic_sin_texto`) | Sí | Migrado a `poslib\fisico.py` |
| `agregar_solo.py`, `agregar_articulo.py`, `agregar.py` (qa-3700) | Agregar artículo por código | Sí | Sí | Cubierto por flujo `agregar_articulo` |
| `abrir_busqueda_y_buscar.py`, `buscar_articulo_win32.py`, `busqueda_sugeridos.py`, `buscar_en_dialogo.py` | Búsqueda de artículos y lectura de grillas | Sí | Sí | Cubierto por flujo `buscar_articulo` |
| `cambiar_cliente.py`, `cambiar_documento.py`, `tipodoc_credito.py` | Cambiar cliente y tipo de documento | Sí | Sí | Cubierto por flujos `cambiar_cliente` y `cambiar_documento` |
| `plansel.py`, `listsel.py`, `lista_seleccionar.py`, `elegir_tipo.py`, `bonificacion_aplicar.py` | Elegir fila de una lista o plan | Sí (`elegir_plan_credito`) y parcial | Sí | Cubierto o referencia (`lista_seleccionar.py` para listas nuevas) |
| `facturar_contado.py`, `facturar_cargada.py`, `facturar_d.py`, `facturar_sin_agregar.py`, `pagar_preventa.py`, `guardar_preventa.py`, `validar_rol.py` | Facturar o guardar preventa con sus diálogos | Sí (`facturar`, `pagar_efectivo`) salvo Validación de Rol | Sí | Cubierto; Validación de Rol queda documentada en `trampas.md` y como referencia (`validar_rol.py`) |
| `escenario_preventa.py`, `esc.py`, `escanear_datamatrix.py` | Escenarios completos de un caso | Se arman con recorridos | Sí | Descartado como script; los recorridos de `recorridos.py` los reemplazan. `escanear_datamatrix.py` queda como referencia |
| `doble_click_fisico.py`, `doble_click_imprimir.py` | Reproducir doble clic en el ícono de imprimir | No | Sí, pero solo para un bug | Referencia (el doble clic por mensajes no reproduce el clic físico, ver `trampas.md`) |
| `vaciar_documento.py`, `cancelar_documento.py` | Vaciar documento | Sí | Sí | Cubierto por flujo `cancelar_documento` |
| `pos_ui.py`, `w32.py`, `w32_*.py`, `ventanas_win32.py`, `hijos_win32.py`, `hijos_rec.py`, `hijos_texto.py`, `setear_edit.py`, `tecla_a.py`, `clic_msg.py`, `clic_hijo.py`, `clic_en_ventana.py` | Librería y utilidades Win32 | Sí (`poslib\base.py`) | Sí | Cubierto; se consultan como referencia para controles raros |
| `uia.py`, `uia_vista.py`, `sonda_uia.py`, `sondear_ventana.py`, `estado.py`, `inspeccionar_pos.py`, `controles_de_ventana.py`, `buscar_controles.py`, `lista_botones.py`, `cap.py`, `cap_principal.py`, `cap_titulo.py`, `mon.py`, `f5.py`, `boton.py`, `rueda.py`, `arrastrar.py`, `cb.py`, `otros.py`, `aceptar_modal.py`, `abrir_cliente_y_capturar.py`, `pulsar_*.py`, `esc.py`, `salida.*`, `sonda.*`, `vigila.*` | Inspección y captura puntual | Parcial | Algunas | Referencia: utilidades de diagnóstico de una sola corrida. Para inspeccionar usar `correr.py` con capturas o `vigilar_modales.py` |
| `ejecutar.ps1`, `abrir-pos-cedi.ps1`, `config-caja-cedi.ps1`, `slot-otros-fix3791.ps1`, scripts `.ps1` y `.sh` de `qa-3700` (`aplicar-scripts-local`, `config-caja`, `01-preparar.sh`) | Preparar el ambiente (slots, caja, scripts SQL) y lanzar con tope de tiempo | No | Sí, atados a un worktree y a rutas personales | Referencia: dependen de rutas personales; la preparación de ambiente es de `rig` y de cada caso |
| `NOTAS.txt`, `FLUJO-*.md` | Notas de cada caso | No aplica | No aplica | Referencia histórica; lo reutilizable ya está en `SKILL.md` y `trampas.md` |

## Pendiente de migrar (no probado o muy específico)

- Validación de Rol al guardar preventa: queda como referencia hasta que haya un caso que la repita.
- Lectura de grillas `SysListView32` de Sustitutos/Sugeridos: cubierta por `buscar_articulo`; no hay flujo propio.
