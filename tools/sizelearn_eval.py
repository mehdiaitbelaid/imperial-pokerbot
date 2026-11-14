"""On our real hands: where does NEW decide differently from OLD when we face a postflop bet,
and what is that worth?

    python3 tools/sizelearn_eval.py OLD.py NEW.py hands/saturday_r0NN.json ...

- call -> fold: exact (the real hand result is known), counted only where we really called.
- anything -> raise: estimated with the bettor team's measured fold rate when a bet of that size
  bucket is raised (all hands on disk, shrunk to the field's), ZERO equity when called.
- fold -> call: counted, with the size bucket and team; no value is claimed."""
import glob, importlib.util, json, os, sys
from collections import Counter, defaultdict
from multiprocessing import Pool
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, BB = 2000, 20
LAB = ["<0.24", "0.24-0.42", "0.42-0.65", "0.65-0.90", "0.90-1.30", ">=1.30"]


def zb(x):
    return 0 if x < 0.24 else 1 if x < 0.42 else 2 if x < 0.65 else 3 if x < 0.90 else 4 if x < 1.30 else 5


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def team_rates(only=None):
    T = defaultdict(lambda: [0, 0]); F = defaultdict(lambda: [0, 0])
    for f in ([only] if only else sorted(glob.glob(os.path.join(ROOT, "hands", "saturday_r0*.json")))):
        d = json.load(open(f)); P = d["players"]
        for h in d["hands"]:
            street = "preflop"; cur = 0; pot = 0; bets = defaultdict(int); fb = None; sr = None
            for e in h["events"]:
                if e[0] == "post":
                    bets[e[1]] += e[2]; cur = max(cur, bets[e[1]]); pot += e[2]
                elif e[0] == "board":
                    street = e[1]; bets = defaultdict(int); cur = 0; fb = None; sr = None
                elif e[0] == "refund":
                    pot -= e[2]
                elif e[0] == "act":
                    s, a, amt = e[1], e[2], e[3]
                    if street != "preflop" and sr is not None and s == sr[0]:
                        T[(P[s], sr[1])][0] += 1; T[(P[s], sr[1])][1] += a == "fold"
                        F[sr[1]][0] += 1; F[sr[1]][1] += a == "fold"; sr = None
                    if a == "raise":
                        if street != "preflop":
                            if cur == 0:
                                fb = (s, amt / float(pot or 1))
                            elif fb is not None and s != fb[0] and sr is None:
                                sr = (fb[0], zb(fb[1])); fb = None
                        pot += amt - bets[s]; bets[s] = amt; cur = amt
                    elif a == "call":
                        pot += amt; bets[s] += amt
    return {k: tuple(v) for k, v in T.items()}, {k: tuple(v) for k, v in F.items()}


def team_pre():
    T3 = defaultdict(lambda: [0, 0]); T4 = defaultdict(lambda: [0, 0])
    for f in sorted(glob.glob(os.path.join(ROOT, "hands", "saturday_r0*.json"))):
        d = json.load(open(f)); P = d["players"]
        for h in d["hands"]:
            rs = []           # raisers in order
            wait = None
            for e in h["events"]:
                if e[0] == "board":
                    break
                if e[0] != "act":
                    continue
                s, a = e[1], e[2]
                if wait is not None and s == wait[0]:
                    (T3 if wait[1] == 3 else T4)[P[s]][0] += 1
                    (T3 if wait[1] == 3 else T4)[P[s]][1] += a == "fold"
                    wait = None
                if a == "raise":
                    rs.append(s)
                    if len(rs) == 2 and rs[0] != s:
                        wait = (rs[0], 3)
                    elif len(rs) == 3 and rs[1] != s:
                        wait = (rs[1], 4)
    return T3, T4


