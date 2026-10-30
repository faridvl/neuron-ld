using System;
using System.Collections.Generic;
using LD.AccesoDatos;
using LD.Catalogos;
using LD.AccesoTablas;
using Newtonsoft.Json;

// Uso: Harness.exe emp cliente plan plazo monto suc finca referencia
// Env: E2E_LDCOM (cadena de LDCOM Docker), E2E_INTEGRATION (cadena de Integrations con clave codificada para el Runner)
public static class Harness
{
    public static int Main(string[] a)
    {
        var logs = new List<string>();
        var conexion = new Acceso_MSSQLServer(Environment.GetEnvironmentVariable("E2E_LDCOM"), TipoBaseDatos.MSSQL);
        if (!conexion.Open()) { Console.WriteLine("ERRORABRIR " + conexion.ErrorDB); return 3; }
        var validador = new TValidadorPlanFinanciamientoIntegracion("TESTING", "DOS_PINOS", Environment.GetEnvironmentVariable("E2E_INTEGRATION"), "e2e");
        var servicio = new TSistemaFinanciamientoSFA(conexion, validador, delegate (string t) { logs.Add(t); });
        var sw = System.Diagnostics.Stopwatch.StartNew();
        string referencia = a[7] == "NULL" ? null : a[7];
        TRegRespuestaValidacionCreditoSFA r = servicio.Validar_Credito(int.Parse(a[0]), int.Parse(a[1]), int.Parse(a[2]), int.Parse(a[3]),
            decimal.Parse(a[4], System.Globalization.CultureInfo.InvariantCulture), int.Parse(a[5]), int.Parse(a[6]), referencia);
        sw.Stop();
        Console.WriteLine(JsonConvert.SerializeObject(new { ms = sw.ElapsedMilliseconds, Estado = r.Estado.ToString(), Razon = r.Razon.ToString(), r.Autorizado, r.NumSolicitud, r.NumCredito, r.PosibleAplicado, r.Mensaje, logs = logs }));
        return 0;
    }
}
