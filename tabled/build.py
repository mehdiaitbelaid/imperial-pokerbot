"""Write the seven replica files (anker.py ... ysl.py) from the measured play of the real teams.

    python3 tabled/build.py            # rewrites tabled/<name>.py for the seven opponents
    python3 tabled/build.py --log      # also say which numbers were taken from the latest third

Frequencies are counted in hands/saturday_r0*.json with tabled/measure.py (the same definitions
as docs/table-d-raw-profiles.txt, plus cuts by the replica's own lines).  Where the latest third
of a team's rounds clearly differs from the earlier ones (two proportion z of 2.6 or more, at
least 25 spots) the latest third is used.  Sizes, 3-bet / 4-bet formulas and the few judgement
calls are in HAND below.  The written files are plain parameter tables: edit them freely.
"""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import base  # noqa: E402
import measure as M  # noqa: E402

A = base.ALLIN
POSS = ("UTG", "UTG+1", "MP", "HJ", "CO", "BTN", "SB")
STREETS = ("flop", "turn", "river")
BUCKETS = base.BUCKETS
NODES = {"flop": ("flop_n", "flop_x", "flop_ms"),
         "turn": ("turn_b2_n", "turn_b2_x", "turn_n", "turn_x", "turn_ms"),
         "river": ("river_b3_n", "river_b3_x", "river_ct_n", "river_ct_x", "river_n", "river_x", "river_ms")}
LOG = []

