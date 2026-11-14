import json, pathlib, collections, itertools, statistics, math, hashlib

ROOT = pathlib.Path("/Users/mehdiaitbelaid/Desktop/imperial-ai-hack-2026/hands-data/hands")
PRIMARY = ["Gherkers", "Attention Is All In", "Equity Engine"]
BRIEF = ["The Market Makers", "AAST", "WBot", "Kojack", "Anker Batteries"]
STREETS = ["preflop", "flop", "turn", "river"]
BUCKETS = ["le33", "33to50", "50to75", "75to100", "over100"]
T = collections.defaultdict(
    lambda: {"c": collections.Counter(), "d": collections.defaultdict(collections.Counter)}
)
SESSIONS = []
DECISIONS = []
QUALITY = collections.Counter()


def bucket(x):
    return BUCKETS[
        next(
            (i for i, v in enumerate((1/3, .5, .75, 1)) if x <= v + 1e-9),
            4,
        )
    ]


def rate(k, n):
    return {
        "yes": k,
        "n": n,
        "pct": round(100*k/n, 2) if n else None,
        "unreliable": n < 30,
    }


def desc(xs):
    return {
        "n": len(xs),
        "median": round(statistics.median(xs), 4) if xs else None,
        "modes": collections.Counter(xs).most_common(6),
    }


def rank(cards):
    best = (-1,)
    for five in itertools.combinations(cards, 5):
        rs = ["23456789TJQKA".index(c[0])+2 for c in five]
        counts = collections.Counter(rs)
        groups = sorted(((n, r) for r, n in counts.items()), reverse=True)
        flush = len({c[1] for c in five}) == 1
        unique = sorted(set(rs))
        straight = (
            5 if unique == [2, 3, 4, 5, 14]
            else unique[-1]
            if len(unique) == 5 and unique[-1]-unique[0] == 4
            else 0
        )
        if flush and straight:
            v = (8, straight)
        elif groups[0][0] == 4:
            v = (7, groups[0][1], groups[1][1])
        elif [g[0] for g in groups] == [3, 2]:
            v = (6, groups[0][1], groups[1][1])
        elif flush:
            v = (5, *sorted(rs, reverse=True))
        elif straight:
            v = (4, straight)
        elif groups[0][0] == 3:
            v = (
                3, groups[0][1],
                *sorted((r for r in rs if r != groups[0][1]), reverse=True),
            )
        elif [g[0] for g in groups][:2] == [2, 2]:
            v = (
                2,
                *sorted((g[1] for g in groups if g[0] == 2), reverse=True),
                groups[-1][1],
            )
        elif groups[0][0] == 2:
            v = (
                1, groups[0][1],
                *sorted((r for r in rs if r != groups[0][1]), reverse=True),
            )
        else:
            v = (0, *sorted(rs, reverse=True))
        best = max(best, v)
    return best


CLASSES = [
    "high card", "pair", "two pair", "trips", "straight",
    "flush", "full house", "quads", "straight flush",
]


def hole_name(cards):
    rs = sorted(
        cards, key=lambda c: "23456789TJQKA".index(c[0]), reverse=True
    )
    return "".join(c[0] for c in rs) + (
        "" if rs[0][0] == rs[1][0]
        else "s" if rs[0][1] == rs[1][1]
        else "o"
    )


def positions(h, N):
    labels = {
        6: ["UTG", "HJ", "CO", "BTN", "SB", "BB"],
        7: ["UTG", "LJ", "HJ", "CO", "BTN", "SB", "BB"],
        8: ["UTG", "UTG1", "LJ", "HJ", "CO", "BTN", "SB", "BB"],
    }[N]
    return {
        (h["button"]+3+j) % N: label
        for j, label in enumerate(labels)
    }


def add(team, key, den=0, num=0):
    T[team]["c"][key+"_n"] += den
    T[team]["c"][key+"_yes"] += num


def sizes(team, key, x):
    T[team]["d"][key][round(x, 3)] += 1


def unpack(counter):
    return [x for x, n in counter.items() for _ in range(n)]


files = sorted(
    p for p in ROOT.glob("saturday_r0*.json")
    if int(p.stem.rsplit("r", 1)[1]) <= 45
)
manifest = []

