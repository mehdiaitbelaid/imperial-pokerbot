"""Chance of finishing 1st / top 2 in simulated finals, with a handicap on our own chips.

    python3 tools/rank_report.py sim/final_rank2.json 8.5      (handicap in chips per hand)"""
import json, os, statistics, sys
d = json.load(open(sys.argv[1])); h = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
H = h * d["hands"]; k = 100.0 / 20 / d["hands"]
print("%d finals of %d hands per bot; handicap on our chips: %.1f bb/100" % (d["rounds"], d["hands"], H * k))
print("  %-14s %9s %6s %8s %7s %7s %9s" % ("bot", "raw bb/100", "+-", "game sd", "1st", "top 2", "prize GBP"))
T = {}
for b in d["bots"]:
    rows = d["data"][b]; n = len(rows); us = [r[0] * k for r in rows]; f = t2 = 0; flags = []
    for r in rows:
        rk = 1 + sum(1 for x in r[1:] if x > r[0] - H); f += rk == 1; t2 += rk <= 2; flags.append(rk)
    T[b] = (us, flags)
    print("  %-14s %+9.1f %6.1f %8.1f %6.1f%% %6.1f%% %9.0f" % (os.path.basename(b)[:-3], statistics.mean(us), statistics.stdev(us) / n ** 0.5, statistics.stdev(us),
          100.0 * f / n, 100.0 * t2 / n, (500.0 * f + 200.0 * (t2 - f)) / n))
ref = d["bots"][-1]
for b in d["bots"][:-1]:
    up = sum(1 for x, y in zip(T[b][1], T[ref][1]) if x <= 2 < y); dn = sum(1 for x, y in zip(T[b][1], T[ref][1]) if y <= 2 < x)
    u1 = sum(1 for x, y in zip(T[b][1], T[ref][1]) if x == 1 and y != 1); d1 = sum(1 for x, y in zip(T[b][1], T[ref][1]) if y == 1 and x != 1)
    df = [x - y for x, y in zip(T[b][0], T[ref][0])]
    print("  %s vs %s, same cards: %+.1f +- %.1f bb/100 | top 2 only for it %d, only for the other %d | 1st only for it %d, only for the other %d" % (
        os.path.basename(b)[:-3], os.path.basename(ref)[:-3], statistics.mean(df), statistics.stdev(df) / len(df) ** 0.5, up, dn, u1, d1))