# ------------------------------------------------------------------ hand-set parts
HAND = {
    "anker": dict(
        doc="Anker Batteries: tight, opens 2.5bb everywhere, c-bets 90% heads up with 1.1 / 2.0 / 0.7 / 0.4 pot "
            "(mixed range), 0.62 pot multiway, never check-raises, folds 78% of its 3-bets to a 4-bet.",
        canon={"flop": [0.4, 0.7, 1.1, 2.0, 0.62, 0.85], "turn": [0.4, 0.7, 1.1, 2.0, 0.62, 0.85],
               "river": [0.4, 0.7, 1.1, 0.62, 0.85]},
        P=dict(
            iso=(2.5, 1.0),
            tb_mult={"ip": [((3.0, 0.0), 0.70), ((3.2, 0.0), 0.30)],
                     "oop": [((3.0, 0.0), 0.62), ((3.2, 0.0), 0.32), ((4.2, 0.0), 0.06)]},
            tb_rand=0.25, fb_rand=0.2,
            fourbet=[(2.3, 1.0)], fivebet=[("allin", 1.0)], shove_max=0.045,
            jam={"spr": 2.5, "p": {"flop": 0.75, "turn": 0.40, "river": 0.45}},
            rsize={"flop": {"value": [(1.8, 0.45), (1.0, 0.30), (0.6, 0.25)], "*": [(0.6, 0.40), (1.0, 0.30), (0.75, 0.20), (1.8, 0.10)]},
                   "turn": {"*": [(0.6, 0.40), (1.0, 0.35), (1.8, 0.25)]},
                   "river": {"*": [(0.6, 0.70), (1.0, 0.30)]}},
        )),
    "cpf": dict(
        doc="Chinese people can fly: loose opener (2.5bb, 3bb from the small blind), folds 81-84% to 3-bets, bets "
            "0.33 pot with air, draws and weak pairs and 1.0 pot with top pair or better, barrels 95%, folds 80% "
            "when a 0.33 bet is raised.",
        canon={"flop": [0.33, 0.66, 1.0], "turn": [0.33, 0.66, 1.0], "river": [0.33, 0.66, 1.0]},
        P=dict(
            iso=(3.0, 1.0),
            tb_mult={"ip": [((3.0, 0.0), 1.0)], "oop": [((3.0, 0.0), 1.0)]},
            tb_rand=0.10,
            fourbet=[("allin", 0.81), (2.3, 0.19)], fivebet=[("allin", 1.0)],
            rsize={"flop": {"*": [(0.85, 0.82), (0.65, 0.18)]}, "turn": {"*": [(0.85, 0.82), (0.65, 0.18)]},
                   "river": {"*": [(0.85, 0.85), (0.65, 0.15)]}},
        )),
    "wbot": dict(
        doc="WBot: opens 2.8bb (3.3 from the small blind) or 3.5bb (4.0), one size per round; bets almost every "
            "time it can: 0.15 pot on most turns and rivers, 3.0 pot or all-in with two pair or better; raises a "
            "quarter of the bets it faces (pot size raises are bluff heavy, 2x pot raises are value); folds 79% "
            "when a 0.15 bet is raised; defends its blinds.",
        canon={"flop": [0.15, 0.33, 0.4, 0.6, 0.75, 1.0, A], "turn": [0.15, 0.33, 0.4, 0.6, 0.75, 1.0, A],
               "river": [0.15, 0.33, 0.6, 0.75, 3.0, A]},
        minbet=True,
        P=dict(
            open_bb={"*": [(2.8, 1.0)], "SB": [(3.3, 1.0)]},
            variants=[(0.6, {"open_bb": {"*": [(2.8, 1.0)], "SB": [(3.3, 1.0)]}}),
                      (0.4, {"open_bb": {"*": [(3.5, 1.0)], "SB": [(4.0, 1.0)]}})],
            iso=("open", 1.0),
            tb_mult={"ip": [((3.0, 0.75), 1.0)], "oop": [((3.5, 0.5), 0.5), ((3.5, 0.75), 0.5)]},
            tb_rand=0.10,
            fourbet=[("allin", 1.0)], fivebet=[("allin", 1.0)],
            rsize={"flop": {"value": [(2.0, 0.60), (1.0, 0.40)], "medium": [(2.0, 0.45), (1.0, 0.55)],
                            "*": [(1.0, 0.88), (2.0, 0.12)]},
                   "turn": {"value": [(A, 0.6), (1.0, 0.2), (2.0, 0.2)], "*": [(1.0, 0.45), (2.0, 0.15), (A, 0.40)]},
                   "river": {"*": [(A, 0.6), (1.0, 0.2), (2.0, 0.2)]}},
        )),
    "gg": dict(
        doc="GamesGone: opens 2.2bb, 3-bets 3% for value only, bets exactly 0.5 pot (air, draws, weak pairs) or "
            "1.0 pot (top pair or better), c-bets and barrels the turn 100% heads up, folds 74% when a 0.5 bet "
            "is raised, calls down (folds 32% to a second barrel and 18% to a third).",
        canon={"flop": [0.5, 1.0], "turn": [0.5, 1.0], "river": [0.5, 1.0]},
        last_sizes=("river",),      # its latest version gave up most 0.5 pot river bluffs (river barrel 70% -> 38%)
        P=dict(
            iso=(3.0, 1.0),
            tb_mult={"ip": [((3.0, 0.0), 0.89), ((4.0, 0.0), 0.11)], "oop": [((3.0, 0.0), 0.67), ((4.0, 0.0), 0.33)]},
            tb_rand=0.05,
            fourbet=[("allin", 1.0)], fivebet=[("allin", 1.0)], shove_max=0.05,
            rsize={"flop": {"value": [(1.0, 0.6), (0.6, 0.4)], "*": [(0.4, 0.55), (0.6, 0.20), (0.7, 0.12), (1.0, 0.13)]},
                   "turn": {"*": [(0.4, 0.6), (1.0, 0.4)]}, "river": {"*": [(1.0, 0.6), (0.4, 0.4)]}},
        )),
    "poke": dict(
        doc="Poke: limps 28% first in and folds most limps to a raise, opens 2.5bb (3bb from the small blind), "
            "bets 1.6 pot with two pair or better, 0.8 pot on the flop with air and draws, 0.33 pot with a mixed "
            "range; folds 71% when a 0.8 bet is raised; folds a lot to bets and never check-raises.",
        canon={"flop": [0.33, 0.55, 0.8, 1.1, 1.6], "turn": [0.33, 0.55, 0.8, 1.1, 1.6],
               "river": [0.33, 0.55, 0.8, 1.1, 1.6]},
        P=dict(
            iso=(3.0, 1.0),
            tb_mult={"ip": [((3.5, 0.0), 1.0)], "oop": [((3.5, 0.0), 0.6), ((3.0, 0.0), 0.4)]},
            tb_rand=0.05,
            fourbet=[("allin", 1.0)], fivebet=[("allin", 1.0)],
            rsize={"flop": {"value": [(1.1, 0.60), (0.75, 0.40)], "*": [(0.75, 0.55), (1.1, 0.45)]},
                   "turn": {"*": [(1.1, 0.6), (0.75, 0.4)]}, "river": {"*": [(1.1, 0.6), (0.75, 0.4)]}},
        )),
    "anton": dict(
        doc="Anton: 3-bets 26-32% with nearly any two cards (3.6x from the blinds, 3x in position), 4-bets 2.3x, "
            "opens 3bb / 4.5bb / 6.6bb (premiums) / 15bb, 0.83 of those on the button; limps to re-raise; bets "
            "0.55 and 0.8 pot mostly with air or weak pairs, 0.6 pot with top pair or better, shoves the flop "
            "with real hands; folds 83-88% when its bet is raised.",
        canon={"flop": [0.33, 0.55, 0.6, 0.8, 1.1, 1.7, A], "turn": [0.33, 0.55, 0.6, 0.75, 0.8, A],
               "river": [0.33, 0.55, 0.6, 0.8, A]},
        P=dict(
            open_bb={"*": {"top": 0.10, "top_sizes": [(6.6, 0.60), (15.0, 0.15), (4.5, 0.15), (3.0, 0.10)],
                           "rest": [(3.0, 0.68), (4.5, 0.20), (6.6, 0.06), (15.0, 0.06)]},
                     "SB": {"top": 0.08, "top_sizes": [(6.6, 0.60), (15.0, 0.15), (4.5, 0.25)],
                            "rest": [(3.0, 0.46), (4.5, 0.42), (15.0, 0.08), (6.6, 0.04)]}},
            open_scale={"BTN": 0.8334},
            vs_limp=(0.03, 0.60), iso=(4.0, 1.0),
            tb_mult={"ip": [((3.0, 0.0), 0.52), ((3.6, 0.0), 0.42), ((4.6, 0.0), 0.06)],
                     "oop": [((3.6, 0.0), 0.80), ((4.6, 0.0), 0.10), ((3.0, 0.0), 0.10)]},
            tb_rand=0.85, fb_rand=0.6, cold_rand=0.8,
            fourbet=[(2.3, 0.93), ("allin", 0.07)], fivebet=[(2.3, 0.84), ("allin", 0.16)],
            shove_max=1.0,          # its shown shoves are not only premiums: KK, AA, 33, KTs, 88, QJs, AKo, Q8o
            pre_noise=0.03,
            rsize={"flop": {"*": [(0.75, 0.65), (1.1, 0.20), (0.9, 0.15)]}, "turn": {"*": [(0.75, 0.6), (1.1, 0.4)]},
                   "river": {"*": [(1.0, 1.0)]}},
        )),
    "ysl": dict(
        doc="YSL_TWIZZY: nit preflop (opens 2.8bb, 2.5 on the button, 3.1 from the small blind; folds 85-88% to "
            "3-bets and 80% of blinds to steals), calling station after the flop, bets only real hands: 0.48 pot "
            "with top pair, 0.77 pot with two pair or better, never folds when raised, never check-raises.",
        canon={"flop": [0.33, 0.38, 0.42, 0.48, 0.66, 0.77, 0.92], "turn": [0.33, 0.38, 0.42, 0.48, 0.66, 0.77, 0.92],
               "river": [0.37, 0.42, 0.48, 0.66, 0.77, 0.92]},
        P=dict(
            open_bb={"*": [(2.8, 1.0)], "BTN": [(2.5, 1.0)], "SB": [(3.1, 1.0)]},
            iso=("open", 0.8),
            tb_mult={"ip": [((2.95, 0.0), 1.0)], "oop": [((3.45, 0.0), 0.88), ((4.05, 0.0), 0.12)]},
            tb_rand=0.05,
            fourbet=[(2.15, 0.85), (2.35, 0.15)], fivebet=[("allin", 1.0)],
            rsize={"flop": {"*": [(0.68, 1.0)]}, "turn": {"*": [(0.68, 1.0)]}, "river": {"*": [(0.68, 1.0)]}},
            commit=1.0, round_bets=True,
        )),
}


