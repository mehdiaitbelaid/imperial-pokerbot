"""Sandbox: duplicate-deal comparison of candidate bots.
Each candidate takes the SAME seat with the SAME cards against the SAME line-up, round by round,
so differences are paired and luck mostly cancels.
  python src/duel.py --cands bots/v5.py bots/mehdi_v2.py --field sparring/a.py ... --rounds 8 --seed 1
"""
import argparse,os,random,sys,statistics,json,time
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,ROOT)
from engine import FixedHandsTable
from engine.players import SubprocessPlayer
ap=argparse.ArgumentParser();ap.add_argument("--cands",nargs="+",required=True);ap.add_argument("--field",nargs="+",required=True)
ap.add_argument("--rounds",type=int,default=8);ap.add_argument("--hands",type=int,default=1000);ap.add_argument("--seed",type=int,default=0)
ap.add_argument("--name",default="table");ap.add_argument("--out",default=None)
a=ap.parse_args()
res={c:[] for c in a.cands};bad={c:[0,0,0,0.0] for c in a.cands};t0=time.time()
for r in range(a.rounds):
    rng=random.Random(a.seed*1000+r);order=list(range(len(a.field)+1));rng.shuffle(order);deck_seed=rng.random()
    for c in a.cands:
        paths=[c]+a.field;seats=[paths[i] for i in order];me=order.index(0)
        ps=[SubprocessPlayer(os.path.join(ROOT,p),bank_ms=10000) for p in seats]
        try: out=FixedHandsTable(ps,hands=a.hands,seed=deck_seed).play()
        finally:
            for p in ps: p.close()
        st=ps[me].stats;res[c].append(out["chips"][me]/20/a.hands*100)
        bad[c][0]+=st.timeouts;bad[c][1]+=st.errors;bad[c][2]+=st.bank_out;bad[c][3]=max(bad[c][3],st.total_ms/1000)
        if st.error_samples: print("ERR",c,st.error_samples[0][-500:],flush=True)
    print("[%s] round %d/%d %.0fs  "%(a.name,r+1,a.rounds,time.time()-t0)+"  ".join("%s %+.0f"%(os.path.basename(c),res[c][-1]) for c in a.cands),flush=True)
print("\n== %s: %d rounds x %d hands vs %s"%(a.name,a.rounds,a.hands,[os.path.basename(f)[:-3] for f in a.field]))
print("%-22s %8s %6s %4s %4s %5s %6s"%("candidate","bb/100","se","to","err","bank","s/rd"))
for c in a.cands:
    v=res[c];print("%-22s %+8.1f %6.1f %4d %4d %5d %6.2f"%(os.path.basename(c),statistics.mean(v),statistics.stdev(v)/len(v)**.5 if len(v)>1 else 0,*bad[c]))
base=a.cands[0]
for c in a.cands[1:]:
    d=[x-y for x,y in zip(res[base],res[c])];se=statistics.stdev(d)/len(d)**.5 if len(d)>1 else 0
    print("paired: %s minus %s = %+.1f +/- %.1f bb/100 (t=%.1f)"%(os.path.basename(base),os.path.basename(c),statistics.mean(d),se,statistics.mean(d)/se if se else 0))
if a.out: json.dump({"name":a.name,"res":res,"bad":bad},open(a.out,"w"))
