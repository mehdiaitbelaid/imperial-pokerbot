"""Measure the replicas (or the real teams) with the definitions of docs/table-d-raw-profiles.txt.

    python3 tabled/measure.py selftest                # hand classes of base.py against the profiles' definition
    python3 tabled/measure.py real --profile          # the seven teams, from hands/saturday_r0*.json (read only)
    python3 tabled/measure.py real --extra --last     # cuts by the replicas' own lines, latest third of the rounds
    python3 tabled/measure.py sim DIR [DIR ...]       # seats of the rounds saved by tools/selfplay.py --out DIR
    python3 tabled/measure.py sim DIR --table         # calibration table: real / replica, "!" = more than 10 points apart
    python3 tabled/measure.py sim DIR --nodes         # freeze each replica's node class mixes into tabled/_nodes.py
                                                      # (calibration step: run it only on a table of the replicas)
    options: --profile (full profile text, same layout as the raw profiles), --extra, --only NAME

The replay, the stat definitions and the hand classes are a port of docs/analysis/top_teams.py
and live_diagnosis.py (branch v1), which produced the raw profiles: `real --profile` prints the
same numbers as the PROFILES and DEEP CUTS blocks.  Extra cuts by the replicas' own lines and
nodes (base.post_ctx) are added under keys starting with x_; build.py reads them.
"""
import glob
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import base  # noqa: E402

BB = 20
TEAMS = [("anker", "Anker Batteries"), ("cpf", "Chinese people can fly"), ("wbot", "WBot"),
         ("gg", "GamesGone"), ("poke", "Poke"), ("anton", "Anton"), ("ysl", "YSL_TWIZZY")]
SHORT = dict((b, a) for a, b in TEAMS)
RANKS = "23456789TJQKA"
CATS = ["High Card", "Pair", "Two Pair", "Three of a Kind", "Straight", "Flush",
        "Full House", "Four of a Kind", "Straight Flush"]
STRONG = {"Two Pair", "Trips/Set", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush"}
POSS = ("UTG", "UTG+1", "MP", "HJ", "CO", "BTN", "SB", "BB")
ACTS = ("fold", "check", "call", "raise")
BUCKETS = ("<40%", "40-75%", "75-110%", "overbet")
NB = {"flop": 3, "turn": 4, "river": 5}


# ------------------------------------------------------------------ cards (verbatim port)
def rv(c):
    return RANKS.index(c[0])


def cat_of(cards):
    rs = Counter(rv(c) for c in cards)
    ss = Counter(c[1] for c in cards)
    flush_suit = next((s for s, k in ss.items() if k >= 5), None)

    def straight(ranks):
        m = set(ranks)
        if 12 in m:
            m.add(-1)
        return any(all(t - i in m for i in range(5)) for t in range(3, 13))

    if flush_suit and straight([rv(c) for c in cards if c[1] == flush_suit]):
        return 8
    cnt = sorted(rs.values(), reverse=True)
    if cnt[0] == 4:
        return 7
    if cnt[0] == 3 and len(cnt) > 1 and cnt[1] >= 2:
        return 6
    if flush_suit:
        return 5
    if straight(list(rs)):
        return 4
    if cnt[0] == 3:
        return 3
    if cnt[0] == 2 and len(cnt) > 1 and cnt[1] == 2:
        return 2
    if cnt[0] == 2:
        return 1
    return 0


def made_class(hole, board):
    if not board:
        return "preflop"
    mine = cat_of(hole + board)
    bc = cat_of(board)
    br = sorted((rv(c) for c in board), reverse=True)
    hr = [rv(c) for c in hole]
    if mine >= 4 and mine > bc:
        return CATS[mine]
    if mine == 3 and bc < 3:
        return "Trips/Set"
    if mine == 2 and bc < 1:
        return "Two Pair"
    if mine == 2 and bc == 1:
        mine = 1
        bc = 0
    if mine == 1 and bc == 0 or (mine == 2 and bc == 1):
        pocket = hr[0] == hr[1]
        if pocket and hr[0] > br[0]:
            return "Overpair"
        if not pocket and br[0] in hr:
            return "Top Pair"
        return "Weak Pair"
    if mine > bc:
        return CATS[mine]
    return "No made hand"


def combo(hole):
    a, b = sorted(hole, key=rv, reverse=True)
    if a[0] == b[0]:
        return a[0] + b[0]
    return a[0] + b[0] + ("s" if a[1] == b[1] else "o")


def has_draw(hole, board):
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


pos_name = base.pos_name
texture = base.texture
bucket = base.bucket


def open_bucket(bb):
    return "<=2.25bb" if bb <= 2.25 else ("2.25-3bb" if bb <= 3 else ">3bb")


# ------------------------------------------------------------------ replay (port + engine history)
def replay(h, n):
    acts = []
    street = "preflop"
    sb = defaultdict(int)
    put = defaultdict(int)
    cur = raises = limpers = callers = 0
    folded = set()
    acted = []
    la = {}
    start = h.get("start_stacks") or [2000] * n
    hist = []
    posts = 0
    for e in h["events"]:
        k = e[0]
        if k == "post":
            sb[e[1]] += e[2]
            put[e[1]] += e[2]
            cur = max(cur, sb[e[1]])
            hist.append({"seat": e[1], "street": "preflop", "action": "small_blind" if posts == 0 else "big_blind",
                         "amount": e[2]})
            posts += 1
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
                   "allin": False, "size": None, "i": len(acts), "hl": len(hist),
                   "stack": start[s] - put[s]}
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
            hist.append({"seat": s, "street": street, "action": a, "amount": amt})
    return acts, la, hist


