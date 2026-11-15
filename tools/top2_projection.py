"""Projection of Sunday's 36-round table from REAL Saturday round results (public standings history).

Each opponent's rounds are drawn from its own real rounds 31-54 (after the weakest team left);
ours from our real rounds 31-54 plus an assumed edge. Each drawn round is re-centred so the table
sums to zero. Reports our chance of finishing in the top 2.

    python3 tools/top2_projection.py /private/tmp/claude-501/real_rounds.json"""
import json, random, statistics, sys
d = json.load(open(sys.argv[1]))
US = 'Resonance Qt'; OPP = [t for t in d if t != US]
rng = random.Random(7); T = 36; DRAWS = 20000
def run(edge, key='late', opp_shift=None):
    rank = [0] * 8; lead = []
    for _ in range(DRAWS):
        tot = {t: 0.0 for t in d}
        for _r in range(T):
            x = {t: rng.choice(d[t][key]) + ((opp_shift or {}).get(t, 0.0)) for t in OPP}
            x[US] = rng.choice(d[US][key]) + edge
            m = sum(x.values()) / 8.0
            for t in x:
                tot[t] += x[t] - m
        oth = sorted((tot[t] for t in OPP), reverse=True)
        rk = 1 + sum(1 for v in oth if v > tot[US]); rank[rk - 1] += 1
        lead.append((tot[US] - oth[1]) / T)
    lead.sort()
    return 100.0 * rank[0] / DRAWS, 100.0 * (rank[0] + rank[1]) / DRAWS, lead[len(lead) // 2]
print("Late-Saturday form, real rounds 31-54 (mean bb/100): " + ", ".join("%s %+.1f" % (t[:12], statistics.mean(d[t]['late'])) for t in d))
print("\nOur chance over 36 rounds if every opponent plays at its late-Saturday level:")
print("  %-52s %6s %7s %s" % ("our bot", "1st", "TOP 2", "median lead over the 2nd-best opponent"))
for lab, e in (("as on late Saturday (+11.5 real average)", 0.0), ("+5 bb/100 better", 5.0), ("+10 bb/100 better (V22's gain on the simulated table)", 10.0), ("+15 bb/100 better", 15.0), ("+20 bb/100 better", 20.0)):
    a, b, c = run(e)
    print("  %-52s %5.1f%% %6.1f%% %+6.1f bb/100" % (lab, a, b, c))
print("\nSame, using only the last hour (rounds 43-54) for everyone:")
for lab, e in (("as in the last hour (+2.2 real average)", 0.0), ("+10 bb/100 better", 10.0), ("+20 bb/100 better", 20.0)):
    a, b, c = run(e, 'last')
    print("  %-52s %5.1f%% %6.1f%% %+6.1f bb/100" % (lab, a, b, c))
