"""Per finalist candidate: what V24's learner counts on its seat in real rounds (fingerprint features and seed totals).
    python3 tools/final_seeds.py BUILD.py hands/*.json"""
import importlib.util, json, os, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, sys.argv[1])); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
M.FINGERPRINTS = False
T = ["Astra La Vista", "Attention Is All In", "Gherkers", "Equity Engine", "Phil AIvey", "matcha mille crêpes cake", "Jump Street", "FisherMen", "Anker Batteries", "The Market Makers"]
rows = defaultdict(list)
for f in sorted(sys.argv[2:]):
    d = json.load(open(f)); n = len(d["players"]); me = d["seat"]; P = d["players"]
    if not any(p in T for p in P): continue
    A = M.Agent(); A.on_table_start({"seat": me, "num_players": n, "hands": 1000, "starting_stack": 2000, "big_blind": 20, "small_blind": 10})
    snap = {}
    for h in d["hands"]:
        hist = []; street = "preflop"; posted = 0
        for ev in h["events"]:
            if ev[0] == "post":
                hist.append({"seat": ev[1], "street": "preflop", "action": "small_blind" if posted == 0 else "big_blind", "amount": ev[2]}); posted += 1
            elif ev[0] == "board": street = ev[1]
            elif ev[0] == "act": hist.append({"seat": ev[1], "street": street, "action": ev[2], "amount": ev[3]})
        shown = {k: v for k, v in h["hole"].items() if k in (h.get("showdown") or {})}
        A._learn({"type": "hand_end", "hand_number": h["n"], "history": hist, "board": h["board"], "shown": shown, "winners": [], "stacks": [2000] * n})
        if h["n"] == 120:
            for i in range(n):
                S = A.st[i]; snap[i] = (S.opn, S.o22, S.o25, S.o28, S.bn, S.b15, S.b33, S.b50, S.b100, S.bov)
    for i in range(n):
        if i != me and P[i] in T:
            rows[P[i]].append((os.path.basename(f), snap.get(i), A.st[i]))
for t in T:
    R = rows.get(t, [])[-6:]
    if not R: continue
    print("\n### %s  (%d rounds: %s .. %s)" % (t, len(R), R[0][0], R[-1][0]))
    for fn, sn, S in R:
        print("  h120 opn %2d o22 %2d o25 %2d o28 %2d | bn %2d b15 %2d b33 %2d b50 %2d b100 %2d bov %2d || end: opn %3d o22 %3d o25 %3d o28 %3d bn %3d b15 %3d b33 %3d b50 %3d b100 %3d bov %3d | 3b %d/%d f3 %d/%d f4 %d/%d limp %d/%d vpip %.2f" % (sn + (S.opn, S.o22, S.o25, S.o28, S.bn, S.b15, S.b33, S.b50, S.b100, S.bov, S.tb, S.tb_o, S.f3, S.f3_o, S.f4, S.f4_o, S.limp, S.rfi_o, S.vpip / max(1, S.hands))))
    def tot(k): return [sum(getattr(S, k)[b] for _, _, S in R) for b in range(len(getattr(R[0][2], k)))]
    def sc(k): return sum(getattr(S, k) for _, _, S in R)
    zo, zf, zn, zs = tot("zo"), tot("zf"), tot("zn"), tot("zs")
    print("  raised/folded by bucket: " + "  ".join("%d/%d" % (zf[b], zo[b]) for b in range(6)))
    print("  shown strong by bucket:  " + "  ".join("%d/%d" % (zs[b], zn[b]) for b in range(6)))
    fo, ff = tot("fo"), tot("ff")
    print("  folds to bets by line: " + "  ".join("%d/%d" % (ff[b], fo[b]) for b in range(5)), "| f3 %d/%d  3bet %d/%d  f4 %d/%d  blind folds %d/%d  smallraise folds %d/%d  cbet %d/%d" % (sc("f3"), sc("f3_o"), sc("tb"), sc("tb_o"), sc("f4"), sc("f4_o"), sc("st_f"), sc("st_o"), sc("sr_f"), sc("sr_o"), sc("cb"), sc("cb_o")))
    def seed(o, f):
        return [min(12, o[b]) for b in range(6)], [round(min(12, o[b]) * f[b] / o[b], 2) if o[b] else 0 for b in range(6)]
    a, b2 = seed(zo, zf); c, e = seed(zn, zs)
    print("  SEED: (%s, %s, %s, %s)" % (a, b2, c, e))
