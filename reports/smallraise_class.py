"""Our raises of a bet under 0.42 pot, split by what we held (nopair / pair / strong) and by bettor.
    python3 -I reports/smallraise_class.py hands/sunday_s1_r002.json ...
"""
import json, sys, os
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bigcalls import klass, AB
agg = defaultdict(lambda: [0, 0, 0, 0])
for f in sys.argv[1:]:
    d = json.load(open(f)); me = d["seat"]; names = [AB.get(p, p[:4]) for p in d["players"]]
    for h in d["hands"]:
        hole = h["hole"].get(str(me))
        if not hole: continue
        street = "pre"; board = []; contrib = defaultdict(int); pot = 0; bet = None; pend = None; seen = False
        for e in h["events"]:
            if e[0] == "post":
                pot += e[2]; contrib[e[1]] += e[2]
            elif e[0] == "board":
                street = e[1]; board = e[2]; contrib = defaultdict(int); bet = None; pend = None
            elif e[0] == "act":
                s, a, amt = e[1], e[2], e[3]
                if pend and s == pend[0]:
                    agg[pend[1]][1] += a == "fold"; pend = None
                if a == "raise":
                    add = amt - contrib[s]
                    if street != "pre":
                        if bet is None:
                            bet = (s, amt / pot if pot else 0)
                        elif s == me and bet[0] != me and bet[1] < 0.42 and not seen:
                            seen = True
                            k = klass(hole, board).split("+")[0]
                            key = (names[bet[0]], street if street == "flop" else "turn/river", k)
                            agg[key][0] += 1; agg[key][2] += h["results"][me]; agg[key][3] += add
                            pend = (bet[0], key)
                    pot += add; contrib[s] = amt
                elif a == "call":
                    pot += amt; contrib[s] += amt
print("bettor street class: raises / he folded at once / net chips of those hands (first such raise per hand) / avg chips we put in")
tot = defaultdict(lambda: [0, 0, 0])
for k, (n, fo, net, put) in sorted(agg.items()):
    print(f"  {k[0]:4s} {k[1]:10s} {k[2]:7s} n={n:3d} folded {fo:3d} ({100*fo//n}%) net {net:+6d} avg raise {put//n}")
    t = tot[(k[0], k[2])]; t[0] += n; t[1] += fo; t[2] += net
print("by bettor and class:")
for k, (n, fo, net) in sorted(tot.items()):
    print(f"  {k[0]:4s} {k[1]:7s} n={n:3d} folded {fo:3d} ({100*fo//n}%) net {net:+6d}")