# ------------------------------------------------------------------ helpers
def cnt(acc, key):
    return acc.o.get(key, Counter())


def pick(short, key, outs, FULL, LAST, need=25, zmin=2.6):
    """Counter of `key`: the latest third when it clearly differs from the earlier rounds."""
    cf, cl = cnt(FULL[short], key), cnt(LAST[short], key)
    nf, nl = cf["n"], cl["n"]
    if nl >= need and nf - nl >= need:
        for o in outs:
            p1 = cl[o] / float(nl)
            p2 = (cf[o] - cl[o]) / float(nf - nl)
            p = cf[o] / float(nf)
            se = (p * (1 - p) * (1.0 / nl + 1.0 / (nf - nl))) ** 0.5
            if se > 0 and abs(p1 - p2) / se >= zmin:
                LOG.append("%s %s: latest third %s %.2f (%d spots) instead of %.2f over the day" % (
                    short, key, o, p1, nl, p))
                return cl
    return cf


def shares(c, outs, prior=None, m=0.0):
    n = float(c["n"])
    if prior is None or m <= 0:
        return tuple((c[o] / n) if n else 0.0 for o in outs)
    return tuple((c[o] + m * prior[i]) / (n + m) for i, o in enumerate(outs))


def r3(x):
    return round(x, 3)


