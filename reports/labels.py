"""Which label does the build give each seat, and at which hand (same replay as tools/labeltest.py).

    python3 reports/labels.py upload/bot_v22.py hands/sunday_s1_r002.json ...
"""
import importlib.util, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, sys.argv[1])); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
TD = {"Anker Batteries": "ANKER", "Chinese people can fly": "CPF", "WBot": "WBOT", "GamesGone": "GG", "Poke": "POKE", "Anton": "ANTON", "YSL_TWIZZY": "YSL"}
for f in sys.argv[2:]:
    d = json.load(open(f)); n = len(d["players"]); me = d["seat"]; P = d["players"]
    A = M.Agent(); A.on_table_start({"seat": me, "num_players": n, "hands": 1000, "starting_stack": 2000, "big_blind": 20, "small_blind": 10})
    when = {}
    for h in d["hands"]:
        hist = []; street = "preflop"; posted = 0
        for ev in h["events"]:
            if ev[0] == "post":
                hist.append({"seat": ev[1], "street": "preflop", "action": "small_blind" if posted == 0 else "big_blind", "amount": ev[2]}); posted += 1
            elif ev[0] == "board":
                street = ev[1]
            elif ev[0] == "act":
                hist.append({"seat": ev[1], "street": street, "action": ev[2], "amount": ev[3]})
        shown = {k: v for k, v in h["hole"].items() if k in (h.get("showdown") or {})}
        A._learn({"type": "hand_end", "hand_number": h["n"], "history": hist, "board": h["board"], "shown": shown, "winners": [], "stacks": [2000] * n})
        for i in range(n):
            if i != me and i not in when and A.st[i].lab:
                when[i] = (A.st[i].lab, h["n"])
    out = []; right = 0
    for i in range(n):
        if i == me:
            continue
        lab, hn = when.get(i, (0, None))
        ok = lab == TD.get(P[i])
        right += ok
        S = A.st[i]
        extra = ""
        try:
            extra = " [tb %d/%d f4 %.0f/%.0f]" % (S.tb, S.tb_o, S.f4, S.f4_o)
        except Exception:
            pass
        out.append("%s=%s%s%s" % (P[i][:6], (lab + "@h" + str(hn)) if lab else "none", "" if ok else (" WRONG" if lab else ""), extra))
    print(os.path.basename(f), "right %d of 7 |" % right, "; ".join(out))
