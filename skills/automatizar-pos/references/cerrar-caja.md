# Cerrar la caja del POS (Docker)

Comando: `python -I scripts\correr.py <pid> cerrar_caja` (parámetros en `recorridos.py`: `efectivo`, `banco`,
`encargado`, `numero_deposito`). Código: `poslib\flujos\cerrar_caja.py`.

## Ruta
Barra F11 (más funciones) > F5 Cerrar Caja > `Frm_Lista` botón `Bn_F2`. En coordenadas de captura (factor 1.25):
F11 en (1093, 693) y F5 en (475, 693).

Pantallas que atiende el flujo, sondeando cada 50 ms: "Cierre de caja", "Retiro de Caja", "Depósito Automático" y
"Confirmación".

## Trampas
- La pantallita **"Cierre de caja" caduca en ~15 s**: por eso se sondea cada 50 ms y se pulsa F1 (VK 0x70) enseguida.
- El **error EMV** (`#32770`, OK) es inocuo en Docker: `modales.cerrar_errores_dotnet`.
- **Éxito** = el POS vuelve al login (`sesion.hay_login`). Si no, el flujo falla con `PasoFallido`.
- Denominaciones: los botones aceptan `BM_CLICK`; el teclado numérico necesita clic físico con el POS al frente.
- Depósito: `set_edit_text` de pywinauto; los combos con `CB_SETCURSEL` más `WM_COMMAND` `CBN_SELCHANGE`.
- `efectivo=0` evita duplicar retiro y depósito al reanudar un cierre cortado.

## Si corre dos veces o se corta
Lo ya guardado (retiro, depósito) queda en la BD. Para reanudar, correr de nuevo con `efectivo=0`. Si la caja ya está
cerrada, el POS está en el login y el flujo termina sin hacer nada.

## Validar en BD (Docker)
```sql
SELECT Cierre_id, Cierre_Estado, Cierre_Fecha_Cierre, Cierre_Total, Cierre_FP_Efectivo, Cierre_Ret_Efectivo
FROM Caja_Cierre WHERE Suc_Id = 1 AND Caja_Id = 1;                 -- Cierre_Estado = CLOSE
SELECT COUNT(*) FROM Ticket_Encabezado WHERE Suc_Id = 1 AND Caja_Id = 1;  -- 0: pasaron a Factura_*
```
La fecha del contenedor es UTC (ver `trampas.md`).
