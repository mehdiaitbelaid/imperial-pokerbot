"""Compare several of our bots from a tools/bucket_sim.py file (same cards and seats for each).

    python3 tools/final_report.py sim/final_a.json"""
import json, os, statistics, sys
d = json.load(open(sys.argv[1]))
k = 100.0 / 20 / d["hands"]; names = ["US"] + [os.path.basename(f)[:-3] for f in d["field"]]
ref = d["bots"][0]; base = [r[0] * k for r in d["data"][ref]]
print("%d games of %d hands per bot (%s hands each); opponents: %s" % (d["rounds"], d["hands"], format(d["rounds"] * d["hands"], ","), ", ".join(names[1:])))
print("%-18s %9s %6s %8s %14s   %s" % ("our bot", "bb/100", "+-", "game sd", "vs " + os.path.basename(ref)[:-3], "timeouts/errors"))
for b in d["bots"]:
    us = [r[0] * k for r in d["data"][b]]; n = len(us)
    diff = [x - y for x, y in zip(us, base)]
    print("%-18s %+9.1f %6.1f %8.0f %+8.1f +- %3.1f   %d/%d" % (os.path.basename(b)[:-3], statistics.mean(us), statistics.stdev(us) / n ** 0.5, statistics.stdev(us),
          statistics.mean(diff), (statistics.stdev(diff) / n ** 0.5) if b != ref else 0.0, d["to"][b], d["err"][b]))
rows = d["data"][ref]
print("opponents against the first bot: " + "  ".join("%s %+.1f" % (names[j], statistics.mean(r[j] * k for r in rows)) for j in range(1, len(names))))
