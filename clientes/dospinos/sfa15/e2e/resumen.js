const fs=require('fs');
for (const l of fs.readFileSync('resultados-e2e-final.txt','utf8').split(/\r?\n/).filter(Boolean)) {
  const o=JSON.parse(l);
  if(o.paso){console.log(JSON.stringify(o));continue;}
  const r=o.res||o.resultados;
  const rs=(x)=>x&&x.Outcome?`${x.Outcome}/${x.UnavailableReason} req=${x.RequestNumber} cred=${x.CreditNumber} disp=${x.AvailableAmount} pa=${x.PossiblyApplied} msg="${(x.Message||'').slice(0,70)}"`:JSON.stringify(x);
  console.log(`[${o.caso}] sim ${o.simAntes}->${o.simDespues} (llamadas ${o.llamadasSim}) ${Array.isArray(r)?r.map(rs).join(' || '):rs(r)} ms=${o.ms||''} sig=${o.sigSolicitud}/${o.sigCredito} attempt=${o.attempt||''} audit=${o.auditoria||''}`);
  if(o.simVio) console.log('    simVio:',JSON.stringify({http:o.simVio.http,auth:o.simVio.auth,Usuario:o.simVio.Usuario,emp:o.simVio.codEmpresa,ag:o.simVio.codAgencia,uc:o.simVio.codUnidadCosto,id:o.simVio.idExterno,mon:o.simVio.monSolicitud}));
  if(o.error||o.stderr) console.log('    err:',o.error,o.stderr);
}