for fi, path in enumerate(files):
    raw = path.read_bytes()
    d = json.loads(raw)
    teams = d["players"]
    N = len(teams)
    our = d["seat"]
    rn = int(path.stem.rsplit("r", 1)[1])
    third = min(2, fi*3//len(files))
    manifest.append({
        "round": rn,
        "slot": d["round"].get("slot"),
        "hands": len(d["hands"]),
        "seats": N,
        "our_version": d["round"].get("version"),
        "sha256": hashlib.sha256(raw).hexdigest(),
    })
    sessions = []
    for seat, team in enumerate(teams):
        session = {
            "team": team, "round": rn, "third": third,
            "features": [], "net": 0,
        }
        SESSIONS.append(session)
        sessions.append(session)
        T[team]["c"]["rounds"] += 1
    QUALITY["files"] += 1

    for h in d["hands"]:
        QUALITY["hands"] += 1
        assert sum(h["results"]) == 0
        assert h["bb"] == 20 and h["sb"] == 10
        assert all(v == 2000 for v in h["start_stacks"])
        c = [0]*N
        contrib = [0]*N
        paid = [0]*N
        alive = set(range(N))
        street = 0
        board = []
        mx = 20
        nr = 0
        limpers = 0
        pfagg = None
        pf_callers = set()
        vp = set()
        pfr = set()
        acted = set()
        seen3 = set()
        seen4 = set()
        raised_at = {}
        fold3 = set()
        fold4 = set()
        flopset = set()
        shown = {
            int(s): cards
            for s, cards in h["hole"].items()
            if str(s) in h["showdown"]
        }
        pos = positions(h, N)
        checked = set()
        check_responded = set()
        firstbettor = None
        streetraises = 0
        streetcalled = False
        prevbettor = None
        street_raisers = set()
        bets_by_street = {}
        last_bet = None
        last_ratio = 0
        last_tag = ""
        fbet = {i: [] for i in range(N)}
        handobs = []
        streetseen = set()
        wager = None

        for s, team in enumerate(teams):
            T[team]["c"]["hands"] += 1
            T[team]["c"]["chips"] += h["results"][s]
            T[team]["c"]["third%d_hands" % third] += 1
            T[team]["c"]["third%d_chips" % third] += h["results"][s]
            sessions[s]["net"] += h["results"][s]
            fbet[s].append(("hand", h["n"]))

        for ei, e in enumerate(h["events"]):
            typ = e[0]
            if typ == "post":
                _, s, v = e
                c[s] += v
                contrib[s] += v
            elif typ == "refund":
                _, s, v = e
                contrib[s] -= v
                c[s] -= v
            elif typ == "win":
                paid[e[1]] += e[2]
            elif typ == "board":
                if street > 0:
                    prevbettor = (
                        firstbettor
                        if streetraises == 1 and streetcalled
                        else None
                    )
                street = STREETS.index(e[1])
                board = e[2]
                c = [0]*N
                mx = 0
                nr = 0
                checked = set()
                check_responded = set()
                streetseen = set()
                firstbettor = None
                streetraises = 0
                streetcalled = False
                street_raisers = set()
                last_bet = None
                last_ratio = 0
                last_tag = ""
                wager = None
                if street == 1:
                    flopset = alive.copy()
                    for s in flopset:
                        T[teams[s]]["c"]["flops"] += 1
            elif typ == "act":
                _, s, a, v = e
                team = teams[s]
                st = STREETS[street]
                pot = sum(contrib)
                cost = max(0, mx-c[s])
                stack = h["start_stacks"][s]-contrib[s]
                delta = v-c[s] if a == "raise" else v if a == "call" else 0
                can_xr = (
                    cost > 0 and s in checked and s not in check_responded
                )
                assert delta >= 0 and delta <= stack
                obs = {
                    "team": team, "round": rn, "hand": h["n"],
                    "seat": s, "street": st, "action": a,
                    "pot": pot, "cost": cost, "delta": delta,
                    "to": v, "position": pos[s],
                    "faced_ratio": last_ratio, "faced_tag": last_tag,
                    "live": len(alive), "hu": len(alive) == 2, "N": N,
                    "checked": s in checked,
                    "own_street_bet": s in street_raisers,
                    "our_live": our in alive,
                    "opp": teams[last_bet] if last_bet is not None else None,
                    "our_opp": wager is not None and wager["seat"] == our,
                    "event": ei, "tags": [], "pf_nr": nr,
                    "own_pf_raise": raised_at.get(s),
                    "pf_callers": len(pf_callers),
                    "pf_agg_pos": pos.get(pfagg),
                    "wager": wager.copy() if wager else None,
                }

                if street == 0:
                    initial = s not in acted
                    if initial:
                        if (
                            nr == 0 and limpers == 0
                            and s != (h["button"]+2) % N
                        ):
                            add(team, "open", 1, a == "raise")
                            add(team, "open_"+pos[s], 1, a == "raise")
                            if a == "raise":
                                sizes(team, "open_"+pos[s], v)
                                fbet[s].append(("open", v, pos[s], 0))
                                obs["tags"].append("open")
                        if a == "call" and nr == 0:
                            add(team, "limp", 0, 1)
                            limpers += 1
                        acted.add(s)
                    if nr == 1 and s not in seen3:
                        add(team, "threebet", 1, a == "raise")
                        seen3.add(s)
                        if a == "raise":
                            sizes(team, "threebet_to", v)
                            sizes(team, "threebet_multiple", v/mx)
                            fbet[s].append(("threebet", v, mx, pos[s]))
                    if nr == 2 and s not in seen4:
                        add(team, "fourbet", 1, a == "raise")
                        seen4.add(s)
                    if nr == 2 and raised_at.get(s) == 1 and s not in fold3:
                        add(team, "fold_threebet", 1, a == "fold")
                        fold3.add(s)
                    if nr == 3 and raised_at.get(s) == 2 and s not in fold4:
                        add(team, "fold_fourbet", 1, a == "fold")
                        fold4.add(s)
                    if initial and cost > 0 and nr > 0 and pos[s] in ("SB", "BB"):
                        add(team, "defend_"+pos[s], 1, a != "fold")
                        if (
                            nr == 1 and pfagg is not None
                            and pos[pfagg] in ("CO", "BTN", "SB")
                            and limpers == 0
                        ):
                            add(team, "steal_defend_"+pos[s], 1, a != "fold")
                            add(team, "steal_threebet_"+pos[s], 1, a == "raise")
                        streetseen.add(s)
                    if a == "call":
                        vp.add(s)
                        if nr > 0:
                            pf_callers.add(s)
                    if a == "raise":
                        vp.add(s)
                        pfr.add(s)
                        nr += 1
                        raised_at[s] = nr
                        pfagg = s
                        pf_callers = set()
                        if nr == 1 and "open" not in obs["tags"]:
                            sizes(team, "iso_to", v)
                            sizes(team, "iso_base", v-20*limpers)
                        if nr == 2:
                            sizes(team, "threebet_formula_33", v-round(mx*3.3))
                            sizes(team, "threebet_formula_38", v-round(mx*3.8))
                        if nr == 3:
                            sizes(team, "fourbet_to", v)
                        if delta == stack:
                            add(team, "pf_shove", 0, 1)
                            if s in shown:
                                T[team]["d"]["pf_shove_shown"][
                                    hole_name(shown[s])
                                ] += 1
                else:
                    if cost == 0:
                        context = "HU" if len(flopset) == 2 else "MW"
                        if street == 1 and pfagg == s:
                            add(team, "cbet_"+context, 1, a == "raise")
                            obs["tags"].append("cbet_"+context)
                        if street in (2, 3) and prevbettor == s:
                            tag = "barrel_"+st
                            add(team, tag, 1, a == "raise")
                            obs["tags"].append(tag)
                            if street == 3 and bets_by_street.get(1) == s:
                                add(team, "triple", 1, a == "raise")
                                obs["tags"].append("triple")
                        if checked:
                            add(team, "checked_to_"+st, 1, a == "raise")
                            obs["tags"].append("checked_to")
                        if a == "raise":
                            ratio = delta/pot
                            obs["ratio"] = ratio
                            obs["bucket"] = bucket(ratio)
                            sizes(team, "bet_"+st, ratio)
                            add(team, "overbet_"+st, 0, ratio > 1)
                            add(team, "bets_"+st, 0, 1)
                            for tag in obs["tags"]:
                                sizes(team, "size_"+tag, ratio)
                            fbet[s].append((
                                "bet", round(ratio, 3), st, len(flopset)
                            ))
                            last_tag = (
                                "cbet"
                                if any(x.startswith("cbet") for x in obs["tags"])
                                else "barrel"
                                if any(x.startswith("barrel") for x in obs["tags"])
                                else "bet"
                            )
                    else:
                        facingraise = streetraises >= 2
                        kind = "vsraise" if facingraise else "vsbet"
                        key = kind+"_"+st+"_"+bucket(last_ratio)
                        T[team]["d"][key][a] += 1
                        T[team]["d"][kind+"_"+st][a] += 1
                        obs["defender_kind"] = kind
                        if facingraise and s in street_raisers:
                            T[team]["d"]["after_own_bet_"+st][a] += 1
                        if last_tag in ("cbet", "barrel"):
                            T[team]["d"]["vs"+last_tag+"_"+st][a] += 1
                        if can_xr:
                            add(team, "checkraise_"+st, 1, a == "raise")
                            check_responded.add(s)
                        if a == "raise":
                            tag = "checkraise" if can_xr else "raise"
                            obs["tags"].append(tag)
                            ratio = (
                                (delta-cost)/(pot+cost) if pot+cost else 0
                            )
                            obs["ratio"] = ratio
                            obs["bucket"] = bucket(ratio)
                            sizes(team, "raise_"+st, ratio)
                            last_tag = tag
                        elif a == "call":
                            streetcalled = True
                    if a == "check":
                        checked.add(s)
                    if a == "raise":
                        if firstbettor is None:
                            firstbettor = s
                            bets_by_street[street] = s
                        streetraises += 1
                        street_raisers.add(s)
                        last_bet = s
                        last_ratio = obs.get("ratio", 0)
                        if s in shown:
                            cat = CLASSES[rank(shown[s]+board)[0]]
                            final = CLASSES[rank(shown[s]+h["board"])[0]]
                            tags = [
                                x for x in obs["tags"]
                                if x.startswith(("cbet", "barrel"))
                                or x in ("raise", "checkraise")
                            ]
                            line = ",".join(tags) or "other_bet"
                            key = "shown_"+st+"_"+line+"_"+obs["bucket"]
                            T[team]["d"][key][cat] += 1
                            T[team]["d"][key+"_final"][final] += 1
                            T[team]["d"][key+"_holes"][
                                hole_name(shown[s])
                            ] += 1
                            obs["shown_class"] = cat
                            obs["shown_hole"] = hole_name(shown[s])
                if a == "raise":
                    wager = {
                        "seat": s, "pot": pot, "risk": delta, "to": v,
                        "oldmax": mx, "previous": c[s],
                        "live": len(alive), "ratio": obs.get("ratio", 0),
                    }
                if a == "fold":
                    alive.remove(s)
                contrib[s] += delta
                c[s] += delta
                if a == "raise":
                    mx = c[s]
                handobs.append(obs)
                DECISIONS.append(obs)

        assert [
            paid[s]-contrib[s] for s in range(N)
        ] == h["results"]
        QUALITY["cash_checks"] += 1
        for s in vp:
            add(teams[s], "vpip", 0, 1)
            T[teams[s]]["c"]["third%d_vpip" % third] += 1
            fbet[s].append(("vpip",))
        for s in pfr:
            add(teams[s], "pfr", 0, 1)
            T[teams[s]]["c"]["third%d_pfr" % third] += 1
        for s in shown:
            T[teams[s]]["c"]["showdowns"] += 1
            T[teams[s]]["c"]["showdown_wins"] += paid[s] > 0
            T[teams[s]]["d"]["shown_holes"][hole_name(shown[s])] += 1
        ranks = {s: rank(shown[s]+h["board"]) for s in shown}
        level = 0
        modelpaid = [0.0]*N
        flow = [0.0]*N
        for lev in sorted(set(contrib)-{0}):
            investors = [s for s in range(N) if contrib[s] >= lev]
            eligible = [s for s in investors if s in alive]
            assert eligible
            if len(eligible) == 1:
                winners = eligible
            else:
                assert all(s in ranks for s in eligible)
                high = max(ranks[s] for s in eligible)
                winners = [s for s in eligible if ranks[s] == high]
            layer = (lev-level)*len(investors)
            share = 1/len(winners)
            for s in winners:
                modelpaid[s] += layer*share
            for s in range(N):
                if s != our:
                    flow[s] += (lev-level)*(
                        (our in investors)*(s in winners)*share
                        - (s in investors)*(our in winners)*share
                    )
            level = lev
        err = max(abs(modelpaid[s]-paid[s]) for s in range(N))
        QUALITY["layer_max_abs_error"] = max(
            QUALITY["layer_max_abs_error"], err
        )
        QUALITY["layer_odd_hands"] += err > 1e-8
        if any(abs(modelpaid[s]-paid[s]) > N for s in range(N)):
            QUALITY["layer_mismatch"] += 1
        for s, team in enumerate(teams):
            if s != our:
                T[team]["c"]["flow_from_us"] += flow[s]
        assert abs(sum(flow)-(-h["results"][our])) <= N
        for s in range(N):
            sessions[s]["features"].append(fbet[s])

    assert (
        sum(h["results"][our] for h in d["hands"])
        == d["round"]["chips"]
    )
    assert len(d["hands"]) == d["round"]["hands"]
    QUALITY["round_checks"] += 1


def team_output(team):
    c = T[team]["c"]
    ds = T[team]["d"]
    rates = {}
    for key in ["vpip", "pfr", "limp", "pf_shove"]:
        rates[key] = rate(c[key+"_yes"], c["hands"])
    for key in sorted({
        k[:-2] for k in c if k.endswith("_n") and c[k] > 0
    }):
        rates[key] = rate(c[key+"_yes"], c[key+"_n"])
    rates["wtsd"] = rate(c["showdowns"], c["flops"])
    rates["showdown_hands"] = rate(c["showdowns"], c["hands"])
    rates["won_showdown"] = rate(c["showdown_wins"], c["showdowns"])
    for st in STREETS[1:]:
        rates["overbet_"+st] = rate(
            c["overbet_"+st+"_yes"], c["bets_"+st+"_yes"]
        )
    return {
        "counts": dict(c),
        "rates": rates,
        "distributions": {
            k: desc(unpack(v))
            if k.startswith((
                "open_", "threebet", "fourbet", "iso_",
                "bet_", "raise_", "size_",
            ))
            else dict(v)
            for k, v in ds.items()
        },
        "rounds": [
            s["round"] for s in SESSIONS if s["team"] == team
        ],
        "bb100": round(c["chips"]*5/c["hands"], 3),
        "thirds": [{
            "hands": c["third%d_hands" % j],
            "chips": c["third%d_chips" % j],
            "vpip": rate(c["third%d_vpip" % j], c["third%d_hands" % j]),
            "pfr": rate(c["third%d_pfr" % j], c["third%d_hands" % j]),
        } for j in range(3)],
    }


OUT = {
    "quality": dict(QUALITY),
    "manifest": manifest,
    "teams": {t: team_output(t) for t in PRIMARY+BRIEF},
    "allteams": len(T),
    "sessions": len(SESSIONS),
}


def near(x, values, tol=.012):
    return any(abs(x-v) <= tol for v in values)


def fingerprint(features, name):
    flat = [f for hand in features for f in hand]
    op = [f for f in flat if f[0] == "open"]
    th = [f for f in flat if f[0] == "threebet"]
    be = [f for f in flat if f[0] == "bet"]
    if name == "Gherkers":
        return (
            len(op) >= 8
            and sum(f[1] == 70 or 71 <= f[1] <= 77 for f in op)/len(op) >= .9
            and len(th) >= 5
            and sum(
                min(abs(f[1]-round(f[2]*q)) for q in (3.2, 3.8)) <= 1
                for f in th
            )/len(th) >= .9
            and len(be) >= 5
            and sum(near(f[1], (.33, .7, 1.1)) for f in be)/len(be) >= .8
        )
    if name == "Equity Engine":
        return (
            len(op) >= 8
            and all(f[1] == 70 for f in op)
            and len(be) >= 8
            and sum(near(f[1], (.45, .5, .8)) for f in be)/len(be) >= .9
            and sum(near(f[1], (.5,)) for f in be) >= 2
            and sum(near(f[1], (.8,)) for f in be) >= 2
        )
    late = [f for f in op if f[2] in ("BTN", "SB")]
    return (
        len(op) >= 8
        and len(late) >= 3
        and all(f[1] == 50 for f in late)
        and sum(f[1] in (40, 80) for f in op) >= 2
        and len(th) >= 5
        and sum(
            f[1] in (3*f[2], 4*f[2], 5*f[2]) for f in th
        )/len(th) >= .95
        and len(be) >= 8
        and sum(
            near(f[1], (.33, .66, 1, .308, .19, .155)) for f in be
        )/len(be) >= .8
    )


FP = {}
for name in PRIMARY:
    pos = []
    neg = []
    blockpos = []
    blockneg = []
    wrong = collections.Counter()
    for sess in SESSIONS:
        alerts = []
        for end in range(200, len(sess["features"])+1, 100):
            match = fingerprint(sess["features"][end-200:end], name)
            if match:
                alerts.append(end)
        matching = sess["team"] == name
        (pos if matching else neg).append(bool(alerts))
        if alerts and not matching:
            wrong[sess["team"]] += 1
        for start in range(0, len(sess["features"])-199, 200):
            (blockpos if matching else blockneg).append(
                fingerprint(sess["features"][start:start+200], name)
            )
    first = [
        next((
            e for e in range(200, 1001, 100)
            if fingerprint(s["features"][e-200:e], name)
        ), None)
        for s in SESSIONS if s["team"] == name
    ]
    FP[name] = {
        "session_TP": rate(sum(pos), len(pos)),
        "session_FP": rate(sum(neg), len(neg)),
        "block_TP": rate(sum(blockpos), len(blockpos)),
        "block_FP": rate(sum(blockneg), len(blockneg)),
        "wrong_teams": dict(wrong),
        "first_detection": first,
    }
OUT["fingerprints"] = FP

ROUNDINFO = {}
for name in PRIMARY:
    rows = []
    for sess in SESSIONS:
        if sess["team"] != name:
            continue
        f = [v for hand in sess["features"] for v in hand]
        th = [v for v in f if v[0] == "threebet"]
        be = [v for v in f if v[0] == "bet"]
        op = [v for v in f if v[0] == "open"]
        ds = [
            v for v in DECISIONS
            if v["team"] == name and v["round"] == sess["round"]
        ]
        cb = [v for v in ds if "cbet_HU" in v["tags"]]
        rows.append({
            "round": sess["round"],
            "chips": sess["net"],
            "vpip": sum(v[0] == "vpip" for v in f),
            "pfr": len({
                v["hand"] for v in ds
                if v["street"] == "preflop" and v["action"] == "raise"
            }),
            "open": collections.Counter(v[1] for v in op).most_common(),
            "threebet": len(th),
            "threebet_formula": rate(sum(
                min(abs(v[1]-round(v[2]*q)) for q in (3.2, 3.8)) <= 1
                for v in th
            ), len(th)),
            "overbet": rate(sum(v[1] > 1 for v in be), len(be)),
            "HU_cbet": rate(sum(v["action"] == "raise" for v in cb), len(cb)),
            "bet_modes": collections.Counter(v[1] for v in be).most_common(5),
        })
    ROUNDINFO[name] = rows
OUT["roundinfo"] = ROUNDINFO


def wilson(k, n):
    if not n:
        return None
    z = 1.96
    p = k/n
    den = 1+z*z/n
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    center = (p+z*z/(2*n))/den
    return [
        round(max(0, center-half), 4),
        round(min(1, center+half), 4),
    ]


def evmodel(ds, name):
    n = len(ds)
    f = sum(o["action"] == "fold" for o in ds)
    if not n:
        return {"n": 0}
    p = f/n
    H = T[name]["c"]["hands"]
    P = statistics.mean(o["wager"]["pot"] for o in ds)
    R = statistics.mean(o["wager"]["risk"] for o in ds)
    lo = wilson(f, n)[0]
    own = sum(o["our_opp"] for o in ds)
    weight = sum(1/(o["N"]-1) for o in ds)
    return {
        "fold": rate(f, n),
        "wilson": wilson(f, n),
        "P": round(P, 3),
        "risk": round(R, 3),
        "break_even": round(R/(P+R), 4),
        "ev_bb": round((p*P-(1-p)*R)/20, 4),
        "equal_seat_opps100": round(100*weight/H, 4),
        "model_bb100": round(100*weight/H*(p*P-(1-p)*R)/20, 4),
        "lower_model_bb100": round(100*weight/H*(lo*P-(1-lo)*R)/20, 4),
        "response_to_our_seat": own,
    }


CANDIDATES = {}
for name in PRIMARY:
    ds = [
        o for o in DECISIONS
        if o["team"] == name and o.get("wager")
        and o["hu"] and o["wager"]["live"] == 2
    ]
    rows = {}
    selectors = {
        "flop_bet80": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and abs(o["faced_ratio"]-.8) <= .012
        ),
        "flop_bet67": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and abs(o["faced_ratio"]-2/3) <= .012
        ),
        "flop_bet100": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and abs(o["faced_ratio"]-1) <= .012
        ),
        "flop_bet110": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and abs(o["faced_ratio"]-1.1) <= .012
        ),
        "flop_raise_3B": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
            and abs(o["wager"]["to"]-3*o["wager"]["oldmax"]) <= 1
            and o["wager"]["previous"] == 0
        ),
        "BB_vs_SB50": lambda o: (
            o["street"] == "preflop" and o["position"] == "BB"
            and o["pf_nr"] == 1 and o["wager"]["to"] == 50
        ),
        "BB_vs_SB40": lambda o: (
            o["street"] == "preflop" and o["position"] == "BB"
            and o["pf_nr"] == 1 and o["wager"]["to"] == 40
        ),
        "fold3_all": lambda o: (
            o["street"] == "preflop" and o["pf_nr"] == 2
            and o["own_pf_raise"] == 1
        ),
        "fold3_3x": lambda o: (
            o["street"] == "preflop" and o["pf_nr"] == 2
            and o["own_pf_raise"] == 1
            and abs(o["wager"]["to"]-3*o["wager"]["oldmax"]) <= 1
        ),
        "fold4_all": lambda o: (
            o["street"] == "preflop" and o["pf_nr"] == 3
            and o["own_pf_raise"] == 2
        ),
        "fold4_23": lambda o: (
            o["street"] == "preflop" and o["pf_nr"] == 3
            and o["own_pf_raise"] == 2
            and abs(o["wager"]["to"]/o["wager"]["oldmax"]-2.3) <= .15
        ),
        "flop_checked_80": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and o["checked"] and abs(o["faced_ratio"]-.8) <= .012
        ),
        "turn_checked_80": lambda o: (
            o["street"] == "turn"
            and o.get("defender_kind") == "vsbet"
            and o["checked"] and abs(o["faced_ratio"]-.8) <= .012
        ),
        "river_checked_80": lambda o: (
            o["street"] == "river"
            and o.get("defender_kind") == "vsbet"
            and o["checked"] and abs(o["faced_ratio"]-.8) <= .012
        ),
        "flop_checked_110": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and o["checked"] and abs(o["faced_ratio"]-1.1) <= .012
        ),
        "flop_after_bet_raise": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
        ),
        "flop_after_bet_raise_small": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
            and o["wager"]["oldmax"] /
            max(1, o["wager"]["pot"]-o["wager"]["oldmax"]) <= .5
        ),
        "flop_raise_pot": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
            and abs(o["faced_ratio"]-1) <= .012
        ),
        "flop_raise_75": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
            and abs(o["faced_ratio"]-.75) <= .012
        ),
        "turn_after_bet_raise": lambda o: (
            o["street"] == "turn"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
        ),
    }
    for key, fn in selectors.items():
        sample = [o for o in ds if fn(o)]
        row = evmodel(sample, name)
        if sample:
            row["size_modes"] = collections.Counter(
                round(
                    o["faced_ratio"] if o["street"] != "preflop"
                    else o["wager"]["to"]/o["wager"]["oldmax"],
                    3,
                )
                for o in sample
            ).most_common(5)
        rows[key] = row
    CANDIDATES[name] = rows
