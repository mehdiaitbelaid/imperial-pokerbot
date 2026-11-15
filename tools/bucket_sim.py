"""Simulate Sunday's bucket stage: our bot in one seat against a fixed field, many 1,000-hand rounds.

    python3 tools/bucket_sim.py OUT.json --bots A.py B.py --field f1.py ... f7.py --rounds 1080 --seed 7

Every round is played once per bot in --bots, with the same cards and seat order (paired).
Saves per-round chips of every seat; tools/bucket_report.py turns them into 36-round tournaments."""
import argparse, json, os, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from duplicate import play


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--bots", nargs="+", required=True)
    ap.add_argument("--field", nargs="+", required=True)
    ap.add_argument("--rounds", type=int, default=360)
    ap.add_argument("--hands", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--par", type=int, default=9)
    ap.add_argument("--ms", type=float, default=60.0)
    a = ap.parse_args()
    cfg = {"betting": "no_limit", "raise_cap": 0}
    jobs = []
    for r in range(a.rounds):
        for b in a.bots:
            jobs.append(([b] + a.field, a.seed * 100000 + r, a.hands, a.ms, cfg))
    with Pool(a.par) as p:
        res = p.map(play, jobs, chunksize=2)
    out = {"bots": a.bots, "field": a.field, "hands": a.hands, "rounds": a.rounds, "data": {b: [] for b in a.bots}, "to": {b: 0 for b in a.bots}, "err": {b: 0 for b in a.bots}}
    i = 0
    for r in range(a.rounds):
        for b in a.bots:
            x = res[i]; i += 1
            out["data"][b].append([x[k][0] for k in range(len(a.field) + 1)])
            out["to"][b] += x[0][1]; out["err"][b] += x[0][2]
    json.dump(out, open(a.out, "w"))
    print("saved", a.out, a.rounds, "rounds x", len(a.bots), "bots")


if __name__ == "__main__":
    main()
