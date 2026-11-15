"""Print our table's standings from the public API JSON on stdin, and our results rows from a second file.

    curl ... /pokerbots/api/public | python3 -I reports/standings.py [results.json]
"""
import json, sys

d = json.load(sys.stdin)
st = d["sunday"]["stages"][0]
print(f"rounds_played {st['rounds_played']} of {st['rounds']} | api now {d.get('now')}")
for t in st["tables"]:
    names = [e["name"] for e in t]
    if "Resonance Qt" in names:
        t = sorted(t, key=lambda e: -e["chips"])
        me = next(i for i, e in enumerate(t) if e["name"] == "Resonance Qt")
        for i, e in enumerate(t):
            print(f"  {i+1}. {e['name']:24s} {e['chips']:+8d} chips  {e['bb100']:+6.1f} bb/100")
        c = t[me]["chips"]
        print(f"US rank {me+1}, chips {c:+d}, gap to 2nd {c - t[1]['chips']:+d}, gap to 3rd {c - t[2]['chips']:+d}, gap to 1st {c - t[0]['chips']:+d}")
if len(sys.argv) > 1:
    r = json.load(open(sys.argv[1]))
    rows = [x for x in r["rounds"] if x["ref"].startswith("sunday")]
    rows.sort(key=lambda x: x["ref"])
    for x in rows[-4:]:
        print(f"  {x['ref']} v{x['version']} bb100 {x['bb100']:+.1f} chips {x['chips']:+d} timeouts {x['timeouts']} errors {x['errors']} bank_out {x['bank_out']} think_s {x['think_s']} viol {len(x['violations'])}")
    v = [x for x in rows if x["version"] != 13]
    if v:
        print(f"  since V22: {len(v)} rounds, avg bb100 {sum(x['bb100'] for x in v)/len(v):+.1f}, chips {sum(x['chips'] for x in v):+d}, timeouts {sum(x['timeouts'] for x in v)}, max think_s {max(x['think_s'] for x in v)}")