OUT["candidates"] = CANDIDATES
OUT["context"] = {
    "bb": 20, "sb": 10, "stack": 2000,
    "n_seats": sorted(set(m["seats"] for m in manifest)),
    "rounds": len(files), "hands": QUALITY["hands"],
    "first_slot": manifest[0]["slot"], "last_slot": manifest[-1]["slot"],
    "sample_min": 30, "fingerprint_window": 200,
    "fingerprint_stride": 100, "fingerprint_size_tolerance": .012,
}

EVIDENCE = {}
for name in PRIMARY:
    ds = [o for o in DECISIONS if o["team"] == name]
    picked = [
        next(o for o in ds if "open" in o["tags"]),
        next(
            o for o in ds
            if o["street"] == "flop"
            and o["action"] == "raise" and o["cost"] == 0
        ),
    ]
    EVIDENCE[name] = []
    for o in picked:
        raw = json.loads(
            (ROOT/("saturday_r%03d.json" % o["round"])).read_text()
        )
        h = next(h for h in raw["hands"] if h["n"] == o["hand"])
        EVIDENCE[name].append({
            "round": o["round"], "hand": o["hand"], "seat": o["seat"],
            "obs": o, "events": h["events"][:o["event"]+1],
        })
OUT["evidence"] = EVIDENCE
OUT["fingerprint_intervals"] = {
    t: {
        "session_FP": wilson(x["session_FP"]["yes"], x["session_FP"]["n"]),
        "block_FP": wilson(x["block_FP"]["yes"], x["block_FP"]["n"]),
    }
    for t, x in FP.items()
}
OUT["formula_checks"] = {}
for name in PRIMARY:
    ds = [
        o for o in DECISIONS
        if o["team"] == name and o["street"] == "preflop"
        and o["action"] == "raise" and o["pf_nr"] == 1
    ]
    OUT["formula_checks"][name] = {
        "3x": rate(sum(
            o["to"] == round(3*o["wager"]["to"]) for o in ds
        ), len(ds)),
        "3.2_or_3.8": rate(sum(
            min(
                abs(o["to"]-round(q*o["wager"]["to"]))
                for q in (3.2, 3.8)
            ) <= 1 for o in ds
        ), len(ds)),
    }
