"""Calibrate sparring/field_like.py so its fold rates match the live field.

    python3 tools/calibrate_field.py               # 3 passes, prints QUANT and fold rates
    python3 tools/calibrate_field.py --check       # one pass with the stored QUANT, no refit

Each pass plays in process tables (field_like seats, our bot, one maniac, one
station), records the strength field_like holds every time it faces a first
bet, and refits the per spot strength quantiles. The fold decision is a
strength cutoff at the measured fold rate, so after a refit the rates land on
the targets while folds still go to the weakest hands.
"""
import argparse
import importlib.util
import os
import random
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from engine import FixedHandsTable  # noqa: E402
from engine.players import LocalPlayer  # noqa: E402


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def play(fl, others, tables, hands, seed):
    rng = random.Random(seed)
    fl.LOG.clear()
    vp = pf = hn = 0
    for t in range(tables):
        n = rng.choice([6, 7, 8])
        classes = list(others)
        classes += [fl.Agent] * (n - len(classes))
        rng.shuffle(classes)
        players = [LocalPlayer(c) for c in classes]
        res = FixedHandsTable(players, hands=hands, seed=rng.random(), record=True).play()
        idx = [i for i, c in enumerate(classes) if c is fl.Agent]
        for rec in res["log"]:
            v, r = set(), set()
            for ev in rec["events"]:
                if ev[0] == "board":
                    break
                if ev[0] == "act" and ev[2] in ("call", "raise"):
                    v.add(ev[1])
                    if ev[2] == "raise":
                        r.add(ev[1])
            for i in idx:
                hn += 1
                vp += i in v
                pf += i in r
    return vp / float(hn), pf / float(hn)


def quantiles(xs):
    xs = sorted(xs)
    out = []
    for k in range(21):
        out.append(round(xs[min(len(xs) - 1, int(k / 20.0 * (len(xs) - 1) + 0.5))], 3))
    out[0] = 0.0
    out[-1] = 0.99
    return out


def report(fl, vpip, pfr):
    print("field_like VPIP %.3f PFR %.3f (field 0.24, 0.15)" % (vpip, pfr))
    by = {}
    for key, s, f, frac in fl.LOG:
        by.setdefault(key, []).append((s, f, frac))
    print("%-12s %6s %7s %7s" % ("spot", "n", "fold", "target"))
    for key in sorted(by):
        xs = by[key]
        print("%-12s %6d %7.2f %7.2f" % (key, len(xs), sum(f for _, f, _ in xs) / len(xs), fl.FOLD[key]))
    cb = by.get("cbet", [])
    for lo, hi in ((0, 0.4), (0.4, 0.7), (0.7, 1.1), (1.1, 99)):
        xs = [f for _, f, fr in cb if lo <= fr < hi]
        if xs:
            print("  cbet size %.1f..%.1f n %d fold %.2f" % (lo, hi, len(xs), sum(xs) / len(xs)))
    return by


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--tables", type=int, default=12)
    ap.add_argument("--hands", type=int, default=500)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true", help="store the refit QUANT in sparring/field_like.py")
    ap.add_argument("--bot", default="versions/v2.py")
    ap.add_argument("--plain", action="store_true", help="no maniac or station, for the preflop rates")
    args = ap.parse_args()
    fl = load("sparring/field_like.py", "field_like_cal")
    fl.RECORD = True
    others = [load(args.bot, "us").Agent, load("sparring/maniac.py", "man").Agent,
              load("sparring/calling_station_plus.py", "sta").Agent]
    if args.plain:
        others = others[:1]
    passes = 1 if args.check else args.passes
    for p in range(passes):
        vpip, pfr = play(fl, others, args.tables, args.hands, 1000 + p)
        by = report(fl, vpip, pfr)
        if args.check:
            return
        new = {}
        for key, xs in by.items():
            if len(xs) >= 40:
                new[key] = quantiles([s for s, _, _ in xs])
        fl.QUANT.update(new)
    text = "QUANT = {\n" + "".join('    "%s": [%s],\n' % (k, ", ".join("%.3f" % x for x in fl.QUANT[k]))
                                    for k in sorted(fl.QUANT)) + "}\n"
    print(text)
    if args.write:
        path = os.path.join(HERE, "sparring", "field_like.py")
        src = open(path).read()
        a = src.index("QUANT = {")
        b = src.index("}\n", a) + 2
        open(path, "w").write(src[:a] + text + src[b:])
        print("wrote QUANT to sparring/field_like.py")
    vpip, pfr = play(fl, others, args.tables, args.hands, 999)
    print("\nafter refit:")
    report(fl, vpip, pfr)


if __name__ == "__main__":
    main()