# ------------------------------------------------------------------ accumulator
class Acc:
    def __init__(self):
        self.o = defaultdict(Counter)
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


def rate(acc, key, outcome="y", raw=False):
    c = acc.o.get(key, Counter())
    n = c["n"]
    if raw:
        return (c[outcome] / float(n)) if n else None, n
    if not n:
        return "n/a (0)"
    return "%.2f (%d/%d%s)" % (c[outcome] / float(n), c[outcome], n, "*" if n < 30 else "")


def mix(acc, key):
    c = acc.o.get(key, Counter())
    n = c["n"]
    if not n:
        return "n=0"
    parts = ["%s %.2f" % (a[0].upper(), c[a] / float(n)) for a in ACTS if c[a]]
    return "%s n=%d%s" % (" ".join(parts), n, "*" if n < 30 else "")


def fcr(acc, key):
    """(fold, call, raise, n) shares of one opportunity."""
    c = acc.o.get(key, Counter())
    n = c["n"]
    if not n:
        return (None, None, None, 0)
    return (c["fold"] / float(n), c["call"] / float(n), c["raise"] / float(n), n)


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else float("nan")


def dist(xs, k=4, fmt="%g"):
    if not xs:
        return "none"
    c = Counter(xs).most_common(k)
    return ", ".join((fmt % (v,)) + " %.0f%%" % (100.0 * m / len(xs)) for v, m in c) + " (n=%d)" % len(xs)


