"""Hands where we 3-bet preflop and Anker cold-called behind us: actual result vs giving up on the flop.
    python3 -I reports/ankcold.py hands/sunday_s1_r008.json ...
"""
import json, sys, os
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bigcalls import klass
T = defaultdict(lambda: [0, 0, 0])
for f in sys.argv[1:]:
    d = json.load(open(f)); me = d["seat"]; ank = d["players"].index("Anker Batteries")
    for h in d["hands"]:
        raises = []; cold = False; street = "pre"; inv = 0; contrib = defaultdict(int); bets = set(); flopk = None; hu = None
        live = set(range(len(d["players"])))
        for e in h["events"]:
            if e[0] == "post":
                contrib[e[1]] += e[2]
            elif e[0] == "board":
                if street == "pre":
                    inv = contrib[me]; hu = len(live) == 2
                    flopk = klass(h["hole"][str(me)], e[2]).split("+")[0]
                street = e[1]; contrib = defaultdict(int); first = True
            elif e[0] == "act":
                s, a, amt = e[1], e[2], e[3]
                if a == "fold": live.discard(s)
                if street == "pre":
                    if a == "raise": raises.append(s); contrib[s] = amt
                    elif a == "call":
                        contrib[s] += amt
                        if s == ank and len(raises) == 2 and raises[1] == me: cold = True
                else:
                    if a == "raise":
                        if s == me and max(contrib.values() or [0]) == 0: bets.add(street)
                        contrib[s] = amt
                    elif a == "call": contrib[s] += amt
        if cold and flopk and len(raises) == 2:
            res = h["results"][me]
            line = "3 barrels" if bets >= {"flop", "turn", "river"} else ("2 barrels" if bets >= {"flop", "turn"} else ("flop bet only" if "flop" in bets else "no flop bet"))
            for key in (("ALL", ""), (flopk, line)):
                T[key][0] += 1; T[key][1] += res; T[key][2] += -inv
print("we 3-bet, Anker cold-called, flop seen | flop class, our line: hands / actual chips / if we had given up on the flop / difference")
for k, (n, res, alt) in sorted(T.items()):
    print(f"  {k[0]:7s} {k[1]:14s} n={n:3d} actual {res:+7d} give-up {alt:+7d} diff {res-alt:+7d}")