OUT["pot_odds"] = {
    str(b): {
        "bluff_fold_pct": round(100*b/(1+b), 2),
        "call_equity_pct": round(100*b/(1+2*b), 2),
    }
    for b in (.33, .5, 2/3, .7, .8, 1, 1.05, 1.1)
}
OUT["third_summary"] = {
    t: [{
        "hands": r["hands"], "chips": r["chips"],
        "bb100": round(r["chips"]*5/r["hands"], 3) if r["hands"] else None,
        "vpip_pct": r["vpip"]["pct"], "pfr_pct": r["pfr"]["pct"],
    } for r in OUT["teams"][t]["thirds"]]
    for t in PRIMARY
}
OUT["brief_summary"] = {
    t: {
        "rounds": x["rounds"], "hands": x["counts"]["hands"],
        "chips": x["counts"]["chips"], "bb100": x["bb100"],
        "flow": round(x["counts"]["flow_from_us"], 3),
        "vpip": x["rates"]["vpip"], "pfr": x["rates"]["pfr"],
        "threebet": x["rates"]["threebet"],
        "fold3": x["rates"].get("fold_threebet"),
        "cbet_HU": x["rates"].get("cbet_HU"),
    }
    for t, x in OUT["teams"].items() if t in BRIEF
}

FIRST = {}
for name in PRIMARY:
    for s in SESSIONS:
        if s["team"] == name:
            FIRST[name, s["round"]] = next((
                end for end in range(200, 1001, 100)
                if fingerprint(s["features"][end-200:end], name)
            ), 1001)