# ------------------------------------------------------------------ per seat stats (port)
def seat_hand(A, h, s, n, acts, la, me):
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
    elif hole and any(a["act"] == "raise" and a["allin"] for a in pre):
        A.l["shove_all"].append(combo(hole))
    pre_all = [a for a in acts if a["street"] == "preflop"]
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
                    if shown:
                        A.l["open_shown"].append(combo(hole))
                        A.l["osz_shown_%g" % bb].append(combo(hole))
            else:
                A.out("limped", f["act"])
                if f["act"] == "raise":
                    A.l["iso"].append((f["limpers"], round(f["amt"] / float(BB), 2)))
            A.hit("limp", f["act"] == "call")
        if f["raises"] == 0 and pos == "BB" and f["limpers"] > 0:          # extra: big blind option
            A.out("bb_option", f["act"])
            if f["act"] == "raise":
                A.l["bb_iso"].append((f["limpers"], round(f["amt"] / float(BB), 2)))
        seen = set()
        for a in pre:
            lv = a["raises"]
            if lv == 0 or lv in seen:
                continue
            seen.add(lv)
            raisers = [x for x in pre_all if x["act"] == "raise" and x["i"] < a["i"]]
            before = [x for x in pre if x["i"] < a["i"]]
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
                    side = "OOP" if pos in ("SB", "BB") else "IP"
                    A.l["3b_mult_" + side].append(round(a["amt"] / float(a["cur"]), 2))
                    A.l["3b_pair_" + side].append((round(a["cur"] / float(BB), 2), round(a["amt"] / float(BB), 2)))
                    if shown:
                        A.l["3b_shown"].append(combo(hole))
                elif a["act"] == "call" and shown:
                    A.l["cc_shown_" + ("BB" if pos == "BB" else "other")].append(combo(hole))
                steal = pos in ("SB", "BB") and a["callers"] == 0 and a["limpers"] == 0 and opos in ("CO", "BTN", "SB")
                if steal:
                    ob = op["amt"] / float(BB)
                    A.out("bd", a["act"])
                    A.out("bd_" + open_bucket(ob), a["act"])
                    if op["seat"] == me:
                        A.out("bd_us", a["act"])
                if op["seat"] == me and a["callers"] == 0:
                    A.out("vs_our_open", a["act"])
                # extra: the replica's own spot types
                if before:                                    # limped (or completed) first
                    A.out("x_limp_raised", a["act"])
                elif a["callers"] >= 1:
                    A.out("x_sq", a["act"])
                elif steal:
                    A.out("x_bd", a["act"])
                elif pos in ("SB", "BB"):
                    A.out("x_vs1_blind", a["act"])
                else:
                    A.out("x_vs1_cold", a["act"])
                if not before:
                    spot = "sq" if a["callers"] >= 1 else ("steal" if steal else "open")
                    grp = pos if pos in ("SB", "BB") else "IP"
                    A.out("x_v1_%s_%s" % (spot, grp), a["act"])
                    if grp == "IP":
                        A.out("x_v1_%s_%s" % (spot, pos), a["act"])
                    if steal:
                        A.out("x_v1_steal_%s_%s" % (pos, open_bucket(op["amt"] / float(BB))), a["act"])
                    A.out("x_vs1_first", a["act"])
                    A.out("x_tb_own_" + pos, a["act"])
                    A.out("x_tb_op_" + opos, a["act"])
                    A.out("x_vs1_open_" + ("<=3" if op["amt"] <= 3 * BB else "<=4" if op["amt"] <= 4 * BB else
                                           "<=7" if op["amt"] <= 7 * BB else ">7"), a["act"])
            elif lv == 2:
                A.out("vs2", a["act"])
                if a["act"] == "raise":
                    A.l["4b_mult"].append(round(a["amt"] / float(a["cur"]), 2))
                    A.hit("4b_allin", a["allin"])
                    if shown:
                        A.l["4b_shown"].append(combo(hole))
                if any(x["act"] == "raise" and x["raises"] == 0 for x in pre):
                    A.out("f3b", a["act"])
                    if raisers[-1]["seat"] == me:
                        A.out("f3b_us", a["act"])
                elif not before:
                    A.out("x_cold3", a["act"])
                else:
                    A.out("x_call_then_3b", a["act"])
            elif lv == 3:
                A.out("vs3", a["act"])
                if a["act"] == "raise":
                    A.hit("5b_allin", a["allin"])
                    A.l["5b_mult"].append(round(a["amt"] / float(a["cur"]), 2))
                if any(x["act"] == "raise" and x["raises"] == 1 for x in pre):
                    A.out("f4b", a["act"])
                    A.out("f4b_" + ("shove" if a["to_call"] >= 800 else "small"), a["act"])
                elif not before:
                    A.out("x_cold4", a["act"])
            elif lv >= 4:
                A.out("vs4", a["act"])
                if any(x["act"] == "raise" and x["raises"] == lv - 2 for x in pre):
                    A.out("x_f5b", a["act"])
    # postflop
    flop = board[:3]
    tex = texture(flop) if len(flop) == 3 else None
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
        bd = board[:NB[street]]
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
            if first["act"] == "check":
                nxt = next((a for a in sa[1:] if a["to_call"] > 0), None)
                if nxt:
                    A.out("xr_" + street, nxt["act"])
                    if pa == s:
                        A.out("stab_after_missed_" + street, nxt["act"])
        for a in sa:
            if a["act"] == "raise":
                kind = "bet" if a["to_call"] == 0 else "raise"
                A.hit("overbet_" + kind, a["size"] > 1.0)
                A.l["all_%s_%s" % (kind, street)].append(round(a["size"], 2))
                if shown:
                    A.l["sd_%s_%s" % (kind, street)].append((bucket(a["size"]), group(hole, bd)))
                    A.l["sdx_%s_%s" % (kind, street)].append((round(a["size"], 2), group(hole, bd), a["allin"]))
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
                A.out("x_barrel2_" + b, fb["act"])
            if street == "river":
                if called_from.get("turn") == bettor and called_from.get("flop") == bettor:
                    A.out("vs_barrel3", fb["act"])
                    A.out("x_barrel3_" + b, fb["act"])
                if "turn" not in la:
                    A.out("vs_river_after_xturn", fb["act"])
            # extra: reply by whether it had checked first on this street
            checked = any(x["act"] == "check" for x in sa if x["i"] < fb["i"])
            A.out("x_fb_%s_%s" % (street, "xr" if checked else "nx"), fb["act"])
            A.out("x_fb_%s_%s_%s" % (street, "xr" if checked else "nx", b), fb["act"])
            if fb["act"] == "call":
                called_from[street] = bettor
                if shown:
                    A.l["sd_call_" + street].append(group(hole, bd))
            elif fb["act"] == "fold" and hole and not shown:
                pass
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
    # deep cuts
    for a in acts:
        if a["seat"] != s or a["act"] != "raise" or a["street"] == "preflop" or a["to_call"] != 0:
            continue
        sz = round(a["size"], 2)
        if shown:
            A.o["szsd|%s|%.2f" % (a["street"], sz)][group(hole, board[:NB[a["street"]]])] += 1
        nxt = next((x for x in acts if x["seat"] == s and x["i"] > a["i"] and x["street"] == a["street"]), None)
        if nxt is not None and nxt["to_call"] > 0:
            A.o["szr|%.2f" % sz][nxt["act"]] += 1
            A.o["szr_%s|%.2f" % (a["street"], sz)][nxt["act"]] += 1
        if a["street"] == "flop":
            A.l["sztex|%s|%s" % (texture(board[:3]), "HU" if a["live"] == 2 else "MW")].append(sz)
    return pos


