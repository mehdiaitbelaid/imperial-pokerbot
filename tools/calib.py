"""Replay real hands through the bot's opponent model and compare the predicted
fold probability of each player facing a postflop bet with what he did.

    python tools/calib.py bots/av3.py            # uses hands/*.json
"""
import glob, importlib.util, json, os, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("botmod", os.path.join(ROOT, sys.argv[1]))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
files = sys.argv[2:] or sorted(glob.glob(os.path.join(ROOT, "hands", "*.json")))
agg = defaultdict(lambda: [0, 0.0, 0, 0.0, 0.0])   # key -> n, sum pred fold, folds, sum sfrac, brier
def bucket(x): return "<0.4" if x < 0.4 else "0.4-0.8" if x < 0.8 else "0.8-1.5" if x < 1.5 else ">1.5"
for f in files:
    d = json.load(open(f)); n = len(d["players"]); me = d["seat"]
    A = M.Agent()
    for h in d["hands"]:
        hist = []; street = "preflop"; board = []; bets = [0] * n; cur = 0; pot = 0; posted = 0
        pending = None      # (key, {seat: pred}) for the live bet
        for ev in h["events"]:
            if ev[0] == "post":
                hist.append({"seat": ev[1], "street": "preflop", "action": "small_blind" if posted == 0 else "big_blind", "amount": ev[2]})
                posted += 1; bets[ev[1]] += ev[2]; cur = max(cur, bets[ev[1]]); pot += ev[2]
            elif ev[0] == "board":
                street = ev[1]; board = [M.CARD[c] for c in ev[2]]; bets = [0] * n; cur = 0; pending = None
            elif ev[0] == "refund":
                pot -= ev[2]
            elif ev[0] == "act":
                s, a, amt = ev[1], ev[2], ev[3]
                if pending and s in pending[1] and cur > bets[s]:
                    key, preds = pending
                    p, sf = preds.pop(s)
                    if s != me:
                        for k in (key, ("all", key[1], key[2]), ("all", "all", key[2])):
                            r = agg[k]; r[0] += 1; r[1] += p; r[2] += a == "fold"; r[3] += sf; r[4] += (p - (a == "fold")) ** 2
                if a == "raise" and street != "preflop":
                    first = cur == 0
                    x = (amt / float(pot)) if first else (amt - cur) / float(pot + cur - bets[s])
                    # model prediction for everybody still in
                    ctx = A._board_ctx(board)
                    bp, sc, sm, bmask, thr, fs, scf, smf, d4b, paired, tb = ctx
                    L = A._lines(hist, n, street)
                    dead = set(board)
                    folded = set(e[1] for e in h["events"][:h["events"].index(ev)] if e[0] == "act" and e[2] == "fold")
                    preds = {}
                    for j in range(n):
                        if j == s or j in folded:
                            continue
                        t = A._tier(j, L, dead, bp, fs, scf, smf, sc, bmask, d4b, len(board), thr)
                        sf = t[3]
                        multi = 1 if (n - len(folded)) > 2 else 0
                        preds[j] = (M.fold_prob(A.st[j], L[7][j], len(board) - 3, multi, L[8], x, not first), sf)
                    pending = ((street, bucket(x), "bet" if first else "raise"), preds)
                hist.append({"seat": s, "street": street, "action": a, "amount": amt})
                if a == "raise":
                    pot += amt - bets[s]; bets[s] = amt; cur = amt
                elif a == "call":
                    pot += amt; bets[s] += amt
        shown = {k: v for k, v in h["hole"].items() if k in (h.get("showdown") or {})}
        A._learn({"history": hist, "board": h["board"], "shown": shown, "stacks": [0] * n})
print("%-7s %-8s %-6s %6s %10s %8s %7s %7s" % ("street", "size", "kind", "n", "predicted", "actual", "sfrac", "brier"))
for k in sorted(agg):
    r = agg[k]
    if r[0] >= 15:
        print("%-7s %-8s %-6s %6d %9.0f%% %7.0f%% %7.2f %7.3f" % (k[0], k[1], k[2], r[0], 100 * r[1] / r[0], 100 * r[2] / r[0], r[3] / r[0], r[4] / r[0]))
