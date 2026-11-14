"""Behaviour numbers for our seat in hand files, against the live targets.

    python3 tools/behaviour.py hands/saturday_r001.json hands/saturday_r002.json
    python3 tools/rule_accounting.py --field fieldonly --dump /tmp/d && python3 tools/behaviour.py /tmp/d/*.json

Targets from docs/live-diagnosis.md: VPIP 0.22 to 0.28, PFR 0.15 to 0.20,
3-bet 8 to 12%, river bet when checked to 35 to 50%, fold to a flop bet
under 45%, commit calls with one pair near zero.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import bot  # noqa: E402


def main(paths):
    c = dict(hands=0, vpip=0, pfr=0, tb_opp=0, tb=0, rv_opp=0, rv_bet=0, ff_opp=0, ff=0,
             commit=0, commit_1p=0, commit_1p_won=0)
    for path in paths:
        d = json.load(open(path))
        me = d["seat"]
        for h in d["hands"]:
            hole = h["hole"].get(str(me))
            if not hole:
                continue
            hc = [bot.CARD[x] for x in hole]
            n = len(h["start_stacks"])
            bets, contrib = [0] * n, [0] * n
            board, street, nraise, first = [], "preflop", 0, False
            v = p = False
            c["hands"] += 1
            for ev in h["events"]:
                if ev[0] == "post":
                    bets[ev[1]] += ev[2]
                    contrib[ev[1]] += ev[2]
                    continue
                if ev[0] == "board":
                    street, board = ev[1], [bot.CARD[x] for x in ev[2]]
                    bets, nraise, first = [0] * n, 0, False
                    continue
                if ev[0] != "act":
                    continue
                seat, act, amt = ev[1], ev[2], ev[3]
                to_call = max(bets) - bets[seat]
                if seat == me:
                    if street == "preflop":
                        if act in ("call", "raise"):
                            v = True
                        if act == "raise":
                            p = True
                        if nraise == 1:
                            c["tb_opp"] += 1
                            c["tb"] += act == "raise"
                    elif to_call == 0 and street == "river":
                        c["rv_opp"] += 1
                        c["rv_bet"] += act == "raise"
                    elif to_call > 0 and street == "flop" and nraise == 1:
                        c["ff_opp"] += 1
                        c["ff"] += act == "fold"
                    if act == "call" and street != "preflop":
                        before = contrib[me]
                        after = before + amt
                        if before <= 30 * 20 < after:
                            c["commit"] += 1
                            if bot.cat_of(hc[0], hc[1], bot.board_info(board)) <= 3:
                                c["commit_1p"] += 1
                                c["commit_1p_won"] += h["result"] > 0
                if act == "raise":
                    contrib[seat] += amt - bets[seat]
                    bets[seat] = amt
                    nraise += 1
                elif act == "call":
                    bets[seat] += amt
                    contrib[seat] += amt
            c["vpip"] += v
            c["pfr"] += p
    hn = float(max(1, c["hands"]))
    r = lambda a, b: c[a] / float(max(1, c[b]))  # noqa: E731
    print("hands %d" % c["hands"])
    print("VPIP %.3f (0.22 to 0.28)  PFR %.3f (0.15 to 0.20)" % (c["vpip"] / hn, c["pfr"] / hn))
    print("3-bet %.3f of %d spots (0.08 to 0.12)" % (r("tb", "tb_opp"), c["tb_opp"]))
    print("river bet when checked to %.3f of %d (0.35 to 0.50)" % (r("rv_bet", "rv_opp"), c["rv_opp"]))
    print("fold to flop bet %.3f of %d (under 0.45)" % (r("ff", "ff_opp"), c["ff_opp"]))
    print("commit calls %d, with one pair or worse %d (won %d), per 1000 hands %.2f" % (
        c["commit"], c["commit_1p"], c["commit_1p_won"], c["commit_1p"] * 1000 / hn))


if __name__ == "__main__":
    main(sys.argv[1:])