def extra_hand(A, h, s, n, acts, la, hist, sim):
    """Cuts by the replica's own lines and nodes (base.post_ctx); with `sim` (all hole cards known)
    also the class mix of every node."""
    hole = h["hole"].get(str(s))
    board = h["board"]
    shown = str(s) in h["showdown"] and hole is not None
    start = {}
    for a in acts:
        if a["street"] != "preflop" and a["street"] not in start:
            start[a["street"]] = a["live"]
    seen = set()
    mine = [a for a in acts if a["seat"] == s and a["street"] != "preflop"]
    for j, a in enumerate(mine):
        street = a["street"]
        hu = start[street] == 2
        m = "hu" if hu else "mw"
        ctx = base.post_ctx(hist[:a["hl"]], s, street)
        cls = base.classify(hole, board[:NB[street]]) if (sim and hole) else None
        if a["to_call"] == 0:
            role = ctx["role"]
            A.out("x_bet_%s_%s_%s" % (street, role, m), a["act"])
            A.out("x_bet_%s_%s" % (street, m), a["act"])
            if a["act"] == "raise":
                nxt = mine[j + 1] if j + 1 < len(mine) and mine[j + 1]["street"] == street else None
                reply = nxt["act"] if nxt is not None and nxt["to_call"] > 0 else None
                A.l["bets"].append((street, role, m, round(a["size"], 4), a["amt"], a["allin"],
                                    group(hole, board[:NB[street]]) if shown else None,
                                    a["stack"] / float(max(1, a["pot"])), reply))
            if cls is not None:
                A.o["node|B|%s|%s" % (street, role)][cls] += 1
                A.o["node|B|%s|%s|%s" % (street, role, m)][cls] += 1
        elif ctx["my_raises"] == 0 and a["raises"] == 1 and street not in seen:
            seen.add(street)
            A.out("x_cell_" + ctx["node"], a["act"])
            A.out("x_cell_%s_%s" % (ctx["node"], m), a["act"])
            if cls is not None:
                A.o["node|F|%s|%s" % (street, ctx["node"])][cls] += 1
                A.o["node|F|%s|%s|%s" % (street, ctx["node"], m)][cls] += 1
        if a["act"] == "raise" and a["to_call"] > 0:
            A.hit("x_raise_allin_" + street, a["allin"])
            A.l["raises"].append((street, round(a["size"], 2), a["allin"],
                                  group(hole, board[:NB[street]]) if shown else None))