def odds(p):
    p = min(0.99, max(0.01, p))
    return p / (1 - p)


def fcr_shift(t, orat):
    """Move the fold share of (fold, call, raise) by an odds ratio; keep call : raise."""
    f, c, r = t
    o = odds(f) * orat
    f2 = o / (1 + o)
    rest = (c + r) or 1.0
    return (f2, (1 - f2) * c / rest, (1 - f2) * r / rest)


def canon(team, street, size, amt, allin):
    cs = HAND[team]["canon"][street]
    real = [c for c in cs if c != A]
    best = min(real, key=lambda c: abs(c - size))
    if abs(best - size) <= max(0.025, 0.035 * best):
        return best
    if amt <= 20:
        return min(real)                       # a minimum bet stands for the smallest size
    if allin and A in cs:
        return A
    return None


# ------------------------------------------------------------------ parameter blocks
def preflop(short, FULL, LAST):
    F, L = FULL[short], LAST[short]
    P = {}
    fi = {}
    for pos in POSS:
        c = pick(short, "fi_" + pos, ("raise", "call"), FULL, LAST)
        r, l = shares(c, ("raise", "call"))
        fi[pos] = (r3(r), r3(l) if l >= 0.005 else 0.0)
    P["fi"] = fi
    # open sizes of the latest third, by position
    ob = {}
    allsz = L.l["osz"] if len(L.l["osz"]) >= 40 else F.l["osz"]
    top = Counter(allsz).most_common(1)[0][0]
    for pos in POSS:
        xs = L.l["osz_" + pos] if len(L.l["osz_" + pos]) >= 25 else F.l["osz_" + pos]
        c = Counter(xs)
        keep = [(s, k) for s, k in c.most_common() if k >= 0.05 * len(xs)]
        tot = float(sum(k for _, k in keep))
        ob[pos] = [(s, r3(k / tot)) for s, k in keep]
    star = [(top, 1.0)]
    P["open_bb"] = {"*": star}
    for pos in POSS:
        if ob[pos] != star:
            P["open_bb"][pos] = ob[pos]
    c = cnt(F, "limped")
    if c["n"] >= 20:
        P["vs_limp"] = tuple(r3(x) for x in shares(c, ("call", "raise")))
    c = cnt(F, "bb_option")
    if c["n"] >= 15:
        P["bb_iso"] = r3(c["raise"] / float(c["n"]))
    elif "vs_limp" in P:
        P["bb_iso"] = P["vs_limp"][1]
    c = cnt(F, "x_limp_raised")
    if c["n"] >= 15:
        P["limp_fold"] = r3(c["fold"] / float(c["n"]))
        P["limp_rr"] = r3(c["raise"] / float(c["n"]))
    P.update(one_raise(short, FULL, LAST))
    c = pick(short, "f3b", ("fold", "raise"), FULL, LAST)
    P["f3b"] = tuple(r3(x) for x in shares(c, ("fold", "call", "raise")))
    c = pick(short, "x_cold3", ("fold", "raise"), FULL, LAST)
    P["cold3"] = tuple(r3(x) for x in shares(c, ("call", "raise")))
    c = cnt(F, "x_call_then_3b")
    if c["n"] >= 15:
        P["call_then_3b"] = r3(1 - c["fold"] / float(c["n"]))
    allf4 = shares(pick(short, "f4b", ("fold",), FULL, LAST), ("fold", "call", "raise"), (0.41, 0.32, 0.27), 4.0)
    P["f4b"] = tuple(r3(x) for x in shares(cnt(F, "f4b_small"), ("fold", "call", "raise"), allf4, 10.0))
    P["f4b_shove"] = r3(shares(cnt(F, "f4b_shove"), ("fold",), (min(0.95, allf4[0] + 0.2),), 8.0)[0])
    P["f5b"] = tuple(r3(x) for x in shares(cnt(F, "x_f5b"), ("fold", "call", "raise"), (0.25, 0.70, 0.05), 6.0))
    return P


