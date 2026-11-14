"""Diagnose our live counted rounds and compare with the winning teams.

    python3 review/live_diagnosis.py                 # counted rounds, all versions
    python3 review/live_diagnosis.py --rivers        # also list every river pot of ours
    python3 review/live_diagnosis.py --practice      # practice rounds instead

Reads hands-data/hands/*.json only. Stdlib only.
All money figures are bb/100 over the hands of the bot version in question
unless a column says chips or bb.
"""
import argparse
import glob
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
HANDS = os.path.join(HERE, "..", "hands-data", "hands")
TOP5 = ["Attention Is All In", "matcha mille crêpes cake", "The Market Makers",
        "Equity Engine", "Gherkers"]
RANKS = "23456789TJQKA"
CATS = ["High Card", "Pair", "Two Pair", "Three of a Kind", "Straight", "Flush",
        "Full House", "Four of a Kind", "Straight Flush"]
STREETS = ["preflop", "flop", "turn", "river"]


# ------------------------------------------------------------------ cards
def rv(c):
    return RANKS.index(c[0])


def cat_of(cards):
    """Category index of the best hand in up to 7 cards (no kickers needed here)."""
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
    """Label our made hand on a board, discounting what the board gives everyone."""
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
        # one of the pairs is on the board, so our real holding is one pair
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


STRONG = {"Two Pair", "Trips/Set", "Straight", "Flush", "Full House", "Four of a Kind",
          "Straight Flush"}
VERY_STRONG = STRONG - {"Two Pair"}


def combo(hole):
    a, b = sorted(hole, key=rv, reverse=True)
    if a[0] == b[0]:
        return a[0] + b[0]
    return a[0] + b[0] + ("s" if a[1] == b[1] else "o")


# roughly the top 5% of starting hands: TT+, 99, AK, AQs, AJs, KQs (64 combos)
TOP5PCT = {"AA", "KK", "QQ", "JJ", "TT", "99", "AKs", "AKo", "AQs", "AJs", "KQs"}


def pos_name(rel, n):
    if rel == 0:
        return "BTN"
    if rel == 1:
        return "SB"
    if rel == 2:
        return "BB"
    fe = n - rel
    return {1: "CO", 2: "HJ", 3: "MP"}.get(fe, "UTG" if rel == 3 else "UTG+1")


# ------------------------------------------------------------------ replay
def replay(h, n):
    """Annotate every action with street, to_call, pot before it, raise count."""
    acts = []
    street = "preflop"
    sb = defaultdict(int)
    put = defaultdict(int)
    put_street = defaultdict(lambda: defaultdict(int))
    cur = 0
    raises = 0
    folded = set()
    last_aggr = {}
    first_in = True  # nobody has voluntarily entered this street yet
    for e in h["events"]:
        k = e[0]
        if k == "post":
            sb[e[1]] += e[2]
            put[e[1]] += e[2]
            put_street["preflop"][e[1]] += e[2]
            cur = max(cur, sb[e[1]])
        elif k == "board":
            street = e[1]
            sb = defaultdict(int)
            cur = 0
            raises = 0
            first_in = True
        elif k == "refund":
            put[e[1]] -= e[2]
            put_street[street][e[1]] -= e[2]
        elif k == "act":
            s, a, amt = e[1], e[2], e[3]
            pot = sum(put.values())
            to_call = cur - sb[s]
            rec = {"seat": s, "street": street, "act": a, "amt": amt, "to_call": to_call,
                   "pot": pot, "raises": raises, "first_in": first_in,
                   "put_before": put[s], "live": n - len(folded)}
            if a == "raise":
                add = amt - sb[s]
                rec["add"] = add
                rec["size"] = (amt - cur) / max(1, pot + to_call)  # raise over pot after calling
                sb[s] = amt
                put[s] += add
                put_street[street][s] += add
                cur = amt
                raises += 1
                last_aggr[street] = s
                first_in = False
            elif a == "call":
                rec["add"] = amt
                sb[s] += amt
                put[s] += amt
                put_street[street][s] += amt
                first_in = False if street == "preflop" else first_in
            elif a == "fold":
                folded.add(s)
            acts.append(rec)
    return acts, last_aggr, folded, put


