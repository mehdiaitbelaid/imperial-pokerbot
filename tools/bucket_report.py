"""Turn tools/bucket_sim.py output into 36-round tournaments (bootstrap) and report each bot's
chance of finishing in the top 2 of the table.

    python3 tools/bucket_report.py OUT.json [--rounds-per-tournament 36] [--draws 20000]"""
import json, os, random, statistics, sys
d = json.load(open(sys.argv[1]))
T = 36; DRAWS = 20000
for i, a in enumerate(sys.argv):
    if a == "--rounds-per-tournament": T = int(sys.argv[i + 1])
    if a == "--draws": DRAWS = int(sys.argv[i + 1])
k = 100.0 / 20 / d["hands"]
names = ["US"] + [os.path.basename(f)[:-3] for f in d["field"]]
rng = random.Random(12345)
print("%d rounds of %d hands per bot (%s hands each); tournaments of %d rounds, %d bootstrap draws" % (d["rounds"], d["hands"], format(d["rounds"] * d["hands"], ","), T, DRAWS))
per = {}
for b in d["bots"]:
    rows = d["data"][b]; n = len(rows)
    us = [r[0] * k for r in rows]
    print("\n== %s in our seat: %+.1f bb/100 (+- %.1f), round sd %.0f, timeouts %d, errors %d" % (os.path.basename(b), statistics.mean(us), statistics.stdev(us) / n ** 0.5, statistics.stdev(us), d["to"][b], d["err"][b]))
    print("   opponents: " + "  ".join("%s %+.1f" % (names[j], statistics.mean(r[j] * k for r in rows)) for j in range(1, len(names))))
    rank = [0] * len(names); margin3 = []
    for _ in range(DRAWS):
        tot = [0.0] * len(names)
        for _i in range(T):
            r = rows[rng.randrange(n)]
            for j in range(len(names)):
                tot[j] += r[j]
        others = sorted(tot[1:], reverse=True)
        rk = 1 + sum(1 for x in tot[1:] if x > tot[0])
        rank[rk - 1] += 1
        margin3.append((tot[0] - others[1]) * k / T)       # our lead over the second-best opponent = cushion for a top-2 finish
    margin3.sort()
    print("   over %d rounds: 1st %.1f%%, 2nd %.1f%%, TOP 2 %.1f%%, 3rd or worse %.1f%%" % (T, 100.0 * rank[0] / DRAWS, 100.0 * rank[1] / DRAWS, 100.0 * (rank[0] + rank[1]) / DRAWS, 100.0 * sum(rank[2:]) / DRAWS))
    print("   lead over the second-best opponent (bb/100): median %+.1f, 5%% worst case %+.1f" % (margin3[len(margin3) // 2], margin3[len(margin3) // 20]))
    # non-overlapping tournaments
    nt = n // T; top2 = 0
    for t in range(nt):
        tot = [sum(rows[t * T + i][j] for i in range(T)) for j in range(len(names))]
        top2 += (1 + sum(1 for x in tot[1:] if x > tot[0])) <= 2
    print("   %d separate tournaments played back to back: top 2 in %d" % (nt, top2))
    per[b] = us
if len(d["bots"]) == 2:
    a, b = d["bots"]; diff = [x - y for x, y in zip(per[a], per[b])]
    print("\nSame cards: %s - %s = %+.1f +- %.1f bb/100" % (os.path.basename(a), os.path.basename(b), statistics.mean(diff), statistics.stdev(diff) / len(diff) ** 0.5))