def one_raise(short, FULL, LAST):
    """Replies to one raise as first action: (call, 3-bet) by own position and spot."""
    F = FULL[short]
    CR = ("call", "raise")
    FCR = ("fold", "call", "raise")

    def drift(key):
        """(call, raise) ratios latest third / day, when the spot clearly moved."""
        cf = cnt(F, key)
        c = pick(short, key, ("fold", "raise"), FULL, LAST)
        if c is cf or not cf["n"]:
            return (1.0, 1.0)
        return tuple((c[o] / float(c["n"])) / (cf[o] / float(cf["n"])) if cf[o] else 1.0 for o in CR)

    def pair(s, d, i=0):
        return (r3(min(0.97, s[i] * d[0])), r3(min(0.97, s[i + 1] * d[1])))

    vs1 = {}
    d = drift("x_v1_open_IP")
    ip = shares(cnt(F, "x_v1_open_IP"), CR)
    vs1["IP"] = pair(ip, d)
    for pos in ("UTG+1", "MP", "HJ", "CO", "BTN"):
        c = cnt(F, "x_v1_open_" + pos)
        if c["n"] >= 60:
            vs1[pos] = pair(shares(c, CR, ip, 30.0), d)
    for pos in ("SB", "BB"):
        vs1[pos] = pair(shares(cnt(F, "x_v1_open_" + pos), CR), drift("x_v1_open_" + pos))
    sq = {}
    allsq = shares(cnt(F, "x_sq"), CR)
    d = drift("x_sq")
    for g in ("IP", "SB", "BB"):
        sq[g] = pair(shares(cnt(F, "x_v1_sq_" + g), CR, allsq, 20.0), d)
    bd = {}
    allbd = shares(cnt(F, "bd"), FCR)
    for pos in ("SB", "BB"):
        d = drift("x_v1_steal_" + pos)
        lvl = shares(cnt(F, "x_v1_steal_" + pos), FCR)
        row = {}
        for k, bname in (("s", "<=2.25bb"), ("m", "2.25-3bb"), ("l", ">3bb")):
            comb = shares(cnt(F, "bd_" + bname), FCR, allbd, 15.0)
            prior = fcr_shift(lvl, odds(comb[0]) / odds(allbd[0]))
            row[k] = pair(shares(cnt(F, "x_v1_steal_%s_%s" % (pos, bname)), FCR, prior, 15.0), d, 1)
        bd[pos] = row
    # opens of 4-7bb and of more than 7bb, relative to opens of 3bb or less (prior: the seven teams together)
    pool = {}
    for b in ("<=3", "<=7", ">7"):
        c = Counter()
        for t in FULL:
            c.update(cnt(FULL[t], "x_vs1_open_" + b))
        pool[b] = shares(c, CR)
    base3 = shares(cnt(F, "x_vs1_open_<=3"), CR)
    big = []
    for b in ("<=7", ">7"):
        prior = tuple(base3[i] * pool[b][i] / pool["<=3"][i] for i in range(2))
        s = shares(cnt(F, "x_vs1_open_" + b), CR, prior, 25.0)
        big.append(tuple(r3(min(1.5, max(0.02, s[i] / base3[i]))) if base3[i] > 0 else 1.0 for i in range(2)))
    return {"vs1": vs1, "sq": sq, "bd": bd, "big_open": tuple(big)}


