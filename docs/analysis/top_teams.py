"""Behaviour dossier tables for the top teams at our counted tables.

    python3 review/top_teams.py               # every table
    python3 review/top_teams.py --check       # also print raw events used for the hand checks
    python3 review/top_teams.py --upto r046   # only rounds up to and including r046 (the dossier's cut)

Reads hands-data/hands/saturday_r0*.json (counted rounds). Stdlib only.
Card helpers and positions come from live_diagnosis.py.
Rates print as k/n; n under 30 is marked * (unreliable).
Chip flow between two seats in one hand: every loser's loss is split across that
hand's winners in proportion to what they won, so the flows of our seat sum to our result.
"""
import glob
import json
import os
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_diagnosis import made_class, pos_name, combo, rv  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
HANDS = os.path.join(HERE, "..", "hands-data", "hands")
US = "Resonance Qt"
BB = 20
PRIMARY = ["Gherkers", "Attention Is All In", "Equity Engine"]
SECONDARY = ["The Market Makers", "AAST", "WBot", "Kojack", "Anker Batteries"]
SHORT = {"Gherkers": "G", "Attention Is All In": "AIAI", "Equity Engine": "EE",
         "The Market Makers": "TMM", "AAST": "AAST", "WBot": "WBot", "Kojack": "Kojack",
         "Anker Batteries": "Anker", US: "us"}
STRONG = {"Two Pair", "Trips/Set", "Straight", "Flush", "Full House", "Four of a Kind",
          "Straight Flush"}
POSS = ("UTG", "UTG+1", "MP", "HJ", "CO", "BTN", "SB", "BB")
ACTS = ("fold", "check", "call", "raise")


# ------------------------------------------------------------------ replay
def replay(h, n):
    """Annotate every action with street, to_call, pot before it, raise level, limpers,
    callers since the last raise, live seats, seats that already acted on the street,
    raise size as a share of the pot after calling, and bet faced as a share of the pot
    before that bet."""
    acts = []
    street = "preflop"
    sb = defaultdict(int)
    put = defaultdict(int)
    cur = raises = limpers = callers = 0
    folded = set()
    acted = []
    la = {}
    start = h["start_stacks"]
    for e in h["events"]:
        k = e[0]
        if k == "post":
            sb[e[1]] += e[2]
            put[e[1]] += e[2]
            cur = max(cur, sb[e[1]])
        elif k == "board":
            street = e[1]
            sb = defaultdict(int)
            cur = raises = callers = 0
            acted = []
        elif k == "refund":
            put[e[1]] -= e[2]
        elif k == "act":
            s, a, amt = e[1], e[2], e[3]
            pot = sum(put.values())
            to_call = cur - sb[s]
            rec = {"seat": s, "street": street, "act": a, "amt": amt, "to_call": to_call,
                   "pot": pot, "raises": raises, "limpers": limpers, "callers": callers,
                   "cur": cur, "live": n - len(folded), "acted": list(acted), "put_before": put[s],
                   "face": to_call / float(max(1, pot - to_call)) if to_call > 0 else 0.0,
                   "allin": False, "size": None, "i": len(acts)}
            if a == "raise":
                rec["size"] = (amt - cur) / float(max(1, pot + to_call))
                put[s] += amt - sb[s]
                sb[s] = amt
                cur = amt
                raises += 1
                callers = 0
                la[street] = s
            elif a == "call":
                sb[s] += amt
                put[s] += amt
                if street == "preflop" and raises == 0:
                    limpers += 1
                else:
                    callers += 1
            elif a == "fold":
                folded.add(s)
            if a in ("raise", "call") and put[s] >= start[s]:
                rec["allin"] = True
            acted.append(s)
            acts.append(rec)
    return acts, la


def flows(h, seat):
    """Chips each other seat paid to (positive) or took from (negative) `seat` this hand."""
    res = h["results"]
    win = sum(r for r in res if r > 0)
    out = {}
    if win <= 0 or res[seat] == 0:
        return out
    for j, r in enumerate(res):
        if j == seat:
            continue
        if res[seat] > 0 and r < 0:
            out[j] = -r * res[seat] / float(win)
        elif res[seat] < 0 and r > 0:
            out[j] = res[seat] * r / float(win)
    return out


# ------------------------------------------------------------------ cards
def has_draw(hole, board):
    """Flush draw or four to a straight using at least one hole card (gutshots count)."""
    cards = hole + board
    for s in "shdc":
        if sum(c[1] == s for c in cards) == 4 and any(c[1] == s for c in hole):
            return True
    rs = set(rv(c) for c in cards)
    hr = set(rv(c) for c in hole)
    if 12 in rs:
        rs.add(-1)
    if 12 in hr:
        hr.add(-1)
    for lo in range(-1, 9):
        w = set(range(lo, lo + 5))
        if len(w & rs) == 4 and w & hr:
            return True
    return False


def group(hole, board):
    mc = made_class(hole, board)
    if mc in STRONG:
        return "value"
    if mc in ("Top Pair", "Overpair"):
        return "medium"
    if mc == "Weak Pair":
        return "weak"
    if len(board) < 5 and has_draw(hole, board):
        return "draw"
    return "air"


def texture(flop):
    rs = sorted((rv(c) for c in flop), reverse=True)
    if len(set(rs)) < 3:
        return "paired"
    if len(set(c[1] for c in flop)) == 1:
        return "monotone"
    if rs[0] <= 7 and rs[0] - rs[2] <= 4:
        return "low connected"
    if rs[0] >= 10:
        return "high card"
    return "other"


def bucket(x):
    if x < 0.4:
        return "<40%"
    if x <= 0.75:
        return "40-75%"
    if x <= 1.12:     # Gherkers' fixed 1.10 pot size lands here even after chip rounding
        return "75-110%"
    return "overbet"


def open_bucket(bb):
    return "<=2.25bb" if bb <= 2.25 else ("2.25-3bb" if bb <= 3 else ">3bb")


# ------------------------------------------------------------------ accumulator
class Acc:
    def __init__(self):
        self.o = defaultdict(Counter)    # key -> Counter of outcomes plus "n"
        self.l = defaultdict(list)
        self.v = defaultdict(float)

    def out(self, key, outcome):
        c = self.o[key]
        c["n"] += 1
        c[outcome] += 1

    def hit(self, key, cond):
        self.out(key, "y" if cond else "no")

    def add(self, other):
        for k, c in other.o.items():
            self.o[k].update(c)
        for k, x in other.l.items():
            self.l[k].extend(x)
        for k, x in other.v.items():
            self.v[k] += x


def merge(accs):
    m = Acc()
    for a in accs:
        m.add(a)
    return m


def rate(acc, key, outcome="y", raw=False):
    c = acc.o.get(key, Counter())
    n = c["n"]
    if raw:
        return (c[outcome] / float(n)) if n else None, n
    if not n:
        return "n/a (0)"
    return "%.2f (%d/%d%s)" % (c[outcome] / float(n), c[outcome], n, "*" if n < 30 else "")


def mix(acc, key):
    """fold / call / raise (and check) shares of one opportunity."""
    c = acc.o.get(key, Counter())
    n = c["n"]
    if not n:
        return "n=0"
    parts = ["%s %.2f" % (a[0].upper(), c[a] / float(n)) for a in ACTS if c[a]]
    return "%s n=%d%s" % (" ".join(parts), n, "*" if n < 30 else "")


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else float("nan")


def dist(xs, k=4, fmt="%g"):
    if not xs:
        return "none"
    c = Counter(xs).most_common(k)
    return ", ".join((fmt % (v,)) + " %.0f%%" % (100.0 * m / len(xs)) for v, m in c) + " (n=%d)" % len(xs)


# ------------------------------------------------------------------ per seat stats
CUR_REF = [""]


