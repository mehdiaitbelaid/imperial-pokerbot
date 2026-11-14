"""Counted-round simulation split by table type.

    python3 tools/league.py --focus A.py B.py C.py --pool <bots> --rounds 40

Every round draws 7 opponents from the pool; each focus bot then plays that table in the same
seat with the same cards. Results are reported separately for tables that contain a
starter-kit whale and tables that do not, with paired differences against the first focus bot.
"""
import argparse, os, random, statistics, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from selfplay import play

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--focus", nargs="+", required=True)
    ap.add_argument("--pool", nargs="+", required=True)
    ap.add_argument("--rounds", type=int, default=40)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--par", type=int, default=10)
    ap.add_argument("--ms", type=float, default=60.0, help="per-decision limit; 60 = relaxed (strategy only), small = also punishes slow decisions")
    a = ap.parse_args()
    seeds = [a.seed * 1000 + r for r in range(a.rounds)]
    tables = [random.Random(s).sample(a.pool, 7) for s in seeds]
    jobs = [([b] + t, s, 1000, False, a.ms) for b in a.focus for t, s in zip(tables, seeds)]
    with Pool(a.par) as p:
        res = p.map(play, jobs, chunksize=1)
    k = 100.0 / 20 / 1000
    val = {b: [res[i * a.rounds + r]["chips"][0] * k for r in range(a.rounds)] for i, b in enumerate(a.focus)}
    tos = {b: sum(res[i * a.rounds + r]["stats"][0][0] for r in range(a.rounds)) for i, b in enumerate(a.focus)}
    thk = {b: sum(res[i * a.rounds + r]["stats"][0][2] for r in range(a.rounds)) / a.rounds for i, b in enumerate(a.focus)}
    print("limit %.1f ms per decision | timeouts over all rounds and thinking seconds per round:" % a.ms)
    for b in a.focus:
        print("  %-22s timeouts %4d   think %.2f s/round" % (b, tos[b], thk[b]))
    whale = [any("starter" in x for x in t) for t in tables]
    groups = (("ALL TABLES", [True] * a.rounds), ("with a starter-kit whale", whale), ("no whale", [not w for w in whale]))
    for name, mask in groups:
        idx = [i for i in range(a.rounds) if mask[i]]
        if len(idx) < 2:
            continue
        print("\n%s (%d rounds = %d hands per bot)" % (name, len(idx), len(idx) * 1000))
        base = [val[a.focus[0]][i] for i in idx]
        for b in a.focus:
            v = [val[b][i] for i in idx]
            d = [x - y for x, y in zip(v, base)]
            se = statistics.stdev(v) / len(v) ** 0.5
            sd = statistics.stdev(d) / len(d) ** 0.5 if b != a.focus[0] else 0.0
            print("  %-22s %+8.1f +- %4.1f%s" % (b, statistics.mean(v), se,
                  "" if b == a.focus[0] else "   vs first: %+6.1f +- %.1f" % (statistics.mean(d), sd)))

if __name__ == "__main__":
    main()
