"""Where our chips go, from real hand histories: exclusive buckets, then the worst hands.
    python3 tools/leaks.py hands/saturday_r003.json ...  [--worst 14]"""
import json, sys
from collections import defaultdict
worst_n = 12
files = []
_it = iter(sys.argv[1:])
for _a in _it:
    if _a == "--worst":
        worst_n = int(next(_it))
    elif not _a.startswith("--"):
        files.append(_a)
B = defaultdict(lambda: [0, 0.0]); N = 0; worst = []
for f in files:
    d = json.load(open(f)); P = d["players"]; me = d["seat"]
    for h in d["hands"]:
        N += 1; r = h["results"][me]; ev = h["events"]
        street = "preflop"; mine = []; cur = 0; mybet = 0; line = []
        for e in ev:
            if e[0] == "board":
                street = e[1]; cur = 0; mybet = 0; line.append("| " + " ".join(e[2][-1:] if e[1] != "flop" else e[2]))
            elif e[0] == "post":
                cur = max(cur, e[2])
                if e[1] == me: mybet = e[2]
            elif e[0] == "act":
                if e[1] == me:
                    facing = cur > mybet
                    mine.append((street, e[2], facing, e[3]))
                    line.append("US %s%s" % (e[2], " %d" % e[3] if e[3] else ""))
                    if e[2] == "raise": mybet = e[3]
                    elif e[2] == "call": mybet += e[3]
                elif e[2] != "fold":
                    line.append("%s %s%s" % (P[e[1]][:8], e[2], " %d" % e[3] if e[3] else ""))
                if e[2] == "raise": cur = e[3]
        sd = str(me) in (h.get("showdown") or {})
        pre = [m for m in mine if m[0] == "preflop"]; post = [m for m in mine if m[0] != "preflop"]
        vol = any(m[1] in ("call", "raise") for m in pre)
        raised = any(m[1] == "raise" for m in pre)
        last = mine[-1] if mine else None
        if not mine or (not vol and not post):
            k = "blinds / folded preflop"
        elif not post:
            k = "won preflop uncontested" if r > 0 else ("raised preflop then folded to a re-raise" if raised else "called preflop then folded preflop") if last[1] == "fold" else "all-in preflop " + ("won" if r > 0 else "lost")
        elif sd:
            rc = last[0] == "river" and last[1] == "call"
            k = "showdown won" if r > 0 else ("showdown lost after our river call" if rc else "showdown lost, other lines")
        elif r > 0:
            k = "won postflop without showdown"
        else:
            st = last[0]
            betted = any(m[1] == "raise" for m in post)
            calledp = any(m[1] == "call" for m in post)
            if st == "river": k = "folded the river after " + ("betting" if betted else "calling" if calledp else "checking")
            elif betted: k = "bet the flop or turn, then folded"
            elif calledp: k = "called the flop, folded the turn"
            else: k = ("raised" if raised else "called") + " preflop, check-folded flop or turn"
        B[k][0] += 1; B[k][1] += r
        if r <= -400: worst.append((r, f.split("_")[-1][:4], h["n"], "".join(h["hole"][str(me)]), k, "; ".join(line),
                                    {P[int(s)][:10]: "".join(c) for s, c in h["hole"].items() if int(s) != me}))
print("%d hands, total %+.1f bb/100" % (N, sum(v[1] for v in B.values()) / 20 / N * 100))
for k, v in sorted(B.items(), key=lambda kv: kv[1][1]):
    print("  %-46s n=%5d  %+7.1f bb/100   (%+.1f bb each)" % (k, v[0], v[1] / 20 / N * 100, v[1] / 20 / v[0]))
print("\nWorst hands:")
for w in sorted(worst)[:worst_n]:
    print("  %+6d %s#%-4d %s [%s]\n         %s\n         shown: %s" % w)