def load(paths):
    rounds = []
    for p in paths:
        d = json.load(open(p))
        rounds.append(d)
    return rounds


# ------------------------------------------------------------------ per seat stats
def new_stats():
    return defaultdict(float)


def median(xs):
    xs = sorted(xs or [])
    return xs[len(xs) // 2] if xs else float("nan")


def seat_stats(st, h, seat, n, acts, last_aggr, folded, shown_cls):
    """Accumulate the opponent profile counters for one seat in one hand."""
    rel = (seat - h["button"]) % n
    pos = pos_name(rel, n)
    st["hands"] += 1
    st["chips"] += h["results"][seat]
    mine = [a for a in acts if a["seat"] == seat]
    pre = [a for a in mine if a["street"] == "preflop"]
    if any(a["act"] in ("call", "raise") for a in pre):
        st["vpip"] += 1
    if any(a["act"] == "raise" for a in pre):
        st["pfr"] += 1
    # 3-bet opportunity: first time we act facing exactly one raise
    for a in pre:
        if a["raises"] == 1:
            st["3b_opp"] += 1
            if a["act"] == "raise":
                st["3b"] += 1
            break
        if a["raises"] > 1:
            break
    # steal / first-in by position
    if pre and pre[0]["raises"] == 0 and not any(
            b["act"] in ("call", "raise") for b in acts
            if b["street"] == "preflop" and acts.index(b) < acts.index(pre[0])):
        st["fi_opp_" + pos] += 1
        if pre[0]["act"] == "raise":
            st["fi_" + pos] += 1
            # what happened after the open
            later = [b for b in acts if b["street"] == "preflop" and acts.index(b) > acts.index(pre[0])]
            if any(b["act"] == "raise" for b in later if b["seat"] != seat):
                st["fi3b_" + pos] += 1
                me_after = [b for b in later if b["seat"] == seat]
                if me_after and me_after[0]["act"] == "fold":
                    st["fi3bf_" + pos] += 1
            elif any(b["act"] == "call" for b in later if b["seat"] != seat):
                st["ficall_" + pos] += 1
            else:
                st["fiwin_" + pos] += 1
            st["fichips_" + pos] += h["results"][seat]
    # opened then faced a 3-bet
    opened = next((a for a in pre if a["act"] == "raise" and a["raises"] == 0), None)
    if opened:
        after = [a for a in pre if acts.index(a) > acts.index(opened)]
        if after and after[0]["raises"] >= 2:
            st["f3b_opp"] += 1
            if after[0]["act"] == "fold":
                st["f3b"] += 1
    # postflop
    pfr = last_aggr.get("preflop") == seat
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
                st["bsize_" + street] += first["size"]
                st.setdefault("sizes_" + street, []).append(first["size"])
            if street == "flop" and pfr:
                st["cb_opp"] += 1
                if first["act"] == "raise":
                    st["cb"] += 1
                    st["cbsize"] += first["size"]
                    st.setdefault("sizes_cb", []).append(first["size"])
        face = next((a for a in sa if a["to_call"] > 0), None)
        if face:
            st["face_" + street] += 1
            if face["act"] == "fold":
                st["fold_" + street] += 1
    if str(seat) in h["showdown"]:
        st["sd"] += 1
        if h["results"][seat] > 0:
            st["sdwon"] += 1
    # river bets of two thirds pot or more that reached showdown
    rb = [a for a in mine if a["street"] == "river" and a["act"] == "raise" and a["size"] >= 0.66]
    if rb:
        st["bigriver"] += 1
        if str(seat) in h["showdown"]:
            st["bigriver_sd"] += 1
            st["bigshow_" + shown_cls] += 1
            if h["results"][seat] > 0:
                st["bigriver_won"] += 1
        elif h["results"][seat] > 0:
            st["bigriver_fold"] += 1


def shown_class(h, seat):
    cards = h["hole"].get(str(seat))
    if not cards or str(seat) not in h["showdown"]:
        return "unknown"
    return made_class(cards, h["board"])


# ------------------------------------------------------------------ our buckets
def line_str(acts, seat):
    out = []
    for street in STREETS:
        sa = [a for a in acts if a["seat"] == seat and a["street"] == street]
        if not sa:
            continue
        toks = []
        for a in sa:
            if a["act"] == "raise":
                toks.append(("B" if a["raises"] == 0 and street != "preflop" else "R")
                            + "%d" % round(a["amt"]))
            elif a["act"] == "call":
                toks.append("C%d" % a["amt"])
            elif a["act"] == "check":
                toks.append("X")
            else:
                toks.append("F")
        out.append(street[0].upper() + ":" + " ".join(toks))
    return " | ".join(out)


def bucket_of(h, seat, acts, last_aggr):
    mine = [a for a in acts if a["seat"] == seat]
    pre = [a for a in mine if a["street"] == "preflop"]
    vol = any(a["act"] in ("call", "raise") for a in pre)
    raised = any(a["act"] == "raise" for a in pre)
    res = h["results"][seat]
    folded_at = next((a["street"] for a in mine if a["act"] == "fold"), None)
    at_sd = str(seat) in h["showdown"]
    streets_seen = {a["street"] for a in acts}
    last_street = [s for s in STREETS if s in streets_seen or s == "preflop"]
    if not vol and folded_at == "preflop":
        return "blinds folded, no contest"
    if not vol and not mine:
        return "walk or no action"
    if folded_at == "preflop":
        return "opened then folded to 3-bet" if raised else "called preflop then folded preflop"
    if at_sd:
        cls = made_class(h["hole"][str(seat)], h["board"])
        riv = [a for a in mine if a["street"] == "river"]
        called_river = any(a["act"] == "call" and a["to_call"] > 0 for a in riv)
        if res > 0:
            return "showdown won"
        if called_river:
            return "showdown lost after river call"
        return "showdown lost, other line"
    if folded_at is None:
        # won without showdown
        if not any(a["street"] != "preflop" for a in acts):
            return "won preflop uncontested"
        return "won postflop, no showdown"
    pfr = last_aggr.get("preflop") == seat
    cbet = any(a["street"] == "flop" and a["act"] == "raise" for a in mine) and pfr
    if folded_at == "river":
        return "river fold"
    if cbet:
        return "c-bet then folded"
    if vol and not raised:
        return "called preflop, folded flop or turn"
    if raised:
        return "raised preflop, no c-bet, folded flop or turn"
    return "BB checked, folded flop or turn"


# ------------------------------------------------------------------ main analysis
def analyse(rounds, verbose_rivers=False):
    by_ver = defaultdict(list)
    for d in rounds:
        by_ver[d["round"]["version"]].append(d)
    team = defaultdict(new_stats)
    report = {}
    for ver, rs in sorted(by_ver.items()):
        R = defaultdict(float)
        C = Counter()
        bucket = defaultdict(float)
        bucket_n = Counter()
        pos_res = defaultdict(float)
        pos_n = Counter()
        street_res = defaultdict(float)
        sd_cls = defaultdict(lambda: [0, 0.0, 0])  # n, chips, won
        river_rows = []
        losers = []
        timeouts = []
        river_calls = defaultdict(lambda: [0, 0.0, 0.0, 0])  # n, chips result, fold delta, won
        river_bets = Counter()
        river_bet_chips = defaultdict(float)
        value_missed = []
        check_raised = Counter()
        face = defaultdict(lambda: [0, 0])  # (street,sizebin) -> faced, folded
        face_be = defaultdict(float)
        probe = Counter()
        open_cls = defaultdict(lambda: [0, 0.0])
        ours = new_stats()
        sd_lines = defaultdict(lambda: [0, 0.0])
        commit = defaultdict(lambda: [0, 0, 0.0, 0.0])  # n, won, actual chips, chips if folded instead
        hands_total = 0
        for d in rs:
            seat = d["seat"]
            n = len(d["players"])
            names = d["players"]
            for h in d["hands"]:
                hands_total += 1
                acts, last_aggr, folded, put = replay(h, n)
                for s in range(n):
                    seat_stats(team[names[s]] if s != seat else ours, h, s, n, acts, last_aggr,
                               folded, shown_class(h, s))
                res = h["results"][seat]
                R["chips"] += res
                rel = (seat - h["button"]) % n
                pos = pos_name(rel, n)
                pos_res[pos] += res
                pos_n[pos] += 1
                streets = [s for s in STREETS if s == "preflop" or any(
                    e[0] == "board" and e[1] == s for e in h["events"])]
                street_res[streets[-1]] += res
                b = bucket_of(h, seat, acts, last_aggr)
                bucket[b] += res
                bucket_n[b] += 1
                hole = h["hole"][str(seat)]
                mine = [a for a in acts if a["seat"] == seat]
                pre = [a for a in mine if a["street"] == "preflop"]
                line = line_str(acts, seat)
                at_sd = str(seat) in h["showdown"]
                opp_sd = [s for s in h["showdown"] if int(s) != seat]
                opp_cls = ",".join("%s %s(%s)" % (names[int(s)], combo(h["hole"][s]),
                                                  made_class(h["hole"][s], h["board"]))
                                   for s in opp_sd if s in h["hole"]) or "-"
                # preflop open by position and hand
                if pre and pre[0]["act"] == "raise" and pre[0]["raises"] == 0:
                    key = (pos, "top5%" if combo(hole) in TOP5PCT else "other")
                    open_cls[key][0] += 1
                    open_cls[key][1] += res
                # facing bets: fold by street and size
                for a in mine:
                    if a["to_call"] > 0 and a["street"] != "preflop":
                        f = a["to_call"] / max(1, a["pot"] - a["to_call"])
                        sbin = "<=40%" if f <= 0.4 else "40-75%" if f <= 0.75 else "75-110%" if f <= 1.1 else ">110%"
                        k = (a["street"], sbin)
                        face[k][0] += 1
                        face[k][1] += a["act"] == "fold"
                        face_be[k] += a["to_call"] / max(1, a["pot"])
                # opponents betting into our check
                for street in ("flop", "turn", "river"):
                    sa = [a for a in acts if a["street"] == street]
                    for i, a in enumerate(sa):
                        if a["seat"] == seat and a["act"] == "check":
                            probe[street + "_checks"] += 1
                            nxt = sa[i + 1:]
                            bet = next((x for x in nxt if x["act"] == "raise"), None)
                            if bet and bet["seat"] != seat:
                                probe[street + "_bet_into"] += 1
                                resp = next((x for x in nxt if x["seat"] == seat and acts.index(x) > acts.index(bet)), None)
                                if resp:
                                    probe[street + "_resp"] += 1
                                    probe[street + "_fold"] += resp["act"] == "fold"
                            break
                # river pots
                if any(a["street"] == "river" for a in mine):
                    riv = [a for a in mine if a["street"] == "river"]
                    cls = made_class(hole, h["board"])
                    facing = [a for a in riv if a["to_call"] > 0]
                    fsz = ["%.0f%%" % (100 * a["to_call"] / max(1, a["pot"] - a["to_call"])) for a in facing]
                    river_rows.append((d["round"]["ref"], h["n"], pos, combo(hole), cls, line,
                                       ",".join(fsz) or "-", res, opp_cls))
                    for a in riv:
                        if a["act"] == "call" and a["to_call"] > 0:
                            grp = cls if cls in ("No made hand", "Weak Pair", "Top Pair", "Overpair") else (
                                "Two Pair" if cls == "Two Pair" else "Trips or better")
                            f = a["to_call"] / max(1, a["pot"] - a["to_call"])
                            szb = "<=60% pot" if f <= 0.6 else ">60% pot"
                            rc = river_calls[(grp, szb)]
                            rc[0] += 1
                            rc[1] += res
                            rc[2] += (-a["put_before"]) - res  # gain from folding instead
                            rc[3] += res > 0
                    rb = [a for a in riv if a["act"] == "raise"]
                    if rb:
                        k = "bet/raise river, " + ("strong" if cls in STRONG else "one pair" if "Pair" in cls else "air")
                        river_bets[k] += 1
                        river_bet_chips[k] += res
                        if at_sd and res < 0:
                            river_bets[k + ", called and lost"] += 1
                        if not at_sd and res > 0:
                            river_bets[k + ", opponent folded"] += 1
                        if at_sd and res > 0:
                            river_bets[k + ", called and won"] += 1
                    if not rb and at_sd and cls in STRONG and all(a["act"] in ("check", "call") for a in riv):
                        value_missed.append((d["round"]["ref"], h["n"], pos, combo(hole), cls, line, res,
                                             any(a["act"] == "check" for a in riv),
                                             not any(a["act"] == "call" for a in riv)))
                # showdown losses by how the money went in and our final class
                if at_sd:
                    allin_st = None
                    for a in mine:
                        if a["act"] in ("call", "raise") and a["put_before"] + a.get("add", 0) >= h["start_stacks"][seat]:
                            allin_st = a["street"]
                            break
                    riv = [a for a in mine if a["street"] == "river"]
                    if allin_st and allin_st != "river":
                        how = "all-in on " + allin_st
                    elif any(a["act"] == "raise" for a in riv):
                        how = "we bet/raised river"
                    elif any(a["act"] == "call" for a in riv):
                        how = "we called river"
                    else:
                        how = "river checked through"
                    k = (how, made_class(hole, h["board"]), "won" if res > 0 else "lost")
                    sd_lines[k][0] += 1
                    sd_lines[k][1] += res
                # commitment: the action that took us past 30 bb in the pot
                for a in mine:
                    if a["act"] in ("call", "raise") and a["put_before"] < 600 <= a["put_before"] + a.get("add", 0):
                        if a["street"] == "preflop":
                            cls = "pre " + ("top5%" if combo(hole) in TOP5PCT else "other")
                        else:
                            brd = h["board"][:{"flop": 3, "turn": 4, "river": 5}[a["street"]]]
                            cls = made_class(hole, brd)
                            cls = cls if cls in ("No made hand", "Weak Pair", "Top Pair", "Overpair", "Two Pair") else "Trips or better"
                        k = (a["street"], cls, a["act"])
                        commit[k][0] += 1
                        commit[k][1] += res > 0
                        commit[k][2] += res
                        commit[k][3] += -a["put_before"]
                        break
                # suspected timeouts
                for a in mine:
                    if a["act"] != "fold" or a["to_call"] <= 0:
                        continue
                    if a["street"] == "preflop" and combo(hole) in TOP5PCT:
                        timeouts.append((d["round"]["ref"], h["n"], pos, combo(hole), "preflop", line, res))
                    elif a["street"] != "preflop":
                        brd = h["board"][:{"flop": 3, "turn": 4, "river": 5}[a["street"]]]
                        c = made_class(hole, brd)
                        if c in STRONG:
                            timeouts.append((d["round"]["ref"], h["n"], pos, combo(hole), a["street"] + " " + c, line, res))
                losers.append((res, d["round"]["ref"], h["n"], pos, combo(hole),
                               made_class(hole, h["board"]) if h["board"] else "preflop",
                               line, opp_cls, h["board"]))
        report[ver] = dict(rounds=[d["round"] for d in rs], hands=hands_total, R=R, bucket=bucket,
                           bucket_n=bucket_n, pos_res=pos_res, pos_n=pos_n, street_res=street_res,
                           river_rows=river_rows, losers=sorted(losers)[:10], timeouts=timeouts,
                           river_calls=river_calls, river_bets=river_bets,
                           river_bet_chips=river_bet_chips, value_missed=value_missed, face=face,
                           face_be=face_be, probe=probe, open_cls=open_cls, ours=ours,
                           sd_lines=sd_lines, commit=commit,
                           tables={d["round"]["ref"]: d["players"] for d in rs})
    return report, team


def bb100(chips, hands, bb=20):
    return 100.0 * chips / bb / max(1, hands)


def pct(a, b):
    return "%.0f%% (%d/%d)%s" % (100.0 * a / b, a, b, " *" if b < 30 else "") if b else "n/a"


def profile_row(name, st):
    def r(a, b):
        return st[a] / st[b] if st[b] else float("nan")
    out = {
        "team": name, "hands": int(st["hands"]), "bb100": bb100(st["chips"], st["hands"]),
        "VPIP": r("vpip", "hands"), "PFR": r("pfr", "hands"), "3bet": r("3b", "3b_opp"),
        "3bet_n": int(st["3b_opp"]), "fold_to_3bet": r("f3b", "f3b_opp"), "f3b_n": int(st["f3b_opp"]),
        "cbet": r("cb", "cb_opp"), "cbet_n": int(st["cb_opp"]), "cbet_size": median(st.get("sizes_cb")),
        "turn_bet": r("bet_turn", "bopp_turn"), "turn_n": int(st["bopp_turn"]),
        "turn_size": median(st.get("sizes_turn")),
        "river_bet": r("bet_river", "bopp_river"), "river_n": int(st["bopp_river"]),
        "river_size": median(st.get("sizes_river")),
        "fold_flop": r("fold_flop", "face_flop"), "ff_n": int(st["face_flop"]),
        "fold_turn": r("fold_turn", "face_turn"), "ft_n": int(st["face_turn"]),
        "fold_river": r("fold_river", "face_river"), "fr_n": int(st["face_river"]),
        "wsd": r("sdwon", "sd"), "sd_n": int(st["sd"]),
    }
    for p in ("UTG", "MP", "HJ", "CO", "BTN", "SB"):
        out["open_" + p] = r("fi_" + p, "fi_opp_" + p)
        out["open_n_" + p] = int(st["fi_opp_" + p])
    late = ("CO", "BTN", "SB")
    op = sum(st["fi_" + p] for p in late)
    out["late_opens"] = int(op)
    out["late_allfold"] = sum(st["fiwin_" + p] for p in late) / op if op else float("nan")
    out["late_3bet"] = sum(st["fi3b_" + p] for p in late) / op if op else float("nan")
    out["late_bb_per_open"] = sum(st["fichips_" + p] for p in late) / 20 / op if op else float("nan")
    out["bigriver"] = int(st["bigriver"])
    out["bigriver_sd"] = int(st["bigriver_sd"])
    out["bigshow"] = {k[8:]: int(v) for k, v in st.items() if k.startswith("bigshow_")}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rivers", action="store_true")
    ap.add_argument("--practice", action="store_true")
    args = ap.parse_args()
    pat = "saturday_practice_r*.json" if args.practice else "saturday_r0*.json"
    paths = sorted(glob.glob(os.path.join(HANDS, pat)))
    rounds = load(paths)
    print("files:", [os.path.basename(p) for p in paths])
    report, team = analyse(rounds)
    for ver, r in report.items():
        H = r["hands"]
        print("\n" + "=" * 70)
        print("VERSION %s  rounds %s  hands %d  result %+.1f bb/100" % (
            ver, [x["ref"] for x in r["rounds"]], H, bb100(r["R"]["chips"], H)))
        for x in r["rounds"]:
            print("  %s table %s seat %s bb100 %+.1f timeouts %s think %.2f" % (
                x["ref"], x["table"], x["seat"], x["bb100"], x["timeouts"], x["think_s"]))
        print("tables:", r["tables"])
        print("\n[1] loss decomposition (exclusive buckets, bb/100 over all %d hands)" % H)
        tot = 0
        for k, v in sorted(r["bucket"].items(), key=lambda kv: kv[1]):
            tot += v
            print("  %-48s n=%5d  %+8.1f bb/100  %+8.0f chips" % (k, r["bucket_n"][k], bb100(v, H), v))
        print("  %-48s          %+8.1f bb/100" % ("SUM", bb100(tot, H)))
        print("\n  by position (bb/100 over all hands; per-100-hands-in-seat in brackets)")
        for p in ("UTG", "UTG+1", "MP", "HJ", "CO", "BTN", "SB", "BB"):
            if r["pos_n"][p]:
                print("  %-6s n=%4d  %+7.1f  (%+7.1f per 100 in seat)" % (
                    p, r["pos_n"][p], bb100(r["pos_res"][p], H), bb100(r["pos_res"][p], r["pos_n"][p])))
        print("  by street pot ended:", {k: round(bb100(v, H), 1) for k, v in r["street_res"].items()})
        o = profile_row("US", r["ours"])
        print("\n[2] our first-in opens and outcomes by position")
        st = r["ours"]
        for p in ("UTG", "UTG+1", "MP", "HJ", "CO", "BTN", "SB"):
            opp = int(st["fi_opp_" + p])
            if not opp:
                continue
            op = int(st["fi_" + p])
            print("  %-6s folded to %4d  open %s  all fold %s  called %s  3-bet %s  folded to 3-bet %s  chips on opens %+.0f (%.2f bb/open)" % (
                p, opp, pct(op, opp), pct(int(st["fiwin_" + p]), op), pct(int(st["ficall_" + p]), op),
                pct(int(st["fi3b_" + p]), op), pct(int(st["fi3bf_" + p]), int(st["fi3b_" + p])),
                st["fichips_" + p], st["fichips_" + p] / 20 / max(1, op)))
        print("  opens by hand group: ", {"%s %s" % k: (v[0], round(v[1] / 20 / max(1, v[0]), 2))
                                          for k, v in sorted(r["open_cls"].items())}, "(n, bb per open)")
        for grp in ("other", "top5%"):
            ep = [v for k, v in r["open_cls"].items() if k[0] in ("UTG", "UTG+1", "MP", "HJ") and k[1] == grp]
            n_ep = sum(v[0] for v in ep)
            c_ep = sum(v[1] for v in ep)
            print("  first-in opens UTG to HJ, %-6s hands: n=%d  result %+.0f chips (%+.1f bb/100, %+.2f bb per open)" % (
                grp, n_ep, c_ep, bb100(c_ep, H), c_ep / 20 / max(1, n_ep)))
        print("\n[3] river")
        print("  river pots reached:", len(r["river_rows"]))
        for k, v in sorted(r["river_calls"].items()):
            print("  river call %-16s %-10s n=%3d won %3d  result %+7.0f chips  folding instead gains %+7.0f chips (%+.1f bb/100)%s" % (
                k[0], k[1], v[0], v[3], v[1], v[2], bb100(v[2], H), " *" if v[0] < 30 else ""))
        for k in sorted(r["river_bets"]):
            print("  %-50s n=%3d" % (k, r["river_bets"][k]),
                  "result %+.0f chips" % r["river_bet_chips"][k] if k in r["river_bet_chips"] else "")
        vm = r["value_missed"]
        print("  strong hand (two pair+) reached showdown without our betting the river: %d, won %d, result %+.0f chips" % (
            len(vm), sum(1 for x in vm if x[6] > 0), sum(x[6] for x in vm)))
        if args.rivers:
            for row in r["river_rows"]:
                print("   ", row)
        print("\n[4] pushed around")
        for s in ("flop", "turn", "river"):
            p = r["probe"]
            print("  %s: we checked %d, opponent bet after our check %s, we folded to it %s" % (
                s, p[s + "_checks"], pct(p[s + "_bet_into"], p[s + "_checks"]), pct(p[s + "_fold"], p[s + "_resp"])))
        print("  open then 3-bet:", {pp: pct(int(st["fi3b_" + pp]), int(st["fi_" + pp])) for pp in ("UTG", "MP", "HJ", "CO", "BTN", "SB") if st["fi_" + pp]})
        print("  fold to 3-bet overall:", pct(int(st["f3b"]), int(st["f3b_opp"])))
        for k in sorted(r["face"]):
            f, fo = r["face"][k]
            print("  facing %-6s %-8s fold %s  break-even fold for a bluff %.0f%%" % (
                k[0], k[1], pct(fo, f), 100 * r["face_be"][k] / f))
        print("\n[1b] showdowns by how the money went in, our final hand class")
        for k, v in sorted(r["sd_lines"].items(), key=lambda kv: kv[1][1]):
            print("  %-24s %-14s %-4s n=%3d  %+7.0f chips  %+7.1f bb/100" % (k[0], k[1], k[2], v[0], v[1], bb100(v[1], H)))
        print("\n[1c] the action that took us past 30 bb: actual result vs folding at that point")
        for k, v in sorted(r["commit"].items(), key=lambda kv: kv[1][3] - kv[1][2], reverse=True):
            print("  %-8s %-16s %-6s n=%3d won %3d  actual %+7.0f  fold instead %+7.0f  gain from folding %+7.0f chips (%+.1f bb/100)%s" % (
                k[0], k[1], k[2], v[0], v[1], v[2], v[3], v[3] - v[2], bb100(v[3] - v[2], H), " *" if v[0] < 30 else ""))
        groups = defaultdict(lambda: [0, 0, 0.0])
        for k, v in r["commit"].items():
            if k[0] == "preflop":
                continue
            weak = k[1] in ("No made hand", "Weak Pair", "Top Pair", "Overpair")
            g = ("call" if k[2] == "call" else "bet/raise") + (" with one pair or worse" if weak else " with two pair or better")
            groups[g][0] += v[0]
            groups[g][1] += v[1]
            groups[g][2] += v[3] - v[2]
        for g, v in sorted(groups.items()):
            print("  GROUP postflop %-38s n=%3d won %3d  gain from folding %+7.0f chips (%+.1f bb/100)" % (
                g, v[0], v[1], v[2], bb100(v[2], H)))
        print("\n[6] ten biggest losses")
        for x in r["losers"]:
            print("  %+6d %s#%d %s %s [%s] board %s | %s | opp %s" % (x[0], x[1], x[2], x[3], x[4], x[5],
                                                                  " ".join(x[8]), x[6], x[7]))
        print("\n[7] suspected timeouts (fold facing a bet with top 5% preflop or two pair+ postflop)")
        for x in r["timeouts"]:
            print("  ", x)
        print("  total", len(r["timeouts"]), "result chips %+.0f" % sum(x[6] for x in r["timeouts"]))
        r["profile"] = o
    print("\n[5] profiles (counted files where they sat with us)")
    rows = [profile_row(t, team[t]) for t in TOP5 if team[t]["hands"]]
    for ver, r in report.items():
        rows.append(dict(r["profile"], team="US v%s" % ver))
    keys = ["hands", "bb100", "VPIP", "PFR", "3bet", "fold_to_3bet", "open_CO", "open_BTN", "open_SB",
            "cbet", "cbet_size", "turn_bet", "turn_size", "river_bet", "river_size", "fold_flop",
            "fold_turn", "fold_river", "wsd"]
    for row in rows:
        print("  " + row["team"])
        print("    " + "  ".join("%s=%s" % (k, ("%.2f" % row[k]) if isinstance(row[k], float) else row[k]) for k in keys))
        print("    n: 3bet %d f3b %d CO %d BTN %d SB %d cbet %d turn %d river %d faceF %d faceT %d faceR %d sd %d" % (
            row["3bet_n"], row["f3b_n"], row["open_n_CO"], row["open_n_BTN"], row["open_n_SB"], row["cbet_n"],
            row["turn_n"], row["river_n"], row["ff_n"], row["ft_n"], row["fr_n"], row["sd_n"]))
        print("    late position opens %d: all fold %.2f, 3-bet %.2f, bb per open %.2f" % (
            row["late_opens"], row["late_allfold"], row["late_3bet"], row["late_bb_per_open"]))
        print("    big river bets %d, reached showdown %d, shown: %s" % (row["bigriver"], row["bigriver_sd"], row["bigshow"]))
    print("\nteams at our tables:", sorted(t for t in team))


if __name__ == "__main__":
    main()
