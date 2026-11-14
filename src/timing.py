"""Measure per-decision time of a bot in-process across a real 8-seat round."""
import os,sys,time,importlib.util,random
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,ROOT)
from engine import FixedHandsTable
from engine.players import LocalPlayer
def load(p):
    s=importlib.util.spec_from_file_location(os.path.basename(p)[:-3]+str(random.random())[2:8],p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.Agent
target=sys.argv[1];others=sys.argv[2:]
T=load(os.path.join(ROOT,target));times=[]
class Timed(T):
    def act(self,st):
        t=time.perf_counter();r=super().act(st);times.append((time.perf_counter()-t)*1000);return r
ps=[LocalPlayer(Timed)]+[LocalPlayer(load(os.path.join(ROOT,o))) for o in others]
FixedHandsTable(ps,hands=1000,seed=1).play()
times.sort();n=len(times)
print("decisions %d  p50 %.2fms  p95 %.2fms  p99 %.2fms  max %.2fms  total %.2fs"%(n,times[n//2],times[int(n*.95)],times[int(n*.99)],times[-1],sum(times)/1000))