# ------------------------------------------------------------------ profile text (port)
def show_profile(name, A, extra=""):
    h = A.v["hands"]
    P = print
    P("\n### %s  hands=%d  bb/100=%+.1f %s" % (name, h, A.v["chips"] / h * 5 if h else 0, extra))
    P("VPIP %s | PFR %s | limp (first action unopened, not BB) %s" % (rate(A, "vpip"), rate(A, "pfr"), rate(A, "limp")))
    P("first in (no limpers): %s" % mix(A, "fi"))
    for p in POSS[:-1]:
        if A.o.get("fi_" + p):
            P("  fi %-5s %s  raise %s  open sizes %s" % (p, mix(A, "fi_" + p), rate(A, "fi_" + p, "raise"),
                                                         dist(A.l["osz_" + p])))
    P("all open sizes: %s" % dist(A.l["osz"]))
    P("facing limpers first action: %s; iso (limpers, bb): %s" % (mix(A, "limped"), dist(A.l["iso"], 6, "%s")))
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
                P("  %s %s: %s" % (kind, st, "; ".join("%s %s" % (b, dict(byb[b])) for b in BUCKETS if b in byb)))
    for st in ("flop", "turn", "river"):
        if A.l["sd_call_" + st]:
            P("  called a %s bet then showed: %s" % (st, dict(Counter(A.l["sd_call_" + st]))))
    P("-- defender")
    for st in ("flop", "turn", "river"):
        P("vs bet %s: %s | HU %s | MW %s" % (st, mix(A, "fb_" + st), mix(A, "fb_%s_hu" % st), mix(A, "fb_%s_mw" % st)))
        P("   by size: " + "; ".join("%s %s" % (b, mix(A, "fb_%s_%s" % (st, b))) for b in BUCKETS))
    P("vs bet all streets by size: " + "; ".join("%s %s" % (b, mix(A, "fb_all_" + b)) for b in BUCKETS))
    P("vs OUR bets: flop %s | turn %s | river %s" % (mix(A, "fb_us_flop"), mix(A, "fb_us_turn"), mix(A, "fb_us_river")))
    P("vs OUR bets by size: " + "; ".join("%s %s" % (b, mix(A, "fb_us_all_" + b)) for b in BUCKETS))
    P("vs raise after their bet: %s (F %s T %s R %s)" % (
        mix(A, "vs_raise_after_bet"), mix(A, "vs_raise_after_bet_flop"), mix(A, "vs_raise_after_bet_turn"),
        mix(A, "vs_raise_after_bet_river")))
    P("vs second barrel (called flop, same bettor turn): %s | vs third barrel: %s | vs river bet after checked turn: %s" % (
        mix(A, "vs_barrel2"), mix(A, "vs_barrel3"), mix(A, "vs_river_after_xturn")))
    P("-- showdown: WTSD (of hands seeing a flop) %s | won at showdown %s" % (rate(A, "wtsd"), rate(A, "wsd")))
    P("  flop bet size by texture and HU/MW:")
    for k in sorted(A.l):
        if k.startswith("sztex|"):
            P("    %-24s %s" % (k[6:].replace("|", " "), dist(A.l[k], 4)))
    P("  showdown class by street and exact bet size (sizes with >=4 shown):")
    for k in sorted(A.o):
        if k.startswith("szsd|") and sum(A.o[k].values()) >= 4:
            _, st, sz = k.split("|")
            P("    %-6s %s pot: %s (n=%d)" % (st, sz, dict(A.o[k]), sum(A.o[k].values())))
    P("  reply when raised after betting, by exact bet size: " + "; ".join(
        "%s %s" % (k[4:], dict(A.o[k])) for k in sorted(A.o) if k.startswith("szr|") and sum(A.o[k].values()) >= 3))


