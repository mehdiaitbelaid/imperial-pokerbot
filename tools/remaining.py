"""Which real calls of big bets does a build still make, and what did they earn?

    python3 tools/remaining.py BUILD.py hands/saturday_r0NN.json ...

For every real postflop call of ours facing a bet of half the pot or more, rebuilds the state,
asks BUILD (3 votes) what it does, and reports the real result of calling compared with folding,
grouped by street, hand class and BUILD's decision."""
import importlib.util, json, os, sys
from collections import Counter, defaultdict
from multiprocessing import Pool
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, BB = 2000, 20


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def klass(M, hole, board):
    hc = [M.CARD[c] for c in hole]; bd = [M.CARD[c] for c in board]
    bp, sc, sm, bmask, thr, fs, scf, smf, d4b, paired, tb = M.Agent._board_ctx(bd)
    v = M.RANK[bp * M.CP[hc[0]] * M.CP[hc[1]]]
    if fs >= 0 and scf + ((hc[0] & 3) == fs) + ((hc[1] & 3) == fs) >= 5:
        m = smf
        for c in hc:
            if (c & 3) == fs: m |= 1 << (c >> 2)
        v = max(v, M.FLUSH[m])
    cat = v >> 20
    br = [c >> 2 for c in bd]; hr = [c >> 2 for c in hc]
    draw = False
    if len(bd) < 5:
        s0, s1 = hc[0] & 3, hc[1] & 3
        c4 = sc[s0] + 2 if s0 == s1 else max(sc[s0], sc[s1]) + 1
        draw = c4 == 4 or bool(not d4b and M.DRAW4[bmask | (1 << hr[0]) | (1 << hr[1])])
    top = max(br)
    hits = sum(1 for x in hr if x in br)
    if cat >= 3 or (cat == 2 and not paired):
        return "two pair or better (real)"
    if cat == 2:                                    # two pair using a board pair
        if hr[0] == hr[1]:
            return "pocket pair + board pair, over the board" if hr[0] > top else "pocket pair + board pair, under top card"
        if hits >= 1:
            return "top pair + board pair" if top in hr else "weaker pair + board pair"
        return "nothing" + (" + draw" if draw else "")
    if cat == 1 and (hr[0] == hr[1] or hits):
        if (hr[0] == hr[1] and hr[0] > top) or top in hr:
            return "top pair / overpair"
        return "weaker pair" + (" + draw" if draw else "")
    return "draw, no pair" if draw else "nothing"


