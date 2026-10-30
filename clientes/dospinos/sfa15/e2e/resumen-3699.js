const fs=require('fs');
for (const l of fs.readFileSync('resultados-e2e-3699.txt','utf8').split(/\r?\n/).filter(Boolean)) {
  const o=JSON.parse(l);
  if(o.paso){console.log(JSON.stringify(o).slice(0,900));continue;}
  if(o.antes){console.log('['+o.caso+'] identicas='+o.identicas+' antes='+JSON.stringify(o.antes)+' despues='+JSON.stringify(o.despues));continue;}
  const r=o.res||o.resultados;
  const rs=(x)=>x&&x.Outcome?`${x.Outcome}/${x.UnavailableReason} req=${x.RequestNumber} cred=${x.CreditNumber} disp=${x.AvailableAmount} pa=${x.PossiblyApplied} msg="${(x.Message||'').slice(0,90)}"`:JSON.stringify(x);
  console.log(`[${o.caso}] sim ${o.simAntes}->${o.simDespues} (sim ${o.llamadasSim}, mini ${o.llamadasMini}) ${Array.isArray(r)?r.map(rs).join(' || '):rs(r)} ms=${o.ms||''} sig=${o.sigSolicitud}/${o.sigCredito} attempt=${o.attempt||''} attMsg=${(o.attemptMessage||'').slice(0,80)} audit=${o.auditoria||''}`);
  if(o.simVio) console.log('    simVio:',JSON.stringify({http:o.simVio.http,auth:o.simVio.auth,Usuario:o.simVio.Usuario,emp:o.simVio.codEmpresa,ag:o.simVio.codAgencia,uc:o.simVio.codUnidadCosto,id:o.simVio.idExterno,mon:o.simVio.monSolicitud,resp:o.simVio.respuesta&&JSON.stringify(o.simVio.respuesta).slice(0,160)}));
  if(o.error||o.stderr) console.log('    err:',o.error,o.stderr);
}
