"""Per-team stats from downloaded hand histories.

    python tools/analyze.py                 # all files in hands/
    python tools/analyze.py hands/x.json    # chosen files
    python tools/analyze.py --me            # also break down our own results

Columns: bb/100, VPIP, PFR, limp, 3-bet, shove (preflop raise to >=50bb), average
open size (bb), cbet (flop bet as preflop aggressor), bet% when checked to, fold /
raise frequency facing a postflop bet, AF (bets+raises / calls postflop),
WTSD (showdowns / flops seen), W$SD, and how often an aggressive hand shown down
was air (no pair with a hole card, no straight+).
"""
import glob
import json
import os
import sys
from collections import defaultdict

RANKS = "23456789TJQKA"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BB = 20


class P:
    def __init__(self):
        self.d = defaultdict(float)
        self.opens = []
        self.bets = []          # postflop bet / pot fractions

    def r(self, a, b):
        return 100.0 * self.d[a] / self.d[b] if self.d[b] else float("nan")


def air(hole, board):
    br = [c[0] for c in board]
    if hole[0][0] == hole[1][0] or hole[0][0] in br or hole[1][0] in br:
        return False
    cards = hole + board
    for s in "cdhs":
        if sum(1 for c in cards if c[1] == s) >= 5:
            return False
    m = 0
    for c in cards:
        m |= 1 << RANKS.index(c[0])
    m = (m << 1) | ((m >> 12) & 1)
    for lo in range(10):
        if (m >> lo) & 31 == 31:
            return False
    return True


