-- ## Direccion de Cliente_Relacion tipo 1 (Tipo_Id de cada lado)
SELECT TOP 5 c1.Tipo_Id AS Tipo_Cliente_Id, c2.Tipo_Id AS Tipo_Cliente_Relacion_Id, COUNT(*) AS Filas
FROM Cliente_Relacion r JOIN Cliente c1 ON c1.Cliente_Id = r.Cliente_Id JOIN Cliente c2 ON c2.Cliente_Id = r.Cliente_Relacion_Id
WHERE r.Cliente_Relacion_Tipo = 1 GROUP BY c1.Tipo_Id, c2.Tipo_Id ORDER BY Filas DESC
-- ## E01 asociado con exactamente 1 finca activa (y E04: la finca de otro asociado sale de la segunda fila)
WITH fincas AS (
  SELECT r.Cliente_Id AS Asociado_Id, COUNT(*) AS Fincas, MIN(r.Cliente_Relacion_Id) AS Finca_Id
  FROM Cliente_Relacion r JOIN Cliente f ON f.Cliente_Id = r.Cliente_Relacion_Id
  WHERE r.Cliente_Relacion_Tipo = 1 AND f.Tipo_Id = 10 AND f.Cliente_Activo = 1 AND ISNULL(f.Cliente_Bloqueado, 0) = 0
  GROUP BY r.Cliente_Id)
SELECT TOP 4 a.Cliente_Id, a.Codigo_Interfaz, a.Cliente_Nombre, a.Cliente_Es_Banca, x.Fincas, x.Finca_Id, f.Codigo_Interfaz AS Finca_Codigo_Interfaz, f.Cliente_Nombre AS Finca_Nombre
FROM fincas x JOIN Cliente a ON a.Cliente_Id = x.Asociado_Id JOIN Cliente f ON f.Cliente_Id = x.Finca_Id
WHERE a.Tipo_Id = 3 AND a.Cliente_Activo = 1 AND ISNULL(a.Cliente_Bloqueado, 0) = 0 AND x.Fincas = 1 AND a.Cliente_Nombre IS NOT NULL
ORDER BY a.Cliente_Id
-- ## E02 asociado con 2 o mas fincas activas
WITH fincas AS (
  SELECT r.Cliente_Id AS Asociado_Id, COUNT(*) AS Fincas, MIN(r.Cliente_Relacion_Id) AS Finca_Id
  FROM Cliente_Relacion r JOIN Cliente f ON f.Cliente_Id = r.Cliente_Relacion_Id
  WHERE r.Cliente_Relacion_Tipo = 1 AND f.Tipo_Id = 10 AND f.Cliente_Activo = 1 AND ISNULL(f.Cliente_Bloqueado, 0) = 0
  GROUP BY r.Cliente_Id)
SELECT TOP 2 a.Cliente_Id, a.Codigo_Interfaz, a.Cliente_Nombre, x.Fincas, x.Finca_Id, f.Codigo_Interfaz AS Finca_Codigo_Interfaz
FROM fincas x JOIN Cliente a ON a.Cliente_Id = x.Asociado_Id JOIN Cliente f ON f.Cliente_Id = x.Finca_Id
WHERE a.Tipo_Id = 3 AND a.Cliente_Activo = 1 AND ISNULL(a.Cliente_Bloqueado, 0) = 0 AND x.Fincas >= 2 AND a.Cliente_Nombre IS NOT NULL
ORDER BY x.Fincas DESC, a.Cliente_Id
-- ## E03 asociado sin fincas
SELECT TOP 2 a.Cliente_Id, a.Codigo_Interfaz, a.Cliente_Nombre
FROM Cliente a
WHERE a.Tipo_Id = 3 AND a.Cliente_Activo = 1 AND ISNULL(a.Cliente_Bloqueado, 0) = 0 AND a.Cliente_Nombre IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM Cliente_Relacion r WHERE r.Cliente_Id = a.Cliente_Id AND r.Cliente_Relacion_Tipo = 1)
ORDER BY a.Cliente_Id
-- ## Planes de financiamiento
SELECT p.PlanFinanciamiento_Id, p.PlanFinanciamiento_Codigo_Externo, p.PlanFinanciamiento_Nombre, p.PlanFinanciamiento_Tasa_Interes,
  p.PlanFinanciamiento_Aplica_Para, p.PlanFinanciamiento_Restringido, CONVERT(varchar(10), p.PlanFinanciamiento_Fec_Inicio, 23) AS Inicio,
  CONVERT(varchar(10), p.PlanFinanciamiento_Fec_Fin, 23) AS Fin, p.PlanFinanciamiento_Activo,
  (SELECT STRING_AGG(CAST(z.PlanFinanciamiento_Plazo_Semanas AS varchar(10)), ',') FROM Plan_Financiamiento_Plazo z WHERE z.PlanFinanciamiento_Id = p.PlanFinanciamiento_Id) AS Plazos_Semanas,
  (SELECT COUNT(*) FROM Plan_Financiamiento_Articulo t WHERE t.PlanFinanciamiento_Id = p.PlanFinanciamiento_Id) AS Articulos
FROM Plan_Financiamiento p ORDER BY p.PlanFinanciamiento_Id
-- ## Sucursales activas
SELECT TOP 8 Suc_Id, Suc_Nombre, Codigo_Interfaz FROM Sucursal WHERE Suc_Activo = 1 ORDER BY Suc_Id
