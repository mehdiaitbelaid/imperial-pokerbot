"""Compare the bot's direct flop/turn equity with a long Monte Carlo on real decision states.
    python3 tools/eqcheck.py bots/av15.py hands/*.json"""
import importlib.util, json, os, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("botmod", os.path.join(ROOT, sys.argv[1]))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
START, BB = 2000, 20
G = defaultdict(lambda: [0, 0.0, 0.0, 0.0])
for f in sys.argv[2:]:
    d = json.load(open(f)); n = len(d["players"]); me = d["seat"]; A = M.Agent()
    A.on_table_start({"seat": me, "num_players": n, "hands": 1000})
    A._budget = lambda st: 5.0
    for h in d["hands"]:
        hist = []; street = "preflop"; board = []; posted = 0
        stacks = [START] * n; bets = [0] * n; folded = [False] * n; pot = 0; cur = 0; min_inc = BB
        for ev in h["events"]:
            if ev[0] == "post":
                s, amt = ev[1], ev[2]
                hist.append({"seat": s, "street": "preflop", "action": "small_blind" if posted == 0 else "big_blind", "amount": amt}); posted += 1
                stacks[s] -= amt; bets[s] += amt; pot += amt; cur = max(cur, bets[s])
            elif ev[0] == "board":
                street = ev[1]; board = ev[2]; bets = [0] * n; cur = 0; min_inc = BB
            elif ev[0] == "refund":
                stacks[ev[1]] += ev[2]; pot -= ev[2]
            elif ev[0] == "act":
                s, a, amt = ev[1], ev[2], ev[3]
                if s == me and street in ("flop", "turn"):
                    to_call = min(cur - bets[s], stacks[s]); max_to = bets[s] + stacks[s]
                    others = any((not folded[j]) and stacks[j] > 0 for j in range(n) if j != s)
                    can_raise = max_to > cur and others
                    state = {"hand_number": h["n"], "street": street, "seat": s, "button": h["button"], "hole_cards": h["hole"][str(me)],
                             "board": list(board), "small_blind": 10, "big_blind": BB, "pot": pot, "stacks": list(stacks), "bets": list(bets),
                             "folded": list(folded), "to_call": to_call, "min_raise_to": min(cur + min_inc, max_to) if can_raise else None,
                             "max_raise_to": max_to if can_raise else None,
                             "legal_actions": (["fold", "call"] if to_call > 0 else ["check"]) + (["raise"] if can_raise else []),
                             "betting": "no_limit", "raise_cap": None, "raises_this_street": 0, "history": list(hist)}
                    M.USE_MC = False; A.act(state); det = A.last_eq
                    M.USE_MC = True; M.MC_MAX = 1500; A.act(state); mc = A.last_eq
                    M.USE_MC = False
                    live = sum(1 for j in range(n) if not folded[j]) - 1
                    for key in (("all", ""), (street, ""), ("heads-up" if live == 1 else "multiway", ""), ("true equity", "%d-%d%%" % (int(mc * 5) * 20, int(mc * 5) * 20 + 20))):
                        g = G[key]; g[0] += 1; g[1] += det - mc; g[2] += abs(det - mc); g[3] += mc
                hist.append({"seat": s, "street": street, "action": a, "amount": amt})
                if a == "raise":
                    inc = amt - cur
                    if inc >= min_inc: min_inc = inc
                    stacks[s] -= amt - bets[s]; pot += amt - bets[s]; bets[s] = amt; cur = amt
                elif a == "call":
                    stacks[s] -= amt; pot += amt; bets[s] += amt
                elif a == "fold":
                    folded[s] = True
        shown = {k: v for k, v in h["hole"].items() if k in (h.get("showdown") or {})}
        A._learn({"history": hist, "board": h["board"], "shown": shown, "stacks": [0] * n})
print("%-14s %-9s %5s %14s %12s" % ("group", "", "n", "direct - MC", "mean |error|"))
for k in sorted(G):
    g = G[k]
    print("%-14s %-9s %5d %+13.1f%% %11.1f%%" % (k[0], k[1], g[0], 100 * g[1] / g[0], 100 * g[2] / g[0]))
