/*
  clonar-usuario-ldcom.sql
  Crea un usuario de aplicacion de LDCOM (Seg_Usuario) clonando los permisos de otro usuario existente,
  para entrar al Admin y al POS con un usuario propio.

  DONDE SE CORRE: en la base LDCOM del ambiente (Testing = LDCOM_DOS_PINOS_NEW). Una sola base, no toca INTEGRATIONS.
  Es reutilizable: cambie solo el bloque PARAMETROS.

  CLAVE: Usuario_Password no es un hash simple, es AES (Rijndael ECB, llave derivada de una llave fija) en Base64.
  No se puede calcular en T-SQL. Se genera con:
      powershell -NoProfile -File generar-clave-ldcom.ps1 -Clave 'LaClaveQueQuiera'
  y el resultado se pega en @ClaveCodificada. El generador reproduce EncriptarAES de NEGOCIO/SEGURIDAD/TSegUsuario.vb.

  QUE COPIA (todo lo que el Admin y el POS consultan por usuario):
    Seg_Usuario (fila nueva con datos propios), Seg_Usuario_x_Rol, Seg_Empresa_x_Usuario, Seg_Sucursal_x_Usuario,
    Seg_Cadena_x_Usuario, Seg_Horario_x_Usuario, Seg_Menu_x_Usuario, Seg_Menu_Opciones_x_Usuario.
  QUE NO COPIA (a proposito):
    Bitacoras, historicos, conexiones, favoritos, claves anteriores, tablas *_Sincro y *_Temporal (no son permisos);
    Seg_Menu_Opciones_x_Usuario_Permiso (solicitudes puntuales de autorizacion); Seg_TipoPreventa_Rol (es por rol:
    Usuario_Id ahi solo dice quien lo actualizo); huellas digitales y datos del segundo factor del usuario origen.

  IDEMPOTENTE: si @LoginNuevo ya existe no se toca su fila (ni su clave); solo se completan los permisos que falten.
  Si el usuario origen cambia despues, volver a correrlo agrega los permisos nuevos (no quita los sobrantes).
*/
SET NOCOUNT ON;
SET XACT_ABORT ON;

-- ============================== PARAMETROS ==============================
DECLARE @LoginOrigen     VARCHAR(20)  = 'logical';
DECLARE @LoginNuevo      VARCHAR(20)  = '>>> LLENAR login nuevo';
DECLARE @NombreNuevo     VARCHAR(80)  = '>>> LLENAR nombre completo';
DECLARE @CorreoNuevo     VARCHAR(100) = '>>> LLENAR correo';
DECLARE @ClaveCodificada VARCHAR(100) = '>>> LLENAR salida de generar-clave-ldcom.ps1';
-- 0 = entra solo con login y clave. 1 = pide el segundo factor (LDCODE); el origen suele tenerlo en 1.
DECLARE @DobleFactor     BIT          = 0;
-- Solo si el origen tiene Usuario_Expira = 1: dias de vigencia de la clave nueva.
DECLARE @DiasVigenciaClave INT        = 365;
-- ========================================================================

DECLARE @PrefijoPendiente      CHAR(3)  = '>>>';
DECLARE @SinBloqueoHasta       DATETIME = '19000101';
DECLARE @ClaveEsAes            BIT      = 1;
DECLARE @UsuarioNoEliminado    BIT      = 0;
DECLARE @Ahora                 DATETIME = GETDATE();
DECLARE @UsuarioIdOrigen       SMALLINT;
DECLARE @UsuarioIdNuevo        SMALLINT;
DECLARE @UsuarioNuevoYaExistia BIT      = 0;

