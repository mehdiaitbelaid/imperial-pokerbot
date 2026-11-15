"""Round tracker for Sunday Table D (read-only on hands/).

    python3 -I reports/track.py hands/sunday_s1_r002.json [more files] [--top 3]

Prints, for the given round(s) together:
  our 3-bets by opener and the opener's next action; our 4-bets by 3-bettor and his reply;
  our postflop raises of a bet, by bettor and V22 size bucket, with the bettor's reply;
  chips won from / lost to each opponent (each hand's result split among the other side in proportion);
  per opponent: open sizes, limp, 3-bet rate, fold to 3-bet, fold to 4-bet, bet sizes, fold when raised;
  the biggest wins and losses with a compact action line.
"""
import json, sys
from collections import Counter, defaultdict

AB = {"Resonance Qt": "US", "Anker Batteries": "ANK", "Chinese people can fly": "CPF", "WBot": "WB",
      "GamesGone": "GG", "Poke": "POK", "Anton": "ANT", "YSL_TWIZZY": "YSL"}
DOSSIER = {
    "ANK": "open 2.5 (100%); bets 1.1/2.0/0.7/0.4, multiway 0.62; 3bet 13% (9% late); f3b 44-57%; f4b 78%",
    "CPF": "open 2.5 (93%) 3.0 (6%); bets 0.33 (65%) 1.0 (25%); 3bet 6%; f3b 81-84%; raised after 0.33 folds 80%",
    "WB": "open 3.5 or 2.8; bets 0.15, river 3.0; 3bet 5%; f3b 53%; raised after 0.15 folds 79%",
    "GG": "open 2.2 (95-99%); bets 0.5/1.0; 3bet 3%; f3b 36%; raised after 0.5 folds 74%",
    "POK": "open 2.5, limps 28%; bets 0.33/0.8/1.6/0.55/1.1; raised after 0.33 folds 59%, 0.8 71%",
    "ANT": "open 3/4.5/2.5/6.6; bets 0.55/0.8/0.33/0.6/1.1; 3bet 26-32%; f4b 59-66%; raised after bet folds 83%",
    "YSL": "open 2.8 (77%) 2.5 (20%); bets 0.48/0.77/0.42/0.38; f3b 85%; raised after bet folds 0%",
}
BUCKETS = [(0.24, "<0.24"), (0.42, "0.24-0.42"), (0.65, "0.42-0.65"), (0.90, "0.65-0.90"), (1.30, "0.90-1.30"), (99, "1.30+")]
RANKS = "23456789TJQKA"


def bucket(x):
    for lim, name in BUCKETS:
        if x < lim:
            return name
    return "1.30+"


def premium(hole):
    if not hole:
        return None
    a, b = sorted((RANKS.index(c[0]) for c in hole), reverse=True)
    suited = hole[0][1] == hole[1][1]
    if a == b:
        return a >= RANKS.index("T")
    if a == 12 and b >= RANKS.index("Q"):
        return True
    if a == 12 and b == RANKS.index("J") and suited:
        return True
    if a == 11 and b == 10 and suited:
        return True
    return False


def pct(k, n):
    return f"{k}/{n}" + (f" ({100*k//n}%)" if n else "")


