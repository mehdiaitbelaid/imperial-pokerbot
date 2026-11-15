"""Weak-pair spots on real hands: a pair below top pair, on the flop or turn, facing a bet of
half the pot or more (the spot V20's rule targets). Lists our calls (result against folding),
our folds, and the folds where a showdown between the others shows we would have won.

    python3 reports/_weakpair.py hands/saturday_r047.json ...   [-q for totals only]

Uses the hand classes of tools/calls.py (read only). Written by the round tracker."""
import contextlib, io, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
quiet = "-q" in sys.argv
files = [a for a in sys.argv[1:] if a != "-q"]
g = {"__name__": "calls", "__file__": os.path.join(ROOT, "tools", "calls.py")}
sys.argv = ["calls.py"]
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(open(g["__file__"]).read(), "calls.py", "exec"), g)
M = g["M"]; hand_class = g["hand_class"]


def has_draw(hole, board):
    if len(board) >= 5:
        return False
    hc = [M.CARD[c] for c in hole]; bd = [M.CARD[c] for c in board]
    bp, sc, sm, bmask, thr, fs, scf, smf, d4b, paired, tb = M.Agent._board_ctx(bd)
    s0, s1 = hc[0] & 3, hc[1] & 3
    c4 = sc[s0] + 2 if s0 == s1 else max(sc[s0], sc[s1]) + 1
    return bool(c4 == 4 or (not d4b and M.DRAW4[bmask | (1 << (hc[0] >> 2)) | (1 << (hc[1] >> 2))]))


def value(cards):
    p = 1; sc = [0] * 4; sm = [0] * 4
    for c in (M.CARD[x] for x in cards):
        p *= M.CP[c]; s = c & 3; sc[s] += 1; sm[s] |= 1 << (c >> 2)
    v = M.RANK[p]
    for s in range(4):
        if sc[s] >= 5 and M.FLUSH[sm[s]] > v:
            v = M.FLUSH[sm[s]]
    return v


def weak_pair(hole, board):
    """V20's own definition (upload/bot_v20.py): one pair, or two pair on a paired board, where
    our pair (pocket pair, or one hole card pairing the board) ranks below the top board card."""
    hr = [M.CARD[c] >> 2 for c in hole]; br = [M.CARD[c] >> 2 for c in board]
    hit0, hit1 = hr[0] in br, hr[1] in br
    pr = -1
    if hr[0] == hr[1] and not hit0:
        pr = hr[0]
    elif hit0 != hit1:
        pr = hr[0] if hit0 else hr[1]
    cat = value(hole + board) >> 20
    return (cat == 1 or (cat == 2 and len(set(br)) < len(br))) and 0 <= pr < max(br)


T = {"calls": 0, "calls_nodraw": 0, "gain": 0.0, "gain_nodraw": 0.0, "folds": 0, "folds_nodraw": 0, "won": 0, "seen": 0, "hands": 0}
for f in files:
    d = json.load(open(f)); me = d["seat"]; P = d["players"]; tag = os.path.basename(f).replace("saturday_", "").replace(".json", "")
    R = {"calls": 0, "calls_nodraw": 0, "gain": 0.0, "gain_nodraw": 0.0, "folds": 0, "folds_nodraw": 0, "won": 0, "seen": 0}
    lines = []
    for h in d["hands"]:
        T["hands"] += 1
        r = h["results"][me]; street = "preflop"; board = []; pot = 0; inv = 0; bets = {}; cur = 0; last = None
        hole = h["hole"][str(me)]
        for e in h["events"]:
            if e[0] == "post":
                pot += e[2]; bets[e[1]] = bets.get(e[1], 0) + e[2]; cur = max(cur, bets[e[1]])
                if e[1] == me: inv += e[2]
            elif e[0] == "board":
                street = e[1]; board = e[2]; bets = {}; cur = 0; last = None
            elif e[0] == "refund":
                pot -= e[2]
                if e[1] == me: inv -= e[2]
            elif e[0] == "act":
                s, a, amt = e[1], e[2], e[3]
                if s == me and street in ("flop", "turn") and a in ("call", "fold"):
                    c = amt if a == "call" else cur - bets.get(me, 0)
                    if c > 0 and c >= 0.5 * (pot - c) and weak_pair(hole, board):
                        dr = has_draw(hole, board); who = P[last][:12] if last is not None else "?"
                        if a == "call":
                            gain = r + inv
                            R["calls"] += 1; R["gain"] += gain
                            if not dr: R["calls_nodraw"] += 1; R["gain_nodraw"] += gain
                            lines.append("  CALL %s#%-4d %s [%s] %s %d into %d vs %s%s -> hand %+d, vs folding %+d" % (
                                tag, h["n"], "".join(hole), " ".join(board), street, c, pot - c, who, " (draw)" if dr else "", r, gain))
                        else:
                            R["folds"] += 1
                            if not dr: R["folds_nodraw"] += 1
                            shown = {k: v for k, v in h["hole"].items() if k != str(me) and k in (h.get("showdown") or {})}
                            verdict = "no showdown"
                            if shown and len(h["board"]) == 5:
                                R["seen"] += 1
                                mv = value(hole + h["board"]); best = max(value(v + h["board"]) for v in shown.values())
                                verdict = "WOULD HAVE WON" if mv > best else ("would have split" if mv == best else "would have lost")
                                if mv > best: R["won"] += 1
                                verdict += " vs " + ", ".join("%s %s" % (P[int(k)][:10], "".join(v)) for k, v in shown.items()) + " on [%s]" % " ".join(h["board"])
                            lines.append("  FOLD %s#%-4d %s [%s] %s %d into %d vs %s%s -> %s" % (
                                tag, h["n"], "".join(hole), " ".join(board), street, c, pot - c, who, " (draw)" if dr else "", verdict))
                if a == "raise":
                    add = amt - bets.get(s, 0); pot += add; bets[s] = amt; cur = max(cur, amt); last = s
                    if s == me: inv += add
                elif a == "call":
                    pot += amt; bets[s] = bets.get(s, 0) + amt
                    if s == me: inv += amt
    for k in R: T[k] += R[k]
    print("%s weak pair, flop/turn, bet >= half pot: calls %d (%+.0f bb vs folding), of which no draw %d (%+.0f bb) | folds %d (no draw %d), showdown seen %d, would have won %d" % (
        tag, R["calls"], R["gain"] / 20, R["calls_nodraw"], R["gain_nodraw"] / 20, R["folds"], R["folds_nodraw"], R["seen"], R["won"]))
    if not quiet:
        for x in lines: print(x)
if len(files) > 1:
    n = T["calls_nodraw"] + T["folds_nodraw"]
    print("TOTAL %d hands: calls %d (%+.0f bb), no-draw calls %d (%+.0f bb), folds %d (no draw %d) | no-draw call rate %d/%d = %.0f%% | folds with showdown %d, would have won %d" % (
        T["hands"], T["calls"], T["gain"] / 20, T["calls_nodraw"], T["gain_nodraw"] / 20, T["folds"], T["folds_nodraw"],
        T["calls_nodraw"], n, 100.0 * T["calls_nodraw"] / n if n else 0, T["seen"], T["won"]))
