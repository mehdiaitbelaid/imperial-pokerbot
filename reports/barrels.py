"""Our river bets as a bluff (no pair or one pair) of 300+ chips, by opponent who faced them, and
what folding instead of calling would have changed for our big turn/river calls.

    python3 -I reports/barrels.py hands/sunday_s1_r002.json ...
"""
import json, sys
from collections import defaultdict
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from bigcalls import klass, AB

files = [a for a in sys.argv[1:] if not a.startswith("--")]
rb = defaultdict(lambda: [0, 0, 0, 0])      # villain -> n, folds, net, 3-barrel count
fold_inst = [0, 0, 0, 0]                    # n calls, won, actual net, net if folded
fi_v = defaultdict(lambda: [0, 0, 0, 0])
for f in files:
    d = json.load(open(f)); me = d["seat"]; names = [AB.get(p, p[:4]) for p in d["players"]]
    for h in d["hands"]:
        hole = h["hole"].get(str(me))
        if not hole:
            continue
        street = "pre"; board = []; contrib = defaultdict(int); inv = 0; last = None; pot = 0
        our_bets = set(); live = set(range(len(names))); counted_call = False; riverbet = None
        for e in h["events"]:
            if e[0] == "post":
                pot += e[2]; contrib[e[1]] += e[2]
                if e[1] == me: inv += e[2]
            elif e[0] == "board":
                street = e[1]; board = e[2]; contrib = defaultdict(int); last = None
            elif e[0] == "act":
                s, a, amt = e[1], e[2], e[3]
                if a == "fold":
                    live.discard(s)
                    if riverbet and s != me:
                        riverbet[1] += 1
                elif a == "raise":
                    add = amt - contrib[s]
                    if s == me:
                        if street != "pre" and last is None:
                            our_bets.add(street)
                            if street == "river" and add >= 300:
                                k = klass(hole, board).split("+")[0]
                                if k != "strong":
                                    riverbet = [[n for n in live if n != me], 0, k]
                        inv += add
                    last = (s, add / pot if pot else 0)
                    pot += add; contrib[s] = amt
                elif a == "call":
                    if s == me:
                        if street in ("turn", "river") and amt >= 500 and last and not counted_call:
                            k = klass(hole, board).split("+")[0]
                            if k != "strong":
                                counted_call = True
                                res = h["results"][me]
                                for A in (fold_inst, fi_v[names[last[0]]]):
                                    A[0] += 1; A[1] += res > 0; A[2] += res; A[3] += -inv
                        inv += amt
                    pot += amt; contrib[s] += amt
        if riverbet:
            res = h["results"][me]
            for v in riverbet[0]:
                A = rb[names[v]]
                A[0] += 1; A[1] += (v not in live); A[2] += res
                A[3] += our_bets >= {"flop", "turn", "river"}
print(f"{len(files)} round(s)")
print("OUR RIVER BETS OF 300+ WITHOUT TWO PAIR OR BETTER, by opponent facing them: n / he folded / net chips of those hands / of which three barrels")
for v, (n, fo, net, tb) in sorted(rb.items(), key=lambda x: x[1][2]):
    print(f"  {v:4s} n={n:2d} folded {fo:2d} net {net:+6d} three-barrels {tb}")
n, w, net, alt = fold_inst
print(f"OUR TURN/RIVER CALLS OF 500+ WITH ONE PAIR OR LESS (first per hand): n={n} won {w} | actual {net:+d} chips | if folded instead {alt:+d} | folding gains {alt-net:+d} chips")
for v, (n, w, net, alt) in sorted(fi_v.items(), key=lambda x: x[1][3] - x[1][2], reverse=True):
    print(f"  vs {v:4s} n={n:2d} won {w} actual {net:+d} if folded {alt:+d} gain {alt-net:+d}")
