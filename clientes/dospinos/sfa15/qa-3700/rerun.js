const fs=require("fs");
const sql=require("C:/Users/fvillacis/ClaudeLocalSession/sfa15/simulador-pruebas/deps/node_modules/mssql");
const envf="C:/Users/FVILLA~1/AppData/Local/Temp/claude/C--Users-fvillacis-ClaudeLocalSession/15c175d7-97e6-4dbf-802d-70c3b80d73b2/scratchpad/migrate-sfa15/.env";
const cs=fs.readFileSync(envf,"utf8").split(/\r?\n/).find(l=>l.startsWith("DB_CONNECTION_STRING=")).slice(21);
const P=Object.fromEntries(cs.split(";").filter(Boolean).map(x=>{const i=x.indexOf("=");return [x.slice(0,i).trim().toLowerCase(),x.slice(i+1)];}));
(async()=>{
 const pool=await new sql.ConnectionPool({server:"localhost",port:1433,database:"ZZ_QA3700_MIG",user:P["user id"],password:P.password,options:{trustServerCertificate:true},requestTimeout:120000}).connect();
 const dir=process.argv[2];
 for(const f of fs.readdirSync(dir).filter(x=>x.endsWith(".sql")).sort()){
  let t=fs.readFileSync(dir+"/"+f,"utf8").replace(/^\uFEFF/,"");
  const lotes=t.split(/^\s*GO\s*$/im).filter(x=>x.trim());
  let ok=true,msg="";
  for(const l of lotes){try{await pool.request().batch(l);}catch(e){ok=false;msg=e.message;break;}}
  console.log(f,ok?"OK":"ERROR "+msg,"(lotes "+lotes.length+")");
 }
 await pool.close();
})();