def gate_model(ds, name):
    gated = [
        o for o in ds if o["hand"] > FIRST[name, o["round"]]
    ]
    return evmodel(gated, name)


for name in PRIMARY:
    ds = [
        o for o in DECISIONS
        if o["team"] == name and o.get("wager")
        and o["hu"] and o["wager"]["live"] == 2
    ]
    samples = {
        "flop_bet80": [
            o for o in ds if o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and abs(o["faced_ratio"]-.8) <= .012
        ],
        "flop_raise_3B": [
            o for o in ds if o["street"] == "flop"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
            and abs(o["wager"]["to"]-3*o["wager"]["oldmax"]) <= 1
            and o["wager"]["previous"] == 0
        ],
        "turn_checked_80": [
            o for o in ds if o["street"] == "turn"
            and o.get("defender_kind") == "vsbet"
            and o["checked"] and abs(o["faced_ratio"]-.8) <= .012
        ],
        "fold3_3x": [
            o for o in ds if o["street"] == "preflop"
            and o["pf_nr"] == 2 and o["own_pf_raise"] == 1
            and abs(o["wager"]["to"]-3*o["wager"]["oldmax"]) <= 1
        ],
    }
    for key, sample in samples.items():
        OUT["candidates"][name][key]["after_detection"] = gate_model(
            sample, name
        )