def show_extra(name, A):
    P = print
    P("\n=== extra cuts: %s" % name)
    P("limped then raised: %s | BB option vs limpers: %s iso %s" % (mix(A, "x_limp_raised"), mix(A, "bb_option"),
                                                                     dist(A.l["bb_iso"], 4, "%s")))
    P("vs one raise, first action: all %s | squeeze %s | blind vs steal %s | blind vs earlier open %s | cold (not blind) %s" % (
        mix(A, "x_vs1_first"), mix(A, "x_sq"), mix(A, "x_bd"), mix(A, "x_vs1_blind"), mix(A, "x_vs1_cold")))
    P("  3-bet first action by own pos: " + "; ".join("%s %s" % (p, rate(A, "x_tb_own_" + p, "raise")) for p in POSS if A.o.get("x_tb_own_" + p)))
    P("  3-bet first action by opener pos: " + "; ".join("%s %s" % (p, rate(A, "x_tb_op_" + p, "raise")) for p in POSS if A.o.get("x_tb_op_" + p)))
    P("  by open size: " + "; ".join("%s %s" % (b, mix(A, "x_vs1_open_" + b)) for b in ("<=3", "<=4", "<=7", ">7")))
    P("  3-bet mult IP %s | OOP %s" % (dist(A.l["3b_mult_IP"], 6), dist(A.l["3b_mult_OOP"], 6)))
    P("  3-bet (open, 3-bet) IP %s | OOP %s" % (dist(A.l["3b_pair_IP"], 8, "%s"), dist(A.l["3b_pair_OOP"], 8, "%s")))
    P("vs 3-bet: after opening %s | cold %s | after calling %s | 4-bet all-in %s mult %s" % (
        mix(A, "f3b"), mix(A, "x_cold3"), mix(A, "x_call_then_3b"), rate(A, "4b_allin"), dist(A.l["4b_mult"], 6)))
    P("vs 4-bet: after 3-betting %s (4-bet small %s, shove %s) | cold %s | 5-bet all-in %s mult %s | vs 5-bet after 4-betting %s" % (
        mix(A, "f4b"), mix(A, "f4b_small"), mix(A, "f4b_shove"), mix(A, "x_cold4"), rate(A, "5b_allin"),
        dist(A.l["5b_mult"], 4), mix(A, "x_f5b")))
    P("shove hands (all known): %s" % dist(A.l["shove_all"] + A.l["shove_shown"], 14, "%s"))
    for st in ("flop", "turn", "river"):
        P("%s bet by line: " % st + " | ".join("%s_%s %s" % (r, m, rate(A, "x_bet_%s_%s_%s" % (st, r, m), "raise"))
                                                 for r in "ADSL" for m in ("hu", "mw")))
        bets = [b for b in A.l["bets"] if b[0] == st]
        for r in "ADSL":
            for m in ("hu", "mw"):
                xs = [round(b[3], 2) for b in bets if b[1] == r and b[2] == m]
                if len(xs) >= 8:
                    P("    sizes %s_%s: %s" % (r, m, dist(xs, 8)))
        P("  all %s bet sizes: %s" % (st, dist(A.l["all_bet_" + st], 14)))
        rs = [x for x in A.l["raises"] if x[0] == st]
        P("  %s raise sizes: %s | all-in %d of %d" % (st, dist([x[1] for x in rs if not x[2]], 10),
                                                      sum(1 for x in rs if x[2]), len(rs)))
        by = defaultdict(Counter)
        for _, sz, ai, g in rs:
            if g:
                by[bucket(sz) + (" allin" if ai else "")][g] += 1
        if by:
            P("  %s raises shown: %s" % (st, "; ".join("%s %s" % (k, dict(v)) for k, v in sorted(by.items()))))
        P("  %s facing a bet by node: " % st + " | ".join(
            "%s %s (hu %s; mw %s)" % (k[7:], mix(A, k), mix(A, k + "_hu"), mix(A, k + "_mw"))
            for k in sorted(A.o) if k.startswith("x_cell_" + st) and not k.endswith(("_hu", "_mw"))))
        P("  %s facing a bet, not having checked: %s; by size %s" % (st, mix(A, "x_fb_%s_nx" % st), "; ".join(
            "%s %s" % (b, mix(A, "x_fb_%s_nx_%s" % (st, b))) for b in BUCKETS)))
        P("  %s facing a bet after checking: %s; by size %s" % (st, mix(A, "x_fb_%s_xr" % st), "; ".join(
            "%s %s" % (b, mix(A, "x_fb_%s_xr_%s" % (st, b))) for b in BUCKETS)))
        low = [b for b in bets if b[7] <= 2.5]
        P("  %s bets with stack/pot <= 2.5: n=%d all-in %d | deeper: n=%d all-in %d sizes %s" % (
            st, len(low), sum(1 for b in low if b[5]), len(bets) - len(low),
            sum(1 for b in bets if b[5] and b[7] > 2.5), dist([round(b[3], 1) for b in bets if b[5] and b[7] > 2.5], 6)))
    P("reply when raised after betting by street and size: " + "; ".join(
        "%s %s" % (k[4:], dict(A.o[k])) for k in sorted(A.o) if k.startswith("szr_") and sum(A.o[k].values()) >= 3))


