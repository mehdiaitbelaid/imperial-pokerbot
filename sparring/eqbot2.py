"""Typical hackathon equity bot: MC equity vs random hands, pot odds, raises strong."""
import os,sys,random,time
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.cards import evaluate, to_int
class Agent:
    def __init__(self): self.r=random.Random()
    def eq(self,hole,board,k):
        dead=set(hole+board);deck=[c for c in range(52) if c not in dead];w=0;n=0;t=time.perf_counter()+0.004
        while time.perf_counter()<t and n<400:
            cs=self.r.sample(deck,5-len(board)+2*k);bd=board+cs[:5-len(board)];o=cs[5-len(board):]
            me=evaluate(hole+bd);ok=1
            for i in range(k):
                if evaluate(o[2*i:2*i+2]+bd)>me: ok=0;break
            w+=ok;n+=1
        return w/max(n,1)
    def act(self,s):
        L=s["legal_actions"];k=max(1,sum(1 for i,f in enumerate(s["folded"]) if not f and i!=s["seat"]))
        e=self.eq([to_int(c) for c in s["hole_cards"]],[to_int(c) for c in s["board"]],min(k,4))
        po=s["to_call"]/max(1,s["pot"]+s["to_call"])
        if "raise" in L and e>max(0.6/k**0.5,0.35):
            return {"action":"raise","amount":min(s["max_raise_to"],max(s["min_raise_to"],max(s["bets"])+s["pot"]*3//4))}
        if s["to_call"]==0: return {"action":"check"}
        if e>po+0.02: return {"action":"call"}
        return {"action":"fold"}