OUT["sd_lines"] = {}
for name in PRIMARY:
    rows = {}
    for o in DECISIONS:
        if o["team"] != name or "shown_class" not in o:
            continue
        tags = [
            tag for tag in o["tags"]
            if tag.startswith(("cbet", "barrel"))
            or tag in ("checkraise", "raise", "checked_to")
        ]
        if not tags:
            tags = ["other_bet"]
        for tag in tags:
            key = o["street"]+" "+tag
            rows.setdefault(
                key, {b: collections.Counter() for b in BUCKETS}
            )[o["bucket"]][o["shown_class"]] += 1
    OUT["sd_lines"][name] = {
        key: {
            b: {"n": sum(c.values()), "classes": dict(c)}
            for b, c in bs.items() if c
        }
        for key, bs in rows.items()
    }

OUT["third_post"] = {}
for name in PRIMARY:
    rows = []
    for j in range(3):
        rr = {
            s["round"] for s in SESSIONS
            if s["team"] == name and s["third"] == j
        }
        ds = [
            o for o in DECISIONS
            if o["team"] == name and o["round"] in rr
        ]
        cb = [o for o in ds if "cbet_HU" in o["tags"]]
        bets = [
            o for o in ds
            if o["street"] != "preflop"
            and o["cost"] == 0 and o["action"] == "raise"
        ]
        f3 = [
            o for o in ds
            if o["street"] == "preflop"
            and o["pf_nr"] == 2 and o["own_pf_raise"] == 1
        ]
        rows.append({
            "rounds": sorted(rr),
            "cbet_HU": rate(
                sum(o["action"] == "raise" for o in cb), len(cb)
            ),
            "overbet": rate(sum(o["ratio"] > 1 for o in bets), len(bets)),
            "fold3": rate(sum(o["action"] == "fold" for o in f3), len(f3)),
        })
    OUT["third_post"][name] = rows

