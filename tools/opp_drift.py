"""Opponent drift test from the public standings only (no hand files needed).

For every team at every Sunday table: the result it should have had if every bot at that table
still played as on Saturday (zero-sum: its Saturday rating minus the table's average rating,
whale rounds excluded), the actual result, the residual and its z-score, a change point in its
Sunday rounds, and which tablemates it wins from. A large positive or negative z means the bot
is not the one we profiled on Saturday, so its Saturday seeds should carry less weight.

    git show origin/rankings-history:rankings/standings-history.csv > /tmp/sat.csv
    git show origin/rankings-history:rankings/sunday-bucket-rounds.csv > /tmp/sun.csv
    python3 tools/opp_drift.py /tmp/sat.csv /tmp/sun.csv"""
import csv, sys, math, statistics as st
sat_p, sun_p = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ('/tmp/sat.csv', '/tmp/sun.csv')
# Saturday rating: mean bb/100 over all counted rounds, and over the last 18 (late form)
rows = [r for r in csv.DictReader(open(sat_p)) if r['phase'] != 'practice']
by = {}
for r in rows: by.setdefault(r['name'], []).append(r)
sat, sat_late, sat_ver = {}, {}, {}
for n, l in by.items():
    l.sort(key=lambda r: r['fetched_at']); prev = None; rr = []
    for r in l:
        if prev and int(r['hands']) > int(prev['hands']):
            rr.append((int(r['chips']) - int(prev['chips'])) / 20 / (int(r['hands']) - int(prev['hands'])) * 100)
        prev = r
    if rr:
        nw = [v for v in rr if v < 120]          # drop whale rounds (ediz_slow tables) before rating
        sat[n] = float(l[-1]['bb100']); sat_late[n] = st.mean(nw[-18:]) if nw else 0.0; sat_ver[n] = l[-1]['version']
# Sunday per-round chips per team
srows = list(csv.DictReader(open(sun_p)))
last = max(int(r['Rounds played']) for r in srows)
cum, table = {}, {}
for r in srows:
    cum.setdefault(r['Team'], {})[int(r['Rounds played'])] = int(r['Chips']); table[r['Team']] = r['Table']
per = {t: [d[k] - d.get(k - 1, 0) for k in sorted(d)] for t, d in cum.items()}
tabs = {}
for t, T in table.items(): tabs.setdefault(T, []).append(t)
print("Sunday rounds:", last, "| snapshot", max(r['Recorded (actual)'] for r in srows))
def corr(a, b):
    ma, mb = st.mean(a), st.mean(b)
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / den if den else 0.0
out = []
for T in sorted(tabs):
    ts = sorted(tabs[T], key=lambda t: -cum[t][last])
    print("\nTable %s" % T)
    print("  %-26s %8s %7s %7s %7s %8s %6s %-7s %s" % ("team", "chips", "sun", "expect", "resid", "z", "sd", "trust", "break"))
    for t in ts:
        x = [c / 200.0 for c in per[t]]       # bb/100 per round
        n = len(x); m = st.mean(x); sd = st.stdev(x)
        others = [o for o in ts if o != t]
        # expected Sunday result if every bot played as on Saturday (late form): zero-sum table,
        # each seat's edge relative to the table average of Saturday ratings
        r_all = [sat_late.get(o, 0.0) for o in ts]
        exp = sat_late.get(t, 0.0) - st.mean(r_all)
        resid = m - exp; z = resid / (sd / math.sqrt(n))
        # change point: split that maximises the difference in means (min 4 rounds a side)
        best = None
        for k in range(4, n - 3):
            a, b = x[:k], x[k:]
            d = st.mean(b) - st.mean(a); se = math.sqrt(st.variance(a) / len(a) + st.variance(b) / len(b))
            if best is None or abs(d / se) > abs(best[1]): best = (k + 1, d / se, d)
        brk = "r%d %+.0f (z %+.1f)" % (best[0], best[2], best[1]) if best and abs(best[1]) >= 2.5 else "-"
        trust = "high" if abs(z) < 2 else ("low" if abs(z) < 3 else "none")
        print("  %-26s %+8d %+7.1f %+7.1f %+7.1f %+8.1f %6.0f %-7s %s" % (t, cum[t][last], m, exp, resid, z, sd, trust, brk))
        out.append((T, t, m, exp, resid, z, sd, brk, x))
    # chip sources for the top two: correlation of their round result with each tablemate's
    for t in ts[:2]:
        x = per[t]
        cs = sorted(((corr(x, per[o]), o) for o in ts if o != t))
        print("    %s wins when these lose (corr): %s" % (t, ", ".join("%s %+.2f" % (o, c) for c, o in cs[:3])))
