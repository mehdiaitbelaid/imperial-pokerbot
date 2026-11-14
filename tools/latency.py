"""Dealer-side latency of each bot, measured exactly as the tournament dealer measures it
(time from sending the act message to reading the reply), with a generous limit so the
tail is recorded instead of turned into timeouts.
  python3 tools/latency.py --rounds 4 bots/a.py bots/b.py ...   (8 seats; run under taskset + burners to emulate a slow box)"""
import argparse,os,sys,time,random,json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,ROOT);sys.path.insert(0,os.path.join(ROOT,"field"))
from engine import FixedHandsTable
from engine.players import SubprocessPlayer
ap=argparse.ArgumentParser();ap.add_argument("bots",nargs="+");ap.add_argument("--rounds",type=int,default=3)
ap.add_argument("--hands",type=int,default=1000);ap.add_argument("--seed",type=int,default=0);ap.add_argument("--out",default=None)
a=ap.parse_args()
class Rec(SubprocessPlayer):
    def __init__(s,*x,**k):
        super().__init__(*x,**k);s.lat=[]
    def act(s,state):
        t=time.perf_counter();r=super().act(state);ms=(time.perf_counter()-t)*1000
        live=sum(1 for f in state["folded"] if not f)
        s.lat.append((ms,state["street"],live,len(state.get("history") or ()),state.get("to_call",0)>0))
        return r
lat={b:[] for b in a.bots};rng=random.Random(a.seed)
for r in range(a.rounds):
    seats=list(a.bots);rng.shuffle(seats)
    ps=[Rec(os.path.join(ROOT,p),timeout_ms=500,bank_ms=None) for p in seats]
    try: FixedHandsTable(ps,hands=a.hands,seed=rng.random()).play()
    finally:
        for p in ps: p.close()
    for p,b in zip(ps,seats): lat[b]+=p.lat
    print("round",r+1,"done",flush=True)
def q(v,f): return v[min(len(v)-1,int(len(v)*f))]
print("%-22s %6s %6s %6s %6s %7s %7s %5s %5s %5s"%("bot","n","p50","p99","p99.9","max",">10ms",">5ms","post>5","pre>5"))
for b in a.bots:
    v=sorted(x[0] for x in lat[b]);n=len(v)
    o10=sum(1 for x in v if x>10);o5=sum(1 for x in v if x>5)
    po=sum(1 for x in lat[b] if x[0]>5 and x[1]!="preflop");pr=o5-po
    print("%-22s %6d %6.2f %6.2f %6.2f %7.2f %7d %5d %5d %5d"%(os.path.basename(b),n,q(v,.5),q(v,.99),q(v,.999),v[-1],o10,o5,po,pr))
if a.out: json.dump({b:lat[b] for b in a.bots},open(a.out,"w"))
