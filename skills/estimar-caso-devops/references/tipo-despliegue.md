# Tipo: hueco de despliegue

"Funciona en un ambiente y en otro no".

1. **`SELECT DB_NAME()` antes de confiar en cualquier consulta.** El ambiente que el equipo llama
   "UAT" puede ser una base `LDCOM_DOS_PINOS_DEMO`. Si un objeto que deberia existir no aparece,
   confirmar con el usuario que esa es la base que usa la aplicacion en ese ambiente.
2. Consultar `dbo._db_migrations` de esa base: si la migracion corrio, cuando y con que resultado.
   No deducirlo por conteos de tablas sueltos.
3. Si figura como aplicada pero el objeto no existe, comparar un objeto de una migracion vieja, uno del
   rango sospechoso y uno reciente: asi se sabe si la perdida es puntual o generalizada.
4. `git log --all --oneline -- <ruta de la migracion>` y `git branch --all --contains <commit>`
   descartan rapido que el fix se haya quedado en una rama sin portar.
5. La herramienta de migraciones (`LogicalData.DatabaseMigration.Cli`, repo `DatabaseMigration` del
   mismo proyecto ADO) **no vuelve a correr** una migracion ya marcada como aplicada. Si el objeto se
   perdio por fuera, la solucion es una migracion NUEVA que lo reponga, no editar el historial.
   Clonar ese repo con `git -c core.longpaths=true clone` (rutas largas en Windows).