OUT["full_open"] = {
    name: {
        k: dict(v) for k, v in T[name]["d"].items()
        if k.startswith("open_")
    }
    for name in PRIMARY
}
OUT["sizing_formula"] = {}
order = {
    p: i for i, p in enumerate(
        ("SB", "BB", "UTG", "UTG1", "LJ", "HJ", "CO", "BTN")
    )
}
for name in PRIMARY:
    ds = [
        o for o in DECISIONS
        if o["team"] == name and o["street"] == "preflop"
        and o["action"] == "raise" and o["pf_nr"] in (1, 2)
    ]
    by = collections.defaultdict(collections.Counter)
    for o in ds:
        w = o["wager"]
        if o["pf_nr"] == 1:
            for q in (3, 3.2, 3.8, 4, 5):
                if abs(o["to"]-round(q*w["to"])) <= 1:
                    by["3-bet"][str(q)] += 1
        else:
            for q in (2.3, 2.5, 3):
                if abs(o["to"]-round(q*w["to"])) <= 1:
                    by["4-bet"][str(q)] += 1
    OUT["sizing_formula"][name] = {
        k: dict(v) for k, v in by.items()
    }

OUT["verification"] = {
    "chip_reconciliations": QUALITY["cash_checks"],
    "layer_mismatches": QUALITY["layer_mismatch"],
    "raw_checks": {
        name: [{
            "round": e["round"], "hand": e["hand"], "seat": e["seat"],
            "amount": e["obs"]["to"], "pot": e["obs"]["pot"],
            "pct": round(100*e["obs"]["to"]/e["obs"]["pot"], 2),
        } for e in es]
        for name, es in EVIDENCE.items()
    },
}
OUT["model_limits"] = {
    "wilson_z": 1.96, "minimum_opportunities": 30,
    "equal_seat_weight": "1/(N-1)", "chip_to_bb": 20,
    "stop_window": 30, "max_counter_bluffs_per100": 1,
    "post_size": .8, "raise_bet_multiple": 3,
    "threebet_open_multiple": 3,
}