def seat_hand(A, h, s, n, acts, la, me, events):
    """Accumulate one seat's hand into A and append fingerprint events (hand index, kind, value)."""
    pos = pos_name((s - h["button"]) % n, n)
    res = h["results"][s]
    hole = h["hole"].get(str(s))
    shown = str(s) in h["showdown"] and hole is not None
    board = h["board"]
    A.v["hands"] += 1
    A.v["chips"] += res
    mine = [a for a in acts if a["seat"] == s]
    pre = [a for a in mine if a["street"] == "preflop"]
    A.hit("vpip", any(a["act"] in ("call", "raise") for a in pre))
    A.hit("pfr", any(a["act"] == "raise" for a in pre))
    A.hit("shove", any(a["act"] == "raise" and a["allin"] for a in pre))
    if shown and any(a["act"] == "raise" and a["allin"] for a in pre):
        A.l["shove_shown"].append(combo(hole))
    pre_all = [a for a in acts if a["street"] == "preflop"]
    hi = h["n"]
    if pre:
        f = pre[0]
        if f["raises"] == 0 and pos != "BB":
            if f["limpers"] == 0:
                A.out("fi_" + pos, f["act"])
                A.out("fi", f["act"])
                if f["act"] == "raise":
                    bb = round(f["amt"] / float(BB), 2)
                    A.l["osz_" + pos].append(bb)
                    A.l["osz"].append(bb)
                    events.append((hi, "open", bb))
                    if shown:
                        A.l["open_shown"].append(combo(hole))
                elif f["act"] == "call":
                    events.append((hi, "limp", 0))
            else:
                A.out("limped", f["act"])
                if f["act"] == "raise":
                    A.l["iso"].append((f["limpers"], round(f["amt"] / float(BB), 2)))
                    events.append((hi, "iso", (f["limpers"], round(f["amt"] / float(BB), 2))))
                elif f["act"] == "call":
                    events.append((hi, "limp", 0))
            A.hit("limp", f["act"] == "call")
        # first action at each raise level
        seen = set()
        for a in pre:
            lv = a["raises"]
            if lv == 0 or lv in seen:
                continue
            seen.add(lv)
            raisers = [x for x in pre_all if x["act"] == "raise" and x["i"] < a["i"]]
            if lv == 1:
                op = raisers[0]
                opos = pos_name((op["seat"] - h["button"]) % n, n)
                A.out("vs1", a["act"])
                A.out("vs1_" + pos, a["act"])
                A.out("vs1_from_" + opos, a["act"])
                if a["callers"] >= 1:
                    A.out("squeeze", a["act"])
                if a["act"] == "raise":
                    A.l["3b_mult"].append(round(a["amt"] / float(a["cur"]), 2))
                    A.l["3b_bb"].append(round(a["amt"] / float(BB), 2))
                    events.append((hi, "3bet", round(a["amt"] / float(a["cur"]), 2)))
                    if shown:
                        A.l["3b_shown"].append(combo(hole))
                elif a["act"] == "call" and shown:
                    A.l["cc_shown_" + ("BB" if pos == "BB" else "other")].append(combo(hole))
                if pos in ("SB", "BB") and a["callers"] == 0 and a["limpers"] == 0 and opos in ("CO", "BTN", "SB"):
                    ob = op["amt"] / float(BB)
                    A.out("bd", a["act"])
                    A.out("bd_" + open_bucket(ob), a["act"])
                    if op["seat"] == me:
                        A.out("bd_us", a["act"])
                if op["seat"] == me and a["callers"] == 0:
                    A.out("vs_our_open", a["act"])
            elif lv == 2:
                A.out("vs2", a["act"])
                if a["act"] == "raise":
                    A.l["4b_mult"].append(round(a["amt"] / float(a["cur"]), 2))
                    if shown:
                        A.l["4b_shown"].append(combo(hole))
                if any(x["act"] == "raise" and x["raises"] == 0 for x in pre):
                    A.out("f3b", a["act"])
                    if raisers[-1]["seat"] == me:
                        A.out("f3b_us", a["act"])
            elif lv == 3:
                A.out("vs3", a["act"])
                if any(x["act"] == "raise" and x["raises"] == 1 for x in pre):
                    A.out("f4b", a["act"])
            elif lv >= 4:
                A.out("vs4", a["act"])
    # postflop
    flop = board[:3]
    tex = texture(flop) if len(flop) == 3 else None
    nb = {"flop": 3, "turn": 4, "river": 5}
    prev = "preflop"
    called_from = {}
    for street in ("flop", "turn", "river"):
        st_acts = [a for a in acts if a["street"] == street]
        sa = [a for a in st_acts if a["seat"] == s]
        if not sa:
            prev = street
            continue
        A.v["saw_" + street] += 1
        nlive = st_acts[0]["live"]
        hu = nlive == 2
        bd = board[:nb[street]]
        pa = la.get(prev)
        first = sa[0]
        if first["to_call"] == 0:
            line = None
            if pa == s:
                line = "cbet" if street == "flop" else "barrel"
                A.out("%s_%s_%s" % (line, street, "hu" if hu else "mw"), first["act"])
                A.out("%s_%s" % (line, street), first["act"])
                if street == "flop":
                    A.out("cbet_tex_" + tex, first["act"])
            elif pa is not None and pa not in [x["seat"] for x in st_acts if x["act"] == "fold"] \
                    and pa not in first["acted"] and any(x["seat"] == pa for x in st_acts):
                line = "donk"
                A.out("donk_" + street, first["act"])
            if first["acted"]:
                A.out("bct_" + street, first["act"])
                line = line or "bct"
            else:
                A.out("lead_" + street, first["act"])
                line = line or "lead"
            if first["act"] == "raise":
                A.l["bsz_%s_%s" % (line, street)].append(round(first["size"], 2))
                if not first["allin"]:      # all-in bets are capped by the stack, so they carry no size habit
                    events.append((hi, "bet_" + line + "_" + street, round(first["size"], 2)))
            if first["act"] == "check":
                nxt = next((a for a in sa[1:] if a["to_call"] > 0), None)
                if nxt:
                    A.out("xr_" + street, nxt["act"])
                    if pa == s:
                        A.out("stab_after_missed_" + street, nxt["act"])
        # every bet or raise: overbet rate and size tells at showdown
        for a in sa:
            if a["act"] == "raise":
                kind = "bet" if a["to_call"] == 0 else "raise"
                A.hit("overbet_" + kind, a["size"] > 1.0)
                A.l["all_%s_%s" % (kind, street)].append(round(a["size"], 2))
                if shown:
                    A.l["sd_%s_%s" % (kind, street)].append((bucket(a["size"]), group(hole, bd)))
        # facing a single bet
        fb = next((a for a in sa if a["to_call"] > 0 and a["raises"] == 1), None)
        if fb:
            bettor = next(x["seat"] for x in reversed(st_acts[:st_acts.index(fb)]) if x["act"] == "raise")
            b = bucket(fb["face"])
            A.out("fb_" + street, fb["act"])
            A.out("fb_%s_%s" % (street, b), fb["act"])
            A.out("fb_all_" + b, fb["act"])
            A.out("fb_%s_%s" % (street, "hu" if hu else "mw"), fb["act"])
            if bettor == me:
                A.out("fb_us_" + street, fb["act"])
                A.out("fb_us_all_" + b, fb["act"])
                if hu:
                    A.out("fb_us_hu_" + street, fb["act"])
            if street == "turn" and called_from.get("flop") == bettor:
                A.out("vs_barrel2", fb["act"])
            if street == "river":
                if called_from.get("turn") == bettor and called_from.get("flop") == bettor:
                    A.out("vs_barrel3", fb["act"])
                if "turn" not in la:
                    A.out("vs_river_after_xturn", fb["act"])
            if fb["act"] == "call":
                called_from[street] = bettor
                if shown:
                    A.l["sd_call_" + street].append(group(hole, bd))
        # facing a raise after they bet or raised on this street
        bi = next((i for i, a in enumerate(sa) if a["act"] == "raise"), None)
        if bi is not None:
            nxt = next((a for a in sa[bi + 1:] if a["to_call"] > 0), None)
            if nxt:
                A.out("vs_raise_after_bet", nxt["act"])
                A.out("vs_raise_after_bet_" + street, nxt["act"])
        prev = street
    if A.v and any(a["street"] != "preflop" for a in mine):
        A.hit("wtsd", str(s) in h["showdown"])
        if str(s) in h["showdown"]:
            A.hit("wsd", res > 0)
    if str(s) in h["showdown"] and hole:
        A.l["big"].append((res, CUR_REF[0], h["n"], combo(hole), made_class(hole, board), " ".join(board)))
    return pos


