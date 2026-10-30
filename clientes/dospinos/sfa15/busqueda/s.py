import sys,json,os,urllib.request,urllib.parse
A=os.environ['ATLASSIAN_BASIC_AUTH']
def get(p,**q):
    u="https://logicaldata.atlassian.net/wiki/rest/api/"+p+("?"+urllib.parse.urlencode(q) if q else "")
    r=urllib.request.Request(u,headers={"Authorization":"Basic "+A})
    return json.load(urllib.request.urlopen(r))
if __name__=="__main__":
    for t in sys.argv[1:]:
        print("==",t)
        d=get("search",cql='text ~ "%s"'%t,limit=30)
        for r in d['results']:
            c=r.get('content',{});print(c.get('id'),r['title'])
