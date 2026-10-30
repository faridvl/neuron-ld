import sys,re,html
from s import get
for i in sys.argv[1:]:
    try:
        a=get("content/%s/child/attachment"%i,limit=50)
        print(i,"ATT:",[(x['title'],x['extensions'].get('fileSize')) for x in a['results']])
    except Exception as e: print(i,"att err",e)
    try:
        c=get("content/%s/child/comment"%i,limit=50,expand="body.storage")
        for x in c['results']:
            t=html.unescape(re.sub(r'<[^>]+>',' ',x['body']['storage']['value']))
            print(i,"COMMENT:",t[:400])
        print(i,"ncomments",len(c['results']))
    except Exception as e: print(i,"com err",e)
