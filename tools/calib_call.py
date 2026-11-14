"""Is the bot's equity estimate right when facing a river bet?

Replays real hands. For every river bet or raise that was called and shown down, computes the
equity the bot's model gives the CALLER's hand against the bettor's range, and compares it with
who actually won. If "predicted 30%" hands win 50% of the time, the bot folds too much.

    python tools/calib_call.py bots/av7.py
"""
import glob, importlib.util, json, os, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("botmod", os.path.join(ROOT, sys.argv[1]))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
files = sys.argv[2:] or sorted(glob.glob(os.path.join(ROOT, "hands", "*.json")))
B = defaultdict(lambda: [0, 0.0, 0.0])
def bucket(p): return min(5, int(p * 6))
for f in files:
    d = json.load(open(f)); n = len(d["players"]); A = M.Agent()
    for h in d["hands"]:
        hist = []; street = "preflop"; board = []; posted = 0; pend = None; cur = 0; bets = [0] * n; pot = 0
        shown = {int(k): v for k, v in h["hole"].items() if k in (h.get("showdown") or {})}
        res = h["results"]
        for ev in h["events"]:
            if ev[0] == "post":
                hist.append({"seat": ev[1], "street": "preflop", "action": "small_blind" if posted == 0 else "big_blind", "amount": ev[2]}); posted += 1
                bets[ev[1]] += ev[2]; cur = max(cur, bets[ev[1]]); pot += ev[2]
            elif ev[0] == "board":
                street = ev[1]; board = [M.CARD[c] for c in ev[2]]; pend = None; cur = 0; bets = [0] * n
            elif ev[0] == "refund":
                pot -= ev[2]
            elif ev[0] == "act":
                s, a, amt = ev[1], ev[2], ev[3]
                if a == "call" and pend and street == "river" and s in shown and pend[0] in shown:
                    bettor, kind, hsnap, x = pend
                    bp, sc, sm, bmask, thr, fs, scf, smf, d4b, paired, tb = A._board_ctx(board)
                    hc = [M.CARD[c] for c in shown[s]]
                    dead = set(board) | set(hc)
                    L = A._lines(hsnap, n, "river")
                    strong, weak, keep, sf = A._tier(bettor, L, dead, bp, fs, scf, smf, sc, bmask, d4b, 5, thr)
                    myv = M.RANK[bp * M.CP[hc[0]] * M.CP[hc[1]]]
                    if fs >= 0 and scf + ((hc[0] & 3) == fs) + ((hc[1] & 3) == fs) >= 5:
                        m = smf
                        for c in hc:
                            if (c & 3) == fs: m |= 1 << (c >> 2)
                        myv = max(myv, M.FLUSH[m])
                    w = sum(1.0 if myv > t[0] else 0.5 if myv == t[0] else 0.0 for t in strong); tot = float(len(strong))
                    if weak:
                        w += keep * sum(1.0 if myv > t[0] else 0.5 if myv == t[0] else 0.0 for t in weak); tot += keep * len(weak)
                    p = w / tot if tot else 0.5
                    bv = [M.CARD[c] for c in shown[bettor]]
                    v2 = M.RANK[bp * M.CP[bv[0]] * M.CP[bv[1]]]
                    if fs >= 0 and scf + ((bv[0] & 3) == fs) + ((bv[1] & 3) == fs) >= 5:
                        m = smf
                        for c in bv:
                            if (c & 3) == fs: m |= 1 << (c >> 2)
                        v2 = max(v2, M.FLUSH[m])
                    won = 1.0 if myv > v2 else 0.5 if myv == v2 else 0.0
                    cls = ("smaller than usual", "usual size", "bigger than usual")[M.size_class(A.st[bettor], x)]
                    for key in ((kind, bucket(p)), (kind, "all"), (kind + ": " + cls if kind == "bet" else kind, "all")):
                        r = B[key]; r[0] += 1; r[1] += p; r[2] += won
                hist.append({"seat": s, "street": street, "action": a, "amount": amt})
                if a == "raise":
                    x = (amt - cur) / float(pot + cur - bets[s]) if cur else amt / float(pot or 1)
                    pend = (s, "raise" if cur else "bet", list(hist), x)
                    pot += amt - bets[s]; bets[s] = amt; cur = amt
                elif a == "call":
                    pot += amt; bets[s] += amt
        A._learn({"history": hist, "board": h["board"], "shown": {str(k): v for k, v in shown.items()}, "stacks": [0] * n})
print("River, caller's equity against the bettor's modelled range vs what happened")
print("%-26s %-14s %5s %10s %8s" % ("facing", "predicted", "n", "predicted", "actual"))
names = ["0-17%", "17-33%", "33-50%", "50-67%", "67-83%", "83-100%"]
for key in sorted(B, key=lambda k: (k[0], str(k[1]))):
    r = B[key]
    if r[0] >= 8:
        print("%-26s %-14s %5d %9.0f%% %7.0f%%" % (key[0], names[key[1]] if key[1] != "all" else "all", r[0], 100 * r[1] / r[0], 100 * r[2] / r[0]))
