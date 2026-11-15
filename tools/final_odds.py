import json, statistics as st, random, sys, os
def load(p): return json.load(open(p))
def rep(p, label):
    d=load(p); k=100.0/20/d["hands"]; names=["us"]+[os.path.basename(f)[:-3] for f in d["field"]]
    ref=d["bots"][0]; out={}
    print("\n%s: %d blocks of %d hands per bot; opponents %s"%(label,d["rounds"],d["hands"],", ".join(names[1:])))
    for b in d["bots"]:
        us=[r[0]*k for r in d["data"][b]]; base=[r[0]*k for r in d["data"][ref]]; diff=[x-y for x,y in zip(us,base)]
        print("  %-5s %+6.1f +- %.1f bb/100 | vs %s %+5.1f +- %.1f | block sd %.0f | timeouts %d errors %d"%(os.path.basename(b)[:-3],st.mean(us),st.stdev(us)/len(us)**.5,os.path.basename(ref)[:-3],st.mean(diff),(st.stdev(diff)/len(diff)**.5 if b!=ref else 0),st.stdev(us),d["to"][b],d["err"][b]))
        rows=d["data"][b]; print("        seats: "+"  ".join("%s %+.0f"%(names[j],st.mean(r[j]*k for r in rows)) for j in range(1,len(names))))
        out[b]=rows
    return d,out
def finals(rows, shift_bb=0.0, n=20000, seed=1):
    rng=random.Random(seed); first=top2=0; m=len(rows[0]); sh=shift_bb*200.0   # chips per 1,000-hand block
    for _ in range(n):
        tot=[0.0]*m
        for _ in range(5):
            r=rng.choice(rows)
            tot[0]+=r[0]-sh
            for j in range(1,m): tot[j]+=r[j]+sh/(m-1)
        rank=1+sum(1 for j in range(1,m) if tot[j]>tot[0])
        first+=rank==1; top2+=rank<=2
    return 100.0*first/n, 100.0*top2/n
if __name__=="__main__":
    for p,l in zip(sys.argv[1::2],sys.argv[2::2]):
        d,out=rep(p,l)
        if "--finals" in sys.argv or True:
            for b,rows in out.items():
                k=100.0/20/d["hands"]; mean=st.mean(r[0]*k for r in rows)
                res=[]
                for edge in ("sim",20,10,0):
                    sh=0.0 if edge=="sim" else mean-edge
                    f,t=finals(rows,sh); res.append("edge %s: 1st %.0f%%, top-2 %.0f%%"%(("%+.0f (as simulated)"%mean) if edge=="sim" else "%+d"%edge,f,t))
                print("  5-block finals, %s: "%os.path.basename(b)[:-3]+" | ".join(res))
