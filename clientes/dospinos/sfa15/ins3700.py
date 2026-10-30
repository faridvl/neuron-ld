import sys
step = '''                # Configuracion con la que NEGOCIO llama al Runner de integraciones desde el sitio del
                # WCF (IntegrationStage, IntegrationTenant y la cadena LDDPINTEGRATIONS). Mismo script
                # que el ADMIN; la cadena es secreta y por eso se mapea con env:. Si falta una variable
                # el script avisa y deja el valor del servidor.
                - task: PowerShell@2
                  displayName: 'Parche Web.config — integraciones'
                  inputs:
                    filePath: '$(Pipeline.Workspace)/wcf-build/pipeline-scripts/sync-integration-settings.ps1'
                    arguments: >-
                      -SiteDir "$(IIS_PATH_WCF)"
                  env:
                    INTEGRATIONS_DB_CONNECTION: $(INTEGRATIONS_DB_CONNECTION)

'''
anchor_a = "displayName: 'Parche Web.config - binding redirects'"
anchor_b = "                # DEBUG temporal:"
for f in sys.argv[1:]:
    t = open(f, encoding='utf-8', newline='').read()
    out=[]; pos=0; n=0
    while True:
        i = t.find(anchor_a, pos)
        if i<0: break
        j = t.find(anchor_b, i)
        out.append(t[pos:j]); out.append(step); pos=j; n+=1
    out.append(t[pos:])
    open(f,'w',encoding='utf-8',newline='').write(''.join(out))
    print(f,n)
