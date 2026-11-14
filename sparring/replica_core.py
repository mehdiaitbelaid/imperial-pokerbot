"""Stat-driven replica of a real opponent: VPIP/PFR preflop, aggression and
fold-to-bet postflop, bluffs at a set rate. Parameters fitted from hand data."""
import random
R = "23456789TJQKA"
ORDER = {}
_cls = []
for i in range(12, -1, -1):
    for j in range(i, -1, -1):
        if i == j: _cls.append((R[i]*2, 6))
        else: _cls += [(R[i]+R[j]+"s", 4), (R[i]+R[j]+"o", 12)]
def _score(c):
    a, b = R.index(c[0]), R.index(c[1]); pair = a == b; s = c.endswith("s")
    return (a + b) / 24 + (0.5 + a / 24 - (a + b) / 24 if pair else 0) + (0.06 if s else 0) - (0.03 * max(0, a - b - 1) if not pair else 0)
_cls.sort(key=lambda x: -_score(x[0]))
cum = 0
for c, w in _cls:
    ORDER[c] = (cum + w / 2) / 1326.0; cum += w
def pct(h):
    a, b = h; ra, rb = R.index(a[0]), R.index(b[0])
    if ra < rb: a, b, ra, rb = b, a, rb, ra
    return ORDER[a[0] + b[0] + ("" if ra == rb else ("s" if a[1] == b[1] else "o"))]
def strength(h, board):
    hr = [R.index(c[0]) for c in h]; br = [R.index(c[0]) for c in board]
    if not br: return 0
    hits = sum(r in br for r in hr)
    if hr[0] == hr[1]: return 3 if hr[0] in br else (2 if hr[0] > max(br) else 1)
    if hits == 2: return 3
    if hits == 1:
        r = [x for x in hr if x in br][0]
        return 2 if r == max(br) else 1
    suits = [c[1] for c in h + board]
    if max(suits.count(s) for s in "cdhs") >= 4: return 1
    return 0
def make(vpip, pfr, agg, ftb, bluff, size=0.66, open_bb=3):
    class Agent:
        def __init__(self): self.r = random.Random()
        def act(self, s):
            L = s["legal_actions"]; h = s["hole_cards"]; r = self.r.random
            def rz(t):
                return {"action": "raise", "amount": int(max(s["min_raise_to"], min(s["max_raise_to"], t)))}
            cur = max(s["bets"])
            if s["street"] == "preflop":
                p = pct(h); raised = cur > s["big_blind"]
                if p <= pfr * (0.45 if raised else 1) and "raise" in L:
                    return rz(cur * 3 if raised else s["big_blind"] * open_bb)
                if p <= vpip * (0.6 if raised else 1) and s["to_call"] <= (s["big_blind"] * 12 if not raised else 400 + 1600 * (vpip > 0.6)):
                    return {"action": "call" if "call" in L else "check"}
                return {"action": "check" if "check" in L else "fold"}
            st = strength(h, s["board"])
            if s["to_call"] == 0:
                if "raise" in L and ((st >= 2 and r() < 0.4 + agg) or (st == 1 and r() < agg * 0.7) or (st == 0 and r() < bluff)):
                    return rz(s["pot"] * size)
                return {"action": "check"}
            if st >= 3 and "raise" in L and r() < agg:
                return rz(cur + s["pot"])
            if st >= 1 or r() > ftb * (1.3 if s["to_call"] > s["pot"] * 0.6 else 1.0):
                if st == 0 and "raise" in L and r() < bluff * 0.3:
                    return rz(cur + s["pot"])
                return {"action": "call"}
            return {"action": "fold"}
    return Agent
