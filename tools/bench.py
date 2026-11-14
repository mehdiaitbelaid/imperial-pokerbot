"""Benchmark bots against named fields, in parallel, with tournament limits.

    python3 tools/bench.py bot.py --field mixed --rounds 20
    python3 tools/bench.py bot.py --field stations --rounds 20 --jobs 4
    python3 tools/bench.py bot.py versions/v0_starter.py --rounds 20
    python3 tools/bench.py bot.py --field self --rounds 10 --betting pot_limit

One bot: it sits with fillers drawn from the field. Two or more bots: they
share every table, fillers fill the rest, and each seed is played twice with
the first two bots swapping seats (and so cards), which cancels most card luck.
Every bot runs in its own process with the 10 ms per decision and 10 s per
round limits, exactly like local_sim.py. Every run is appended to
results/bench.csv.
"""
import argparse
import csv
import glob
import math
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from engine import FixedHandsTable  # noqa: E402
from engine.players import SubprocessPlayer  # noqa: E402

BIG_BLIND = 20
# Fields that always seat these bots before drawing the rest from the pool.
# "field" is the main accept or reject field: field_like models the live
# practice tables (a model of the field, not the field), plus one maniac and
# one station as the live tables have.
FIXED = {"tight": ["sparring/maniac.py"],
         "field": ["sparring/maniac.py", "sparring/calling_station_plus.py"]}
# Behaviour bands a release candidate should sit in (from docs/x-findings.md).
VPIP_BAND = (0.22, 0.35)
PFR_BAND = (0.17, 0.27)


def _glob(pattern):
    return sorted(p for p in glob.glob(os.path.join(HERE, pattern)) if not os.path.basename(p).startswith("_"))


def fields():
    sp = lambda name: os.path.join(HERE, "sparring", name + ".py")  # noqa: E731
    ex = lambda name: os.path.join(HERE, "examples", name + ".py")  # noqa: E731
    return {
        "field": [sp("field_like")],
        "fieldonly": [sp("field_like")],
        "tight": [sp("nit"), sp("tag_basic"), sp("pot_odds_bot"), ex("tight_aggressive"), sp("tag_basic")],
        "house": _glob("examples/*.py"),
        "mixed": _glob("sparring/*.py") + _glob("examples/*.py"),
        "stations": [sp("calling_station_plus"), ex("calling_station")],
        "maniacs": [sp("maniac"), sp("allin_spammer")],
        "nits": [sp("nit")],
        "minraisers": [sp("minraiser")],
        "tags": [sp("tag_basic")],
        "lags": [sp("lag_basic")],
        "potodds": [sp("pot_odds_bot")],
        "random": [ex("random_bot")],
        "self": _glob("versions/*.py"),
    }


def label(path):
    rel = os.path.relpath(path, HERE)
    return os.path.basename(path) if rel.startswith("..") else rel


def resolve(path):
    for cand in (os.path.abspath(path), os.path.join(HERE, path)):
        if os.path.isfile(cand):
            return cand
    sys.exit("Can't find bot file: %s" % path)


def play_table(job):
    """Run one 1,000 hand table in this worker. Returns per seat results."""
    seats, hands, config, seed, timeout_ms, bank_s = job
    players = [SubprocessPlayer(p, timeout_ms=timeout_ms, bank_ms=bank_s * 1000) for p in seats]
    t0 = time.time()
    try:
        res = FixedHandsTable(players, hands=hands, config=config, seed=seed, record=True).play()
    finally:
        for p in players:
            p.close()
    vpip = [0] * len(seats)
    pfr = [0] * len(seats)
    for rec in res["log"] or []:
        v, r = set(), set()
        for ev in rec["events"]:
            if ev[0] == "board":
                break
            if ev[0] == "act" and ev[2] in ("call", "raise"):
                v.add(ev[1])
                if ev[2] == "raise":
                    r.add(ev[1])
        for i in v:
            vpip[i] += 1
        for i in r:
            pfr[i] += 1
    out = []
    for i, p in enumerate(players):
        st = p.stats
        out.append({"path": seats[i], "chips": res["chips"][i], "hands": res["hands"],
                    "timeouts": st.timeouts, "errors": st.errors, "bank_out": st.bank_out,
                    "think_s": st.total_ms / 1000.0, "max_ms": st.max_ms,
                    "vpip": vpip[i], "pfr": pfr[i],
                    "error": st.error_samples[0] if st.error_samples else None})
    return {"seed": seed, "seats": out, "wall": time.time() - t0}