def betting(short, FULL, LAST):
    F, L = FULL[short], LAST[short]
    betf = {}
    for st in STREETS:
        row = {}
        for m in ("hu", "mw"):
            call = pick(short, "x_bet_%s_%s" % (st, m), ("raise",), FULL, LAST)
            base_f = (call["raise"] / float(call["n"])) if call["n"] else 0.3
            for role in "ADSL":
                c = pick(short, "x_bet_%s_%s_%s" % (st, role, m), ("raise",), FULL, LAST)
                row["%s_%s" % (role, m)] = r3((c["raise"] + 6.0 * base_f) / (c["n"] + 6.0))
        betf[st] = row
    # joint tables
    J = {}
    for st in STREETS:
        fb = [(b, canon(short, st, b[3], b[4], b[5])) for b in F.l["bets"] if b[0] == st]
        lb = [(b, canon(short, st, b[3], b[4], b[5])) for b in L.l["bets"] if b[0] == st]
        fb = [x for x in fb if x[1] is not None]
        lb = [x for x in lb if x[1] is not None]
        comp = {}
        allc = Counter()
        for b, s in fb:
            if b[6]:
                comp.setdefault(s, Counter())[b[6]] += 1
                allc[b[6]] += 1
        tot = float(sum(allc.values())) or 1.0
        sizes = sorted(set(s for _, s in fb))
        table = {}
        for s in sizes:
            c = comp.get(s, Counter())
            table[s] = dict((k, round(c[k] + 0.4 * allc[k] / tot, 2)) for k in base.CLS5
                            if c[k] + 0.4 * allc[k] / tot >= 0.01)

        def dist(bets):
            c = Counter(s for _, s in bets)
            n = float(sum(c.values()))
            return dict((s, c[s] / n) for s in c) if n else {}

        def group(bets, role, m):
            own = [x for x in bets if x[0][1] == role and x[0][2] == m]
            if len(own) >= 12:
                return own
            ag = [x for x in bets if (x[0][1] == "A") == (role == "A") and x[0][2] == m]
            if len(ag) >= 25:
                return ag
            mm = [x for x in bets if x[0][2] == m]
            return mm if len(mm) >= 15 else bets

        share = {}
        for role in "ADSL":
            for m in ("hu", "mw"):
                g = group(fb, role, m)
                d = dist(g)
                gl = group(lb, role, m)
                if st in HAND[short].get("last_sizes", ()) and len(gl) >= 20:
                    d = dist(gl)
                elif len(gl) >= 50 and len(g) - len(gl) >= 50:
                    dl = dist(gl)
                    tv = 0.5 * sum(abs(d.get(s, 0) - dl.get(s, 0)) for s in set(d) | set(dl))
                    if tv >= 0.12:
                        LOG.append("%s %s sizes %s_%s: latest third (TV %.2f, %d bets)" % (short, st, role, m, tv, len(gl)))
                        d = dl
                d = dict((s, x) for s, x in d.items() if x >= 0.012)
                t = sum(d.values()) or 1.0
                share["%s_%s" % (role, m)] = dict((s, r3(d[s] / t)) for s in sorted(d))
        J[st] = {"sizes": table, "share": share}
    # reply when raised after betting, by canonical size (and by street where there are 8 or more)
    rep = {}
    allr = Counter()
    for b in F.l["bets"]:
        if b[8] is None:
            continue
        s = canon(short, b[0], b[3], b[4], b[5])
        allr[b[8]] += 1
        if s is not None and s != A:
            rep.setdefault(s, {}).setdefault(b[0], Counter())[b[8]] += 1
    n = float(sum(allr.values())) or 1.0
    FCR = ("fold", "call", "raise")
    dflt = (allr["fold"] / n, allr["call"] / n, allr["raise"] / n)
    raised = {"default": tuple(r3(x) for x in dflt)}
    for s in sorted(rep):
        c = Counter()
        for st in rep[s]:
            c.update(rep[s][st])
        k = sum(c.values())
        if k < 3:
            continue
        lvl = tuple((c[o] + 4.0 * dflt[i]) / (k + 4.0) for i, o in enumerate(FCR))
        row = {"*": tuple(r3(x) for x in lvl)}
        for st in STREETS:
            cs = rep[s].get(st)
            if cs and sum(cs.values()) >= 8:
                ks = sum(cs.values())
                row[st] = tuple(r3((cs[o] + 6.0 * lvl[i]) / (ks + 6.0)) for i, o in enumerate(FCR))
        raised[s] = row if len(row) > 1 else row["*"]
    return {"betf": betf, "J": J, "raised": raised}


