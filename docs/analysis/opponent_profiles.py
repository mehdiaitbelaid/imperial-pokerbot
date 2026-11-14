"""Profile every team at our counted tables, our own bot by version, and archetypes.

    python3 review/opponent_profiles.py            # all sections
    python3 review/opponent_profiles.py --check    # also print the hands used for hand checks

Reads hands-data/hands/saturday_r[0-9]*.json (counted rounds only). Stdlib only.
Builds on live_diagnosis.py (card classes, positions, loss buckets).
Rates print as k/n; n under 30 is marked * (unreliable).
Money flow between two seats in one hand: every loser's loss is split across that
hand's winners in proportion to what they won, so our flows sum to our result.
"""
import glob
import json
import os
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_diagnosis import made_class, pos_name, bucket_of, combo, TOP5PCT  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
HANDS = os.path.join(HERE, "..", "hands-data", "hands")
US = "Resonance Qt"
BB = 20
ABOVE = ["Attention Is All In", "Gherkers", "Equity Engine", "AAST", "ND", "The Market Makers"]
STRONG = {"Two Pair", "Trips/Set", "Straight", "Flush", "Full House", "Four of a Kind",
          "Straight Flush"}
ONEPAIR = {"Overpair", "Top Pair", "Weak Pair"}


def replay(h, n):
    """Annotate every action: street, to_call, pot before it, raises, limpers, current bet,
    stack before, all in flag, faced bet as a share of the pot before that bet."""
    acts = []
    street = "preflop"
    sb = defaultdict(int)
    put = defaultdict(int)
    cur = 0
    raises = 0
    limpers = 0
    folded = set()
    last_aggr = {}
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
            cur = 0
            raises = 0
        elif k == "refund":
            put[e[1]] -= e[2]
        elif k == "act":
            s, a, amt = e[1], e[2], e[3]
            pot = sum(put.values())
            to_call = cur - sb[s]
            rec = {"seat": s, "street": street, "act": a, "amt": amt, "to_call": to_call,
                   "pot": pot, "raises": raises, "limpers": limpers, "cur": cur,
                   "put_before": put[s], "live": n - len(folded),
                   "face": to_call / float(max(1, pot - to_call)) if to_call > 0 else 0.0,
                   "allin": False}
            if a == "raise":
                add = amt - sb[s]
                rec["size"] = (amt - cur) / float(max(1, pot + to_call))
                sb[s] = amt
                put[s] += add
                cur = amt
                raises += 1
                last_aggr[street] = s
            elif a == "call":
                sb[s] += amt
                put[s] += amt
                if street == "preflop" and raises == 0:
                    limpers += 1
            elif a == "fold":
                folded.add(s)
            if a in ("raise", "call") and put[s] >= start[s]:
                rec["allin"] = True
            acts.append(rec)
    return acts, last_aggr, folded, put


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
            out[j] = -r * res[seat] / win
        elif res[seat] < 0 and r > 0:
            out[j] = res[seat] * r / win
    return out


def size_bin(x):
    return "small<40%" if x < 0.4 else ("mid40-75%" if x <= 0.75 else "big>75%")


