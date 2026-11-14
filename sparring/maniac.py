"""Loose-aggressive maniac: raises often, barrels, calls wide."""
import random
R="23456789TJQKA"
class Agent:
    def __init__(self): self.r=random.Random()
    def act(self,s):
        L=s["legal_actions"];a,b=sorted((R.index(c[0]) for c in s["hole_cards"]),reverse=True)
        good=a==b or a>=9 or s["hole_cards"][0][1]==s["hole_cards"][1][1]
        if "raise" in L and self.r.random()<(0.55 if good else 0.25):
            return {"action":"raise","amount":min(s["max_raise_to"],s["min_raise_to"]+s["pot"])}
        if s["to_call"]==0: return {"action":"check"}
        if self.r.random()<(0.85 if good else 0.45) or s["to_call"]<=s["big_blind"]: return {"action":"call"}
        return {"action":"fold"}