def run(files, me_detail):
    players = defaultdict(P)
    mine = defaultdict(float)
    big = []
    odd_folds = []
    for f in files:
        d = json.load(open(f))
        names = d["players"]
        myseat = d["seat"]
        if FOCUS and FOCUS in names:
            myseat = names.index(FOCUS)
        for h in d["hands"]:
            n = len(names)
            street = "preflop"
            bets = [0] * n
            cur = 0
            pot = 0
            raises = 0
            first_raiser = None
            last_agg = None
            pf_agg = None
            acted_pf = set()
            saw_flop = set()
            folded = set()
            aggr_post = set()
            vp, pr = set(), set()
            faced3 = set()
            my_last = None
            for ev in h["events"]:
                k = ev[0]
                if k == "post":
                    bets[ev[1]] += ev[2]
                    cur = max(cur, bets[ev[1]])
                    pot += ev[2]
                elif k == "board":
                    if ev[1] == "flop":
                        saw_flop = set(range(n)) - folded
                        pf_agg = last_agg
                    street = ev[1]
                    bets = [0] * n
                    cur = 0
                    last_agg = None
                elif k == "refund":
                    pot -= ev[2]
                elif k == "act":
                    s, a, amt = ev[1], ev[2], ev[3]
                    p = players[names[s]]
                    facing = cur > bets[s]
                    if s == myseat:
                        my_last = (street, a, facing, cur - bets[s], pot)
                    if street == "preflop":
                        first = s not in acted_pf
                        acted_pf.add(s)
                        if first:
                            if raises == 0:
                                p.d["rfi_opp"] += 1
                                if a == "raise":
                                    p.d["rfi"] += 1
                                    p.opens.append(amt / BB)
                                elif a == "call":
                                    p.d["limp"] += 1
                            elif raises == 1:
                                p.d["3b_opp"] += 1
                                if a == "raise":
                                    p.d["3b"] += 1
                                elif a == "call":
                                    p.d["cc"] += 1
                        elif s == first_raiser and raises == 2 and s not in faced3:
                            faced3.add(s)
                            p.d["f3b_opp"] += 1
                            if a == "fold":
                                p.d["f3b"] += 1
                        if a in ("call", "raise"):
                            vp.add(s)
                        if a == "raise":
                            pr.add(s)
                            if raises == 0:
                                first_raiser = s
                            raises += 1
                            if amt >= 1000:
                                p.d["shove"] += 1
                    else:
                        if facing:
                            p.d["fb_opp"] += 1
                            if a == "fold":
                                p.d["fb_fold"] += 1
                            elif a == "raise":
                                p.d["fb_raise"] += 1
                        else:
                            p.d["bet_opp"] += 1
                            if a == "raise":
                                p.d["bet"] += 1
                                if pot:
                                    p.bets.append(amt / pot)
                            if street == "flop" and s == pf_agg:
                                p.d["cb_opp"] += 1
                                if a == "raise":
                                    p.d["cb"] += 1
                        if a == "raise":
                            p.d["agg"] += 1
                            aggr_post.add(s)
                        elif a == "call":
                            p.d["pcall"] += 1
                    if a == "raise":
                        pot += amt - bets[s]
                        bets[s] = amt
                        cur = amt
                        last_agg = s
                    elif a == "call":
                        pot += amt
                        bets[s] += amt
                    elif a == "fold":
                        folded.add(s)
            res = h["results"]
            shown = h.get("showdown") or {}
            for s in range(n):
                p = players[names[s]]
                p.d["hands"] += 1
                p.d["chips"] += res[s]
                if s in vp:
                    p.d["vpip"] += 1
                if s in pr:
                    p.d["pfr"] += 1
                if s in saw_flop:
                    p.d["flops"] += 1
                    if str(s) in shown:
                        p.d["sd"] += 1
                        if res[s] > 0:
                            p.d["wsd"] += 1
                if str(s) in shown and s in aggr_post and len(h["board"]) == 5:
                    hc = h["hole"].get(str(s))
                    if hc:
                        p.d["agg_sd"] += 1
                        if air(hc, h["board"]):
                            p.d["agg_air"] += 1
            r = res[myseat]
            kind = "showdown" if str(myseat) in shown else ("postflop" if myseat in saw_flop else "preflop")
            mine[kind] += r
            mine[kind + "_n"] += 1
            if abs(r) >= 600:
                big.append((r, os.path.basename(f), h["n"], h["hole"].get(str(myseat)), h["board"],
                            {names[int(k)]: v for k, v in h["hole"].items() if int(k) != myseat}))
            if my_last and my_last[1] == "fold" and r < 0:
                hc = h["hole"].get(str(myseat))
                rk = sorted((RANKS.index(c[0]) for c in hc), reverse=True)
                premium = (rk[0] == rk[1] and rk[0] >= 8) or (rk[0] == 12 and rk[1] >= 10)
                if (premium and my_last[0] == "preflop" and my_last[3] <= 200) or -r >= 300:
                    odd_folds.append((r, os.path.basename(f), h["n"], hc, h["board"], my_last))

    cols = ["team", "hands", "bb/100", "VPIP", "PFR", "limp", "3bet", "f3b", "shove", "open", "cbet",
            "bet%", "bsize", "foldB", "raisB", "AF", "WTSD", "W$SD", "air"]
    print("%-24s %5s %7s %5s %5s %5s %5s %5s %5s %5s %5s %5s %5s %5s %5s %5s %5s %5s %5s" % tuple(cols))
    for name, p in sorted(players.items(), key=lambda kv: -kv[1].d["chips"] / max(1, kv[1].d["hands"])):
        d = p.d
        af = d["agg"] / d["pcall"] if d["pcall"] else float("nan")
        op = sum(p.opens) / len(p.opens) if p.opens else float("nan")
        bs = sorted(p.bets)[len(p.bets) // 2] if p.bets else float("nan")
        print("%-24s %5d %+7.1f %5.0f %5.0f %5.0f %5.0f %5.0f %5.1f %5.1f %5.0f %5.0f %5.2f %5.0f %5.0f %5.1f %5.0f %5.0f %5.0f" % (
            name[:24], d["hands"], d["chips"] / BB / d["hands"] * 100, p.r("vpip", "hands"), p.r("pfr", "hands"),
            p.r("limp", "rfi_opp"), p.r("3b", "3b_opp"), p.r("f3b", "f3b_opp"), p.r("shove", "hands"), op,
            p.r("cb", "cb_opp"), p.r("bet", "bet_opp"), bs, p.r("fb_fold", "fb_opp"), p.r("fb_raise", "fb_opp"),
            af, p.r("sd", "flops"), p.r("wsd", "sd"), p.r("agg_air", "agg_sd")))
    if me_detail:
        print("\nOur chips by how the hand ended:")
        for k in ("preflop", "postflop", "showdown"):
            print("  %-9s %6d hands  %+8d chips  (%+.1f bb/100 of all hands)" % (
                k, mine[k + "_n"], mine[k], mine[k] / BB / max(1, sum(mine[x + "_n"] for x in ("preflop", "postflop", "showdown"))) * 100))
        print("\nBiggest pots (|result| >= 600):")
        for b in sorted(big)[:12] + sorted(big)[-8:]:
            print("  %+6d %s #%d we=%s board=%s shown=%s" % b)
        print("\nSuspicious folds (premium preflop for cheap, or folding after investing >= 300):")
        for o in sorted(odd_folds)[:25]:
            print("  %+6d %s #%d we=%s board=%s last=(street=%s act=%s facing=%s to_call=%s pot=%s)" % (o[:5] + o[5]))


FOCUS = None
if __name__ == "__main__":
    for _a in sys.argv[1:]:
        if _a.startswith("--focus="):
            FOCUS = _a.split("=", 1)[1]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = args or sorted(glob.glob(os.path.join(ROOT, "hands", "*.json")))
    run(files, "--me" in sys.argv)
