const fs=require("fs"),path=require("path");
function leer(f){const b=fs.readFileSync(f);if(b[0]===0xFF&&b[1]===0xFE)return b.slice(2).toString("utf16le");if(b[0]===0xEF&&b[1]===0xBB&&b[2]===0xBF)return b.slice(3).toString("utf8");return b.toString("utf8");}
function* walk(d){for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())yield* walk(p);else if(/\.(sql|vb|cs)$/i.test(e.name))yield p;}}
const root=process.argv[2];const reg=[
 [/insert\s+(into\s+)?(dbo\.)?\[?(Factura|Ticket)_Encabezado\]?/ig,"INSERT enc"],
 [/into\s+#?@?\w+\s+from\s+(dbo\.)?\[?(Factura|Ticket)_Encabezado/ig,"SELECT INTO enc"],
 [/select\s+(top\s+\d+\s+)?\*\s+from\s+(dbo\.)?\[?(Factura|Ticket)_Encabezado/ig,"SELECT * enc"],
 [/(\w+)\.\*\s*[\s\S]{0,40}?from\s+(dbo\.)?\[?(Factura|Ticket)_Encabezado\]?\s+(as\s+)?\1\b/ig,"alias.* enc"]];
const out={};
for(const f of walk(root)){let t;try{t=leer(f);}catch(e){continue;}
 for(const [re,n] of reg){re.lastIndex=0;let m;while((m=re.exec(t))){const line=t.slice(0,m.index).split("\n").length;(out[n]=out[n]||[]).push(path.relative(root,f).replace(/\\/g,"/")+":"+line);}}}
for(const n in out){console.log("== "+n+" ("+out[n].length+")");const seen=new Set();for(const x of out[n]){const k=x.split(":")[0];if(seen.has(k))continue;seen.add(k);console.log("  "+x);}}