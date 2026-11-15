"""Anker's reply when we 3-bet and he is still to act behind us (not the opener).
    python3 -I reports/ank4.py hands/sunday_s1_r029.json ...
"""
import json, sys
for f in sys.argv[1:]:
    d = json.load(open(f)); me = d["seat"]; ank = d["players"].index("Anker Batteries")
    halves = {0: [0, 0, 0, 0, 0, 0], 1: [0, 0, 0, 0, 0, 0]}   # n, fold, call, 4bet, our chips, our reply fold
    for h in d["hands"]:
        r = []; we3 = False; rep = None; ourrep = None
        for e in h["events"]:
            if e[0] == "board": break
            if e[0] != "act": continue
            s, a = e[1], e[2]
            if we3 and rep is None and s == ank and len(r) == 2:
                rep = a
            elif we3 and rep == "raise" and s == me and ourrep is None:
                ourrep = a
            if a == "raise":
                r.append(s)
                if len(r) == 2 and s == me and r[0] != ank: we3 = True
        if we3 and rep:
            H = halves[0 if h["n"] <= 500 else 1]
            H[0] += 1; H[1] += rep == "fold"; H[2] += rep == "call"; H[3] += rep == "raise"; H[4] += h["results"][me]; H[5] += ourrep == "fold"
    for k, lab in ((0, "h1-500"), (1, "h501-1000")):
        n, fo, ca, ra, net, of = halves[k]
        print("%s %s: we 3-bet with Anker behind %d | he folded %d, called %d, 4-bet %d (we then folded %d) | our chips in those hands %+d" % (f[-9:-5], lab, n, fo, ca, ra, of, net))
