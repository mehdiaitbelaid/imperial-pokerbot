"""Our turn/river FOLDS facing 500+ chips with one pair or less; says if the hand history shows we would have won.
    python3 -I reports/bigfolds.py hands/sunday_s1_r008.json ...
"""
import json, sys, os
from collections import defaultdict
from itertools import combinations
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bigcalls import klass, AB, R
from collections import Counter
def score5(cs):
    rs = sorted((R.index(c[0]) for c in cs), reverse=True)
    cnt = Counter(rs); order = sorted(cnt, key=lambda r: (cnt[r], r), reverse=True)
    fl = len({c[1] for c in cs}) == 1; u = sorted(set(rs)); st = len(u) == 5 and (u[-1] - u[0] == 4 or u == [0, 1, 2, 3, 12])
    hi = 3 if u == [0, 1, 2, 3, 12] else rs[0]
    v = sorted(cnt.values(), reverse=True)
    if st and fl: c = 8
    elif v[0] == 4: c = 7
    elif v[:2] == [3, 2]: c = 6
    elif fl: c = 5
    elif st: c = 4
    elif v[0] == 3: c = 3
    elif v[:2] == [2, 2]: c = 2
    elif v[0] == 2: c = 1
    else: c = 0
    return (c, [hi] if st else order)
def best7(cs): return max(score5(c) for c in combinations(cs, 5))
n = shown_n = wouldwin = 0; rows = []
for f in sys.argv[1:]:
    d = json.load(open(f)); me = d["seat"]; names = [AB.get(p, p[:4]) for p in d["players"]]; tag = f.split("_")[-1][:4]
    for h in d["hands"]:
        hole = h["hole"].get(str(me))
        if not hole: continue
        street = "pre"; board = []; contrib = defaultdict(int); last = None
        for e in h["events"]:
            if e[0] == "post": contrib[e[1]] += e[2]
            elif e[0] == "board": street = e[1]; board = e[2]; contrib = defaultdict(int); last = None
            elif e[0] == "act":
                s, a, amt = e[1], e[2], e[3]
                if a == "raise": last = (s, amt); contrib[s] = amt
                elif a == "call": contrib[s] += amt
                elif a == "fold" and s == me and street in ("turn", "river") and last and last[1] - contrib[me] >= 500:
                    k = klass(hole, board).split("+")[0]
                    if k == "strong": continue
                    n += 1; note = "no showdown"
                    others = {x: c for x, c in h["hole"].items() if int(x) != me}
                    if others and len(h["board"]) == 5:
                        shown_n += 1
                        mine = best7(hole + h["board"]); bestopp = max(best7(c + h["board"]) for c in others.values())
                        w = mine > bestopp; wouldwin += w
                        note = ("WOULD HAVE WON" if w else "would have lost") + " vs " + ",".join(names[int(x)] + " " + "".join(c) for x, c in others.items())
                    rows.append(f"{tag}#{h['n']} {street} {''.join(hole)} on {''.join(board)} {k} folded to {names[last[0]]} facing {last[1]-contrib[me]} -> {h['results'][me]:+d} ({note})")
print(f"OUR TURN/RIVER FOLDS FACING 500+ WITH ONE PAIR OR LESS: n={n}, opponent cards known in {shown_n}, would have won {wouldwin}")
for r in rows[-12:]: print("   ", r)
