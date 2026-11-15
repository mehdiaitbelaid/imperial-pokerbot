"""Our turn and river bets heads-up, by opponent and hand strength: how often he folds, and chips won from that
point (hand result + what we had already put in): an upper bound on what the bet earned against giving up.
    python3 tools/barrel_ev.py hands/sunday_s1_r0*.json"""
import json, sys
from collections import defaultdict, Counter
R = "23456789TJQKA"
def cat(hole, board):
    cs = hole + board; rk = Counter(c[0] for c in cs); su = Counter(c[1] for c in cs)
    if max(su.values()) >= 5: return 2
    idx = sorted(set(R.index(c[0]) for c in cs)); idx = ([-1] if 12 in idx else []) + idx
    run = 1
    for a, b in zip(idx, idx[1:]):
        run = run + 1 if b == a + 1 else 1
        if run >= 5: return 2
    mine = [r for r in set(c[0] for c in hole) if rk[r] >= 2]
    if any(rk[r] >= 3 for r in mine): return 2
    pairs = [r for r in rk if rk[r] >= 2]
    if mine and len(pairs) >= 2 and (len(mine) >= 2 or hole[0][0] != hole[1][0]) and len([r for r in mine]) >= 1 and len(pairs) >= 2 and any(r in mine for r in pairs) and len(set(pairs) & set(c[0] for c in hole)) >= 2: return 2
    return 1 if mine else 0
T = defaultdict(lambda: [0, 0, 0, 0, 0.0])
for f in sys.argv[1:]:
    d = json.load(open(f)); me = d["seat"]; P = d["players"]
    for h in d["hands"]:
        inv = defaultdict(int); live = set(range(len(P))); street = "preflop"; sb = defaultdict(int); cur = 0; pot = 0; board = []
        hole = h["hole"].get(str(me))
        for ev in h["events"]:
            if ev[0] == "post": sb[ev[1]] = ev[2]; cur = max(cur, ev[2])
            elif ev[0] == "board":
                for s, v in sb.items(): inv[s] += v
                pot = sum(inv.values()); sb = defaultdict(int); cur = 0; street = ev[1]; board = ev[2]
            elif ev[0] == "act":
                s, a, amt = ev[1], ev[2], ev[3]
                if a == "fold": live.discard(s)
                elif a in ("call", "raise", "all_in", "bet"):
                    if s == me and cur == 0 and amt > 0 and street in ("turn", "river") and len(live) == 2 and hole:
                        opp = [x for x in live if x != me][0]; c = cat(hole, board)
                        # his reply
                        rest = h["events"][h["events"].index(ev) + 1:]
                        rep = next((e[2] for e in rest if e[0] == "act" and e[1] == opp), "fold")
                        k = (P[opp], street, "two pair+" if c == 2 else "one pair or less", "big" if amt >= 0.6 * pot else "small")
                        t = T[k]; t[0] += 1; t[1] += rep == "fold"; t[2] += rep == "call"; t[3] += rep not in ("fold", "call"); t[4] += h["result"] + inv[me]
                    sb[s] = max(sb[s], amt) if a != "call" else amt; cur = max(cur, sb[s])
for k in sorted(T):
    t = T[k]
    if t[0] >= 4: print("%-24s %-5s %-16s %-5s n %3d | fold %3d call %3d raise %2d | chips from the bet on %+7.0f (%+5.0f each)" % (k + (t[0], t[1], t[2], t[3], t[4], t[4] / t[0])))
