"""Duplicate duel: every deal is played twice with A and B swapping seats; the rest of the table,
the cards and the seat order are identical. Reports the paired difference A - B.

    python3 tools/duplicate.py A.py B.py --field x.py y.py ... --rounds 30 [--hands 1000] [--betting no_limit] [--raise-cap 0]"""
import argparse, os, random, statistics, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from engine import FixedHandsTable
from engine.players import SubprocessPlayer


def play(job):
    bots, seed, hands, ms, cfg = job
    rng = random.Random(seed)
    order = list(range(len(bots))); rng.shuffle(order)
    seats = [bots[i] for i in order]
    ps = [SubprocessPlayer(os.path.join(ROOT, p), timeout_ms=ms, bank_ms=1e9) for p in seats]
    try:
        res = FixedHandsTable(ps, hands=hands, config=cfg, seed=rng.random()).play()
    finally:
        for p in ps:
            p.close()
    out = {}
    for i, slot in enumerate(order):
        out[slot] = (res["chips"][i], ps[i].stats.timeouts, ps[i].stats.errors)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("A"); ap.add_argument("B")
    ap.add_argument("--field", nargs="+", required=True)
    ap.add_argument("--rounds", type=int, default=30)
    ap.add_argument("--hands", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--par", type=int, default=10)
    ap.add_argument("--ms", type=float, default=60.0)
    ap.add_argument("--betting", default="no_limit")
    ap.add_argument("--raise-cap", type=int, default=0)
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    cfg = {"betting": a.betting, "raise_cap": a.raise_cap}
    seeds = [a.seed * 1000 + r for r in range(a.rounds)]
    jobs = []
    for s in seeds:
        jobs.append(([a.A, a.B] + a.field, s, a.hands, a.ms, cfg))
        jobs.append(([a.B, a.A] + a.field, s, a.hands, a.ms, cfg))
    with Pool(a.par) as p:
        res = p.map(play, jobs, chunksize=1)
    k = 100.0 / 20 / a.hands
    d = []; va = []; vb = []; err = [0, 0]; to = [0, 0]
    for i in range(a.rounds):
        r1, r2 = res[2 * i], res[2 * i + 1]
        A1, B1 = r1[0][0], r1[1][0]          # run 1: A in slot 0
        B2, A2 = r2[0][0], r2[1][0]          # run 2: B in slot 0 (A's former seat)
        va.append((A1 + A2) / 2 * k); vb.append((B1 + B2) / 2 * k)
        d.append(va[-1] - vb[-1])
        to[0] += r1[0][1] + r2[1][1]; to[1] += r1[1][1] + r2[0][1]
        err[0] += r1[0][2] + r2[1][2]; err[1] += r1[1][2] + r2[0][2]
    se = statistics.stdev(d) / len(d) ** 0.5
    print("%-34s %3d deals x2 | %s %+7.1f  %s %+7.1f | A - B = %+6.1f +- %4.1f bb/100 | timeouts %d/%d errors %d/%d" % (
        a.label, a.rounds, os.path.basename(a.A)[:-3], statistics.mean(va), os.path.basename(a.B)[:-3], statistics.mean(vb),
        statistics.mean(d), se, to[0], to[1], err[0], err[1]), flush=True)


if __name__ == "__main__":
    main()
