using System;
using System.Diagnostics;
using Integration.SDK;
using Integration.SDK.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

// Anfitrion minimo .NET Framework: llama IntegrationBridge.ValidateFinancingPlan como lo haria NEGOCIO.
// Uso: host.exe <monto> <referencia> [codigoCliente]   (cadena de conexion en la variable E2E_CONNECTION)
public static class Host
{
    public static int Main(string[] args)
    {
        var bridge = new IntegrationBridge("TESTING", "DOS_PINOS", Environment.GetEnvironmentVariable("E2E_CONNECTION"), "e2e");
        var request = new FinancingPlanValidationRequest
        {
            CustomerCode = args.Length > 2 ? args[2] : "4000010",
            BranchId = 99,
            DocumentDate = new DateTime(2026, 10, 27),
            CustomerName = "Luis Mangel Alfaro Leal",
            UsesCreditLine = true,
            CreditLineNumber = 0,
            ExternalReference = args[1],
            FarmCustomerId = 99999999,
            TermInWeeks = 4,
            FinancingPlanExternalCode = "201",
            Amount = decimal.Parse(args[0], System.Globalization.CultureInfo.InvariantCulture),
            Notes = "prueba e2e SDK"
        };
        var stopwatch = Stopwatch.StartNew();
        var response = bridge.ValidateFinancingPlan(request);
        stopwatch.Stop();
        Console.WriteLine(JsonConvert.SerializeObject(new { elapsedMs = stopwatch.ElapsedMilliseconds, response = response }, new StringEnumConverter()));
        return 0;
    }
}