T95 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26,
       10: 2.23, 12: 2.18, 15: 2.13, 20: 2.09, 25: 2.06, 30: 2.04}


def tcrit(df):
    if df <= 0:
        return float("nan")
    best = 1.96
    for k in sorted(T95):
        if df <= k:
            return T95[k]
    return best


def mean_se(xs):
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan")
    m = sum(xs) / n
    if n == 1:
        return m, float("nan")
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(var / n)


def git_commit():
    try:
        h = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=HERE,
                                    stderr=subprocess.DEVNULL).decode().strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=HERE,
                                        stderr=subprocess.DEVNULL).decode().strip()
        return h + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bots", nargs="+", help="bot files to test")
    ap.add_argument("--field", default="mixed", help="filler pool: " + ", ".join(sorted(fields())))
    ap.add_argument("--rounds", type=int, default=20, help="seeds to play (two tables each when comparing bots)")
    ap.add_argument("--hands", type=int, default=1000)
    ap.add_argument("--seats", type=int, default=8, help="seats per table; 0 draws 6 to 8 each table")
    ap.add_argument("--jobs", type=int, default=0, help="parallel tables (default a third of the cores, capped at half)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--betting", choices=["no_limit", "pot_limit", "fixed_limit"], default="no_limit")
    ap.add_argument("--raise-cap", type=int, default=0)
    ap.add_argument("--timeout", type=float, default=10.0, help="ms per decision")
    ap.add_argument("--bank", type=float, default=10.0, help="seconds of thinking per round")
    ap.add_argument("--no-mirror", action="store_true", help="do not replay seeds with seats swapped")
    ap.add_argument("--no-csv", action="store_true")
    args = ap.parse_args()

    bots = [resolve(b) for b in args.bots]
    if len(set(bots)) != len(bots):
        sys.exit("Name each bot once.")
    if len(bots) > (args.seats or 6):
        sys.exit("Too many bots for %d seats." % args.seats)
    pool_map = fields()
    if args.field not in pool_map:
        sys.exit("Unknown field %s. Pick one of: %s" % (args.field, ", ".join(sorted(pool_map))))
    pool = [p for p in pool_map[args.field] if p not in bots and os.path.isfile(p)]
    fixed = [os.path.join(HERE, p) for p in FIXED.get(args.field, [])]
    if not pool:
        sys.exit("Field %s has no filler bots left." % args.field)

    cores = os.cpu_count() or 2
    cap = max(1, cores // 2)
    jobs = args.jobs or max(1, cores // 3)
    if jobs > cap:
        print("jobs capped at %d (half of %d cores) so timing stays honest" % (cap, cores))
        jobs = cap

    seed = args.seed if args.seed is not None else random.randrange(1 << 30)
    rng = random.Random(seed)
    config = {"betting": args.betting, "raise_cap": args.raise_cap}
    mirror = len(bots) >= 2 and not args.no_mirror
    tables = []
    for r in range(args.rounds):
        nseat = args.seats or rng.choice([6, 7, 8])
        seats = list(bots) + fixed[:max(0, nseat - len(bots))]
        seats += [rng.choice(pool) for _ in range(nseat - len(seats))]
        rng.shuffle(seats)
        tseed = rng.random()
        tables.append((r, seats, tseed))
        if mirror:
            sw = list(seats)
            i, j = sw.index(bots[0]), sw.index(bots[1])
            sw[i], sw[j] = sw[j], sw[i]
            tables.append((r, sw, tseed))

    print("field %s, %d table(s) of %d hands, %d job(s), seed %d, %s%s" % (
        args.field, len(tables), args.hands, jobs, seed, args.betting,
        ", raise cap %d" % args.raise_cap if args.raise_cap else ""))
    work = [(seats, args.hands, config, tseed, args.timeout, args.bank) for _, seats, tseed in tables]
    t0 = time.time()
    results = []
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        for k, res in enumerate(ex.map(play_table, work)):
            results.append(res)
            print("\rtable %d/%d" % (k + 1, len(work)), end="", flush=True)
    print()

    per = {b: {"bb": [], "to": 0, "er": 0, "bo": 0, "think": 0.0, "maxms": 0.0, "err": None,
               "hands": 0, "vpip": 0, "pfr": 0} for b in bots}
    per_seed = {}
    for (r, _, _), res in zip(tables, results):
        for s in res["seats"]:
            b = s["path"]
            if b not in per:
                continue
            d = per[b]
            bb100 = s["chips"] / BIG_BLIND / max(1, s["hands"]) * 100
            d["bb"].append(bb100)
            d["to"] += s["timeouts"]
            d["er"] += s["errors"]
            d["bo"] += s["bank_out"]
            d["think"] = max(d["think"], s["think_s"])
            d["maxms"] = max(d["maxms"], s["max_ms"])
            d["hands"] += s["hands"]
            d["vpip"] += s["vpip"]
            d["pfr"] += s["pfr"]
            if s["error"] and not d["err"]:
                d["err"] = s["error"]
            per_seed.setdefault(r, {}).setdefault(b, []).append(bb100)

    print("\n%-30s %9s %7s %19s %8s %6s %8s %8s %8s" % (
        "bot", "bb/100", "se", "95% interval", "timeouts", "errors", "bank out", "think s", "max ms"))
    rows = []
    for b in bots:
        d = per[b]
        m, se = mean_se(d["bb"])
        h = tcrit(len(d["bb"]) - 1) * se if len(d["bb"]) > 1 else float("nan")
        print("%-30s %+9.1f %7.1f %8.1f to %8.1f %8d %6d %8d %8.2f %8.1f" % (
            label(b), m, se, m - h, m + h, d["to"], d["er"], d["bo"], d["think"], d["maxms"]))
        rows.append((b, m, se, m - h, m + h, d))
        if d["err"]:
            print("  first error from %s:\n%s" % (label(b), d["err"]))
    print("\nbehaviour (bands: VPIP %.0f to %.0f%%, PFR %.0f to %.0f%%)" % (
        VPIP_BAND[0] * 100, VPIP_BAND[1] * 100, PFR_BAND[0] * 100, PFR_BAND[1] * 100))
    for b in bots:
        d = per[b]
        v = d["vpip"] / float(max(1, d["hands"]))
        r = d["pfr"] / float(max(1, d["hands"]))
        flag = []
        if not VPIP_BAND[0] <= v <= VPIP_BAND[1]:
            flag.append("VPIP OUT OF BAND")
        if not PFR_BAND[0] <= r <= PFR_BAND[1]:
            flag.append("PFR OUT OF BAND")
        d["vp"], d["pf"] = v, r
        print("%-30s VPIP %5.1f%%  PFR %5.1f%%  %s" % (label(b), v * 100, r * 100, ", ".join(flag)))
    if len(bots) >= 2:
        a, b = bots[0], bots[1]
        diffs = []
        for r in sorted(per_seed):
            xa, xb = per_seed[r].get(a), per_seed[r].get(b)
            if xa and xb:
                diffs.append(sum(xa) / len(xa) - sum(xb) / len(xb))
        m, se = mean_se(diffs)
        h = tcrit(len(diffs) - 1) * se if len(diffs) > 1 else float("nan")
        print("\npaired difference %s minus %s: %+.1f bb/100, se %.1f, 95%% interval %.1f to %.1f over %d seeds" % (
            label(a), label(b), m, se, m - h, m + h, len(diffs)))
    print("%.1fs elapsed" % (time.time() - t0))

    if not args.no_csv:
        os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
        path = os.path.join(HERE, "results", "bench.csv")
        new = not os.path.exists(path)
        commit = git_commit()
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        others = ";".join(label(x) for x in bots)
        with open(path, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["timestamp", "commit", "bot", "field", "rounds", "tables", "hands", "betting",
                            "raise_cap", "bb100", "se", "ci95_lo", "ci95_hi", "timeouts", "errors",
                            "bank_out", "think_s_max", "max_ms", "seed", "bots_at_table", "vpip", "pfr"])
            for b, m, se, lo, hi, d in rows:
                w.writerow([stamp, commit, label(b), args.field, args.rounds, len(d["bb"]), args.hands,
                            args.betting, args.raise_cap, "%.2f" % m, "%.2f" % se, "%.2f" % lo, "%.2f" % hi,
                            d["to"], d["er"], d["bo"], "%.2f" % d["think"], "%.1f" % d["maxms"], seed, others,
                            "%.3f" % d["vp"], "%.3f" % d["pf"]])
        print("appended %d row(s) to %s" % (len(rows), label(path)))


if __name__ == "__main__":
    main()
