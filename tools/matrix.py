"""Who wins chips from whom. python tools/matrix.py sim/league/*.json
Each hand's losses are shared among that hand's winners in proportion to what they won."""
import json, sys
from collections import defaultdict
flow = defaultdict(float); hands = defaultdict(int); net = defaultdict(float)
for f in sys.argv[1:]:
    d = json.load(open(f)); P = d["players"]
    for h in d["hands"]:
        res = h["results"]; gain = sum(r for r in res if r > 0)
        for i, r in enumerate(res):
            hands[P[i]] += 1; net[P[i]] += r
            if r < 0 and gain > 0:
                for j, w in enumerate(res):
                    if w > 0:
                        flow[(P[j], P[i])] += -r * w / gain
names = sorted(net, key=lambda n: -net[n] / hands[n])
print("bb/100 won by ROW from COLUMN (row minus column flow)")
print("%-12s %8s | " % ("", "TOTAL") + " ".join("%8s" % n[:8] for n in names))
for a in names:
    row = [(flow[(a, b)] - flow[(b, a)]) / 20 / hands[a] * 100 if a != b else 0.0 for b in names]
    print("%-12s %+8.1f | " % (a[:12], net[a] / 20 / hands[a] * 100) + " ".join("%+8.1f" % v if a != b else "%8s" % "-" for v, b in zip(row, names)))