def accumulate(st, h, seat, n, acts, last_aggr):
    """Per seat counters for one hand. st is a defaultdict(float) with list values for sizes."""
    rel = (seat - h["button"]) % n
    pos = pos_name(rel, n)
    res = h["results"][seat]
    st["hands"] += 1
    st["chips"] += res
    st["pos_n_" + pos] += 1
    st["pos_c_" + pos] += res
    mine = [a for a in acts if a["seat"] == seat]
    pre = [a for a in mine if a["street"] == "preflop"]
    vol = any(a["act"] in ("call", "raise") for a in pre)
    if vol:
        st["vpip"] += 1
    if any(a["act"] == "raise" for a in pre):
        st["pfr"] += 1
    if any(a["act"] == "raise" and a["allin"] for a in pre):
        st["shove_pre"] += 1
    if any(a["act"] == "raise" and a["allin"] for a in mine):
        st["shove_any"] += 1
    if pre:
        f = pre[0]
        if f["raises"] == 0:
            if pos != "BB":
                st["limp_opp"] += 1
                if f["act"] == "call":
                    st["limp"] += 1
            if f["limpers"] == 0:
                st["fi_opp"] += 1
                st["fi_opp_" + pos] += 1
                if f["act"] == "raise":
                    st["fi_" + pos] += 1
                    st["fi_chips_" + pos] += res
                    st["open_bb"].append(round(f["amt"] / float(BB), 2))
                    if f["allin"]:
                        st["open_shove"] += 1
            elif f["act"] == "raise":
                st["iso_sz"].append((f["limpers"], round(f["amt"] / float(BB), 2)))
    # 3-bet, 4-bet: first action facing exactly one or two raises
    for need, key in ((1, "3b"), (2, "4b")):
        a = next((x for x in pre if x["raises"] == need), None)
        if a:
            st[key + "_opp"] += 1
            if a["act"] == "raise":
                st[key] += 1
                st[key + "_mult"].append(round(a["amt"] / float(max(1, a["cur"])), 2))
    opened = next((a for a in pre if a["act"] == "raise" and a["raises"] == 0), None)
    if opened:
        after = [a for a in pre if acts.index(a) > acts.index(opened)]
        if after and after[0]["raises"] >= 2:
            st["f3b_opp"] += 1
            if after[0]["act"] == "fold":
                st["f3b"] += 1
    # blind defence against a first-in steal from CO, BTN or SB with no callers
    if pos in ("SB", "BB") and pre:
        a = pre[0]
        if a["raises"] == 1 and a["limpers"] == 0:
            pa = [x for x in acts if x["street"] == "preflop" and acts.index(x) < acts.index(a)]
            opener = next((x for x in pa if x["act"] == "raise"), None)
            callers = [x for x in pa if x["act"] == "call" and acts.index(x) > acts.index(opener)] if opener else []
            if opener and not callers and pos_name((opener["seat"] - h["button"]) % n, n) in ("CO", "BTN", "SB"):
                st["bd_opp"] += 1
                st["bd_" + a["act"]] += 1
    # postflop
    pfa = last_aggr.get("preflop") == seat
    for street in ("flop", "turn", "river"):
        sa = [a for a in mine if a["street"] == street]
        if not sa:
            continue
        st["saw_" + street] += 1
        first = sa[0]
        if first["to_call"] == 0:
            st["bopp_" + street] += 1
            if first["act"] == "raise":
                st["bet_" + street] += 1
                st["bsz_" + street].append(first["size"])
            if street == "flop" and pfa:
                st["cb_opp"] += 1
                if first["act"] == "raise":
                    st["cb"] += 1
                    st["cbsz"].append(first["size"])
        face = next((a for a in sa if a["to_call"] > 0), None)
        if face:
            b = size_bin(face["face"])
            st["fb_opp_" + street] += 1
            st["fb_opp_%s_%s" % (street, b)] += 1
            if face["act"] == "fold":
                st["fb_" + street] += 1
                st["fb_%s_%s" % (street, b)] += 1
            elif face["act"] == "raise":
                st["rb_" + street] += 1
        # facing a raise after our own bet on this street
        bi = next((i for i, a in enumerate(sa) if a["act"] == "raise"), None)
        if bi is not None and bi + 1 < len(sa) and sa[bi + 1]["to_call"] > 0:
            st["fr_opp"] += 1
            if sa[bi + 1]["act"] == "fold":
                st["fr"] += 1
    if any(a["street"] != "preflop" for a in mine):
        st["saw_any"] += 1
    sd = str(seat) in h["showdown"]
    if sd:
        st["sd"] += 1
        if res > 0:
            st["sdwon"] += 1
        cls = made_class(h["hole"][str(seat)], h["board"]) if str(seat) in h["hole"] else "unknown"
        big = [a for a in mine if a["street"] in ("turn", "river") and a["act"] == "raise"
               and a.get("size", 0) >= 0.66]
        if big:
            st["show_big"].append(cls)
        if any(a["street"] != "preflop" and a["act"] == "raise" and a["raises"] >= 1 for a in mine):
            st["show_raise"].append(cls)
    return pos


