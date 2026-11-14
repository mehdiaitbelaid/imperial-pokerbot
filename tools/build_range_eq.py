"""tools/range_eq.json: equity of each of the 169 hand classes against the top X% of hands
(all-in preflop, card removal included), for X in BUCKETS. Built from the 169x169 class-vs-class
equity matrix in tools/data (Monte Carlo, 100k samples per matchup)."""
import json, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
RD = "AKQJT98765432"
CLASSES = [a + b if i == j else (a + b + "s" if i < j else b + a + "o") for i, a in enumerate(RD) for j, b in enumerate(RD)]
E = np.load(os.path.join(HERE, "data", "eq169_E.npy"))
P = np.load(os.path.join(HERE, "data", "eq169_P.npy"))
PF = json.load(open(os.path.join(HERE, "preflop.json")))
BUCKETS = [0.015, 0.025, 0.04, 0.06, 0.09, 0.13, 0.18, 0.25, 0.35, 0.5, 0.7, 1.0]
nc = lambda c: 6 if len(c) == 2 else (4 if c[2] == "s" else 12)
order = sorted(CLASSES, key=lambda c: -(PF[c][0] + 1.6 * PF[c][1]))      # same ordering the bot uses for ranges
out = {}
for b in BUCKETS:
    w = np.zeros(169); left = b * 1326
    for c in order:
        take = min(nc(c), left); w[CLASSES.index(c)] = take / nc(c); left -= take
        if left <= 0: break
    num = (E * P * w).sum(axis=1); den = (P * w).sum(axis=1)
    for i, c in enumerate(CLASSES):
        out.setdefault(c, []).append(int(round(1000 * num[i] / den[i])))
json.dump({"buckets": BUCKETS, "eq": out}, open(os.path.join(HERE, "range_eq.json"), "w"), separators=(",", ":"))
for c in ("AA", "KK", "QQ", "JJ", "TT", "99", "AKs", "AKo", "AQs", "AJo", "KQs", "76s", "72o"):
    print(c, out[c])
print("bytes", os.path.getsize(os.path.join(HERE, "range_eq.json")), "| E shape", E.shape, "AA vs KK", round(float(E[CLASSES.index('AA')][CLASSES.index('KK')]), 3))
