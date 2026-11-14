"""What happened when WE raised a small bet (under 40% of the pot) in the given rounds.

    python3 tools/smallraise_live.py hands/saturday_r053.json ..."""
import json, sys
from collections import defaultdict
tot = defaultdict(float); rows = []
for f in sys.argv[1:]:
    d = json.load(open(f)); me = d["seat"]; P = d["players"]
    for h in d["hands"]:
        street = "preflop"; cur = 0; pot = 0; bets = defaultdict(int); fb = None; wait = None; inv = 0; live = set(range(len(P)))
        for e in h["events"]:
            if e[0] == "post":
                bets[e[1]] += e[2]; cur = max(cur, bets[e[1]]); pot += e[2]
                if e[1] == me: inv += e[2]
            elif e[0] == "board":
                street = e[1]; bets = defaultdict(int); cur = 0; fb = None
            elif e[0] == "refund":
                pot -= e[2]
                if e[1] == me: inv -= e[2]
            elif e[0] == "act":
                s, a, amt = e[1], e[2], e[3]
                if wait is not None and s == wait[0]:
                    rows.append((f[-8:-5], h["n"], P[s], wait[1], a, wait[2], wait[3], h["results"][me], "".join(h["hole"][str(me)]), wait[4]))
                    wait = None
                if a == "raise":
                    if street != "preflop":
                        if cur == 0:
                            fb = (s, amt / float(pot or 1))
                        elif fb is not None and fb[1] < 0.4 and s == me and s != fb[0] and wait is None:
                            wait = (fb[0], street, pot, amt - bets[s], len(live))
                            fb = None
                    if s == me: inv += amt - bets[s]
                    pot += amt - bets[s]; bets[s] = amt; cur = amt
                elif a == "call":
                    if s == me: inv += amt
                    pot += amt; bets[s] += amt
                elif a == "fold":
                    live.discard(s)
n = len(rows); fo = sum(1 for r in rows if r[4] == "fold"); ca = sum(1 for r in rows if r[4] == "call"); ra = sum(1 for r in rows if r[4] == "raise")
net = sum(r[7] for r in rows) / 20.0
print("%d round(s): we raised a small bet %d times -> bettor folded %d (%.0f%%), called %d, re-raised %d | net result of those hands %+.0f bb" % (
    len(sys.argv) - 1, n, fo, 100.0 * fo / max(1, n), ca, ra, net))
bt = defaultdict(lambda: [0, 0, 0.0])
for r in rows:
    bt[r[2]][0] += 1; bt[r[2]][1] += r[4] == "fold"; bt[r[2]][2] += r[7] / 20.0
for k, v in sorted(bt.items(), key=lambda kv: -kv[1][0]):
    print("   %-24s raised %2d, folded %2d, net %+.0f bb" % (k[:24], v[0], v[1], v[2]))
bad = sorted(rows, key=lambda r: r[7])[:4]
for r in bad:
    if r[7] < -200: print("   worst: r%s#%d %s vs %s on the %s: he %s, hand result %+d chips" % (r[0], r[1], r[8], r[2], r[3], r[4], r[7]))