def new():
    st = defaultdict(float)
    for k in ("open_bb", "iso_sz", "3b_mult", "4b_mult", "bsz_flop", "bsz_turn", "bsz_river",
              "cbsz", "show_big", "show_raise"):
        st[k] = []
    return st


def r(st, k, n):
    a, b = st[k], st[n]
    if not b:
        return "n/a (0)"
    return "%.2f (%d/%d%s)" % (a / b, a, b, "*" if b < 30 else "")


def rr(st, k, n):
    b = st[n]
    return st[k] / b if b else None


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else float("nan")


def size_habit(xs):
    """Most common open sizes, as share of opens."""
    if not xs:
        return "none"
    c = Counter(xs).most_common(3)
    return ", ".join("%gbb %.0f%%" % (v, 100.0 * k / len(xs)) for v, k in c) + " (n=%d)" % len(xs)


def load_rounds():
    paths = sorted(p for p in glob.glob(os.path.join(HANDS, "saturday_r[0-9]*.json")))
    return [json.load(open(p)) for p in paths]


def main():
    check = "--check" in sys.argv
    rounds = load_rounds()
    team = defaultdict(new)          # every non-us seat, by team
    ver = defaultdict(new)           # us, by version
    flow = defaultdict(float)        # chips team -> us
    together = defaultdict(int)      # hands seated with us
    team_rounds = defaultdict(list)
    bucket = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    ended = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    ver_hands = Counter()
    ver_rounds = defaultdict(list)
    site_total = Counter()
    # extra us-only measurements
    commit = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))   # n, won, chips, gain from folding
    riv_chk = defaultdict(lambda: defaultdict(lambda: [0, 0, 0.0]))   # n, won, pot chips
    ep_open = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    prem_fold = defaultdict(list)
    flop_def = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for d in rounds:
        me = d["seat"]
        v = d["round"]["version"]
        n = len(d["players"])
        ver_hands[v] += len(d["hands"])
        ver_rounds[v].append(d["ref"])
        site_total[v] += d["round"]["chips"]
        for name in set(d["players"]) - {US}:
            team_rounds[name].append(d["ref"].split("/")[1])
        for h in d["hands"]:
            acts, la, folded, put = replay(h, n)
            for s, name in enumerate(d["players"]):
                if s == me:
                    pos = accumulate(ver[v], h, s, n, acts, la)
                else:
                    accumulate(team[name], h, s, n, acts, la)
                    together[name] += 1
            for j, c in flows(h, me).items():
                flow[d["players"][j]] += c
            b = bucket_of(h, me, acts, la)
            bucket[v][b][0] += 1
            bucket[v][b][1] += h["results"][me]
            last = acts[-1]["street"] if acts else "preflop"
            ended[v][last][0] += 1
            ended[v][last][1] += h["results"][me]
            hole = h["hole"][str(me)]
            cls_hand = combo(hole)
            mine = [a for a in acts if a["seat"] == me]
            # commit calls: a call that takes our total past 30 bb
            for a in mine:
                if a["act"] == "call" and a["street"] != "preflop" and a["put_before"] < 600 <= a["put_before"] + a["amt"]:
                    board = h["board"][:{"flop": 3, "turn": 4, "river": 5}[a["street"]]]
                    mc = made_class(hole, board)
                    grp = "one pair or less" if (mc in ONEPAIR or mc == "No made hand") else "two pair or better"
                    c = commit[v][grp]
                    c[0] += 1
                    c[1] += h["results"][me] > 0
                    c[2] += h["results"][me]
                    c[3] += -a["put_before"] - h["results"][me]
                    break
            # river: heads up, checked to us or we act first, we check, with a made hand
            rv_ = [a for a in mine if a["street"] == "river"]
            if rv_ and rv_[0]["to_call"] == 0 and rv_[0]["live"] == 2:
                mc = made_class(hole, h["board"])
                grp = ("two pair or better" if mc in STRONG else
                       ("top pair or overpair" if mc in ("Top Pair", "Overpair") else "weak or none"))
                c = riv_chk[v][(grp, "bet" if rv_[0]["act"] == "raise" else "check")]
                c[0] += 1
                c[1] += h["results"][me] > 0
                c[2] += rv_[0]["pot"]
            # unraised first-in opens from UTG to HJ
            pre = [a for a in mine if a["street"] == "preflop"]
            if pre and pre[0]["raises"] == 0 and pre[0]["limpers"] == 0 and pre[0]["act"] == "raise" \
                    and pos in ("UTG", "UTG+1", "MP", "HJ"):
                g = "top5%" if cls_hand in TOP5PCT else "other"
                ep_open[v][g][0] += 1
                ep_open[v][g][1] += h["results"][me]
            # premium hand folded facing a bet (timeout suspect)
            for a in mine:
                if a["act"] == "fold" and a["to_call"] > 0 and a["street"] == "preflop" and cls_hand in TOP5PCT \
                        and a["to_call"] < 0.35 * (2000 - a["put_before"]):
                    prem_fold[v].append("%s#%d %s to_call %d" % (d["ref"].split("/")[1], h["n"], cls_hand, a["to_call"]))
                    break
            # flop defence after we called preflop and face one bet of 75% pot or less
            fl = [a for a in mine if a["street"] == "flop" and a["to_call"] > 0]
            if fl and la.get("preflop") != me and fl[0]["face"] <= 0.75 and fl[0]["raises"] == 1:
                mc = made_class(hole, h["board"][:3])
                g = "pair or better" if mc != "No made hand" else "no pair"
                c = flop_def[v][(g, fl[0]["act"])]
                c[0] += 1
                c[1] += h["results"][me]

    print("# rounds and hands per version (us)")
    for v in sorted(ver_hands):
        print("v%d rounds=%d hands=%d site chips=%d bb100=%.1f rounds=%s" % (
            v, len(ver_rounds[v]), ver_hands[v], site_total[v], site_total[v] / ver_hands[v] * 5,
            ",".join(x.split("/")[1] for x in ver_rounds[v])))

    def prof(name, st, extra=""):
        h = st["hands"]
        print("\n## %s  hands=%d  bb100=%.1f %s" % (name, h, st["chips"] / h * 5 if h else 0, extra))
        print("VPIP %s | PFR %s | limp %s | 3bet %s | 4bet %s | fold to 3bet %s" % (
            r(st, "vpip", "hands"), r(st, "pfr", "hands"), r(st, "limp", "limp_opp"),
            r(st, "3b", "3b_opp"), r(st, "4b", "4b_opp"), r(st, "f3b", "f3b_opp")))
        print("open sizes first in: %s" % size_habit(st["open_bb"]))
        if st["iso_sz"]:
            print("raise over limpers (limpers, bb): %s" % Counter(st["iso_sz"]).most_common(4))
        print("3bet x prior raise median %.2f (n=%d); 4bet x median %.2f (n=%d)" % (
            med(st["3b_mult"]), len(st["3b_mult"]), med(st["4b_mult"]), len(st["4b_mult"])))
        print("first in open by pos: " + " ".join(
            "%s %s" % (p, r(st, "fi_" + p, "fi_opp_" + p)) for p in ("UTG", "UTG+1", "MP", "HJ", "CO", "BTN", "SB")))
        print("blind defence vs CO/BTN/SB steal: fold %s call %s 3bet %s" % (
            r(st, "bd_fold", "bd_opp"), r(st, "bd_call", "bd_opp"), r(st, "bd_raise", "bd_opp")))
        print("cbet %s median size %.2f | turn bet when checked to %s size %.2f | river %s size %.2f" % (
            r(st, "cb", "cb_opp"), med(st["cbsz"]), r(st, "bet_turn", "bopp_turn"), med(st["bsz_turn"]),
            r(st, "bet_river", "bopp_river"), med(st["bsz_river"])))
        print("flop bet when checked to %s size %.2f" % (r(st, "bet_flop", "bopp_flop"), med(st["bsz_flop"])))
        print("fold to bet F/T/R %s / %s / %s" % (r(st, "fb_flop", "fb_opp_flop"), r(st, "fb_turn", "fb_opp_turn"),
                                                  r(st, "fb_river", "fb_opp_river")))
        print("fold to bet by size (all streets): " + " ".join(
            "%s %s" % (b, "%.2f (%d/%d%s)" % (
                sum(st["fb_%s_%s" % (s, b)] for s in ("flop", "turn", "river")) / max(1, sum(st["fb_opp_%s_%s" % (s, b)] for s in ("flop", "turn", "river"))),
                sum(st["fb_%s_%s" % (s, b)] for s in ("flop", "turn", "river")),
                sum(st["fb_opp_%s_%s" % (s, b)] for s in ("flop", "turn", "river")),
                "*" if sum(st["fb_opp_%s_%s" % (s, b)] for s in ("flop", "turn", "river")) < 30 else ""))
            for b in ("small<40%", "mid40-75%", "big>75%")))
        print("flop fold by size: " + " ".join("%s %s" % (b, r(st, "fb_flop_" + b, "fb_opp_flop_" + b))
                                                for b in ("small<40%", "mid40-75%", "big>75%")))
        print("raise vs bet F/T/R %s / %s / %s | fold to raise after betting %s" % (
            r(st, "rb_flop", "fb_opp_flop"), r(st, "rb_turn", "fb_opp_turn"), r(st, "rb_river", "fb_opp_river"),
            r(st, "fr", "fr_opp")))
        print("shove preflop per hand %s | open shove %s | any shove per hand %s" % (
            r(st, "shove_pre", "hands"), r(st, "open_shove", "fi_opp"), r(st, "shove_any", "hands")))
        print("WTSD (of hands that saw a flop) %s | won at showdown %s" % (r(st, "sd", "saw_any"), r(st, "sdwon", "sd")))
        print("shown after turn/river bet >=66%% pot: %s" % dict(Counter(st["show_big"])))
        print("shown after postflop raise: %s" % dict(Counter(st["show_raise"])))
        print("result by position (bb/100 in that seat, n): " + " ".join(
            "%s %.0f (%d)" % (p, st["pos_c_" + p] / st["pos_n_" + p] * 5, st["pos_n_" + p])
            for p in ("UTG", "UTG+1", "MP", "HJ", "CO", "BTN", "SB", "BB") if st["pos_n_" + p]))
        print("late opens CO/BTN/SB chips per open: " + " ".join(
            "%s %.2fbb (%d)" % (p, st["fi_chips_" + p] / BB / st["fi_" + p], st["fi_" + p])
            for p in ("CO", "BTN", "SB") if st["fi_" + p]))

    for v in sorted(ver_hands):
        xs = [x["round"]["bb100"] for x in rounds if x["round"]["version"] == v]
        m = sum(xs) / len(xs)
        sd = (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5 if len(xs) > 1 else float("nan")
        print("v%d per round bb/100 %s mean %.1f sd %.1f" % (v, [round(x, 1) for x in xs], m, sd))
    print("\n# PART 1: us by version")
    for v in sorted(ver):
        prof("us v%d" % v, ver[v])
        tot = sum(x[1] for x in bucket[v].values())
        print("buckets (n, bb/100 over the version's hands), total %.1f:" % (tot / ver_hands[v] * 5))
        for b, (k, c) in sorted(bucket[v].items(), key=lambda x: x[1][1]):
            print("  %-48s n=%5d %+7.1f" % (b, k, c / ver_hands[v] * 5))
        print("pot ended on street:", {s: (k, round(c / ver_hands[v] * 5, 1)) for s, (k, c) in ended[v].items()})
        print("commit calls (past 30bb, postflop) [n, won, chips, gain from folding]:", {k: x for k, x in commit[v].items()})
        print("river heads up first action to_call=0 [n, won, sum pot]:", {"%s/%s" % k: x for k, x in sorted(riv_chk[v].items())})
        print("UTG..HJ first in opens [n, chips]:", {k: (x[0], x[1], round(x[1] / BB / max(1, x[0]), 2)) for k, x in ep_open[v].items()})
        print("premium preflop folds facing a bet (<35%% stack): %d %s" % (len(prem_fold[v]), prem_fold[v][:8]))
        print("flop defence vs one bet <=75%% pot after calling pre [n, chips]:", {"%s/%s" % k: x for k, x in sorted(flop_def[v].items())})
        print("site timeouts by round:", [(x["round"]["ref"], x["round"]["timeouts"]) for x in rounds if x["round"]["version"] == v])

    print("\n# PART 2: every team at our tables (counted rounds)")
    names = sorted(team, key=lambda t: -team[t]["hands"])
    for t in names:
        prof(t, team[t], "rounds=%s flow to us=%+d chips (%+.1f bb/100 together)" % (
            ",".join(team_rounds[t]), flow[t], flow[t] / together[t] * 5))
    print("\n# flow check: sum of flows %.1f, our total %d" % (sum(flow.values()), sum(v["chips"] for v in ver.values())))

    # archetypes from seat level stats
    print("\n# archetype features (teams with >=500 hands)")
    rows = []
    for t in names:
        st = team[t]
        if st["hands"] < 500:
            continue
        f = dict(vpip=rr(st, "vpip", "hands"), pfr=rr(st, "pfr", "hands"), limp=rr(st, "limp", "limp_opp"),
                 tb=rr(st, "3b", "3b_opp"), shove=rr(st, "shove_pre", "hands"),
                 ffl=rr(st, "fb_flop", "fb_opp_flop"), cb=rr(st, "cb", "cb_opp"),
                 agg=(st["bet_turn"] + st["bet_river"]) / max(1, st["bopp_turn"] + st["bopp_river"]),
                 wtsd=rr(st, "sd", "saw_any"), tr_size=med(st["bsz_turn"] + st["bsz_river"]))
        a = archetype(f)
        rows.append((t, a, f, st["hands"]))
        print("%-26s %-18s n=%4d vpip %.2f pfr %.2f limp %.2f 3b %.2f shove %.3f foldflop %.2f cb %.2f TRagg %.2f wtsd %.2f bb100 %+.1f flow %+.1f" % (
            t, a, st["hands"], f["vpip"], f["pfr"], f["limp"] or 0, f["tb"] or 0, f["shove"], f["ffl"] or 0, f["cb"] or 0,
            f["agg"], f["wtsd"] or 0, st["chips"] / st["hands"] * 5, flow[t] / together[t] * 5))
    print("\n# archetypes: teams, share, flow to us per 100 hands together")
    agg = defaultdict(lambda: [0, 0.0, 0, []])
    for t, a, f, hn in rows:
        agg[a][0] += 1
        agg[a][1] += flow[t]
        agg[a][2] += together[t]
        agg[a][3].append(t)
    for a, (k, fl, hn, ts) in sorted(agg.items()):
        print("%-18s teams=%d share=%.0f%% flow=%+.0f chips over %d hands = %+.1f bb/100 | %s" % (
            a, k, 100.0 * k / len(rows), fl, hn, fl / hn * 5, ", ".join(ts)))
    print("\n# archetype pooled profiles")
    for a, (k, fl, hn, ts) in sorted(agg.items()):
        pool = new()
        for t in ts:
            for key, val in team[t].items():
                if isinstance(val, list):
                    pool[key].extend(val)
                else:
                    pool[key] += val
        prof("ARCHETYPE " + a, pool, "teams=%d" % k)
    spots(rounds, team)
    if check:
        hand_checks(rounds)


def archetype(f):
    """Seat level rule, usable after 50 to 100 hands. Order matters."""
    if f["shove"] >= 0.03 or f["pfr"] >= 0.40:
        return "maniac/shover"
    if (f["limp"] or 0) >= 0.20 or f["vpip"] >= 0.45 or (f["vpip"] >= 0.32 and (f["ffl"] or 1) < 0.30):
        return "whale/limper"
    if f["vpip"] < 0.18:
        return "nit"
    if (f["tb"] or 0) >= 0.15:
        return "3-bet aggressor"
    if f["agg"] >= 0.60:
        return "small-bet barreler" if f["tr_size"] <= 0.40 else "barreler"
    if f["pfr"] < 0.6 * f["vpip"]:
        return "passive caller"
    return "standard TAG"


def spots(rounds, team):
    """Opportunity counts and realised chips for the improvement list, per version."""
    def frate(t):
        st = team.get(t)
        return (st["fr"] / st["fr_opp"]) if st and st["fr_opp"] >= 10 else None
    out = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    hands = Counter()
    pots = defaultdict(list)
    for d in rounds:
        me, v, n, pl = d["seat"], d["round"]["version"], len(d["players"]), d["players"]
        hands[v] += len(d["hands"])
        for h in d["hands"]:
            acts, la, folded, put = replay(h, n)
            res = h["results"][me]
            hole = h["hole"][str(me)]
            cls = combo(hole)
            pre = [a for a in acts if a["street"] == "preflop"]
            mine = [a for a in acts if a["seat"] == me]
            pos = pos_name((me - h["button"]) % n, n)
            # our 3-bet that then folds to a 4-bet, by who 4-bet
            tb = next((a for a in mine if a["street"] == "preflop" and a["raises"] == 1 and a["act"] == "raise"), None)
            if tb:
                after = [a for a in mine if a["street"] == "preflop" and pre.index(a) > pre.index(tb)]
                if after and after[0]["raises"] >= 3 and after[0]["act"] == "fold":
                    four = next(a for a in pre if pre.index(a) > pre.index(tb) and a["act"] == "raise")
                    key = "3bet then fold to 4bet: %s" % ("value TT+/AK/AQs" if cls in ("AA", "KK", "QQ", "JJ", "TT", "AKs", "AKo", "AQs") else "other")
                    out[v][key][0] += 1
                    out[v][key][1] += res
                    out[v]["4bettor " + pl[four["seat"]]][0] += 1
                    out[v]["4bettor " + pl[four["seat"]]][1] += res
            # SB or BB facing a single raise with a top 5% hand, our action
            f = next((a for a in mine if a["street"] == "preflop"), None)
            if f and pos == "SB" and f["raises"] == 1 and cls in TOP5PCT:
                out[v]["SB top5%% vs one raise: %s" % f["act"]][0] += 1
                out[v]["SB top5%% vs one raise: %s" % f["act"]][1] += res
            # postflop: first facing action, heads up, by bet size and bettor fold-to-raise
            for street in ("flop", "turn", "river"):
                fa = next((a for a in mine if a["street"] == street and a["to_call"] > 0), None)
                if not fa or fa["live"] != 2:
                    continue
                bettor = next((a["seat"] for a in reversed(acts[:acts.index(fa)]) if a["act"] == "raise"), None)
                fr = frate(pl[bettor]) if bettor is not None else None
                if fa["face"] <= 0.5 and fr is not None and fr >= 0.65 and fa["raises"] == 1:
                    k = "HU facing <=50%% pot bet from seat folding >=65%% to raises: %s" % fa["act"]
                    out[v][k][0] += 1
                    out[v][k][1] += res
                    pots[v].append(fa["pot"] - fa["to_call"])
                if street == "river":
                    k = "HU river facing bet %s: %s" % (size_bin(fa["face"]), fa["act"])
                    out[v][k][0] += 1
                    out[v][k][1] += res
                if fa["act"] == "raise":
                    out[v]["postflop raise vs a bet " + street][0] += 1
                    out[v]["postflop raise vs a bet " + street][1] += res
    print("\n# median pot before the bet in the high fold-to-raise spots:", {v: (med(x), len(x)) for v, x in pots.items()})
    print("\n# spots [n, chips, chips per 100 hands of the version]")
    for v in sorted(out):
        print("v%d (%d hands)" % (v, hands[v]))
        for k, (c, x) in sorted(out[v].items()):
            print("  %-80s n=%4d chips=%+7d per100=%+.1fbb" % (k, c, x, x / hands[v] * 5))


def hand_checks(rounds):
    """Print raw events for two hands so the numbers can be checked by eye."""
    d = rounds[-1]
    for h in d["hands"][:2]:
        print("\n# check %s hand %d players %s" % (d["ref"], h["n"], d["players"]))
        for e in h["events"]:
            print("  ", e)
        print("   results", h["results"])


if __name__ == "__main__":
    main()