def main():
    args = [a for a in sys.argv[1:]]
    top = 3
    if "--top" in args:
        i = args.index("--top")
        top = int(args[i + 1])
        del args[i:i + 2]
    files = args
    our3 = defaultdict(lambda: {"n": 0, "light": 0, "fold": 0, "call": 0, "raise": 0, "other": 0, "net": 0, "lnet": 0, "lfold": 0,
                                "opp": 0, "won_pre": 0, "we_fold": 0, "flop": 0})
    our4 = defaultdict(lambda: {"n": 0, "fold": 0, "call": 0, "raise": 0, "other": 0, "net": 0})
    they3us = defaultdict(lambda: {"n": 0, "fold": 0, "call": 0, "raise": 0, "net": 0})
    ourraise = defaultdict(lambda: {"n": 0, "fold": 0, "call": 0, "raise": 0, "net": 0})
    flow = Counter()
    cold4 = Counter()
    opp = defaultdict(lambda: {"open": Counter(), "nopen": 0, "limp": 0, "hands": 0, "t3": 0, "o3": 0, "f3": 0, "f3n": 0,
                               "f3us": 0, "f3usn": 0, "f4": 0, "f4n": 0, "bets": Counter(), "nbet": 0,
                               "rf": Counter(), "rn": Counter(), "vpip": 0, "pfr": 0, "net": 0})
    hands_all = []
    total = 0
    nh = 0
    for f in files:
        d = json.load(open(f))
        me = d["seat"]
        names = [AB.get(p, p[:4]) for p in d["players"]]
        tag = f.split("_")[-1].split(".")[0]
        for h in d["hands"]:
            nh += 1
            bb = h["bb"]
            res = h["results"]
            mine = res[me]
            total += mine
            for s, r in enumerate(res):
                opp[names[s]]["net"] += r
                opp[names[s]]["hands"] += 1
            # chip flow
            if mine < 0:
                w = {s: r for s, r in enumerate(res) if r > 0}
                tw = sum(w.values())
                for s, r in w.items():
                    flow[names[s]] += mine * r / tw
            elif mine > 0:
                l = {s: -r for s, r in enumerate(res) if r < 0}
                tl = sum(l.values())
                for s, r in l.items():
                    flow[names[s]] += mine * r / tl
            street = "pre"
            contrib = defaultdict(int)
            pot = 0
            raises = []           # preflop raisers in order
            limpers = 0
            acted3 = set()
            pend3 = None          # (opener, threebettor) waiting for opener's reply
            pend4 = None          # (threebettor, fourbettor)
            vp = set()
            pf = set()
            street_bet = None     # (bettor, sizefrac) first bet on this postflop street
            street_raised = False
            pendr = None          # (bettor, bucket, raiser) waiting for bettor's reply
            line = []
            we3 = None
            we_fold_pre = False
            hole = h.get("hole", {}).get(str(me))
            for e in h["events"]:
                k = e[0]
                if k == "post":
                    contrib[e[1]] += e[2]
                    pot += e[2]
                elif k == "board":
                    street = e[1]
                    contrib = defaultdict(int)
                    street_bet = None
                    street_raised = False
                    pendr = None
                    line.append("| " + " ".join(e[2][-3:] if street == "flop" else e[2][-1:]))
                elif k == "act":
                    s, a, amt = e[1], e[2], e[3]
                    nm = names[s]
                    if a != "fold" and not (a == "check"):
                        line.append(f"{nm} {a[0]}{amt}")
                    if street == "pre":
                        nr = len(raises)
                        # replies to pending 3-bet / 4-bet
                        if pend3 and s == pend3[0] and nr == 2:
                            o, tb = pend3
                            key = a if a in ("fold", "call", "raise") else "other"
                            opp[names[o]]["f3n"] += 1
                            opp[names[o]]["f3"] += a == "fold"
                            if tb == me:
                                opp[names[o]]["f3usn"] += 1
                                opp[names[o]]["f3us"] += a == "fold"
                                our3[names[o]][key] += 1
                                if premium(hole) is False and a == "fold":
                                    our3[names[o]]["lfold"] += 1
                            if o == me:
                                they3us[names[tb]][key] += 1
                            pend3 = None
                        elif pend3 and s == pend3[0]:
                            pend3 = None
                        if pend4 and s == pend4[0] and nr == 3:
                            tb, fb = pend4
                            key = a if a in ("fold", "call", "raise") else "other"
                            opp[names[tb]]["f4n"] += 1
                            opp[names[tb]]["f4"] += a == "fold"
                            if fb == me:
                                our4[names[tb]][key] += 1
                            pend4 = None
                        elif pend4 and s == pend4[0]:
                            pend4 = None
                        if s == me and a == "fold":
                            we_fold_pre = True
                        if nr == 1 and s != raises[0] and s not in acted3:
                            if s == me:
                                our3[names[raises[0]]]["opp"] += 1
                            acted3.add(s)
                            opp[nm]["o3"] += 1
                            opp[nm]["t3"] += a == "raise"
                        if a == "call":
                            vp.add(s)
                            if nr == 0:
                                limpers += 1
                                opp[nm]["limp"] += 1
                            contrib[s] += amt
                            pot += amt
                        elif a == "raise":
                            vp.add(s)
                            pf.add(s)
                            if nr == 0:
                                if limpers == 0:
                                    opp[nm]["open"][round(amt / bb, 1)] += 1
                                    opp[nm]["nopen"] += 1
                            elif nr == 1:
                                pend3 = (raises[0], s)
                                if s == me:
                                    we3 = names[raises[0]]
                                    o3 = our3[names[raises[0]]]
                                    o3["n"] += 1
                                    o3["net"] += mine
                                    if premium(hole) is False:
                                        o3["light"] += 1
                                        o3["lnet"] += mine
                                if raises[0] == me:
                                    they3us[nm]["n"] += 1
                                    they3us[nm]["net"] += mine
                            elif nr == 2:
                                pend4 = (raises[1], s)
                                if raises[1] == me:
                                    cold4[nm + ("(opener)" if s == raises[0] else "(cold)")] += 1
                                if s == me:
                                    our4[names[raises[1]]]["n"] += 1
                                    our4[names[raises[1]]]["net"] += mine
                            raises.append(s)
                            pot += amt - contrib[s]
                            contrib[s] = amt
                    else:
                        if pendr and s == pendr[0]:
                            b, bk, rz = pendr
                            key = a if a in ("fold", "call", "raise") else "call"
                            opp[names[b]]["rn"][bk] += 1
                            opp[names[b]]["rf"][bk] += a == "fold"
                            if rz == me:
                                ourraise[(names[b], bk)][key] += 1
                            pendr = None
                        if a == "call":
                            contrib[s] += amt
                            pot += amt
                        elif a == "raise":
                            if street_bet is None:
                                frac = amt / pot if pot else 0
                                street_bet = (s, frac)
                                opp[nm]["bets"][round(frac * 20) / 20] += 1
                                opp[nm]["nbet"] += 1
                            elif not street_raised:
                                street_raised = True
                                b, frac = street_bet
                                if b != s:
                                    pendr = (b, bucket(frac), s)
                                    if s == me:
                                        ourraise[(names[b], bucket(frac))]["n"] += 1
                                        ourraise[(names[b], bucket(frac))]["net"] += mine
                            pot += amt - contrib[s]
                            contrib[s] = amt
            if we3:
                our3[we3]["we_fold" if we_fold_pre else ("flop" if street != "pre" else "won_pre")] += 1
            for s in vp:
                opp[names[s]]["vpip"] += 1
            for s in pf:
                opp[names[s]]["pfr"] += 1
            sd = h.get("showdown", {}) or {}
            shown = {names[int(s)]: "".join(c) + ("=" + str(sd[s]) if s in sd else "") for s, c in h.get("hole", {}).items() if int(s) != me}
            hands_all.append((mine, tag, h["n"], "".join(hole or []), " ".join(line), shown))

    print(f"{len(files)} round(s), {nh} hands, our total {total:+d} chips = {total/20/nh*100:+.1f} bb/100")
    print("\nOUR PREFLOP 3-BETS by opener (light = not TT+, AK, AQ, AJs, KQs):")
    for o, v in sorted(our3.items(), key=lambda x: -x[1]["n"]):
        rep = v["fold"] + v["call"] + v["raise"]
        print(f"  {o:4s} n={v['n']:3d} of {v['opp']:3d} opps, light={v['light']:3d} | opener folded {pct(v['fold'], rep)}, called {v['call']}, 4-bet {v['raise']}"
              f" | ended: won preflop {v['won_pre']}, we folded to a 4-bet {v['we_fold']}, flop {v['flop']}"
              f" | net {v['net']:+d} chips (light {v['lnet']:+d})")
    t = {k: sum(v[k] for v in our3.values()) for k in ("n", "light", "fold", "call", "raise", "net", "lnet")}
    print(f"  ALL  n={t['n']} light={t['light']} folded {pct(t['fold'], t['fold']+t['call']+t['raise'])} net {t['net']:+d} (light {t['lnet']:+d})")
    print("  who 4-bet our 3-bets: " + ", ".join(f"{k} {v}" for k, v in cold4.most_common()))
    print("OUR 4-BETS by 3-bettor:")
    for o, v in sorted(our4.items(), key=lambda x: -x[1]["n"]):
        rep = v["fold"] + v["call"] + v["raise"]
        print(f"  {o:4s} n={v['n']:3d} | he folded {pct(v['fold'], rep)}, called {v['call']}, 5-bet {v['raise']} | net {v['net']:+d} chips")
    print("THEIR 3-BETS OF OUR OPENS (our reply):")
    for o, v in sorted(they3us.items(), key=lambda x: -x[1]["n"]):
        print(f"  {o:4s} n={v['n']:3d} | we folded {v['fold']}, called {v['call']}, 4-bet {v['raise']} | net {v['net']:+d} chips")
    print("OUR POSTFLOP RAISES OF A BET (bettor, bet size bucket -> his reply):")
    for (o, bk), v in sorted(ourraise.items(), key=lambda x: (x[0][0], x[0][1])):
        rep = v["fold"] + v["call"] + v["raise"]
        print(f"  {o:4s} {bk:10s} n={v['n']:3d} | folded {pct(v['fold'], rep)}, called {v['call']}, re-raised {v['raise']} | net {v['net']:+d} chips")
    small = [v for (o, bk), v in ourraise.items() if bk in ("<0.24", "0.24-0.42")]
    mid = [v for (o, bk), v in ourraise.items() if bk in ("0.42-0.65", "0.65-0.90")]
    for nm_, grp in (("under 0.42 pot", small), ("0.42-0.90 pot", mid)):
        n = sum(v["n"] for v in grp); fo = sum(v["fold"] for v in grp); net = sum(v["net"] for v in grp)
        print(f"  total {nm_}: n={n}, folded {pct(fo, n)}, net {net:+d} chips")
    print("\nCHIPS FROM EACH OPPONENT (our result split among the other side in proportion):")
    print("  " + "  ".join(f"{o} {int(round(v)):+d}" for o, v in sorted(flow.items(), key=lambda x: -x[1])))
    print("\nOPPONENTS (this sample | dossier):")
    for o in ("ANK", "CPF", "WB", "GG", "POK", "ANT", "YSL"):
        v = opp[o]
        if not v["hands"]:
            continue
        op = " ".join(f"{sz}:{100*c//v['nopen']}%" for sz, c in v["open"].most_common(4)) if v["nopen"] else "-"
        bt = " ".join(f"{sz:.2f}:{100*c//v['nbet']}%" for sz, c in v["bets"].most_common(5)) if v["nbet"] else "-"
        rf = " ".join(f"{bk}:{v['rf'][bk]}/{v['rn'][bk]}" for _, bk in BUCKETS if v["rn"][bk])
        print(f"  {o:4s} {v['net']/20/v['hands']*100:+6.1f} bb/100 VPIP {100*v['vpip']//v['hands']} PFR {100*v['pfr']//v['hands']} limp {100*v['limp']//v['hands']}%"
              f" | opens(n={v['nopen']}) {op} | 3bet {pct(v['t3'], v['o3'])} | f3b {pct(v['f3'], v['f3n'])}, to ours {pct(v['f3us'], v['f3usn'])}"
              f" | f4b {pct(v['f4'], v['f4n'])}")
        print(f"       bets(n={v['nbet']}) {bt} | folds when raised: {rf or '-'}")
        print(f"       dossier: {DOSSIER[o]}")
    hands_all.sort()
    print(f"\nBIGGEST LOSSES:")
    for m, tag, n, hole, line, shown in hands_all[:top]:
        print(f"  {m:+6d} {tag}#{n} {hole} :: {line} :: shown {shown}")
    print("BIGGEST WINS:")
    for m, tag, n, hole, line, shown in hands_all[::-1][:top]:
        print(f"  {m:+6d} {tag}#{n} {hole} :: {line} :: shown {shown}")


if __name__ == "__main__":
    main()