def facing(short, FULL, LAST):
    F = FULL[short]
    FCR = ("fold", "call", "raise")
    face = {}
    allb = dict((b, shares(cnt(F, "fb_all_" + b), FCR, (0.5, 0.4, 0.1), 4.0)) for b in BUCKETS)
    for st in STREETS:
        full = shares(cnt(F, "fb_" + st), FCR)
        now = shares(pick(short, "fb_" + st, ("fold",), FULL, LAST), FCR)
        drift = odds(now[0]) / odds(full[0])
        S = {}
        for chk in ("nx", "xr"):
            lvl = shares(cnt(F, "x_fb_%s_%s" % (st, chk)), FCR, full, 5.0)
            T = {"all": tuple(r3(x) for x in lvl)}
            for b in BUCKETS:
                street_b = shares(cnt(F, "fb_%s_%s" % (st, b)), FCR, allb[b], 10.0)
                prior = fcr_shift(lvl, odds(street_b[0]) / odds(full[0]))
                T[b] = tuple(r3(x) for x in shares(cnt(F, "x_fb_%s_%s_%s" % (st, chk, b)), FCR, prior, 10.0))
            S[chk] = T
        cells = {}
        for node in NODES[st]:
            lvl0 = shares(cnt(F, "x_fb_%s_%s" % (st, "nx" if node.endswith("_n") else "xr")), FCR, full, 5.0)
            lvl1 = shares(cnt(F, "x_cell_" + node), FCR, lvl0, 10.0)
            for m in ("hu", "mw"):
                fm = cnt(F, "fb_%s_%s" % (st, m))
                orat = odds(fm["fold"] / float(fm["n"])) / odds(full[0]) if fm["n"] >= 20 else 1.0
                c2 = cnt(F, "x_cell_%s_%s" % (node, m))
                prior = fcr_shift(lvl1, orat)
                # the node's own heads up / multiway mix already sits in lvl1: lean on it when one side dominates
                c1 = cnt(F, "x_cell_" + node)
                if c1["n"] and c2["n"] >= 0.85 * c1["n"]:
                    prior = lvl1
                cells["%s_%s" % (node, m)] = tuple(r3(x) for x in fcr_shift(shares(c2, FCR, prior, 10.0), drift))
        S["cells"] = cells
        xr = cnt(F, "xr_" + st)
        S["no_xr"] = bool(xr["n"] >= 20 and xr["raise"] == 0)
        if S["no_xr"]:
            for k in list(cells):
                if "_x_" in k or "_ms_" in k:
                    f, c, r = cells[k]
                    cells[k] = (f, r3(c + r), 0.0)
        face[st] = S
    rc = {}
    dflt = base.DEFAULTS["raise_comp"]
    for st in STREETS:
        c = Counter(g for _, g in F.l["sd_raise_" + st])
        n = sum(c.values())
        w = 3.0 if n < 15 else 1.0
        t = float(sum(dflt[st].values()))
        rc[st] = dict((k, round(c[k] + w * dflt[st].get(k, 0) / t, 1)) for k in base.CLS5
                      if c[k] + w * dflt[st].get(k, 0) / t >= 0.05)
    return {"face": face, "raise_comp": rc}


# share of its raises that are all-in only because the chosen size is more than the stack
# (counted once in self-play with no all-in raise size in the tables)
NAT = {"anker": (0.22, 0.31, 0.62), "cpf": (0.07, 0.20, 0.39), "wbot": (0.21, 0.74, 0.85), "gg": (0.06, 0.17, 0.54),
       "poke": (0.13, 0.43, 0.49), "anton": (0.13, 0.56, 0.52), "ysl": (0.0, 0.0, 0.0)}


def allin_raises(short, rsize, FULL):
    """Add an all-in raise size so that the share of all-in raises matches the real one."""
    out = {}
    for i, st in enumerate(STREETS):
        spec = dict(rsize[st])
        c = cnt(FULL[short], "x_raise_allin_" + st)
        if short != "wbot" and c["n"] >= 8:
            real = c["y"] / float(c["n"])
            w = (real - NAT[short][i]) / (1.0 - NAT[short][i])
            if w >= 0.05:
                for k in ("value", "medium", "*"):
                    lst = spec.get(k) or spec["*"]
                    wk = min(0.9, w * (1.6 if k != "*" else 0.5))
                    spec[k] = [(s, r3(x * (1.0 - wk))) for s, x in lst if s != A] + [(A, r3(wk))]
        out[st] = spec
    return out


