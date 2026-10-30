# Asociados sin fincas y planes de financiamiento (solo lectura)

Base: LDCOM_DOS_PINOS_STAGING en TESTINGSQL\SQL2022 (Staging, NO Testing). Fecha de consulta: 2026-10-28.

## Esquema confirmado
- Cliente(Emp_Id, Cliente_Id, Tipo_Id, Grupo_Precio_Id, Codigo_Interfaz, Cliente_Activo bit, Cliente_Es_Banca bit, Cliente_Nombre)
- Tipo_Cliente(Tipo_Id, Tipo_Nombre, Tipo_Comportamiento): 3 = LD - ASOCIADO (comport. 2), 10 = LD - ENTREGAS DE LECHE (comport. 3 = Pertenece_Otro_Cliente = la finca).
- Cliente_Relacion(Emp_Id, Cliente_Id=padre, Cliente_Relacion_Id=hijo, Cliente_Relacion_Tipo)
- Plan_Financiamiento(..Aplica_Para 1=Banca 2=No Banca 3=Ambos 4=Cliente especifico, Restringido, Fec_Inicio, Fec_Fin, Activo)
- Plan_Financiamiento_Cliente(PlanFinanciamiento_Id, Cliente_Id): solo para Aplica_Para=4. Tiene 0 filas.
- Elegibilidad: TPlanesFinanciamiento.vb Lista_Elegibilidad/EvaluarElegibilidad (no hay SP GetPlanes... en BD).

## Resultados
Clientes por tipo: LD-ASOCIADO (3) 5.758 activos; LD-ENTREGAS DE LECHE (10, fincas) 1.487 activas; resto (publico, empleado, suma, etc.) otros.
Relacion tipo 1: 1.461 filas, solo padre Tipo 3 -> hijo Tipo 10, 1.219 asociados distintos. Tipo 2: 1 fila (Tipo 5 -> Tipo 7). Tipo 0: 13.481.

Q1 asociados activos (Tipo 3) por fincas activas: 0 fincas = 4.539 | 1 finca = 1.030 | 2+ fincas = 189 (max 6). Total 5.758.
Fincas: 1.487; con asociado 1.461; huerfanas (sin asociado) 26; ninguna con mas de 1 asociado.

Q2 Cliente_Es_Banca = 1: 0 clientes en toda la base. Planes activos y vigentes hoy (No Banca/Ambos): 4 (ids 3, 5 hasta 31-oct-2026; 7, 8 hasta 2099).
Todo cliente es No Banca, asi que los 5.758 asociados (incluidos los 4.539 sin fincas) son elegibles a esos 4 planes.
Los planes Banca (1,2,4,6,9) no aplican a nadie; ningun plan es "cliente especifico".

Q3 ejemplos asociados con 0 fincas: 1083801 DP - EL ABANICO S.A.; 4000054 SALGADO ULLOA RAFAEL EDUARDO; 4000056 LIZANO BARQUERO MARTA EUGENIA; 4000131 MESEN VILLALOBOS WALTER; 4000265 VARGAS VILLALOBOS EDUARDO.

Q4 codigos: asociados Cliente_Id 1083801..10027596 (todos >= 1.000.000; la mayoria 4000xxx), Codigo_Interfaz = mismo numero que Cliente_Id (1 vacio; max 8 caracteres).
Fincas Cliente_Id 1..5691, Codigo_Interfaz = mismo numero que Cliente_Id (1..998 de largo max 4; ninguna vacia). Ninguno trae un codigo SAP distinto.

## Consultas usadas (resumen)
- Q1: WITH a AS (SELECT c.Cliente_Id,(SELECT COUNT(*) FROM Cliente_Relacion r JOIN Cliente f ON f.Emp_Id=r.Emp_Id AND f.Cliente_Id=r.Cliente_Relacion_Id AND f.Tipo_Id=10 AND f.Cliente_Activo=1 WHERE r.Emp_Id=c.Emp_Id AND r.Cliente_Id=c.Cliente_Id AND r.Cliente_Relacion_Tipo=1) nf FROM Cliente c WHERE c.Tipo_Id=3 AND c.Cliente_Activo=1) SELECT nf,COUNT(*) FROM a GROUP BY nf
- Q2: SELECT COUNT(*) FROM Cliente WHERE Cliente_Es_Banca=1; SELECT ... FROM Plan_Financiamiento WHERE Activo=1; SELECT COUNT(*) FROM Plan_Financiamiento_Cliente
- Q3: TOP 5 asociados activos con NOT EXISTS de la relacion tipo 1 a finca activa
- Q4: GROUP BY Tipo_Id IN (3,10) con MIN/MAX(Cliente_Id), conteo de Codigo_Interfaz vacio