# ------------------------------------------------------------------ spot labels for item 8
def spot_label(acts, me, them):
    """Name the line between our seat and theirs that decided the hand."""
    if not acts:
        return "no action"
    end = acts[-1]["street"]
    ourf = next((a for a in acts if a["seat"] == me and a["act"] == "fold"), None)
    thf = next((a for a in acts if a["seat"] == them and a["act"] == "fold"), None)

    def last_raiser_before(a):
        r = next((x for x in reversed(acts[:a["i"]]) if x["act"] == "raise"), None)
        return r

    def level(r):
        if r["street"] != "preflop":
            return "bet" if r["raises"] == 0 else "raise"
        return {0: "open", 1: "3-bet", 2: "4-bet"}.get(r["raises"], "5-bet+")

    if ourf:
        r = last_raiser_before(ourf)
        if r and r["seat"] == them:
            return "%s: we fold to their %s" % (ourf["street"], level(r))
        return "%s: we fold (other raiser)" % ourf["street"]
    if thf:
        r = last_raiser_before(thf)
        if r and r["seat"] == me:
            return "%s: they fold to our %s" % (thf["street"], level(r))
        return "%s: they fold (other raiser)" % thf["street"]
    rs = [a for a in acts if a["act"] == "raise" and a["seat"] in (me, them)]
    if not rs:
        return "%s: showdown, no raise by either" % end
    r = rs[-1]
    who = "we" if r["seat"] == me else "they"
    return "showdown: %s made the last %s (%s)" % (who, level(r), r["street"])


def line_str(h, acts, names, me, them):
    """Compact readable line of one hand: who did what by street."""
    def nm(s):
        return "us" if s == me else (SHORT.get(names[s], "x%d" % s) if s == them else "x%d" % s)
    parts = []
    street = None
    nb = {"flop": 3, "turn": 4, "river": 5}
    for a in acts:
        if a["act"] == "fold" and a["seat"] not in (me, them):
            continue
        if a["street"] != street:
            street = a["street"]
            tag = street[0].upper()
            if street != "preflop":
                tag += "[" + " ".join(h["board"][:nb[street]]) + "]"
            parts.append(tag + ":")
        if a["act"] == "raise":
            if a["street"] == "preflop":
                txt = "r%gbb" % (a["amt"] / float(BB))
            else:
                txt = "%s%.0f%%" % ("b" if a["to_call"] == 0 else "r", 100 * a["size"])
            if a["allin"]:
                txt += "AI"
        else:
            txt = {"fold": "f", "check": "x", "call": "c"}[a["act"]]
        parts.append("%s %s" % (nm(a["seat"]), txt))
    ours = combo(h["hole"][str(me)])
    th = h["hole"].get(str(them))
    return "us %s vs %s; %s; us %+d" % (ours, combo(th) if th else "unseen", " ".join(parts), h["results"][me])


# ------------------------------------------------------------------ main
def load_rounds():
    paths = sorted(glob.glob(os.path.join(HANDS, "saturday_r0*.json")))
    if "--upto" in sys.argv:
        last = sys.argv[sys.argv.index("--upto") + 1]
        paths = [p for p in paths if os.path.basename(p)[len("saturday_"):-len(".json")] <= last]
    return [json.load(open(p)) for p in paths]


def show_profile(name, A, extra=""):
    h = A.v["hands"]
    P = lambda *a: print(*a)  # noqa: E731
    P("\n### %s  hands=%d  bb/100=%+.1f %s" % (name, h, A.v["chips"] / h * 5 if h else 0, extra))
    P("VPIP %s | PFR %s | limp (first action unopened, not BB) %s" % (
        rate(A, "vpip"), rate(A, "pfr"), rate(A, "limp")))
    P("first in (no limpers): %s" % mix(A, "fi"))
    for p in POSS[:-1]:
        if A.o.get("fi_" + p):
            P("  fi %-5s %s  raise %s  open sizes %s" % (p, mix(A, "fi_" + p), rate(A, "fi_" + p, "raise"),
                                                         dist(A.l["osz_" + p])))
    P("all open sizes: %s" % dist(A.l["osz"]))
    P("facing limpers first action: %s; iso (limpers, bb): %s" % (mix(A, "limped"),
                                                                  dist(A.l["iso"], 6, "%s")))
    P("vs one raise: %s; 3-bet %s; mult %s median %.2f; 3-bet bb %s" % (
        mix(A, "vs1"), rate(A, "vs1", "raise"), dist(A.l["3b_mult"], 5), med(A.l["3b_mult"]), dist(A.l["3b_bb"], 4)))
    P("  3-bet by own pos: " + "; ".join("%s %s" % (p, rate(A, "vs1_" + p, "raise")) for p in POSS if A.o.get("vs1_" + p)))
    P("  3-bet vs opener pos: " + "; ".join("%s %s" % (p, rate(A, "vs1_from_" + p, "raise")) for p in POSS if A.o.get("vs1_from_" + p)))
    P("  squeeze (raise + >=1 caller): %s raise %s" % (mix(A, "squeeze"), rate(A, "squeeze", "raise")))
    P("vs 3-bet (4-bet opp): %s; fold to 3-bet after opening %s; 4-bet mult %s" % (
        mix(A, "vs2"), mix(A, "f3b"), dist(A.l["4b_mult"], 4)))
    P("vs 4-bet: %s; fold to 4-bet after 3-betting %s; vs 5-bet+: %s" % (mix(A, "vs3"), mix(A, "f4b"), mix(A, "vs4")))
    P("fold to OUR 3-bet after opening: %s" % mix(A, "f3b_us"))
    P("blind defence vs CO/BTN/SB steal: %s | by open size: %s" % (mix(A, "bd"), "; ".join(
        "%s %s" % (b, mix(A, "bd_" + b)) for b in ("<=2.25bb", "2.25-3bb", ">3bb"))))
    P("blind defence vs OUR steal: %s | vs any open of ours (no callers): %s" % (mix(A, "bd_us"), mix(A, "vs_our_open")))
    P("preflop shove per hand %s; shown after shove %s" % (rate(A, "shove"), dist(A.l["shove_shown"], 12, "%s")))
    P("open raise hands shown: %s" % dist(A.l["open_shown"], 14, "%s"))
    P("3-bet hands shown: %s" % dist(A.l["3b_shown"], 14, "%s"))
    P("4-bet hands shown: %s" % dist(A.l["4b_shown"], 10, "%s"))
    P("cold call shown (not BB): %s" % dist(A.l["cc_shown_other"], 14, "%s"))
    P("BB call shown: %s" % dist(A.l["cc_shown_BB"], 14, "%s"))
    P("-- aggressor")
    for st in ("flop", "turn", "river"):
        ln = "cbet" if st == "flop" else "barrel"
        P("%s %s: HU %s | MW %s | sizes %s med %.2f" % (
            ln, st, mix(A, "%s_%s_hu" % (ln, st)), mix(A, "%s_%s_mw" % (ln, st)),
            dist(A.l["bsz_%s_%s" % (ln, st)], 4), med(A.l["bsz_%s_%s" % (ln, st)])))
    P("cbet by texture: " + "; ".join("%s %s" % (t, rate(A, "cbet_tex_" + t, "raise"))
                                      for t in ("paired", "monotone", "high card", "low connected", "other")))
    for st in ("flop", "turn", "river"):
        P("%s: bet when checked to %s sizes %s | lead first %s | donk %s | check-raise %s | after missed cbet/barrel facing stab %s" % (
            st, rate(A, "bct_" + st, "raise"), dist(A.l["bsz_bct_%s" % st], 3), rate(A, "lead_" + st, "raise"),
            rate(A, "donk_" + st, "raise"), rate(A, "xr_" + st, "raise"), mix(A, "stab_after_missed_" + st)))
    P("overbet share of bets %s, of raises %s" % (rate(A, "overbet_bet"), rate(A, "overbet_raise")))
    for st in ("flop", "turn", "river"):
        P("all bet sizes %s: %s" % (st, dist(A.l["all_bet_" + st], 5)))
    P("-- showdown class by line and size bucket (value=two pair+, medium=TP/overpair, weak pair, draw, air)")
    for kind in ("bet", "raise"):
        for st in ("flop", "turn", "river"):
            xs = A.l["sd_%s_%s" % (kind, st)]
            if xs:
                byb = defaultdict(Counter)
                for b, g in xs:
                    byb[b][g] += 1
                P("  %s %s: %s" % (kind, st, "; ".join(
                    "%s %s" % (b, dict(byb[b])) for b in ("<40%", "40-75%", "75-110%", "overbet") if b in byb)))
    for st in ("flop", "turn", "river"):
        if A.l["sd_call_" + st]:
            P("  called a %s bet then showed: %s" % (st, dict(Counter(A.l["sd_call_" + st]))))
    P("-- defender")
    for st in ("flop", "turn", "river"):
        P("vs bet %s: %s | HU %s | MW %s" % (st, mix(A, "fb_" + st), mix(A, "fb_%s_hu" % st), mix(A, "fb_%s_mw" % st)))
        P("   by size: " + "; ".join("%s %s" % (b, mix(A, "fb_%s_%s" % (st, b)))
                                     for b in ("<40%", "40-75%", "75-110%", "overbet")))
    P("vs bet all streets by size: " + "; ".join("%s %s" % (b, mix(A, "fb_all_" + b))
                                                 for b in ("<40%", "40-75%", "75-110%", "overbet")))
    P("vs OUR bets: flop %s | turn %s | river %s" % (mix(A, "fb_us_flop"), mix(A, "fb_us_turn"), mix(A, "fb_us_river")))
    P("vs OUR bets HU: flop %s | turn %s | river %s" % (mix(A, "fb_us_hu_flop"), mix(A, "fb_us_hu_turn"), mix(A, "fb_us_hu_river")))
    P("vs OUR bets by size: " + "; ".join("%s %s" % (b, mix(A, "fb_us_all_" + b))
                                          for b in ("<40%", "40-75%", "75-110%", "overbet")))
    P("vs raise after their bet: %s (F %s T %s R %s)" % (
        mix(A, "vs_raise_after_bet"), mix(A, "vs_raise_after_bet_flop"), mix(A, "vs_raise_after_bet_turn"),
        mix(A, "vs_raise_after_bet_river")))
    P("vs second barrel (called flop, same bettor turn): %s | vs third barrel: %s | vs river bet after checked turn: %s" % (
        mix(A, "vs_barrel2"), mix(A, "vs_barrel3"), mix(A, "vs_river_after_xturn")))
    P("-- showdown: WTSD (of hands seeing a flop) %s | won at showdown %s" % (rate(A, "wtsd"), rate(A, "wsd")))
    big = sorted(A.l["big"])
    P("biggest showdown losses: %s" % big[:4])
    P("biggest showdown wins: %s" % big[::-1][:4])


