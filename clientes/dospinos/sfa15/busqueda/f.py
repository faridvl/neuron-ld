import re,sys,json,html
from s import get
ids=sys.argv[1:]
for i in ids:
    d=get("content/"+i,expand="body.storage,version")
    t=d['body']['storage']['value']
    t=re.sub(r'<br\s*/?>|</p>|</tr>|</li>|</h\d>','\n',t); t=re.sub(r'</t[dh]>',' | ',t)
    t=html.unescape(re.sub(r'<[^>]+>','',t))
    open("pg/%s.txt"%i,"w",encoding="utf-8").write(d['title']+"\n"+t)
    print(i,d['title'],len(t))
