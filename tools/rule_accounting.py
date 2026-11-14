"""Count the bets each named rule in bot.py makes and the chips they realise.

    python3 tools/rule_accounting.py                    # bot.py on the field bench, 20 tables
    python3 tools/rule_accounting.py --field tight --tables 10

Tables run in process (no time limits), seated like tools/bench.py. The bot
tags each rule driven action in Agent.acct: the count of actions, and for the
first tagged action of a hand the chips from that decision to the end of the
hand (final stack minus stack before the action). Later tagged actions in the
same hand are counted but carry no chips, so rows do not double count.
"""
import argparse
import importlib.util
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "tools"))
from engine import FixedHandsTable  # noqa: E402
from engine.players import LocalPlayer  # noqa: E402
import bench  # noqa: E402


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Agent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bot", nargs="?", default="bot.py")
    ap.add_argument("--field", default="field")
    ap.add_argument("--tables", type=int, default=20)
    ap.add_argument("--hands", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--dump", default=None, help="write each table as a hand file analyze_hands.py reads")
    args = ap.parse_args()
    ours = load(bench.resolve(args.bot), "acct_bot")
    pool = bench.fields()[args.field]
    fixed = [os.path.join(HERE, p) for p in bench.FIXED.get(args.field, [])]
    cache = {}
    rng = random.Random(args.seed)
    total = {}
    hands = 0
    chips = 0
    for t in range(args.tables):
        n = rng.choice([6, 7, 8])
        seats = ["US"] + fixed[:n - 1]
        seats += [rng.choice(pool) for _ in range(n - len(seats))]
        rng.shuffle(seats)
        classes = []
        for p in seats:
            if p == "US":
                classes.append(ours)
            else:
                if p not in cache:
                    cache[p] = load(p, "f%d" % len(cache))
                classes.append(cache[p])
        players = [LocalPlayer(c) for c in classes]
        res = FixedHandsTable(players, hands=args.hands, seed=rng.random(), record=bool(args.dump)).play()
        i = seats.index("US")
        if args.dump:
            os.makedirs(args.dump, exist_ok=True)
            hands_out = []
            for rec in res["log"]:
                results = [e - s0 for e, s0 in zip(rec["end"], rec["stacks"])]
                hands_out.append({"n": rec["n"], "button": rec["button"], "sb": rec["sb"], "bb": rec["bb"],
                                  "start_stacks": rec["stacks"], "hole": {str(i): rec["hole"][str(i)]},
                                  "showdown": {k: rec["hole"][k] for k in (rec.get("showdown") or {})},
                                  "board": rec["board"], "events": rec["events"], "results": results,
                                  "result": results[i]})
            names = ["us" if p == "US" else os.path.basename(p)[:-3] + "_%d" % k for k, p in enumerate(seats)]
            with open(os.path.join(args.dump, "table_%02d.json" % t), "w") as f:
                json.dump({"seat": i, "players": names, "hands": hands_out}, f)
        hands += res["hands"]
        chips += res["chips"][i]
        for rule, (cnt, ch) in getattr(players[i].agent, "acct", {}).items():
            a = total.setdefault(rule, [0, 0])
            a[0] += cnt
            a[1] += ch
    bb = float(bench.BIG_BLIND)
    print("%s on %s: %d tables, %d hands, overall %+.1f bb/100" % (
        args.bot, args.field, args.tables, hands, chips / bb / hands * 100))
    print("%-14s %8s %9s %12s %12s" % ("rule", "actions", "per 100h", "chips bb", "bb per act"))
    for rule in sorted(total):
        cnt, ch = total[rule]
        print("%-14s %8d %9.2f %12.1f %12.2f" % (rule, cnt, cnt * 100.0 / hands, ch / bb, ch / bb / max(1, cnt)))


if __name__ == "__main__":
    main()