# ------------------------------------------------------------------ loading
def real_rounds(last_third=False):
    paths = sorted(glob.glob(os.path.join(ROOT, "hands", "saturday_r0*.json")))
    rounds = [json.load(open(p)) for p in paths]
    if not last_third:
        return rounds, None
    keep = {}
    for _, team in TEAMS:
        refs = [d["ref"] for d in rounds if team in d["players"]]
        k = len(refs)
        first = refs[:k // 3 + (1 if k % 3 > 0 else 0)]
        rest = refs[len(first):]
        keep[team] = set(rest[(len(rest) + 1) // 2:])
    return rounds, keep


def measure_real(last_third=False):
    rounds, keep = real_rounds(last_third)
    accs = dict((short, Acc()) for short, _ in TEAMS)
    for d in rounds:
        n = len(d["players"])
        me = d["seat"]
        seats = [(s, SHORT[t]) for s, t in enumerate(d["players"]) if t in SHORT and s != me
                 and (keep is None or d["ref"] in keep[t])]
        if not seats:
            continue
        for h in d["hands"]:
            acts, la, hist = replay(h, n)
            for s, short in seats:
                seat_hand(accs[short], h, s, n, acts, la, me)
                extra_hand(accs[short], h, s, n, acts, la, hist, False)
    return accs


def measure_sim(dirs):
    accs = defaultdict(Acc)
    files = []
    for d in dirs:
        files += sorted(glob.glob(os.path.join(d, "*.json"))) if os.path.isdir(d) else [d]
    for f in files:
        d = json.load(open(f))
        n = len(d["players"])
        me = d.get("seat", -1)
        for h in d["hands"]:
            acts, la, hist = replay(h, n)
            for s, name in enumerate(d["players"]):
                seat_hand(accs[name], h, s, n, acts, la, me)
                extra_hand(accs[name], h, s, n, acts, la, hist, True)
    return accs, len(files)


def write_nodes(accs, path):
    out = {}
    for name, A in sorted(accs.items()):
        if name not in dict(TEAMS):
            continue
        out[name] = dict((k[5:], [A.o[k][c] for c in range(base.K)]) for k in sorted(A.o) if k.startswith("node|"))
    with open(path, "w") as fh:
        fh.write('"""Class mix of each replica\'s own range at every postflop node, counted in self-play by\n'
                 'tabled/measure.py --nodes and then frozen.  Order: air (low), air (ace high or two overcards),\n'
                 'draw, weak pair, top pair or overpair, two pair or better.  B|street|line: nothing to call\n'
                 '(A c-bet/barrel, D donk, S checked to, L lead).  F|street|node: facing a single bet.\n'
                 'A trailing |hu or |mw: the same node heads up or multiway only."""\n')
        fh.write("NODES = {\n")
        for name in out:
            fh.write("    %r: {\n" % name)
            for k, v in out[name].items():
                fh.write("        %r: %r,\n" % (k, v))
            fh.write("    },\n")
        fh.write("}\n")
    return out


# ------------------------------------------------------------------ calibration table
def tp_share(A, street_sizes):
    """Share of top pair or better among hands shown down after a bet of one of the sizes."""
    c = Counter()
    for st, sizes in street_sizes:
        for k in A.o:
            if k.startswith("szsd|%s|" % st) and any(abs(float(k.split("|")[2]) - z) <= 0.011 for z in sizes):
                c.update(A.o[k])
    n = sum(c.values())
    return ((c["medium"] + c["value"]) / float(n)) if n else None, n


def raised_fold(A, sizes):
    c = Counter()
    for k in A.o:
        if k.startswith("szr|") and any(abs(float(k[4:]) - z) <= 0.011 for z in sizes):
            c.update(A.o[k])
    n = sum(c.values())
    return (c["fold"] / float(n)) if n else None, n


def size_share(A, street, sizes):
    xs = A.l["all_bet_" + street]
    if not xs:
        return None
    return sum(1 for x in xs if any(abs(x - z) <= 0.011 for z in sizes)) / float(len(xs))


# bluff size(s), value size(s), main sizes reported per street
SIZES = {
    "anker": dict(bluff=(1.1,), value=(0.4,), main=((1.1,), (2.0,), (0.7,), (0.4,), (0.62, 0.61))),
    "cpf": dict(bluff=(0.33, 0.32), value=(1.0,), main=((0.33, 0.32), (1.0,))),
    "wbot": dict(bluff=(0.15, 0.14, 0.16), value=(3.0,), main=((0.15, 0.14, 0.16), (0.75,), (1.0,), (3.0,))),
    "gg": dict(bluff=(0.5,), value=(1.0,), main=((0.5,), (1.0,))),
    "poke": dict(bluff=(0.8,), value=(1.6,), main=((0.33, 0.32), (0.8,), (1.6,), (0.55,), (1.1,))),
    "anton": dict(bluff=(0.55, 0.8), value=(0.6,), main=((0.55,), (0.8,), (0.33,), (0.6,), (1.1,))),
    "ysl": dict(bluff=(0.48,), value=(0.77, 0.76), main=((0.48,), (0.77, 0.76), (0.42,), (0.38, 0.37))),
}


def pc(x):
    return " n/a" if x is None else "%3.0f" % (100 * x)


def rows(A, short):
    S = SIZES[short]
    r = []
    r.append(("VPIP", rate(A, "vpip", raw=True)[0]))
    r.append(("PFR", rate(A, "pfr", raw=True)[0]))
    r.append(("limp", rate(A, "limp", raw=True)[0]))
    r.append(("3-bet", rate(A, "vs1", "raise", raw=True)[0]))
    r.append(("fold to 3-bet", rate(A, "f3b", "fold", raw=True)[0]))
    r.append(("c-bet HU", rate(A, "cbet_flop_hu", "raise", raw=True)[0]))
    for st in ("flop", "turn", "river"):
        for sz in S["main"]:
            r.append(("%s %.2f" % (st, sz[0]), size_share(A, st, sz)))
    allst = [("flop", S["bluff"]), ("turn", S["bluff"]), ("river", S["bluff"])]
    r.append(("TP+ shown after bluff size %s" % (S["bluff"][0],), tp_share(A, allst)[0]))
    allst = [("flop", S["value"]), ("turn", S["value"]), ("river", S["value"])]
    r.append(("TP+ shown after value size %s" % (S["value"][0],), tp_share(A, allst)[0]))
    r.append(("fold when raised after bluff size", raised_fold(A, S["bluff"])[0]))
    r.append(("fold vs 40-75%", rate(A, "fb_all_40-75%", "fold", raw=True)[0]))
    r.append(("fold vs 75-110%", rate(A, "fb_all_75-110%", "fold", raw=True)[0]))
    r.append(("fold to 3rd barrel", rate(A, "vs_barrel3", "fold", raw=True)[0]))
    return r


def table(real, sim):
    for short, team in TEAMS:
        if short not in sim:
            continue
        print("\n%s (%s): real / replica" % (team, short))
        a, b = rows(real[short], short), rows(sim[short], short)
        line = []
        for (k, x), (_, y) in zip(a, b):
            flag = "!" if (x is not None and y is not None and abs(x - y) > 0.10) else ""
            line.append("%s %s/%s%s" % (k, pc(x).strip(), pc(y).strip(), flag))
        print("  " + " | ".join(line))


def selftest():
    import random
    deck = [r + s for r in RANKS for s in "cdhs"]
    rng = random.Random(5)
    bad = 0
    names = ("air", "air", "draw", "weak", "medium", "value")
    for _ in range(60000):
        cs = rng.sample(deck, 7)
        nb = rng.choice((3, 4, 5))
        a = names[base.classify(cs[:2], cs[2:2 + nb])]
        b = group(cs[:2], cs[2:2 + nb])
        if a != b:
            bad += 1
            if bad < 5:
                print("MISMATCH", cs[:2], cs[2:2 + nb], a, b)
    print("classifier check against the profile's definition: %d mismatches in 60000" % bad)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opt = set(a for a in sys.argv[1:] if a.startswith("--"))
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
        args = [a for a in args if a != only]
    if not args or args[0] == "selftest":
        selftest()
        return
    mode = args[0]
    if mode == "real":
        accs = measure_real("--last" in opt)
        for short, team in TEAMS:
            if only and only != short:
                continue
            if "--profile" in opt:
                show_profile(team, accs[short])
            if "--extra" in opt or "--profile" not in opt:
                show_extra(team, accs[short])
        return
    accs, nf = measure_sim(args[1:])
    print("# %d round files" % nf)
    if "--nodes" in opt:
        write_nodes(accs, os.path.join(HERE, "_nodes.py"))
        print("# wrote tabled/_nodes.py")
    for name in sorted(accs):
        if only and only != name:
            continue
        if "--profile" in opt:
            show_profile(name, accs[name])
        if "--extra" in opt:
            show_extra(name, accs[name])
    if "--table" in opt:
        table(measure_real(False), accs)
    print("\n%-10s %7s %7s" % ("seat", "hands", "bb/100"))
    for name in sorted(accs, key=lambda k: -accs[k].v["chips"] / max(1, accs[k].v["hands"])):
        A = accs[name]
        print("%-10s %7d %+7.1f" % (name, A.v["hands"], A.v["chips"] / max(1, A.v["hands"]) * 5))


if __name__ == "__main__":
    main()
