"""Our big postflop calls (to call >= MIN chips), by what we held at the moment of the call.

    python3 -I reports/bigcalls.py hands/sunday_s1_r002.json ... [--min 500] [--list]

Class at the call: nopair (hole cards add no pair or better), pair (one pair made with a hole card,
also when the board itself is paired), strong (two pair using a hole card on an unpaired board, trips or better).
"fd" marks four to a flush with a hole card before the river.
"""
import json, sys
from collections import defaultdict, Counter
from itertools import combinations

R = "23456789TJQKA"
AB = {"Resonance Qt": "US", "Anker Batteries": "ANK", "Chinese people can fly": "CPF", "WBot": "WB",
      "GamesGone": "GG", "Poke": "POK", "Anton": "ANT", "YSL_TWIZZY": "YSL"}


def cat5(cs):
    rs = sorted((R.index(c[0]) for c in cs), reverse=True)
    cnt = sorted(Counter(rs).values(), reverse=True)
    fl = len(cs) == 5 and len({c[1] for c in cs}) == 1
    u = sorted(set(rs))
    st = len(cs) == 5 and len(u) == 5 and (u[-1] - u[0] == 4 or u == [0, 1, 2, 3, 12])
    if st and fl: return 8
    if cnt[0] == 4: return 7
    if cnt[0] == 3 and len(cnt) > 1 and cnt[1] >= 2: return 6
    if fl: return 5
    if st: return 4
    if cnt[0] == 3: return 3
    if cnt[0] == 2 and len(cnt) > 1 and cnt[1] == 2: return 2
    if cnt[0] == 2: return 1
    return 0


def best(cs):
    if len(cs) <= 5:
        return cat5(cs)
    return max(cat5(c) for c in combinations(cs, 5))


def klass(hole, board):
    c7 = best(hole + board)
    cb = best(board)
    fd = ""
    if len(board) < 5:
        for s in "shdc":
            if sum(1 for c in hole + board if c[1] == s) == 4 and any(c[1] == s for c in hole):
                fd = "+fd"
    if c7 == cb:
        return "nopair" + fd
    if c7 == 1 or (c7 == 2 and cb == 1):
        return "pair" + fd
    return "strong"


def main():
    args = sys.argv[1:]
    mn = 500
    if "--min" in args:
        i = args.index("--min"); mn = int(args[i + 1]); del args[i:i + 2]
    lst = "--list" in args
    files = [a for a in args if not a.startswith("--")]
    agg = defaultdict(lambda: [0, 0, 0])
    aggv = defaultdict(lambda: [0, 0, 0])
    aggs = defaultdict(lambda: [0, 0, 0])
    rows = []
    for f in files:
        d = json.load(open(f)); me = d["seat"]; names = [AB.get(p, p[:4]) for p in d["players"]]
        tag = f.split("_")[-1].split(".")[0]
        for h in d["hands"]:
            hole = h["hole"].get(str(me))
            if not hole:
                continue
            street = "pre"; board = []; pot = 0; contrib = defaultdict(int); last = None
            for e in h["events"]:
                if e[0] == "post":
                    pot += e[2]; contrib[e[1]] += e[2]
                elif e[0] == "board":
                    street = e[1]; board = e[2]; contrib = defaultdict(int); last = None
                elif e[0] == "act":
                    s, a, amt = e[1], e[2], e[3]
                    if a == "raise":
                        last = (s, (amt - contrib[s]) / pot if pot else 0, amt)
                        pot += amt - contrib[s]; contrib[s] = amt
                    elif a == "call":
                        if s == me and street != "pre" and amt >= mn and last:
                            k = klass(hole, board)
                            v = names[last[0]]
                            res = h["results"][me]
                            base = k.split("+")[0]
                            if base != "strong":
                                sz = "bet<0.7" if last[1] < 0.7 else ("bet 0.7-1.3" if last[1] < 1.3 else "bet 1.3+")
                                A = aggs[("flop" if street == "flop" else "turn/river", sz)]
                                A[0] += 1; A[1] += res > 0; A[2] += res
                            for key, A in ((base, agg), ((v, base), aggv)):
                                A[key][0] += 1; A[key][1] += res > 0; A[key][2] += res
                            rows.append((res, f"{tag}#{h['n']} {street} {''.join(hole)} on {''.join(board)} {k} called {amt} vs {v} bet {last[1]:.2f} pot -> {res:+d}"))
                        pot += amt; contrib[s] += amt
    print(f"OUR POSTFLOP CALLS OF {mn}+ CHIPS, {len(files)} round(s): class n / hands won / net chips of those hands")
    for k in ("nopair", "pair", "strong"):
        n, w, net = agg[k]
        print(f"  {k:7s} n={n:3d} won {w:3d} net {net:+d}")
    for (v, k), (n, w, net) in sorted(aggv.items()):
        if k != "strong":
            print(f"    vs {v:4s} {k:7s} n={n:2d} won {w:2d} net {net:+d}")
    print("  nopair+pair by street and bet size: " + "; ".join(f"{k[0]} {k[1]}: n={v[0]} won {v[1]} net {v[2]:+d}" for k, v in sorted(aggs.items())))
    if lst:
        for res, r in sorted(rows):
            if "strong" not in r:
                print("   ", r)


if __name__ == "__main__":
    main()
