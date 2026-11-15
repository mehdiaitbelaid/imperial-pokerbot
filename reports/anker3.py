"""V25 rule check: hands where Anker called our flop bet and our turn bet, and the river came.
    python3 reports/anker3.py BUILD.py hands/sunday_s1_r022.json ...
Says whether Anker's seat was already labelled ANKER (replay of the build's learner), what we held on the river,
whether we bet the river (three-street bet) or checked (rule fired when we had less than two pair), and the result.
"""
import importlib.util, json, os, sys
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from bigcalls import klass
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, sys.argv[1])); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
tot = defaultdict(lambda: [0, 0, 0])
for f in sys.argv[2:]:
    d = json.load(open(f)); n = len(d["players"]); me = d["seat"]; ank = d["players"].index("Anker Batteries"); tag = os.path.basename(f).split("_")[-1][:4]
    A = M.Agent(); A.on_table_start({"seat": me, "num_players": n, "hands": 1000, "starting_stack": 2000, "big_blind": 20, "small_blind": 10})
    for h in d["hands"]:
        labelled = A.st[ank].lab == "ANKER"
        hist = []; street = "preflop"; posted = 0; contrib = defaultdict(int); ourbet = {}; ankcall = set(); river_act = None; ank_river = None
        for ev in h["events"]:
            if ev[0] == "post":
                hist.append({"seat": ev[1], "street": "preflop", "action": "small_blind" if posted == 0 else "big_blind", "amount": ev[2]}); posted += 1
            elif ev[0] == "board":
                street = ev[1]; contrib = defaultdict(int)
            elif ev[0] == "act":
                s, a, amt = ev[1], ev[2], ev[3]
                hist.append({"seat": s, "street": street, "action": a, "amount": amt})
                if street != "preflop":
                    if a == "raise":
                        if s == me and max(contrib.values() or [0]) == 0: ourbet[street] = amt
                        if street == "river" and s == me and river_act is None: river_act = "bet %d" % amt
                        if street == "river" and s == ank and river_act and river_act.startswith("check") and ank_river is None: ank_river = "Anker bet %d" % amt
                        if street == "river" and s == ank and river_act and river_act.startswith("bet"): ank_river = "Anker raised"
                        contrib[s] = amt
                    elif a == "call":
                        if s == ank and street in ourbet and street in ("flop", "turn"): ankcall.add(street)
                        if street == "river" and s == ank and river_act and river_act.startswith("bet"): ank_river = "Anker called"
                        contrib[s] += amt
                    elif a == "check" and street == "river" and s == me and river_act is None: river_act = "check"
                    elif a == "fold" and street == "river" and s == ank and river_act and river_act.startswith("bet"): ank_river = "Anker folded"
        if ankcall == {"flop", "turn"} and len(h["board"]) == 5 and river_act:
            k = klass(h["hole"][str(me)], h["board"]).split("+")[0]; res = h["results"][me]
            weak = k != "strong"
            if river_act.startswith("bet"):
                key = "three-street bet, less than two pair, " + ("labelled" if labelled else "not yet labelled") if weak else "three-street bet, two pair or better"
            else:
                key = ("river check, less than two pair, " + ("labelled (rule spot)" if labelled else "not yet labelled")) if weak else "river check, two pair or better"
            tot[key][0] += 1; tot[key][1] += res > 0; tot[key][2] += res
            if weak:
                sd = "".join(h["hole"].get(str(ank), [])) or "no showdown"
                print("  %s#%d %s on %s %s | %s, %s | Anker %s | %+d" % (tag, h["n"], "".join(h["hole"][str(me)]), "".join(h["board"]), k, river_act, ank_river or "-", sd, res))
        shown = {k2: v for k2, v in h["hole"].items() if k2 in (h.get("showdown") or {})}
        A._learn({"type": "hand_end", "hand_number": h["n"], "history": hist, "board": h["board"], "shown": shown, "winners": [], "stacks": [2000] * n})
print("TOTAL (%d round(s)): spot / hands / won / chips" % len(sys.argv[2:]))
for k, (c, w, net) in sorted(tot.items()):
    print("  %-62s n=%2d won %2d net %+d" % (k, c, w, net))