BEGIN TRY
    IF LEFT(@LoginNuevo, 3) = @PrefijoPendiente OR LEFT(@NombreNuevo, 3) = @PrefijoPendiente
       OR LEFT(@CorreoNuevo, 3) = @PrefijoPendiente OR LEFT(@ClaveCodificada, 3) = @PrefijoPendiente
        THROW 50001, 'Complete los parametros marcados con >>> LLENAR antes de correr el script.', 1;

    SELECT @UsuarioIdOrigen = Usuario_Id
    FROM Seg_Usuario
    WHERE Usuario_Login = @LoginOrigen AND Usuario_Eliminado = @UsuarioNoEliminado;

    IF @UsuarioIdOrigen IS NULL
        THROW 50002, 'El usuario origen no existe (o esta eliminado) en Seg_Usuario.', 1;

    BEGIN TRANSACTION;

    -- Mismo criterio del Admin: Usuario_Id = MAX + 1 (la columna no es IDENTITY).
    SELECT @UsuarioIdNuevo = Usuario_Id
    FROM Seg_Usuario WITH (UPDLOCK, HOLDLOCK)
    WHERE Usuario_Login = @LoginNuevo;

    IF @UsuarioIdNuevo IS NOT NULL
        SET @UsuarioNuevoYaExistia = 1;
    ELSE
    BEGIN
        SELECT @UsuarioIdNuevo = ISNULL(MAX(Usuario_Id), 0) + 1 FROM Seg_Usuario WITH (UPDLOCK, HOLDLOCK);

        INSERT INTO Seg_Usuario (
            Usuario_Id, Rol_Id, Usuario_Nombre, Usuario_Login, Usuario_Password, Usuario_Fecha_Exp_Pw,
            Usuario_Corporativo, Usuario_Email, Usuario_Expira, Usuario_Fec_Actualizacion,
            Usuario_Forzar_Politica_Pw, Usuario_Cambiar_Pw_Siguiente_Ingreso, Usuario_Puede_Cambiar_Pw,
            Usuario_Cuenta_Deshabilitada, Usuario_Cuenta_Bloqueada, Usuario_Cuenta_Bloqueada_Hasta, Usuario_Intento,
            Usuario_Muestra_Costos, Usuario_Huella1, Usuario_Huella2, Usuario_Huella1_Varbinary, Usuario_Huella2_Varbinary,
            Usuario_Password_AES, Usuario_Muestra_Precio, Usuario_Id_Crea, Usuario_Id_Actualiza, Usuario_Id_Inhabilita,
            Usuario_Fec_Creacion, Usuario_Fec_Deshabilitado, Usuario_Id_Elimina, Usuario_Fec_Eliminado, Usuario_Eliminado,
            Usuario_DobleFactor, Usuario_DobleFactor_PIN, Usuario_DobleFactor_Fecha_Autentica,
            Usuario_DobleFactor_Dispositivo, Usuario_DobleFactor_Dispositivo_Nombre, Usuario_DobleFactor_Dispositivo_OS,
            Usuario_Tipo_Identificacion, Usuario_Cedula, Usuario_SSO_Id)
        SELECT
            @UsuarioIdNuevo, 0 /* el Admin guarda Rol_Id = 0; los roles viven en Seg_Usuario_x_Rol */,
            @NombreNuevo, @LoginNuevo, @ClaveCodificada,
            CASE WHEN Usuario_Expira = 1 THEN DATEADD(DAY, @DiasVigenciaClave, @Ahora) ELSE @Ahora END,
            Usuario_Corporativo, @CorreoNuevo, Usuario_Expira, @Ahora,
            Usuario_Forzar_Politica_Pw, 0 /* sin forzar cambio de clave: es un ambiente de pruebas */, Usuario_Puede_Cambiar_Pw,
            0, 0, @SinBloqueoHasta, 0,
            Usuario_Muestra_Costos, '', '', 0x, 0x,
            @ClaveEsAes, Usuario_Muestra_Precio, @UsuarioIdOrigen, 0, 0,
            @Ahora, @Ahora, 0, @Ahora, @UsuarioNoEliminado,
            @DobleFactor, '', @Ahora,
            '', '', '',
            Usuario_Tipo_Identificacion, '', ''
        FROM Seg_Usuario
        WHERE Usuario_Id = @UsuarioIdOrigen;
    END;

    INSERT INTO Seg_Usuario_x_Rol (Usuario_Id, Rol_Id, Fec_Actualizacion)
    SELECT @UsuarioIdNuevo, o.Rol_Id, @Ahora
    FROM Seg_Usuario_x_Rol o
    WHERE o.Usuario_Id = @UsuarioIdOrigen
      AND NOT EXISTS (SELECT 1 FROM Seg_Usuario_x_Rol n WHERE n.Usuario_Id = @UsuarioIdNuevo AND n.Rol_Id = o.Rol_Id);

    INSERT INTO Seg_Empresa_x_Usuario (Emp_Id, Usuario_Id, ExU_Fec_Actualizacion)
    SELECT o.Emp_Id, @UsuarioIdNuevo, @Ahora
    FROM Seg_Empresa_x_Usuario o
    WHERE o.Usuario_Id = @UsuarioIdOrigen
      AND NOT EXISTS (SELECT 1 FROM Seg_Empresa_x_Usuario n WHERE n.Usuario_Id = @UsuarioIdNuevo AND n.Emp_Id = o.Emp_Id);

    INSERT INTO Seg_Sucursal_x_Usuario (Usuario_Id, Emp_Id, Suc_Id, SxU_Fec_Actualizacion)
    SELECT @UsuarioIdNuevo, o.Emp_Id, o.Suc_Id, @Ahora
    FROM Seg_Sucursal_x_Usuario o
    WHERE o.Usuario_Id = @UsuarioIdOrigen
      AND NOT EXISTS (SELECT 1 FROM Seg_Sucursal_x_Usuario n
                      WHERE n.Usuario_Id = @UsuarioIdNuevo AND n.Emp_Id = o.Emp_Id AND n.Suc_Id = o.Suc_Id);

    INSERT INTO Seg_Cadena_x_Usuario (Usuario_Id, Emp_Id, Cadena_Id, CxU_Fec_Actualizacion)
    SELECT @UsuarioIdNuevo, o.Emp_Id, o.Cadena_Id, @Ahora
    FROM Seg_Cadena_x_Usuario o
    WHERE o.Usuario_Id = @UsuarioIdOrigen
      AND NOT EXISTS (SELECT 1 FROM Seg_Cadena_x_Usuario n
                      WHERE n.Usuario_Id = @UsuarioIdNuevo AND n.Emp_Id = o.Emp_Id AND n.Cadena_Id = o.Cadena_Id);

    INSERT INTO Seg_Horario_x_Usuario (Usuario_Id, Horario_Id, HxU_Fec_Actualizacion)
    SELECT @UsuarioIdNuevo, o.Horario_Id, @Ahora
    FROM Seg_Horario_x_Usuario o
    WHERE o.Usuario_Id = @UsuarioIdOrigen
      AND NOT EXISTS (SELECT 1 FROM Seg_Horario_x_Usuario n
                      WHERE n.Usuario_Id = @UsuarioIdNuevo AND n.Horario_Id = o.Horario_Id);

    INSERT INTO Seg_Menu_x_Usuario (Modulo_Id, Menu_Id, Rol_Id, Usuario_Id, MxU_Fec_Actualizacion)
    SELECT o.Modulo_Id, o.Menu_Id, o.Rol_Id, @UsuarioIdNuevo, @Ahora
    FROM Seg_Menu_x_Usuario o
    WHERE o.Usuario_Id = @UsuarioIdOrigen
      AND NOT EXISTS (SELECT 1 FROM Seg_Menu_x_Usuario n
                      WHERE n.Usuario_Id = @UsuarioIdNuevo AND n.Modulo_Id = o.Modulo_Id
                        AND n.Menu_Id = o.Menu_Id AND n.Rol_Id = o.Rol_Id);

    INSERT INTO Seg_Menu_Opciones_x_Usuario (Modulo_Id, Menu_Id, Opcion_Id, Usuario_Id, Opcion_Fec_Actualizacion)
    SELECT o.Modulo_Id, o.Menu_Id, o.Opcion_Id, @UsuarioIdNuevo, @Ahora
    FROM Seg_Menu_Opciones_x_Usuario o
    WHERE o.Usuario_Id = @UsuarioIdOrigen
      AND NOT EXISTS (SELECT 1 FROM Seg_Menu_Opciones_x_Usuario n
                      WHERE n.Usuario_Id = @UsuarioIdNuevo AND n.Modulo_Id = o.Modulo_Id
                        AND n.Menu_Id = o.Menu_Id AND n.Opcion_Id = o.Opcion_Id);

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    THROW;
END CATCH;

