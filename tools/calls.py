"""Which of our postflop calls make or lose money, on real hands.

    python3 tools/calls.py hands/saturday_r003.json ...

For every postflop call we made: the result of the hand compared with folding at that moment
("gain from calling"), grouped by street, by the size of the bet faced and by what we held then."""
import importlib.util, json, os, sys
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("botmod", os.path.join(ROOT, "bots", "av20.py"))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
G = defaultdict(lambda: [0, 0, 0.0]); N = 0


def hand_class(hole, board):
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
    if cat >= 2 and not (cat == 2 and paired and hr[0] != hr[1] and sum(1 for x in hr if x in br) < 2 and not (hr[0] == hr[1])):
        return "two pair or better"
    if cat >= 1 and (hr[0] == hr[1] or hr[0] in br or hr[1] in br):
        top = max(br)
        if (hr[0] == hr[1] and hr[0] > top) or top in hr:
            return "top pair / overpair"
        return "weaker pair"
    if len(bd) < 5:
        s0, s1 = hc[0] & 3, hc[1] & 3
        c4 = sc[s0] + 2 if s0 == s1 else max(sc[s0], sc[s1]) + 1
        if c4 == 4 or (not d4b and M.DRAW4[bmask | (1 << hr[0]) | (1 << hr[1])]):
            return "draw, no pair"
    return "nothing"


for f in sys.argv[1:]:
    d = json.load(open(f)); me = d["seat"]
    for h in d["hands"]:
        N += 1; r = h["results"][me]; street = "preflop"; board = []; pot = 0; inv = 0; bets = defaultdict(int)
        for e in h["events"]:
            if e[0] == "post":
                pot += e[2]; bets[e[1]] += e[2]
                if e[1] == me: inv += e[2]
            elif e[0] == "board":
                street = e[1]; board = e[2]; bets = defaultdict(int)
            elif e[0] == "refund":
                pot -= e[2]
                if e[1] == me: inv -= e[2]
            elif e[0] == "act":
                s, a, amt = e[1], e[2], e[3]
                if s == me and a == "call" and street != "preflop":
                    # pot already holds the bet we face; odds: amt to win pot
                    size = "under half pot" if amt < 0.34 * pot else ("half to pot" if amt < 0.49 * pot else "pot or more")
                    gain = r + inv
                    cls = hand_class(h["hole"][str(me)], board)
                    for key in ((street, "ALL", ""), (street, cls, ""), ("any street", "ALL", size), ("any street", cls, size), (street, cls, size)):
                        g = G[key]; g[0] += 1; g[1] += r > 0; g[2] += gain
                if a == "raise":
                    add = amt - bets[s]; pot += add; bets[s] = amt
                    if s == me: inv += add
                elif a == "call":
                    pot += amt; bets[s] += amt
                    if s == me: inv += amt
print("%d hands. Gain from calling = hand result compared with folding at that call." % N)
print("%-11s %-20s %-15s %5s %6s %12s %12s" % ("street", "we held", "bet faced", "calls", "won", "gain bb", "bb/100"))
for key in sorted(G, key=lambda k: (k[0], k[2], k[1])):
    g = G[key]
    if g[0] >= 8:
        print("%-11s %-20s %-15s %5d %5.0f%% %+12.0f %+12.1f" % (key[0], key[1], key[2], g[0], 100.0 * g[1] / g[0], g[2] / 20, g[2] / 20 / N * 100))