def main():
    check = "--check" in sys.argv
    rounds = load_rounds()
    acc = defaultdict(Acc)                 # (team, ref) -> Acc
    flow = defaultdict(float)              # (team, ref) -> chips paid to us
    together = defaultdict(int)            # (team, ref) -> hands
    team_refs = defaultdict(list)
    seat_events = {}                       # (team, ref) -> events
    spots = defaultdict(lambda: defaultdict(lambda: [0, 0.0, []]))   # team -> label -> [n, chips, examples]
    ver_of = {}
    us_total = 0
    flow_total = 0.0
    per_hand_bad = 0
    for d in rounds:
        me = d["seat"]
        ref = d["ref"].split("/")[1]
        ver_of[ref] = d["round"]["version"]
        CUR_REF[0] = ref
        n = len(d["players"])
        pl = d["players"]
        for s, name in enumerate(pl):
            if s != me:
                team_refs[name].append(ref)
                seat_events[(name, ref)] = []
        for h in d["hands"]:
            acts, la = replay(h, n)
            for s, name in enumerate(pl):
                if s == me:
                    seat_hand(acc[(US, ref)], h, s, n, acts, la, me, [])
                    continue
                seat_hand(acc[(name, ref)], h, s, n, acts, la, me, seat_events[(name, ref)])
                together[(name, ref)] += 1
            fl = flows(h, me)
            if abs(sum(fl.values()) - h["results"][me]) > 1e-6:
                per_hand_bad += 1
            us_total += h["results"][me]
            for j, c in fl.items():
                flow[(pl[j], ref)] += c
                flow_total += c
                if pl[j] in PRIMARY + SECONDARY and c != 0:
                    lab = spot_label(acts, me, j)
                    sp = spots[pl[j]][lab]
                    sp[0] += 1
                    sp[1] += c
                    sp[2].append((c, ref, h["n"], line_str(h, acts, pl, me, j)))
        site = d["round"]["chips"]
        mine = sum(h["results"][me] for h in d["hands"])
        if site != mine:
            print("WARNING %s site chips %d != hand sum %d" % (ref, site, mine))

    print("# data: %d counted rounds %s to %s, %d hands" % (
        len(rounds), rounds[0]["ref"], rounds[-1]["ref"], sum(len(d["hands"]) for d in rounds)))
    print("# flow check: per hand mismatches %d; sum of flows %.1f; our total %d" % (per_hand_bad, flow_total, us_total))

    by_v = defaultdict(list)
    for d in rounds:
        by_v[d["round"]["version"]].append(d["round"]["bb100"])
    for v, xs in sorted(by_v.items()):
        m = sum(xs) / len(xs)
        sd = (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5 if len(xs) > 1 else float("nan")
        print("# us v%d: %d rounds, mean %+.1f bb/100, sd per 1,000 hand round %.1f" % (v, len(xs), m, sd))

    # ---------------- item 1: sample and money, by our version
    print("\n## SAMPLE AND MONEY")
    for t in PRIMARY + SECONDARY:
        refs = team_refs[t]
        hands = sum(together[(t, r)] for r in refs)
        A = merge(acc[(t, r)] for r in refs)
        fl = sum(flow[(t, r)] for r in refs)
        print("\n%s: rounds=%d (%s) hands=%d their bb/100=%+.1f flow to us=%+.0f chips (%+.1f bb/100 together)" % (
            t, len(refs), ",".join(refs), hands, A.v["chips"] / hands * 5, fl, fl / hands * 5))
        byv = defaultdict(list)
        for r in refs:
            byv[ver_of[r]].append(r)
        for v in sorted(byv):
            rs = byv[v]
            hn = sum(together[(t, r)] for r in rs)
            ch = sum(acc[(t, r)].v["chips"] for r in rs)
            f2 = sum(flow[(t, r)] for r in rs)
            our = sum(acc[(US, r)].v["chips"] for r in rs)
            print("  our v%d: rounds %s hands %d | their bb/100 %+.1f | flow to us %+.0f (%+.1f bb/100) | our bb/100 those rounds %+.1f" % (
                v, ",".join(rs), hn, ch / hn * 5, f2, f2 / hn * 5, our / hn * 5))
        print("  per round their bb/100: " + ", ".join("%s %+.1f" % (r, acc[(t, r)].v["chips"] / together[(t, r)] * 5) for r in refs))

    # ---------------- profiles
    print("\n## PROFILES")
    for t in PRIMARY + SECONDARY:
        refs = team_refs[t]
        show_profile(t, merge(acc[(t, r)] for r in refs), "rounds=%s" % ",".join(refs))
    allus = merge(acc[(US, r)] for r in ver_of)
    show_profile("POOL all other seats", merge(a for (t, r), a in acc.items() if t != US))

    # ---------------- drift
    print("\n## DRIFT (rounds in time order, split into thirds)")
    keys = [("VPIP", "vpip", "y"), ("PFR", "pfr", "y"), ("limp", "limp", "y"), ("fi raise", "fi", "raise"),
            ("3-bet", "vs1", "raise"), ("fold to 3-bet", "f3b", "fold"), ("4-bet", "vs2", "raise"),
            ("cbet flop", "cbet_flop", "raise"), ("barrel turn", "barrel_turn", "raise"),
            ("barrel river", "barrel_river", "raise"), ("bet ct turn", "bct_turn", "raise"),
            ("bet ct river", "bct_river", "raise"), ("fold vs flop bet", "fb_flop", "fold"),
            ("fold vs turn bet", "fb_turn", "fold"), ("fold vs river bet", "fb_river", "fold"),
            ("fold vs >75% bets", "fb_all_75-110%", "fold"), ("fold to raise after bet", "vs_raise_after_bet", "fold"),
            ("fold to 4-bet after 3-bet", "f4b", "fold"), ("check-raise flop", "xr_flop", "raise"),
            ("donk flop", "donk_flop", "raise"), ("bets >100% pot", "overbet_bet", "y"),
            ("blind def fold", "bd", "fold"), ("shove/hand", "shove", "y"), ("WTSD", "wtsd", "y"), ("W$SD", "wsd", "y")]
    for t in PRIMARY:
        refs = team_refs[t]
        k = len(refs)
        cuts = [refs[:k // 3 + (1 if k % 3 > 0 else 0)]]
        rest = refs[len(cuts[0]):]
        cuts.append(rest[:(len(rest) + 1) // 2])
        cuts.append(rest[len(cuts[1]):])
        print("\n%s thirds: %s" % (t, [",".join(c) for c in cuts]))
        As = [merge(acc[(t, r)] for r in c) for c in cuts]
        Rs = [acc[(t, r)] for r in refs]
        print("  %-24s %s" % ("stat", " | ".join("third %d" % (i + 1) for i in range(3))))
        for lab, key, o in keys:
            print("  %-24s %s" % (lab, " | ".join(rate(a, key, o) for a in As)))
        print("  %-24s %s" % ("open sizes", " | ".join(dist(a.l["osz"], 3) for a in As)))
        print("  %-24s %s" % ("3-bet mult", " | ".join(dist(a.l["3b_mult"], 3) for a in As)))
        print("  %-24s %s" % ("cbet size med", " | ".join("%.2f (n=%d)" % (med(a.l["bsz_cbet_flop"]), len(a.l["bsz_cbet_flop"])) for a in As)))
        print("  %-24s %s" % ("turn/river bet med", " | ".join("%.2f (n=%d)" % (med(a.l["all_bet_turn"] + a.l["all_bet_river"]), len(a.l["all_bet_turn"] + a.l["all_bet_river"])) for a in As)))
        print("  %-24s %s" % ("bb/100", " | ".join("%+.1f" % (a.v["chips"] / a.v["hands"] * 5) for a in As)))
        print("  per round: " + "; ".join("%s VPIP %.2f PFR %.2f 3b %s open %s cb %s fold3b %s" % (
            r, rate(a, "vpip", raw=True)[0], rate(a, "pfr", raw=True)[0], rate(a, "vs1", "raise"),
            dist(a.l["osz"], 2), rate(a, "cbet_flop", "raise"), rate(a, "f3b", "fold")) for r, a in zip(refs, Rs)))

    fingerprints(seat_events, team_refs)
    R = us_spots(rounds, acc, team_refs, together)
    deep(rounds)
    rules(R, {t: merge(acc[(t, r)] for r in team_refs[t]) for t in PRIMARY},
          {t: sum(together[(t, r)] for r in team_refs[t]) for t in PRIMARY})

    # ---------------- item 8
    print("\n## SPOTS BETWEEN US AND EACH TEAM (flow to us; positive = we won)")
    for t in PRIMARY + SECONDARY:
        sp = spots[t]
        tot = sum(x[1] for x in sp.values())
        hands = sum(together[(t, r)] for r in team_refs[t])
        print("\n%s total %+.0f chips over %d hands" % (t, tot, hands))
        for lab, (k, c, ex) in sorted(sp.items(), key=lambda x: x[1][1]):
            if abs(c) < 800 and t not in PRIMARY:
                continue
            print("  %-56s n=%4d chips %+8.0f (%+.1f bb/100)" % (lab, k, c, c / hands * 5))
        if t in PRIMARY:
            worst = sorted(sp.items(), key=lambda x: x[1][1])[:3]
            best = sorted(sp.items(), key=lambda x: -x[1][1])[:3]
            for title, grp, rev in (("LOST MOST", worst, False), ("WON MOST", best, True)):
                print(" %s:" % title)
                for lab, (k, c, ex) in grp:
                    print("  [%s] n=%d %+.0f" % (lab, k, c))
                    for e in sorted(ex, reverse=rev)[:3]:
                        print("     %s #%d flow %+.0f | %s" % (e[1], e[2], e[0], e[3]))

    # ---------------- secondary briefs, all teams baseline for fingerprints
    print("\n## ALL TEAMS QUICK TABLE (for fingerprint comparison)")
    for t in sorted(team_refs, key=lambda x: -len(team_refs[x])):
        A = merge(acc[(t, r)] for r in team_refs[t])
        print("%-26s r=%2d VPIP %.2f PFR %.2f limp %.2f 3b %.2f opens %s 3bx %s bets %s" % (
            t, len(team_refs[t]), rate(A, "vpip", raw=True)[0], rate(A, "pfr", raw=True)[0],
            rate(A, "limp", raw=True)[0] or 0, rate(A, "vs1", "raise", raw=True)[0] or 0,
            dist(A.l["osz"], 3), dist(A.l["3b_mult"], 2),
            "%.2f med n=%d" % (med(sum((A.l[k] for k in A.l if k.startswith("all_bet_")), [])),
                               len(sum((A.l[k] for k in A.l if k.startswith("all_bet_")), [])))))

    if check:
        hand_checks(rounds)


# ------------------------------------------------------------------ fingerprints
def _opens(ev):
    return [v for _, k, v in ev if k == "open"]


def _bets(ev):
    return [v for _, k, v in ev if k.startswith("bet_")]


def _threes(ev):
    return [v for _, k, v in ev if k == "3bet"]


def _near(x, zs, tol=0.015):
    return any(abs(x - z) <= tol for z in zs)


def _share(xs, pred):
    return sum(1 for x in xs if pred(x)) / float(len(xs)) if xs else 0.0


def fp_g(ev):
    """Gherkers: at least 3 opens, 90% or more of them exactly 3.5bb, and either a non all-in
    postflop bet of 1.08 to 1.12 pot or a 3-bet of 3.78x to 3.82x the open."""
    o = _opens(ev)
    if len(o) < 3 or _share(o, lambda x: abs(x - 3.5) < 1e-6) < 0.9:
        return False
    return any(_near(x, (1.10,), 0.02) for x in _bets(ev)) or any(_near(x, (3.8,), 0.02) for x in _threes(ev))


def fp_ee(ev):
    """Equity Engine: at least 5 opens, 90% or more exactly 3.5bb; at least 3 non all-in
    postflop bets, 90% or more of them at 0.45, 0.50, 0.80 or 1.05 pot (within 0.015) with at
    least one at 0.80; every 3-bet between 2.9x and 3.45x the open."""
    o = _opens(ev)
    b = _bets(ev)
    if len(o) < 5 or _share(o, lambda x: abs(x - 3.5) < 1e-6) < 0.9 or len(b) < 3:
        return False
    return _share(b, lambda x: _near(x, (0.45, 0.5, 0.8, 1.05))) >= 0.9 and any(_near(x, (0.8,)) for x in b) \
        and all(2.9 <= x <= 3.45 for x in _threes(ev))


def fp_aiai(ev):
    """Attention Is All In: at least 5 opens, 90% or more of them at 2, 2.5, 3 or 4bb, with a
    4bb or a 2bb open seen; at least 3 non all-in postflop bets, half or more at 0.31 to 0.35 pot."""
    o = _opens(ev)
    b = _bets(ev)
    if len(o) < 5 or _share(o, lambda x: x in (2.0, 2.5, 3.0, 4.0)) < 0.9 or not (4.0 in o or 2.0 in o):
        return False
    return len(b) >= 3 and _share(b, lambda x: _near(x, (0.33,), 0.02)) >= 0.5


def _mk(open_sizes, bet_sizes, bet_share, doc, need_open=5, need_bets=3):
    def f(ev):
        o = _opens(ev)
        b = _bets(ev)
        if len(o) < need_open or _share(o, lambda x: any(abs(x - z) < 1e-6 for z in open_sizes)) < 0.9:
            return False
        return len(b) >= need_bets and _share(b, lambda x: _near(x, bet_sizes, 0.015)) >= bet_share
    f.__doc__ = doc
    return f


fp_tmm = _mk((2.5,), (0.5, 0.7, 1.0, 0.6), 0.8, "The Market Makers: 90% of opens 2.5bb (>=5) and 80% of postflop bets at 0.5, 0.6, 0.7 or 1.0 pot (>=3).")
fp_aast = _mk((3.0,), (1.1, 0.7, 0.33, 0.8), 0.7, "AAST: 90% of opens 3bb (>=5) and 70% of postflop bets at 1.1, 0.8, 0.7 or 0.33 pot (>=3).")
fp_wbot = _mk((3.5, 2.8, 4.0, 3.3), (0.15,), 0.4, "WBot: 90% of opens at 2.8, 3.3, 3.5 or 4bb (>=5) and 40% of postflop bets at 0.15 pot (>=3).")
fp_kojack = _mk((2.5, 3.0), (0.55, 0.72, 0.4, 0.45), 0.6, "Kojack: 90% of opens 2.5 or 3bb (>=5) and 60% of postflop bets at 0.40, 0.45, 0.55 or 0.72 pot (>=3).")
fp_anker = _mk((2.5,), (1.1, 2.0, 0.4, 0.62, 0.7), 0.7, "Anker Batteries: 90% of opens 2.5bb (>=5) and 70% of postflop bets at 0.4, 0.62, 0.7, 1.1 or 2.0 pot (>=3).")


FP_RULES = [("FG", "Gherkers", fp_g), ("FEE", "Equity Engine", fp_ee),
            ("FA", "Attention Is All In", fp_aiai), ("FTMM", "The Market Makers", fp_tmm),
            ("FAAST", "AAST", fp_aast), ("FW", "WBot", fp_wbot), ("FK", "Kojack", fp_kojack),
            ("FANK", "Anker Batteries", fp_anker)]


def fingerprints(seat_events, team_refs):
    print("\n## FINGERPRINTS (each seat round is one seat for one 1,000 hand round)")
    for doc in FP_RULES:
        print("%s: %s" % (doc[0], " ".join(doc[2].__doc__.split())))
    nseat = len(seat_events)
    for code, target, f in FP_RULES:
        print("\n%s (target %s)" % (code, target))
        first = []
        for (t, r), ev in seat_events.items():
            if t != target:
                continue
            hit = next((H for H in range(10, 1001, 10) if f([x for x in ev if x[0] <= H])), None)
            first.append((r, hit))
        print("  first hand at which the rule fires, per target seat round: %s" % first)
        for H in (50, 100, 200, 300, 500, 1000):
            fire = defaultdict(lambda: [0, 0])
            for (t, r), ev in seat_events.items():
                ok = f([x for x in ev if x[0] <= H])
                fire[t][1] += 1
                fire[t][0] += ok
            tk, tn = fire[target]
            others = {t: "%d/%d" % tuple(v) for t, v in fire.items() if t != target and v[0]}
            ok_n = sum(v[0] for t, v in fire.items() if t != target)
            on = sum(v[1] for t, v in fire.items() if t != target)
            print("  H=%4d target %d/%d | false positives %d/%d other seat rounds (%.1f%%), %d teams %s" % (
                H, tk, tn, ok_n, on, 100.0 * ok_n / on, len(others), others))
    print("  (total seat rounds %d)" % nseat)


# ------------------------------------------------------------------ spots involving our seat
def us_spots(rounds, acc, team_refs, together):
    R = defaultdict(lambda: defaultdict(list))
    for d in rounds:
        me = d["seat"]
        n = len(d["players"])
        pl = d["players"]
        tseats = {s: t for s, t in enumerate(pl) if t in PRIMARY + SECONDARY}
        if not tseats:
            continue
        for h in d["hands"]:
            acts, la = replay(h, n)
            res = h["results"][me]
            pre = [a for a in acts if a["street"] == "preflop"]
            for t, T in tseats.items():
                X = R[T]
                # preflop
                op = next((a for a in pre if a["act"] == "raise" and a["raises"] == 0 and a["limpers"] == 0), None)
                if op and op["seat"] == t:
                    ours = next((a for a in pre if a["seat"] == me and a["i"] > op["i"]), None)
                    if ours and ours["raises"] == 1 and ours["callers"] == 0:
                        X["face_open"].append({"act": ours["act"], "res": res, "after": res + ours["put_before"],
                                               "size": op["amt"] / float(BB), "hand": combo(h["hole"][str(me)])})
                        if ours["act"] == "raise":
                            resp = next((a for a in pre if a["seat"] == t and a["i"] > ours["i"]), None)
                            if resp:
                                X["we3bet"].append({"act": resp["act"], "res": res,
                                                    "risk": ours["amt"] / float(BB), "pot": ours["pot"] / float(BB)})
                if op and op["seat"] == me:
                    pos = pos_name((me - h["button"]) % n, n)
                    tpos = pos_name((t - h["button"]) % n, n)
                    tr = next((a for a in pre if a["seat"] == t and a["i"] > op["i"]), None)
                    if tr and tr["raises"] == 1 and tr["callers"] == 0:
                        if pos in ("CO", "BTN", "SB") and tpos in ("SB", "BB"):
                            X["steal"].append({"act": tr["act"], "res": res, "size": op["amt"] / float(BB)})
                        if tr["act"] == "raise":
                            nxt = next((a for a in pre if a["seat"] == me and a["i"] > tr["i"]), None)
                            if nxt and nxt["raises"] == 2:
                                X["face_3bet"].append({"act": nxt["act"], "res": res, "pot": nxt["pot"] / float(BB),
                                                       "after": res + nxt["put_before"], "hand": combo(h["hole"][str(me)]),
                                                       "tc": nxt["to_call"] / float(BB), "amt": tr["amt"] / float(BB),
                                                       "open": op["amt"] / float(BB)})
                                if nxt["act"] == "raise":
                                    r4 = next((a for a in pre if a["seat"] == t and a["i"] > nxt["i"]), None)
                                    if r4:
                                        X["we4bet"].append({"act": r4["act"], "res": res})
                # postflop
                for street in ("flop", "turn", "river"):
                    sa = [a for a in acts if a["street"] == street]
                    if not sa or sa[0]["live"] != 2:
                        continue
                    seats = set(a["seat"] for a in sa)
                    if seats != {me, t} and not (seats <= {me, t}):
                        continue
                    for a in sa:
                        if a["seat"] == me and a["to_call"] > 0 and a["raises"] == 1:
                            rec = {"act": a["act"], "res": res, "pot": (a["pot"] - a["to_call"]) / float(BB), "b": a["face"],
                                   "after": res + a["put_before"], "street": street,
                                   "cls": group(h["hole"][str(me)], h["board"][:{"flop": 3, "turn": 4, "river": 5}[street]])}
                            X["face_bet_%s_%s" % (street, bucket(a["face"]))].append(rec)
                            X["face_bet_all"].append(rec)
                            X["face_bet_any_" + bucket(a["face"])].append({"act": a["act"], "res": res})
                            if a["act"] == "raise":
                                r = next((x for x in sa if x["seat"] == t and x["i"] > a["i"]), None)
                                if r:
                                    X["weraise"].append({"act": r["act"], "res": res})
                            break
                    ourbet = next((a for a in sa if a["seat"] == me and a["act"] == "raise" and a["to_call"] == 0), None)
                    if ourbet:
                        r = next((x for x in sa if x["seat"] == t and x["i"] > ourbet["i"]), None)
                        if r:
                            X["webet_%s_%s" % (street, bucket(ourbet["size"]))].append(
                                {"act": r["act"], "res": res, "pot": ourbet["pot"] / float(BB), "b": ourbet["size"]})
                            X["webet_" + street].append({"act": r["act"], "res": res, "pot": ourbet["pot"] / float(BB), "b": ourbet["size"]})
                            X["webet_all"].append({"act": r["act"], "res": res, "pot": ourbet["pot"] / float(BB), "b": ourbet["size"],
                                                   "after": res + ourbet["put_before"],
                                                   "cls": group(h["hole"][str(me)], h["board"][:{"flop": 3, "turn": 4, "river": 5}[street]])})
                    tf = sa[0]
                    if tf["seat"] == t and tf["act"] == "check" and len(sa) > 1 and sa[1]["seat"] == me:
                        ours = sa[1]
                        resp = next((x for x in sa if x["seat"] == t and x["i"] > ours["i"]), None)
                        X["tcheck_" + street].append({"act": ours["act"], "res": res, "pot": ours["pot"] / float(BB),
                                                      "after": res + ours["put_before"], "street": street,
                                                      "cls": group(h["hole"][str(me)], h["board"][:{"flop": 3, "turn": 4, "river": 5}[street]]),
                                                      "resp": resp["act"] if resp else None,
                                                      "pfa": la.get("preflop") == t})
    print("\n## SPOTS INVOLVING OUR SEAT (heads up postflop; counts per 100 hands seated together)")
    for T in PRIMARY + SECONDARY:
        hands = sum(together[(T, r)] for r in team_refs[T])
        print("\n%s (%d hands together)" % (T, hands))
        for key in sorted(R[T]):
            xs = R[T][key]
            c = Counter(x["act"] for x in xs)
            chips = defaultdict(float)
            for x in xs:
                chips[x["act"]] += x["res"]
            pots = [x["pot"] for x in xs if "pot" in x]
            extra = ""
            if key in ("face_bet_all", "webet_all"):
                continue
            if key.startswith("tcheck"):
                rc = Counter(x["resp"] for x in xs if x["act"] == "raise")
                extra = " | their reply to our bet %s" % dict(rc)
            if key == "face_3bet":
                extra = " | their 3-bet bb %s | to call bb med %.1f" % (dist([round(x["amt"], 1) for x in xs], 4), med([x["tc"] for x in xs]))
            print("  %-26s n=%4d (%.2f/100) acts %s chips by act %s pot med %sbb%s" % (
                key, len(xs), 100.0 * len(xs) / hands, dict(c),
                {k: int(v) for k, v in chips.items()}, ("%.1f" % med(pots)) if pots else "n/a", extra))
    return R


# ------------------------------------------------------------------ deeper single team cuts
def deep(rounds):
    print("\n## DEEP CUTS (primary targets)")
    global SIZE_RAISED
    ip3 = defaultdict(lambda: defaultdict(list))
    osz_shown = defaultdict(lambda: defaultdict(list))
    osz_round = defaultdict(lambda: defaultdict(list))
    size_sd = defaultdict(lambda: defaultdict(Counter))
    size_raised = defaultdict(lambda: defaultdict(Counter))
    size_tex = defaultdict(lambda: defaultdict(list))
    three_vs_open = defaultdict(list)
    for d in rounds:
        n = len(d["players"])
        ref = d["ref"].split("/")[1]
        for s, T in enumerate(d["players"]):
            if T not in PRIMARY:
                continue
            for h in d["hands"]:
                acts, la = replay(h, n)
                hole = h["hole"].get(str(s))
                shown = str(s) in h["showdown"] and hole is not None
                pos = pos_name((s - h["button"]) % n, n)
                pre = [a for a in acts if a["street"] == "preflop"]
                for a in pre:
                    if a["seat"] != s or a["act"] != "raise":
                        continue
                    if a["raises"] == 0 and a["limpers"] == 0:
                        bb = round(a["amt"] / float(BB), 2)
                        osz_round[T][ref].append(bb)
                        if shown:
                            osz_shown[T][bb].append(combo(hole))
                    if a["raises"] == 1:
                        op = next(x for x in pre if x["act"] == "raise")
                        side = "OOP (blinds)" if pos in ("SB", "BB") else "IP"
                        ip3[T][side].append(round(a["amt"] / float(a["cur"]), 2))
                        three_vs_open[T].append((round(a["cur"] / float(BB), 2), round(a["amt"] / float(BB), 2), side))
                nb = {"flop": 3, "turn": 4, "river": 5}
                for a in acts:
                    if a["seat"] != s or a["act"] != "raise" or a["street"] == "preflop" or a["to_call"] != 0:
                        continue
                    sz = round(a["size"], 2)
                    if shown:
                        size_sd[T][(a["street"], sz)][group(hole, h["board"][:nb[a["street"]]])] += 1
                    nxt = next((x for x in acts if x["seat"] == s and x["i"] > a["i"] and x["street"] == a["street"]), None)
                    if nxt is not None and nxt["to_call"] > 0:
                        size_raised[T][sz][nxt["act"]] += 1
                    if a["street"] == "flop":
                        size_tex[T][(texture(h["board"][:3]), "HU" if a["live"] == 2 else "MW")].append(sz)
    SIZE_RAISED = size_raised
    for T in PRIMARY:
        print("\n### %s" % T)
        for side, xs in sorted(ip3[T].items()):
            print("  3-bet multiple %s: %s" % (side, dist(xs, 4)))
        print("  3-bet (open bb -> 3-bet bb, side) most common: %s" % Counter(three_vs_open[T]).most_common(8))
        print("  open size per round: " + "; ".join("%s %s" % (r, dist(xs, 4)) for r, xs in sorted(osz_round[T].items())))
        for bb, xs in sorted(osz_shown[T].items()):
            print("  shown after %gbb open: %s" % (bb, dist(xs, 20, "%s")))
        print("  flop bet size by texture and HU/MW:")
        for k, xs in sorted(size_tex[T].items()):
            print("    %-24s %s" % ("%s %s" % k, dist(xs, 4)))
        print("  showdown class by street and exact bet size (sizes with >=4 shown):")
        for (st, sz), c in sorted(size_sd[T].items()):
            if sum(c.values()) >= 4:
                print("    %-6s %.2f pot: %s (n=%d)" % (st, sz, dict(c), sum(c.values())))
        print("  reply when raised after betting, by exact bet size: " + "; ".join(
            "%.2f %s" % (sz, dict(c)) for sz, c in sorted(size_raised[T].items()) if sum(c.values()) >= 3))



# ------------------------------------------------------------------ counter rules arithmetic
SIZE_RAISED = {}
WEAK = ("air", "draw", "weak")
PREMIUM = {"AA", "KK", "QQ", "AKs", "AKo"}


def _raised_fold(T, sizes):
    c = Counter()
    for sz, x in SIZE_RAISED[T].items():
        if any(abs(sz - z) <= 0.021 for z in sizes):
            c.update(x)
    n = sum(c.values())
    return c["fold"], n


def _mean(xs):
    return sum(xs) / float(len(xs)) if xs else 0.0


def rule_line(code, text, f, n_f, spots, hands, ev_rule, ev_now, be, extra=""):
    """Print one rule: measured rate, break even, EV per spot (bb), spots per 100, gain per 100."""
    per100 = 100.0 * len(spots) / hands
    gain = per100 * (ev_rule - ev_now)
    print("%-6s %s\n       measured %.2f (%d/%d%s) | break even %.2f | EV rule %+.2fbb vs now %+.2fbb per spot | "
          "spots %d (%.2f/100) | gain %+.2f bb/100%s" % (
              code, text, f, round(f * n_f), n_f, "*" if n_f < 30 else "", be, ev_rule, ev_now, len(spots),
              per100, gain, extra))
    return gain


def rules(R, A, hands):
    """Expected gain of each counter rule when seated with the team.
    EV of a bluff assumes zero equity when called or raised (a floor for hands with draws).
    'now' is our realised result from the decision point on (chips after minus chips already in),
    measured on the same spots, so gain = (rule EV - realised EV) x spots per 100 hands."""
    print("\n## COUNTER RULE ARITHMETIC (bb; spots are our seat's spots against that team)")
    for T in PRIMARY:
        X = R[T]
        H = hands[T]
        a = A[T]
        print("\n### %s (%d hands together)" % (T, H))

        def raise_small(code, sizes, label):
            fk, fn = _raised_fold(T, sizes)
            f = fk / float(fn) if fn else 0.0
            sp = [x for x in X["face_bet_all"] if any(abs(x["b"] - z) <= 0.03 for z in sizes)
                  and x["cls"] in WEAK and x["act"] != "raise"]
            # raise to 3x the bet: risk 3B to win P + B
            evs = [f * (x["pot"] * (1 + x["b"])) - (1 - f) * 3 * x["b"] * x["pot"] for x in sp]
            be = 3 * sizes[0] / (1 + 4 * sizes[0])
            return rule_line(code, label, f, fn, sp, H, _mean(evs), _mean([x["after"] / BB for x in sp]), be)

        def stab(code, label, size=0.66):
            rep = Counter()
            for st in ("flop", "turn", "river"):
                rep.update(x["resp"] for x in X["tcheck_" + st] if x["act"] == "raise" and x["resp"])
            n_r = sum(rep.values())
            f = rep["fold"] / float(n_r) if n_r else 0.0
            sp = [x for st in ("flop", "turn", "river") for x in X["tcheck_" + st] if x["act"] == "check" and x["cls"] in WEAK]
            evs = [f * x["pot"] - (1 - f) * size * x["pot"] for x in sp]
            return rule_line(code, label, f, n_r, sp, H, _mean(evs), _mean([x["after"] / BB for x in sp]), size / (1 + size))

        def fold_vs(code, label, pred):
            sp = [x for x in X["face_bet_all"] if pred(x)]
            return rule_line(code, label, 0.0, 0, sp, H, 0.0, _mean([x["after"] / BB for x in sp]), 0.0,
                             " (fold rule: EV rule 0; measured is our realised result calling)")

        def bluff_size(code, label, f_big_key, f_mid_key, b_big):
            fb = a.o[f_big_key]
            fm = a.o[f_mid_key]
            f_big = fb["fold"] / float(fb["n"])
            f_mid = fm["fold"] / float(fm["n"])
            sp = [x for x in X["webet_all"] if 0.4 <= x["b"] <= 0.75 and x["cls"] in WEAK]
            ev_big = [f_big * x["pot"] - (1 - f_big) * b_big * x["pot"] for x in sp]
            ev_mid = [f_mid * x["pot"] - (1 - f_mid) * x["b"] * x["pot"] for x in sp]
            return rule_line(code, label + " (fold at mid sizes %.2f of %d)" % (f_mid, fm["n"]), f_big, fb["n"], sp, H,
                             _mean(ev_big), _mean(ev_mid), b_big / (1 + b_big))

        if T == "Gherkers":
            fk = a.o["f4b"]
            f = fk["fold"] / float(fk["n"])
            sp = [x for x in X["face_3bet"] if x["act"] == "fold"]
            evs = []
            for x in sp:
                risk = 2.3 * x["amt"] - (x["amt"] - x["tc"])
                evs.append(f * x["pot"] - (1 - f) * risk)
            rule_line("G1", "4-bet to 2.3x instead of folding when G 3-bets our open", f, fk["n"], sp, H,
                      _mean(evs), 0.0, _mean([2.3 * x["amt"] - (x["amt"] - x["tc"]) for x in sp]) /
                      max(1e-9, _mean([2.3 * x["amt"] - (x["amt"] - x["tc"]) + x["pot"] for x in sp])))
            sp = [x for x in X["face_3bet"] if x["act"] == "call" and x["hand"] not in PREMIUM]
            rule_line("G2", "fold instead of flatting G's 3-bet with hands below QQ/AK", 0.0, 0, sp, H, 0.0,
                      _mean([x["after"] / BB for x in sp]), 0.0, " (fold rule)")
            raise_small("G3", (0.33, 0.35), "raise G's 0.33 pot bets to 3x with weak pair, draw or air")
            bluff_size("G4", "bluff G at 0.8 pot instead of 40 to 75%", "fb_all_75-110%", "fb_all_40-75%", 0.8)
            fold_vs("G5", "fold weak pair or air to G's 1.10 pot bets on turn and river",
                    lambda x: abs(x["b"] - 1.1) <= 0.03 and x["street"] != "flop" and x["cls"] in ("weak", "air") and x["act"] == "call")
            stab("G6", "bet 0.66 pot with weak hands when G checks to us heads up")
        if T == "Attention Is All In":
            raise_small("A1", (0.33, 0.31, 0.32, 0.34), "raise AIAI's 0.31 to 0.34 pot bets to 3x with weak pair, draw or air")
            stab("A2", "bet 0.66 pot with weak hands when AIAI checks to us heads up")
            fold_vs("A3", "fold weak pair or air to AIAI's 0.5 pot or larger bets",
                    lambda x: x["b"] >= 0.5 and x["cls"] in ("weak", "air") and x["act"] == "call")
            sp = [x for x in X["face_open"] if x["size"] == 4.0 and x["act"] != "fold" and x["hand"] not in PREMIUM]
            rule_line("A4", "fold everything below QQ/AK to AIAI's 4bb open", 0.0, 0, sp, H, 0.0,
                      _mean([x["after"] / BB for x in sp]), 0.0, " (fold rule)")
            fold_vs("A5", "do not call AIAI's 0.33 pot bets with weak pair or air (raise per A1 or fold)",
                    lambda x: abs(x["b"] - 0.33) <= 0.03 and x["cls"] in ("weak", "air") and x["act"] == "call")
        if T == "Equity Engine":
            raise_small("E1", (0.45, 0.5), "raise EE's 0.45 and 0.50 pot bets to 3x with weak pair, draw or air")
            fold_vs("E2", "fold weak pair or air to EE's 0.80 pot turn and river bets",
                    lambda x: abs(x["b"] - 0.8) <= 0.03 and x["street"] != "flop" and x["cls"] in ("weak", "air") and x["act"] == "call")
            stab("E3", "bet 0.66 pot with weak hands when EE checks to us heads up")
            bluff_size("E4", "bluff EE at 0.8 pot instead of 40 to 75%", "fb_all_75-110%", "fb_all_40-75%", 0.8)
            sp = [x for x in X["face_open"] if x["act"] == "raise"]
            print("E5     our 3-bets over EE opens: n=%d (%.2f/100), realised %+.2fbb per 3-bet from the decision on "
                  "(EE folds %s to our 3-bets after opening)" % (
                      len(sp), 100.0 * len(sp) / H, _mean([x["after"] / BB for x in sp]), rate(a, "f3b_us", "fold")))
            sp = [x for x in X["face_open"] if x["act"] == "call"]
            print("       our flats of EE opens: n=%d, realised %+.2fbb per call" % (len(sp), _mean([x["after"] / BB for x in sp])))
            three = [x for x in X["face_open"] if x["act"] == "raise"]
            print("       converting every flat into a 3-bet at the realised 3-bet result: %+.2f bb/100 (upper bound, "
                  "the flatted hands are weaker than the 3-bet range)" % (
                      100.0 * len(sp) / H * (_mean([x["after"] / BB for x in three]) - _mean([x["after"] / BB for x in sp]))))



def hand_checks(rounds):
    """Raw events for the hands quoted as checks in the dossier."""
    want = {("r036", 349), ("r021", 163), ("r003", 714)}
    for d in rounds:
        ref = d["ref"].split("/")[1]
        for h in d["hands"]:
            if (ref, h["n"]) in want:
                print("\n# check %s hand %d players %s button %d" % (ref, h["n"], d["players"], h["button"]))
                for e in h["events"]:
                    print("  ", e)
                print("   results", h["results"])


if __name__ == "__main__":
    main()