def team_shown(mod, only=None):
    """(team, bucket) -> [shown, strong] for first bets of a street, with the build's own yardstick."""
    A0 = mod.Agent(); C = mod.CARD; Z = defaultdict(lambda: [0, 0])
    for f in ([only] if only else sorted(glob.glob(os.path.join(ROOT, "hands", "saturday_r0*.json")))):
        d = json.load(open(f)); P = d["players"]
        for h in d["hands"]:
            sd = h.get("showdown") or {}
            if not sd:
                continue
            street = "preflop"; cur = 0; pot = 0; bets = defaultdict(int); nb = 0
            for e in h["events"]:
                if e[0] == "post":
                    bets[e[1]] += e[2]; cur = max(cur, bets[e[1]]); pot += e[2]
                elif e[0] == "board":
                    street = e[1]; bets = defaultdict(int); cur = 0; nb = len(e[2])
                elif e[0] == "refund":
                    pot -= e[2]
                elif e[0] == "act":
                    s, a, amt = e[1], e[2], e[3]
                    if a == "raise":
                        if street != "preflop" and cur == 0 and str(s) in sd and str(s) in h["hole"] and len(h["board"]) >= nb:
                            hc = h["hole"][str(s)]
                            k = (P[s], zb(amt / float(pot or 1)))
                            Z[k][0] += 1
                            Z[k][1] += bool(A0._zstrong(C[hc[0]], C[hc[1]], [C[x] for x in h["board"][:nb]]))
                        pot += amt - bets[s]; bets[s] = amt; cur = amt
                    elif a == "call":
                        pot += amt; bets[s] += amt
    return Z