OUT["context"].update({
    "final_hands_given": 5000, "final_seats_given": 8,
    "advancers_given": 2,
    "third_rounds": [[1, 15], [16, 30], [31, 45]],
})
OUT["round_specific"] = {}
for name in PRIMARY:
    rows = []
    for sess in SESSIONS:
        if sess["team"] != name:
            continue
        ds = [
            o for o in DECISIONS
            if o["team"] == name and o["round"] == sess["round"]
        ]
        opp3 = [
            o for o in ds
            if o["street"] == "preflop" and o["pf_nr"] == 1
        ]
        rows.append({
            "round": sess["round"],
            "vpip": rate(
                sum(
                    f[0] == "vpip"
                    for h in sess["features"] for f in h
                ),
                len(sess["features"]),
            ),
            "threebet": rate(
                sum(o["action"] == "raise" for o in opp3), len(opp3)
            ),
        })
    OUT["round_specific"][name] = rows

OUT["summary_counts"] = {
    t: {
        "rounds": x["counts"]["rounds"],
        "hands": x["counts"]["hands"],
        "chips": x["counts"]["chips"],
        "bb100": x["bb100"],
        "from_our_seat": round(x["counts"]["flow_from_us"], 3),
    }
    for t, x in OUT["teams"].items()
}
OUT["our_result"] = {
    "hands": T["Resonance Qt"]["c"]["hands"],
    "chips": T["Resonance Qt"]["c"]["chips"],
    "bb100": round(
        T["Resonance Qt"]["c"]["chips"]*5 /
        T["Resonance Qt"]["c"]["hands"], 3
    ),
}

for team in list(OUT["teams"]):
    if team not in PRIMARY:
        del OUT["teams"][team]
    else:
        OUT["teams"][team]["distributions"] = {
            k: v for k, v in OUT["teams"][team]["distributions"].items()
            if not k.startswith("shown_")
        }
OUT["ran_end_to_end"] = True

OUT["formula_detail"] = {}
for name in PRIMARY:
    ds = [
        o for o in DECISIONS
        if o["team"] == name and o["street"] == "preflop"
        and o["action"] == "raise" and o["pf_nr"] == 1
    ]
    ip = [
        o for o in ds
        if order[o["position"]] > order[o["pf_agg_pos"]]
    ]
    oop = [
        o for o in ds
        if order[o["position"]] < order[o["pf_agg_pos"]]
    ]
    OUT["formula_detail"][name] = {
        "3plus_callers": rate(sum(
            o["to"] == (3+o["pf_callers"])*o["wager"]["to"]
            for o in ds
        ), len(ds)),
        "IP_3.2": rate(sum(
            abs(o["to"]-round(3.2*o["wager"]["to"])) <= 1
            for o in ip
        ), len(ip)),
        "OOP_3.8": rate(sum(
            abs(o["to"]-round(3.8*o["wager"]["to"])) <= 1
            for o in oop
        ), len(oop)),
    }
    opens = [
        o for o in DECISIONS
        if o["team"] == name and "open" in o["tags"]
    ]
    OUT["formula_detail"][name]["open_size_counts"] = dict(
        collections.Counter(o["to"] for o in opens)
    )
OUT["ran_end_to_end"] = True

OUT["defender"] = {
    name: {
        key: {
            "n": sum(c.values()),
            "fold": c["fold"], "call": c["call"], "raise": c["raise"],
            "unreliable": sum(c.values()) < 30,
        }
        for key, c in T[name]["d"].items()
        if key.startswith((
            "vsbet", "vsraise", "vscbet", "vsbarrel", "after_own_bet"
        ))
    }
    for name in PRIMARY
}
OUT["checked_sizes"] = {}
for name in PRIMARY:
    OUT["checked_sizes"][name] = {}
    for st in STREETS[1:]:
        for tag in ("checked_to", "checkraise"):
            vals = [
                o["ratio"] for o in DECISIONS
                if o["team"] == name and o["street"] == st
                and o["action"] == "raise" and tag in o["tags"]
            ]
            OUT["checked_sizes"][name][st+"_"+tag] = desc(
                [round(v, 3) for v in vals]
            )
OUT["ran_end_to_end"] = True
print(json.dumps(OUT))