# ------------------------------------------------------------------ writing
def lit(x, ind=0):
    """Python literal with ALLIN spelled out and a readable layout."""
    if isinstance(x, float):
        if x == A:
            return "ALLIN"
        return repr(round(x, 4))
    if isinstance(x, (int, str, bool)) or x is None:
        return repr(x)
    if isinstance(x, tuple):
        return "(" + ", ".join(lit(v) for v in x) + ("," if len(x) == 1 else "") + ")"
    if isinstance(x, list):
        return "[" + ", ".join(lit(v) for v in x) + "]"
    if isinstance(x, dict):
        items = ["%s: %s" % (lit(k), lit(v, ind + 4)) for k, v in x.items()]
        one = "{" + ", ".join(items) + "}"
        if len(one) + ind <= 118:
            return one
        pad = " " * (ind + 4)
        return "{\n" + "".join("%s%s,\n" % (pad, it) for it in items) + " " * ind + "}"
    raise TypeError(type(x))


ORDER = ["fi", "open_bb", "open_scale", "variants", "vs_limp", "bb_iso", "iso", "limp_fold", "limp_rr", "bd", "sq",
         "vs1", "big_open", "tb_rand", "tb_mult", "f3b", "fb_rand", "fourbet", "cold3", "cold_rand",
         "call_then_3b", "f4b", "f4b_shove", "fivebet", "f5b", "shove_max", "pre_noise", "betf", "J", "jam", "raised", "face",
         "raise_comp", "rsize"]
NOTE = {
    "fi": "first in, by position: (raise, limp)",
    "open_bb": "open sizes in big blinds: [(size, weight)]",
    "vs_limp": "facing limpers: (call, raise)",
    "bd": "blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)",
    "sq": "one raise and at least one caller: (call, 3-bet)",
    "vs1": "any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)",
    "big_open": "(call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb",
    "tb_mult": "3-bet size: (multiple of the raise, plus big blinds)",
    "f3b": "opened and was 3-bet: (fold, call, 4-bet)",
    "cold3": "3-bet in front, not yet in the pot: (call, 4-bet)",
    "f4b": "3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove",
    "f5b": "4-bet and was raised again: (fold, call, raise)",
    "betf": "bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway",
    "J": "per street: hands shown down after each bet size, and each line's size shares",
    "raised": "raised after betting this size: (fold, call, re-raise)",
    "face": "facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)",
    "raise_comp": "hands shown down after its raises",
    "rsize": "raise sizes as a share of the pot after calling",
}


def write(short, team, P, doc):
    path = os.path.join(HERE, short + ".py")
    with open(path, "w") as fh:
        fh.write('"""Replica of %s for the Table D sparring table.\n\n' % team)
        words = doc.split()
        line = ""
        for w in words:
            if len(line) + len(w) + 1 > 96:
                fh.write(line + "\n")
                line = w
            else:
                line = (line + " " + w).strip()
        fh.write(line + "\n\n")
        fh.write("Parameters written by tabled/build.py from the team's real hands (same definitions as\n"
                 "docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).\n"
                 '"""\n')
        fh.write("import os\nimport sys\n\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
                 "from base import ALLIN, Base  # noqa: E402,F401\n\n\n")
        fh.write("class Agent(Base):\n    NAME = %r\n    P = dict(\n" % short)
        for k in ORDER + sorted(set(P) - set(ORDER)):
            if k not in P:
                continue
            if k in NOTE:
                fh.write("        # %s\n" % NOTE[k])
            fh.write("        %s=%s,\n" % (k, lit(P[k], 8)))
        fh.write("    )\n")
    return path


def main():
    FULL = M.measure_real(False)
    LAST = M.measure_real(True)
    for short, team in M.TEAMS:
        P = {}
        P.update(preflop(short, FULL, LAST))
        P.update(betting(short, FULL, LAST))
        P.update(facing(short, FULL, LAST))
        P.update(HAND[short]["P"])
        P["rsize"] = allin_raises(short, P["rsize"], FULL)
        print("wrote", os.path.relpath(write(short, team, P, HAND[short]["doc"]), os.path.dirname(HERE)))
    if "--log" in sys.argv:
        print("\nTaken from the latest third:")
        for x in LOG:
            print("  " + x)


if __name__ == "__main__":
    main()