-- Verificacion (no muestra claves)
SELECT CASE WHEN @UsuarioNuevoYaExistia = 1 THEN 'ya existia: solo se completaron permisos' ELSE 'usuario creado' END AS Resultado,
       u.Usuario_Id, u.Usuario_Login, u.Usuario_Nombre, u.Usuario_Email,
       CASE WHEN u.Usuario_Password = @ClaveCodificada THEN 'SI' ELSE 'NO (el usuario ya tenia otra clave)' END AS ClaveCoincideConLaIndicada,
       u.Usuario_Password_AES, u.Usuario_Cuenta_Deshabilitada, u.Usuario_Cuenta_Bloqueada, u.Usuario_Eliminado,
       u.Usuario_Cambiar_Pw_Siguiente_Ingreso, u.Usuario_DobleFactor
FROM Seg_Usuario u
WHERE u.Usuario_Id = @UsuarioIdNuevo;

SELECT t.Tabla, t.Origen, t.Nuevo, CASE WHEN t.Origen = t.Nuevo THEN 'OK' ELSE 'DIFERENTE' END AS Estado
FROM (
    SELECT 'Seg_Usuario_x_Rol' AS Tabla,
           (SELECT COUNT(*) FROM Seg_Usuario_x_Rol WHERE Usuario_Id = @UsuarioIdOrigen) AS Origen,
           (SELECT COUNT(*) FROM Seg_Usuario_x_Rol WHERE Usuario_Id = @UsuarioIdNuevo) AS Nuevo
    UNION ALL SELECT 'Seg_Empresa_x_Usuario',
           (SELECT COUNT(*) FROM Seg_Empresa_x_Usuario WHERE Usuario_Id = @UsuarioIdOrigen),
           (SELECT COUNT(*) FROM Seg_Empresa_x_Usuario WHERE Usuario_Id = @UsuarioIdNuevo)
    UNION ALL SELECT 'Seg_Sucursal_x_Usuario',
           (SELECT COUNT(*) FROM Seg_Sucursal_x_Usuario WHERE Usuario_Id = @UsuarioIdOrigen),
           (SELECT COUNT(*) FROM Seg_Sucursal_x_Usuario WHERE Usuario_Id = @UsuarioIdNuevo)
    UNION ALL SELECT 'Seg_Cadena_x_Usuario',
           (SELECT COUNT(*) FROM Seg_Cadena_x_Usuario WHERE Usuario_Id = @UsuarioIdOrigen),
           (SELECT COUNT(*) FROM Seg_Cadena_x_Usuario WHERE Usuario_Id = @UsuarioIdNuevo)
    UNION ALL SELECT 'Seg_Horario_x_Usuario',
           (SELECT COUNT(*) FROM Seg_Horario_x_Usuario WHERE Usuario_Id = @UsuarioIdOrigen),
           (SELECT COUNT(*) FROM Seg_Horario_x_Usuario WHERE Usuario_Id = @UsuarioIdNuevo)
    UNION ALL SELECT 'Seg_Menu_x_Usuario',
           (SELECT COUNT(*) FROM Seg_Menu_x_Usuario WHERE Usuario_Id = @UsuarioIdOrigen),
           (SELECT COUNT(*) FROM Seg_Menu_x_Usuario WHERE Usuario_Id = @UsuarioIdNuevo)
    UNION ALL SELECT 'Seg_Menu_Opciones_x_Usuario',
           (SELECT COUNT(*) FROM Seg_Menu_Opciones_x_Usuario WHERE Usuario_Id = @UsuarioIdOrigen),
           (SELECT COUNT(*) FROM Seg_Menu_Opciones_x_Usuario WHERE Usuario_Id = @UsuarioIdNuevo)
) t
ORDER BY t.Tabla;
