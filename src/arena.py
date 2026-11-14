"""Arena: fixed 8-seat line-up, many rounds, report bb/100 with std error per bot."""
import argparse,os,random,sys,time,statistics
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,ROOT)
from engine import FixedHandsTable
from engine.players import SubprocessPlayer
ap=argparse.ArgumentParser();ap.add_argument("bots",nargs="+");ap.add_argument("--rounds",type=int,default=6)
ap.add_argument("--hands",type=int,default=1000);ap.add_argument("--seed",type=int,default=0);ap.add_argument("--betting",default="no_limit")
a=ap.parse_args();rng=random.Random(a.seed)
per={b:[] for b in a.bots};stats={b:[0,0,0,0.0] for b in a.bots}
t=time.time()
for r in range(a.rounds):
    seats=list(a.bots);rng.shuffle(seats)
    ps=[SubprocessPlayer(os.path.join(ROOT,p),bank_ms=10000) for p in seats]
    try: res=FixedHandsTable(ps,hands=a.hands,config={"betting":a.betting},seed=rng.random()).play()
    finally:
        for p in ps: p.close()
    for i,p in enumerate(seats):
        per[p].append(res["chips"][i]/20/a.hands*100);st=ps[i].stats
        stats[p][0]+=st.timeouts;stats[p][1]+=st.errors;stats[p][2]+=st.bank_out;stats[p][3]=max(stats[p][3],st.total_ms/1000)
        if st.error_samples and stats[p][1]==st.errors: print("ERR",p,st.error_samples[0][-600:])
    print("round",r+1,"done %.0fs"%(time.time()-t),flush=True)
print("%-26s %8s %7s %5s %5s %5s %6s"%("bot","bb/100","se","to","err","bank","s/rd"))
for b in sorted(a.bots,key=lambda b:-statistics.mean(per[b])):
    v=per[b];se=statistics.stdev(v)/len(v)**0.5 if len(v)>1 else 0
    print("%-26s %+8.1f %7.1f %5d %5d %5d %6.2f"%(b,statistics.mean(v),se,*stats[b]))
