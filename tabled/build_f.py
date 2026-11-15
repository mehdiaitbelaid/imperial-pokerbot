"""Write the replicas of the likely finalists (tabled/f_*.py), same method as build.py.

    python3 tabled/build_f.py             # rewrites the nine f_*.py files
    python3 tabled/build_f.py --log       # also list what was taken from the latest third and the auto-set parts

Nothing here touches the Table D replicas: build.py, measure.py, base.py and _nodes.py are only
imported.  Frequencies come from hands/saturday_r0*.json (read only) through measure.py; the
latest third of a team's rounds is used where it clearly differs (build.pick).  The parts that
build.py sets by hand for Table D (bet size set, 3-bet / 4-bet / 5-bet sizes, raise sizes, iso
size, share of random 3-bets, preflop shove range) are derived from the same hands by auto_hand.
The replicas' node class mixes live in tabled/_nodes_f.py (written by calib_f.py).
"""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import base  # noqa: E402
import build as B  # noqa: E402
import measure as M  # noqa: E402

A = base.ALLIN
TEAMS_F = [("f_attention", "Attention Is All In"), ("f_gherkers", "Gherkers"), ("f_tmm", "The Market Makers"),
           ("f_ee", "Equity Engine"), ("f_kojack", "Kojack"), ("f_fishermen", "FisherMen"),
           ("f_mohil", "Mohil'sPokerBot"), ("f_phil", "Phil AIvey"), ("f_durahim", "Durahim 1453")]
STREETS = ("flop", "turn", "river")
NOTES = {}


def measure():
    """(FULL, LAST, rounds per team) for the finalists, with measure.py's own code."""
    old = M.TEAMS, M.SHORT
    M.TEAMS = TEAMS_F
    M.SHORT = dict((b, a) for a, b in TEAMS_F)
    try:
        full = M.measure_real(False)
        last = M.measure_real(True)
        rounds, keep = M.real_rounds(True)
        info = {}
        for short, team in TEAMS_F:
            refs = [d["ref"].split("/")[1] for d in rounds if team in d["players"]]
            info[short] = (refs, sorted(r.split("/")[1] for r in keep[team]))
    finally:
        M.TEAMS, M.SHORT = old
    return full, last, info


def clusters(xs, tol, min_share, cap=8):
    """Most used values of xs, near values merged into the most frequent one: [(value, share)]."""
    c = Counter(xs)
    n = float(len(xs)) or 1.0
    cl = []
    for v, k in c.most_common():
        for item in cl:
            if abs(item[0] - v) <= tol(item[0]):
                item[1] += k
                break
        else:
            cl.append([v, k])
    out = [(v, k / n) for v, k in cl if k / n >= min_share]
    out.sort(key=lambda t: -t[1])
    return out[:cap]


def combo_pct(cmb):
    hi, lo = base._RV[cmb[0]], base._RV[cmb[1]]
    return base.PCT[(hi, lo, len(cmb) == 3 and cmb[2] == "s")]