def one(args):
    build, f = args
    M = load(build, "b" + os.path.basename(f))
    d = json.load(open(f)); n = len(d["players"]); me = d["seat"]; P = d["players"]
    A = M.Agent()
    A.on_table_start({"seat": me, "num_players": n, "hands": 1000, "starting_stack": START, "big_blind": BB, "small_blind": 10})
    rows = []
    for h in d["hands"]:
        hist = []; street = "preflop"; board = []; posted = 0
        stacks = [START] * n; bets = [0] * n; folded = [False] * n; pot = 0; cur = 0; mi = BB; inv = 0; last_agg = None
        for ev in h["events"]:
            if ev[0] == "post":
                s, amt = ev[1], ev[2]
                hist.append({"seat": s, "street": "preflop", "action": "small_blind" if posted == 0 else "big_blind", "amount": amt}); posted += 1
                stacks[s] -= amt; bets[s] += amt; pot += amt; cur = max(cur, bets[s])
                if s == me: inv += amt
            elif ev[0] == "board":
                street = ev[1]; board = ev[2]; bets = [0] * n; cur = 0; mi = BB; last_agg = None
            elif ev[0] == "refund":
                stacks[ev[1]] += ev[2]; pot -= ev[2]
                if ev[1] == me: inv -= ev[2]
            elif ev[0] == "act":
                s, a, amt = ev[1], ev[2], ev[3]
                if s == me:
                    tc = min(cur - bets[s], stacks[s]); mx = bets[s] + stacks[s]
                    oth = any((not folded[j]) and stacks[j] > 0 for j in range(n) if j != s); cr = mx > cur and oth
                    st = {"type": "act", "hand_number": h["n"], "street": street, "seat": s, "button": h["button"],
                          "hole_cards": h["hole"][str(me)], "board": list(board), "small_blind": 10, "big_blind": BB, "blind_level": 0,
                          "pot": pot, "stacks": list(stacks), "bets": list(bets), "folded": list(folded), "to_call": tc,
                          "min_raise_to": min(cur + mi, mx) if cr else None, "max_raise_to": mx if cr else None,
                          "legal_actions": (["fold", "call"] if tc > 0 else ["check"]) + (["raise"] if cr else []),
                          "betting": "no_limit", "raise_cap": None, "raises_this_street": 0, "history": list(hist)}
                    target = street != "preflop" and a == "call" and tc >= 0.5 * (pot - tc) and tc >= 60
                    votes = Counter(A.act(st)["action"] for _ in range(3 if target else 1))
                    if target:
                        dec = votes.most_common(1)[0][0]
                        xb = tc / float(max(1, pot - tc))
                        rows.append((street, klass(M, h["hole"][str(me)], board), "pot or more" if xb >= 1.0 else "half to pot",
                                     "FOLD" if dec == "fold" else "continue", (h["results"][me] + inv) / 20.0, h["results"][me] > 0,
                                     P[last_agg] if last_agg is not None else "?", os.path.basename(f)[9:13], h["n"], tc, pot - tc))
                hist.append({"seat": s, "street": street, "action": a, "amount": amt})
                if a == "raise":
                    inc = amt - cur
                    if inc >= mi: mi = inc
                    if s == me: inv += amt - bets[s]
                    stacks[s] -= amt - bets[s]; pot += amt - bets[s]; bets[s] = amt; cur = amt; last_agg = s
                elif a == "call":
                    if s == me: inv += amt
                    stacks[s] -= amt; pot += amt; bets[s] += amt
                elif a == "fold":
                    folded[s] = True
        shown = {k2: v for k2, v in h["hole"].items() if k2 in (h.get("showdown") or {})}
        A.on_hand_end({"type": "hand_end", "hand_number": h["n"], "history": hist, "board": h["board"], "shown": shown, "winners": [], "stacks": [START] * n})
    return rows


if __name__ == "__main__":
    build = sys.argv[1]; files = sys.argv[2:]
    with Pool(10) as p:
        res = p.map(one, [(build, f) for f in files], chunksize=1)
    rows = [r for rr in res for r in rr]
    json.dump(rows, open("/private/tmp/claude-501/remaining_rows.json", "w"))
    N = 1000 * len(files)
    print("%d rounds, %d real calls of a bet of half the pot or more. Gain = result of calling compared with folding." % (len(files), len(rows)))
    G = defaultdict(lambda: [0, 0, 0.0])
    for r in rows:
        k = (r[3], r[0], r[1]); G[k][0] += 1; G[k][1] += r[5]; G[k][2] += r[4]
    for dec in ("continue", "FOLD"):
        print("\n== the build's decision today: %s" % dec)
        tot = [0, 0.0]
        for k, v in sorted(G.items(), key=lambda kv: kv[1][2]):
            if k[0] != dec: continue
            tot[0] += v[0]; tot[1] += v[2]
            if v[0] >= 4:
                print("   %-6s %-42s n=%3d  won %3.0f%%  gain %+7.0f bb  (%+.1f bb/100)" % (k[1], k[2], v[0], 100.0 * v[1] / v[0], v[2], v[2] / N * 100))
        print("   TOTAL %s: n=%d  gain from calling %+.0f bb (%+.1f bb/100)" % (dec, tot[0], tot[1], tot[1] / N * 100))
