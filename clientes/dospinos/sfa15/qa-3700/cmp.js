const fs=require("fs");
function leer(f){const b=fs.readFileSync(f);if(b[0]===0xFF&&b[1]===0xFE)return b.slice(2).toString("utf16le");if(b[0]===0xEF&&b[1]===0xBB&&b[2]===0xBF)return b.slice(3).toString("utf8");return b.toString("utf8");}
function cuerpo(t){t=t.replace(/\r\n/g,"\n").replace(/[ \t]+$/gm,"").replace(/\n\s*GO\s*$/i,"");const m=t.search(/(CREATE|ALTER)\s+(OR\s+ALTER\s+)?PROC(EDURE)?\s+/i);return t.slice(m).trim().replace(/^(CREATE|ALTER)\s+(OR\s+ALTER\s+)?PROC(EDURE)?/i,"PROC");}
const a=cuerpo(leer(process.argv[2])),b=cuerpo(leer(process.argv[3]));
console.log(process.argv[4]||"",a===b?"IGUALES":"DIFERENTES",a.length,b.length);
if(a!==b){const A=a.split("\n"),B=b.split("\n");let n=0;for(let i=0;i<Math.max(A.length,B.length)&&n<12;i++){if(A[i]!==B[i]){console.log("L"+(i+1)+" <"+(A[i]||"").slice(0,150)+"\n   >"+(B[i]||"").slice(0,150));n++;}}}