def auto_hand(short, F, L):
    """The hand-set part of build.HAND, derived from the team's hands."""
    notes = []
    canon = {}
    for st in STREETS:
        bets = [b for b in F.l["bets"] if b[0] == st]
        plain = [round(b[3], 2) for b in bets if not b[5] and b[4] > 20]
        cl = clusters(plain, lambda s: max(0.022, 0.035 * s), 0.035)
        cover = sum(x for _, x in cl)
        if cover < 0.75:                                   # no fixed size set: coarser buckets
            cl = clusters(plain, lambda s: 0.05 + 0.06 * s, 0.03)
            notes.append("%s sizes are not a fixed set: grouped in buckets (%.0f%% covered)" % (st, 100 * sum(x for _, x in cl)))
        sizes = sorted(v for v, _ in cl) or [0.66]
        far = [b for b in bets if b[5] and min(abs(round(b[3], 2) - s) for s in sizes) > 0.04]
        if bets and len(far) >= 0.03 * len(bets):
            sizes.append(A)
        canon[st] = sizes
    P = {}
    # 3-bet multiples, in and out of position
    tb = {}
    for side, key in (("ip", "3b_mult_IP"), ("oop", "3b_mult_OOP")):
        xs = L.l[key] if len(L.l[key]) >= 30 else F.l[key]
        cl = clusters([min(x, 40.0) for x in xs], lambda s: 0.06, 0.08, 4)
        tb[side] = [((round(v, 2), 0.0), round(x, 3)) for v, x in cl] or [((3.0, 0.0), 1.0)]
    P["tb_mult"] = tb
    c = F.o.get("vs1", Counter())
    r3 = c["raise"] / float(c["n"]) if c["n"] else 0.05
    P["tb_rand"] = round(min(0.85, max(0.10, (r3 - 0.06) / r3 if r3 > 0 else 0.1)), 2)
    c = F.o.get("f3b", Counter())
    r4 = c["raise"] / float(c["n"]) if c["n"] else 0.1
    P["fb_rand"] = round(min(0.7, max(0.0, (r4 - 0.12) / r4 if r4 > 0 else 0.0)), 2)
    c = F.o.get("x_cold3", Counter())
    P["cold_rand"] = 0.7 if c["n"] and c["raise"] / float(c["n"]) > 0.05 else 0.0
    # 4-bet and 5-bet sizes
    for name, ka, km, dflt in (("fourbet", "4b_allin", "4b_mult", 0.3), ("fivebet", "5b_allin", "5b_mult", 1.0)):
        c = F.o.get(ka, Counter())
        a = c["y"] / float(c["n"]) if c["n"] >= 5 else dflt
        small = sorted(x for x in F.l[km] if x < 5.0)
        m = round(small[len(small) // 2], 2) if small else 2.3
        P[name] = [x for x in ((m, round(1 - a, 3)), ("allin", round(a, 3))) if x[1] > 0.02]
    # iso raise size
    one = Counter(bb for k, bb in F.l["iso"] if k == 1)
    two = Counter(bb for k, bb in F.l["iso"] if k == 2)
    if one:
        x1 = one.most_common(1)[0][0]
        per = two.most_common(1)[0][0] - x1 if two else 1.0
        per = per if 0 < per <= 2 else 1.0
        P["iso"] = (round(x1 - per, 2), round(per, 2))
    # raise sizes
    rs = {}
    for st in STREETS:
        xs = [x[1] for x in F.l["raises"] if x[0] == st and not x[2]]
        cl = clusters(xs, lambda s: 0.05, 0.12, 4) if len(xs) >= 8 else []
        rs[st] = {"*": [(round(v, 2), round(x, 3)) for v, x in cl] or [(0.75, 1.0)]}
    P["rsize"] = rs
    # preflop shoves: premium only unless the shown ones say otherwise
    sh = [combo_pct(x) for x in F.l["shove_shown"] + F.l["shove_all"]]
    if len(sh) >= 6:
        wide = sum(1 for x in sh if x >= 0.06) / float(len(sh))
        if wide >= 0.35:
            P["shove_max"] = 1.0
            notes.append("preflop shoves are not premium only (%d of %d shown outside the top 6%%)" % (round(wide * len(sh)), len(sh)))
        else:
            P["shove_max"] = round(min(0.08, max(0.038, sorted(sh)[int(0.85 * (len(sh) - 1))] + 0.005)), 3)
    # all-in bets when the stack is short
    jam = {}
    for st in STREETS:
        low = [b for b in F.l["bets"] if b[0] == st and b[7] <= 2.5]
        if len(low) >= 10:
            jam[st] = sum(1 for b in low if b[5]) / float(len(low))
    if jam.get("flop", 0) >= 0.5:
        P["jam"] = {"spr": 2.5, "p": dict((st, round(0.85 * jam.get(st, jam["flop"]), 2)) for st in STREETS)}
    NOTES[short] = notes
    return {"canon": canon, "P": P}


def fix(P):
    """Guards for sections with no data at all."""
    P["open_bb"] = dict((k, v) for k, v in P["open_bb"].items() if v)
    for st in STREETS:
        T = P["J"][st]
        good = [d for d in T["share"].values() if d]
        fill = good[0] if good else {0.66: 1.0}
        for k in list(T["share"]):
            if not T["share"][k]:
                T["share"][k] = dict(fill)
    return P


def write(short, team, P, doc):
    path = os.path.join(HERE, short + ".py")
    with open(path, "w") as fh:
        fh.write('"""Replica of %s (likely finalist) for the final-table sparring games.\n\n' % team)
        line = ""
        for w in doc.split():
            if len(line) + len(w) + 1 > 96:
                fh.write(line + "\n")
                line = w
            else:
                line = (line + " " + w).strip()
        fh.write(line + "\n\n")
        fh.write("Parameters written by tabled/build_f.py from the team's real hands (same definitions as\n"
                 "docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).\n"
                 '"""\n')
        fh.write("import os\nimport sys\n\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
                 "import base as _base  # noqa: E402\nfrom base import ALLIN, Base  # noqa: E402,F401\n\n"
                 "try:                                    # this replica's frozen node class mixes\n"
                 "    from _nodes_f import NODES as _NF\n"
                 "    _base._NODES.setdefault(%r, _NF.get(%r, {}))\n"
                 "except Exception:\n    pass\n\n\n" % (short, short))
        fh.write("class Agent(Base):\n    NAME = %r\n    P = dict(\n" % short)
        for k in B.ORDER + sorted(set(P) - set(B.ORDER)):
            if k not in P:
                continue
            if k in B.NOTE:
                fh.write("        # %s\n" % B.NOTE[k])
            fh.write("        %s=%s,\n" % (k, B.lit(P[k], 8)))
        fh.write("    )\n")
    return path


def describe(short, team, F, info, hand, P):
    refs, last = info
    opens = Counter(F.l["osz"]).most_common(2)
    v = F.o["vpip"]
    p = F.o["pfr"]
    t = F.o.get("vs1", Counter())
    sizes = ", ".join("%s %s" % (st, "/".join("all-in" if s == A else "%g" % s for s in hand["canon"][st])) for st in STREETS)
    return ("%s. Measured on %d rounds, %d hands (%s); latest third: %s. VPIP %.0f, PFR %.0f, 3-bet %.0f; opens %s. "
            "Bet sizes (share of pot): %s." % (
                team, len(refs), int(F.v["hands"]), ", ".join(refs), ", ".join(last),
                100.0 * v["y"] / v["n"], 100.0 * p["y"] / p["n"], 100.0 * t["raise"] / max(1, t["n"]),
                ", ".join("%gbb %.0f%%" % (s, 100.0 * k / max(1, len(F.l["osz"]))) for s, k in opens), sizes))


def build():
    FULL, LAST, info = measure()
    out = {}
    for short, team in TEAMS_F:
        hand = auto_hand(short, FULL[short], LAST[short])
        B.HAND[short] = hand
        B.NAT.setdefault(short, (0.15, 0.40, 0.55))
        P = {}
        P.update(B.preflop(short, FULL, LAST))
        P.update(B.betting(short, FULL, LAST))
        P.update(B.facing(short, FULL, LAST))
        P.update(hand["P"])
        P["rsize"] = B.allin_raises(short, P["rsize"], FULL)
        P = fix(P)
        out[short] = (team, P, describe(short, team, FULL[short], info[short], hand, P), hand)
    return FULL, LAST, info, out


def main():
    FULL, LAST, info, out = build()
    for short, team in TEAMS_F:
        _, P, doc, hand = out[short]
        print("wrote", os.path.relpath(write(short, team, P, doc), os.path.dirname(HERE)),
              "| %d rounds, %d hands" % (len(info[short][0]), int(FULL[short].v["hands"])))
    if "--log" in sys.argv:
        print("\nTaken from the latest third:")
        for x in B.LOG:
            print("  " + x)
        print("\nAuto-set notes:")
        for short, _ in TEAMS_F:
            for x in NOTES[short]:
                print("  %s: %s" % (short, x))
            print("  %s canon %s" % (short, out[short][3]["canon"]))
            print("  %s %s" % (short, dict((k, out[short][3]["P"][k]) for k in out[short][3]["P"] if k != "rsize")))


if __name__ == "__main__":
    main()
