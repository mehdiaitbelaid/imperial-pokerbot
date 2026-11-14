"""Local matches with low-noise comparisons.

    # line-up of up to 8 bots, 20 rounds, 4 in parallel, hands saved for tools/analyze.py
    python tools/selfplay.py bots/avengers.py bots/v2.py sparring/tag.py ... --rounds 20 --out sim/run1

    # A/B: same seats and same cards, first bot swapped for --vs; reports the paired difference
    python tools/selfplay.py bots/avengers.py sparring/tag.py ... --vs bots/v2.py --rounds 20

Rounds run in parallel with a relaxed clock (strategy test, not a timing test);
use local_sim.py for timing.
"""
import argparse
import json
import os
import random
import statistics
import sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine import FixedHandsTable  # noqa: E402
from engine.players import SubprocessPlayer  # noqa: E402


def play(job):
    bots, seed, hands, record, ms = job
    rng = random.Random(seed)
    order = list(range(len(bots)))
    rng.shuffle(order)
    seats = [bots[i] for i in order]
    ps = [SubprocessPlayer(os.path.join(ROOT, p), timeout_ms=ms, bank_ms=1e9) for p in seats]
    try:
        res = FixedHandsTable(ps, hands=hands, seed=rng.random(), record=record).play()
    finally:
        for p in ps:
            p.close()
    out = {"chips": {}, "stats": {}, "log": None, "seats": seats}
    for i, slot in enumerate(order):
        out["chips"][slot] = res["chips"][i]
        st = ps[i].stats
        out["stats"][slot] = (st.timeouts, st.errors, st.total_ms / 1000.0, st.max_ms,
                              st.error_samples[0][-500:] if st.error_samples else None)
    if record:
        out["log"] = [{"n": h["n"], "button": h["button"], "hole": h["hole"], "showdown": h.get("showdown", {}),
                       "board": h["board"], "events": h["events"],
                       "results": [e - s for e, s in zip(h["end"], h["stacks"])]} for h in res["log"]]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bots", nargs="+")
    ap.add_argument("--vs", nargs="*", default=[], help="replay every round with the first bot replaced by each of these")
    ap.add_argument("--rounds", type=int, default=12)
    ap.add_argument("--hands", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--par", type=int, default=4)
    ap.add_argument("--ms", type=float, default=60.0)
    ap.add_argument("--out", help="directory to save hand histories (analyze.py format)")
    ap.add_argument("--pool", nargs="*", default=[], help="tournament mode: each round the first bot meets 7 bots drawn from this pool")
    a = ap.parse_args()
    bots = a.bots
    seeds = [a.seed * 1000 + r for r in range(a.rounds)]
    if a.pool:
        tables = [[bots[0]] + random.Random(s).sample(a.pool, 7) for s in seeds]
    else:
        tables = [bots for s in seeds]
    jobs = [(t, s, a.hands, bool(a.out), a.ms) for t, s in zip(tables, seeds)]
    for alt_bot in a.vs:
        jobs += [([alt_bot] + t[1:], s, a.hands, False, a.ms) for t, s in zip(tables, seeds)]
    with Pool(a.par) as pool:
        res = pool.map(play, jobs, chunksize=1)
    main_res = res[:a.rounds]
    k = 100.0 / 20 / a.hands
    print("%-28s %8s %6s %4s %4s %6s %7s" % ("bot", "bb/100", "se", "to", "err", "s/rd", "max ms"))
    rows = []
    if a.pool:
        per = {}
        for t, r in zip(tables, main_res):
            for slot, b in enumerate(t):
                per.setdefault(b, []).append(r["chips"][slot] * k)
        print("tournament mode, %d rounds, opponents drawn from a pool of %d" % (a.rounds, len(a.pool)))
        for b, v in sorted(per.items(), key=lambda kv: -statistics.mean(kv[1])):
            se = statistics.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0
            print("%-28s %+8.1f %6.1f   (%d rounds)" % (b, statistics.mean(v), se, len(v)))
    for slot, b in enumerate(bots if not a.pool else []):
        v = [r["chips"][slot] * k for r in main_res]
        se = statistics.stdev(v) / len(v) ** 0.5 if len(v) > 1 else 0.0
        st = [r["stats"][slot] for r in main_res]
        rows.append((statistics.mean(v), b, se, sum(s[0] for s in st), sum(s[1] for s in st),
                     max(s[2] for s in st), max(s[3] for s in st)))
        for s in st:
            if s[4]:
                print("ERROR in", b, "\n", s[4])
                break
    for m, b, se, to, er, srd, mx in sorted(rows, reverse=True):
        print("%-28s %+8.1f %6.1f %4d %4d %6.2f %7.1f" % (b, m, se, to, er, srd, mx))
    if a.vs:
        base = [r["chips"][0] * k for r in main_res]
        print("\nSame seat, same cards (%d rounds x %d hands):" % (a.rounds, a.hands))
        print("  %-26s %+8.1f  (reference)" % (bots[0], statistics.mean(base)))
        for j, alt_bot in enumerate(a.vs):
            alt = res[a.rounds * (j + 1): a.rounds * (j + 2)]
            vb = [r["chips"][0] * k for r in alt]
            d = [vb[i] - base[i] for i in range(a.rounds)]
            se = statistics.stdev(d) / len(d) ** 0.5 if len(d) > 1 else 0.0
            to = sum(r["stats"][0][0] for r in alt); er = sum(r["stats"][0][1] for r in alt)
            print("  %-26s %+8.1f  vs reference %+7.1f +- %.1f%s" % (alt_bot, statistics.mean(vb), statistics.mean(d), se,
                  "  ERRORS %d" % er if er else ""))
    if a.out:
        os.makedirs(os.path.join(ROOT, a.out), exist_ok=True)
        for i, r in enumerate(main_res):
            seat = r["seats"].index(bots[0])
            json.dump({"players": [os.path.basename(p)[:-3] for p in r["seats"]], "seat": seat, "hands": r["log"]},
                      open(os.path.join(ROOT, a.out, "r%03d.json" % i), "w"))
        print("saved", a.rounds, "rounds to", a.out)


if __name__ == "__main__":
    main()
