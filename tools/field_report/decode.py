import json,sys,base64,gzip,os,glob
out=sys.argv[1]
for f in sys.argv[2:]:
    t=open(f).read()
    try:
        arr=json.loads(t); txt=arr[0]['text'] if isinstance(arr,list) else t
    except Exception:
        txt=t
    i=min(x for x in (txt.find('"'),txt.find('{')) if x>=0)
    obj,_=json.JSONDecoder().raw_decode(txt[i:])
    if isinstance(obj,str): obj=json.loads(obj)
    for ref,b in obj.items():
        d=json.loads(gzip.decompress(base64.b64decode(b)))
        name=ref.replace('/','_')+'.json'
        json.dump(d,open(os.path.join(out,name),'w'))
        print(name,len(d['hands']),d['players'],d['round']['bb100'])