def one(args):
    old, new, f, seed = args
    MO = load(old, "o" + os.path.basename(f)); MN = load(new, "n" + os.path.basename(f))
    d = json.load(open(f)); n = len(d["players"]); me = d["seat"]; P = d["players"]
    info = {"seat": me, "num_players": n, "hands": 1000, "starting_stack": START, "big_blind": BB, "small_blind": 10}
    A = MO.Agent(); B = MN.Agent(); A.on_table_start(info); B.on_table_start(info)
    if seed:                                     # oracle: what each team did in the OTHER rounds
        ST, SZ = seed
        for i, name in enumerate(P):
            if i == me:
                continue
            for b in range(6):
                o, fo = ST.get((name, b), (0, 0)); zn, zs_ = SZ.get((name, b), (0, 0))
                if o >= 6:
                    w = min(o, 12.0); B.st[i].zo[b] = w; B.st[i].zf[b] = w * fo / o
                if zn >= 6:
                    w = min(zn, 12.0); B.st[i].zn[b] = w; B.st[i].zs[b] = w * zs_ / zn
    rows = []
    for h in d["hands"]:
        hist = []; street = "preflop"; board = []; posted = 0
        stacks = [START] * n; bets = [0] * n; folded = [False] * n; pot = 0; cur = 0; mi = BB; inv = 0; last_agg = None; last_x = 0.0
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
                    spot = street != "preflop" and tc > 0
                    nraise = sum(1 for x in hist if x["street"] == "preflop" and x["action"] == "raise")
                    pspot = street == "preflop" and tc > 0 and nraise in (1, 2)
                    k = 3 if spot else 1
                    ra = [A.act(st) for _ in range(k)]; rb = [B.act(st) for _ in range(k)]
                    if pspot and ra[0]["action"] != rb[0]["action"]:
                        risk = (rb[0].get("amount", 0) - bets[s]) if rb[0]["action"] == "raise" else 0
                        if rb[0]["action"] == "all_in":
                            risk = stacks[s]
                        rows.append(("PRE%d %s -> %s" % (nraise, ra[0]["action"], rb[0]["action"]), P[last_agg] if last_agg is not None else "?", street, 0, pot, risk, a,
                                     (h["results"][me] + inv) / 20.0, os.path.basename(f)[9:13], h["n"], tc))
                    if spot:
                        ca = Counter(x["action"] for x in ra).most_common(1)[0]; cb = Counter(x["action"] for x in rb).most_common(1)[0]
                        if ca[0] != cb[0] and ca[1] >= 2 and cb[1] >= 2:
                            risk = 0
                            if cb[0] == "raise":
                                risk = sorted(x.get("amount", 0) for x in rb if x["action"] == "raise")[0] - bets[s]
                            rows.append((ca[0] + " -> " + cb[0], P[last_agg] if last_agg is not None else "?", street, zb(last_x), pot, risk, a,
                                         (h["results"][me] + inv) / 20.0, os.path.basename(f)[9:13], h["n"], tc))
                hist.append({"seat": s, "street": street, "action": a, "amount": amt})
                if a == "raise":
                    inc = amt - cur
                    if inc >= mi: mi = inc
                    if street != "preflop":
                        last_x = (amt - cur) / float(pot + cur - bets[s]) if cur > 0 else amt / float(pot or 1)
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
    oracle = "--oracle" in sys.argv
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    old, new = argv[0], argv[1]; files = argv[2:]
    T, F = team_rates()
    T3, T4 = team_pre()
    zmod = load(new, "zmod")
    Z = team_shown(zmod)
    jobs = []
    for f in files:
        seed = None
        if oracle:
            Tf, _ = team_rates(f); Zf = team_shown(zmod, f)
            ST = {k: (v[0] - Tf.get(k, (0, 0))[0], v[1] - Tf.get(k, (0, 0))[1]) for k, v in T.items()}
            SZ = {k: (v[0] - Zf.get(k, (0, 0))[0], v[1] - Zf.get(k, (0, 0))[1]) for k, v in Z.items()}
            seed = (ST, SZ)
        jobs.append((old, new, f, seed))
    if oracle:
        print("ORACLE SEEDING: each seat starts with what its team did in the other rounds (leave one round out)")
    with Pool(8) as p:
        res = p.map(one, jobs, chunksize=1)
    rows = [r for rr in res for r in rr]
    json.dump(rows, open("/private/tmp/claude-501/sizelearn_rows.json", "w"))
    N = 1000 * len(files)
    print("%d rounds, %d decisions facing a postflop bet where NEW differs from OLD (both consistent)" % (len(files), len(rows)))
    G = defaultdict(list)
    for r in rows:
        G[r[0]].append(r)
    for kind, rr in sorted(G.items(), key=lambda kv: -len(kv[1])):
        print("\n== %s: %d" % (kind, len(rr)))
        if kind.startswith("PRE"):
            TT = T3 if kind.startswith("PRE1") else T4
            if kind.endswith("-> raise"):
                ev = now = 0.0; bt = defaultdict(lambda: [0, 0.0, 0.0])
                for r in rr:
                    o, fo = TT.get(r[1], (0, 0)); p_ = (fo + 2.0) / (o + 4.0)
                    e_ = (p_ * r[4] - (1 - p_) * r[5]) / 20.0
                    ev += e_; now += r[7]; bt[r[1]][0] += 1; bt[r[1]][1] += e_; bt[r[1]][2] += r[7]
                print("   estimated value (his fold rate, zero equity otherwise) %+.0f bb against %+.0f bb really made: %+.1f bb/100" % (ev, now, (ev - now) / N * 100))
                print("   by raiser: " + "; ".join("%s x%d est %+.0f real %+.0f (folds %d/%d)" % ((k[:14], v[0], v[1], v[2]) + tuple(reversed(TT.get(k, (0, 0))))) for k, v in sorted(bt.items(), key=lambda kv: -kv[1][0])[:8]))
            else:
                print("   really made in those spots: %+.0f bb" % sum(r[7] for r in rr))
            continue
        if kind.endswith("-> fold") and kind.startswith("call"):
            real = [r for r in rr if r[6] == "call"]
            g = sum(r[7] for r in real)
            print("   really called in %d of them: calling made %+.0f bb, so folding is worth %+.1f bb/100" % (len(real), g, -g / N * 100))
        if kind.endswith("-> raise"):
            ev = now = 0.0
            for r in rr:
                o, fo = T.get((r[1], r[3]), (0, 0)); fn, ff = F.get(r[3], (1, 0))
                p_ = (fo + 4.0 * ff / max(1, fn)) / (o + 4.0)
                ev += (p_ * r[4] - (1 - p_) * r[5]) / 20.0; now += r[7]
            print("   estimated value %+.0f bb against %+.0f bb really made: %+.1f bb/100" % (ev, now, (ev - now) / N * 100))
        if kind == "fold -> call":
            est = 0.0; nn = 0
            for r in rr:
                zn, zs_ = Z.get((r[1], r[3]), (0, 0))
                if zn >= 8:
                    q = zs_ / float(zn); est += ((1 - q) * (r[4] + r[10]) - r[10]) / 20.0; nn += 1
            print("   rough value where the team showed 8+ hands after that size (%d spots): %+.0f bb (we win when he is weak, lose when strong)" % (nn, est))
        by = defaultdict(lambda: [0, 0.0])
        for r in rr:
            by[(LAB[r[3]], r[1])][0] += 1; by[(LAB[r[3]], r[1])][1] += r[7] if r[6] == "call" else 0.0
        top = sorted(by.items(), key=lambda kv: -kv[1][0])[:10]
        print("   by size and bettor: " + "; ".join("%s %s x%d" % (k[1][:14], k[0], v[0]) for k, v in top))
