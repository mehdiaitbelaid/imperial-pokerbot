"""How well does a build recognise seats? Feeds every real round to the build's learner (no decisions)
and reports, per team, which label its seat got and at which hand.

    python3 tools/labeltest.py BUILD.py hands/saturday_r0NN.json ..."""
import importlib.util, json, os, sys, statistics
from collections import defaultdict, Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, sys.argv[1])); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
res = defaultdict(list)
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
    for i in range(n):
        if i != me:
            res[P[i]].append(when.get(i, (0, None)))
TD = {"Anker Batteries": "ANKER", "Attention Is All In": "ATT", "Gherkers": "GHERK", "Phil AIvey": "PHIL", "FisherMen": "FISH", "Astra La Vista": "ASTRA", "JoCal": "JOCAL", "SARS": "SARS", "Jump Street": "NONE"}
print("TABLE D TEAMS (right label / wrong label / none; hand at which the right label came)")
for t, code in TD.items():
    r = res.get(t, [])
    ok = [w for l, w in r if l == code]; bad = Counter(l for l, w in r if l and l != code); none = sum(1 for l, w in r if not l)
    print("  %-24s rounds %2d | right %2d (hand: median %s, worst %s) | wrong %s | none %d" % (
        t, len(r), len(ok), int(statistics.median(ok)) if ok else "-", max(ok) if ok else "-", dict(bad) or 0, none))
print("OTHER TEAMS that got a label (false positives):")
tot = fp = 0
for t, r in sorted(res.items()):
    if t in TD: continue
    tot += len(r); c = Counter(l for l, w in r if l)
    if c:
        fp += sum(c.values()); print("  %-24s rounds %2d | %s" % (t, len(r), dict(c)))
print("  total other seat-rounds %d, labelled %d (%.0f%%)" % (tot, fp, 100.0 * fp / max(1, tot)))
