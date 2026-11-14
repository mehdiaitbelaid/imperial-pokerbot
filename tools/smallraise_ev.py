"""Estimate, on our real hands, what V21's new raises of small bets are worth.

    python3 tools/smallraise_ev.py OLD.py NEW.py hands/saturday_r0NN.json ...

1. From every hand on disk: how often each team gives up when its own small first bet (under 40%
   of the pot) is raised (any raiser).
2. Replays our real decisions through both builds; keeps the spots where NEW raises and OLD does not.
3. Values each raise with the bettor team's measured fold rate and ZERO equity when called
   (a floor), and compares with what we really made from that decision on."""
import glob, importlib.util, json, os, sys
from collections import Counter, defaultdict
from multiprocessing import Pool
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, BB = 2000, 20


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def team_rates():
    T = defaultdict(lambda: [0, 0])
    for f in sorted(glob.glob(os.path.join(ROOT, "hands", "saturday_r0*.json"))):
        d = json.load(open(f)); P = d["players"]
        for h in d["hands"]:
            street = "preflop"; cur = 0; pot = 0; bets = defaultdict(int); fb = None; sr = -1
            for e in h["events"]:
                if e[0] == "post":
                    bets[e[1]] += e[2]; cur = max(cur, bets[e[1]]); pot += e[2]
                elif e[0] == "board":
                    street = e[1]; bets = defaultdict(int); cur = 0; fb = None; sr = -1
                elif e[0] == "refund":
                    pot -= e[2]
                elif e[0] == "act":
                    s, a, amt = e[1], e[2], e[3]
                    if street != "preflop" and s == sr:
                        sr = -1; T[P[s]][0] += 1; T[P[s]][1] += a == "fold"
                    if a == "raise":
                        if street != "preflop":
                            if cur == 0:
                                fb = (s, amt / float(pot or 1))
                            elif fb is not None and fb[1] < 0.4 and s != fb[0]:
                                sr = fb[0]; fb = None
                        pot += amt - bets[s]; bets[s] = amt; cur = amt
                    elif a == "call":
                        pot += amt; bets[s] += amt
    return {k: tuple(v) for k, v in T.items()}


def one(args):
    old, new, f = args
    MO = load(old, "o" + os.path.basename(f)); MN = load(new, "n" + os.path.basename(f))
    d = json.load(open(f)); n = len(d["players"]); me = d["seat"]; P = d["players"]
    info = {"seat": me, "num_players": n, "hands": 1000, "starting_stack": START, "big_blind": BB, "small_blind": 10}
    A = MO.Agent(); B = MN.Agent(); A.on_table_start(info); B.on_table_start(info)
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
                    spot = street != "preflop" and tc > 0 and cr and tc < 0.4 * (pot - tc)
                    k = 3 if spot else 1
                    ra = [A.act(st) for _ in range(k)]; rb = [B.act(st) for _ in range(k)]
                    if spot:
                        va = Counter(x["action"] for x in ra).most_common(1)[0][0]
                        vb = Counter(x["action"] for x in rb).most_common(1)[0][0]
                        if vb == "raise" and va != "raise":
                            r_to = sorted(x.get("amount", 0) for x in rb if x["action"] == "raise")[0]
                            rows.append((P[last_agg] if last_agg is not None else "?", street, pot, r_to - bets[s], a, va,
                                         (h["results"][me] + inv) / 20.0, os.path.basename(f)[9:13], h["n"]))
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
        summ = {"type": "hand_end", "hand_number": h["n"], "history": hist, "board": h["board"], "shown": shown, "winners": [], "stacks": [START] * n}
        A.on_hand_end(summ); B.on_hand_end(summ)
    return rows


if __name__ == "__main__":
    old, new = sys.argv[1], sys.argv[2]; files = sys.argv[3:]
    T = team_rates()
    tot = [sum(v[0] for v in T.values()), sum(v[1] for v in T.values())]
    print("Field, all hands on disk: a small first bet that gets raised is given up %d of %d times (%.0f%%)" % (tot[1], tot[0], 100.0 * tot[1] / max(1, tot[0])))
    with Pool(10) as p:
        res = p.map(one, [(old, new, f) for f in files], chunksize=1)
    rows = [r for rr in res for r in rr]
    N = 1000 * len(files)
    ev = now = evf = 0.0
    by = defaultdict(lambda: [0, 0.0, 0.0])
    for team, street, pot, risk, a, va, real, rf, hn in rows:
        o, fo = T.get(team, (0, 0))
        p_ = (fo + 5 * 0.70) / (o + 5)
        e = (p_ * pot - (1 - p_) * risk) / 20.0
        ev += e; now += real; evf += (0.70 * pot - 0.30 * risk) / 20.0
        by[team][0] += 1; by[team][1] += e; by[team][2] += real
    print("%d rounds: NEW raises a small bet where OLD does not in %d spots (%.1f per round)" % (len(files), len(rows), len(rows) / float(len(files))))
    print("   value of the raises, team fold rates, zero equity when called: %+.0f bb | what we really made in those spots: %+.0f bb" % (ev, now))
    print("   ESTIMATED GAIN: %+.1f bb/100 (with the flat field rate of 70%%: %+.1f bb/100)" % ((ev - now) / N * 100, (evf - now) / N * 100))
    print("   by bettor (spots, estimated value, really made, team's folds when raised):")
    for team, v in sorted(by.items(), key=lambda kv: -kv[1][0])[:16]:
        o, fo = T.get(team, (0, 0))
        print("     %-24s %3d  %+6.0f  %+6.0f   %d/%d" % (team[:24], v[0], v[1], v[2], fo, o))
