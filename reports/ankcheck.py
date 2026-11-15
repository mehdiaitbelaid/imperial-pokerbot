"""Anker change check: his stats in the given round(s) against his r002-r020 average.
    python3 -I reports/ankcheck.py hands/sunday_s1_r023.json [...]
VPIP, PFR, 3-bet, open size, overbet share (bets over 1.05 pot), fold to OUR bets by street,
river bet after WE check the river (and what he showed: weak = less than two pair... one pair or less).
"""
import json, sys, os, glob
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from bigcalls import klass

def stats(files):
    S = defaultdict(float)
    for f in files:
        d = json.load(open(f)); me = d["seat"]; ank = d["players"].index("Anker Batteries")
        for h in d["hands"]:
            S["hands"] += 1
            street = "pre"; contrib = defaultdict(int); pot = 0; raises = 0; vp = pf = False; acted3 = False
            pend = None; we_checked_river = False; river_bet_before = False; live = set(range(len(d["players"]))); ank_rbet = False
            for e in h["events"]:
                if e[0] == "post":
                    contrib[e[1]] += e[2]; pot += e[2]
                elif e[0] == "board":
                    street = e[1]; contrib = defaultdict(int); pend = None
                elif e[0] == "act":
                    s, a, amt = e[1], e[2], e[3]
                    if a == "fold": live.discard(s)
                    if street == "pre":
                        if s == ank:
                            if raises == 1 and not acted3 and not pf:
                                acted3 = True; S["tb_o"] += 1; S["tb"] += a == "raise"
                            if a in ("call", "raise"): vp = True
                            if a == "raise":
                                pf = True
                                if raises == 0: S["open_n"] += 1; S["open_bb"] += amt / h["bb"]
                        if a == "raise": raises += 1; pot += amt - contrib[s]; contrib[s] = amt
                        elif a == "call": pot += amt; contrib[s] += amt
                    else:
                        if pend and s == ank:
                            S["fb_o_" + pend] += 1; S["fb_" + pend] += a == "fold"; pend = None
                        if street == "river" and s == ank and we_checked_river and not river_bet_before and me in live and a in ("check", "raise"):
                            S["rc_o"] += 1
                            if a == "raise":
                                S["rc"] += 1; ank_rbet = True
                            we_checked_river = False
                        if a == "raise":
                            if max(contrib.values() or [0]) == 0:
                                if s == ank:
                                    S["bets"] += 1; S["over"] += amt / pot > 1.05 if pot else 0
                                if s == me and ank in live: pend = street
                                if street == "river" and s != ank: river_bet_before = True
                            pot += amt - contrib[s]; contrib[s] = amt
                        elif a == "call": pot += amt; contrib[s] += amt
                        elif a == "check" and street == "river" and s == me and not river_bet_before and ank in live:
                            we_checked_river = True
            S["vpip"] += vp; S["pfr"] += pf
            if ank_rbet and str(ank) in h["hole"]:
                k = klass(h["hole"][str(ank)], h["board"]).split("+")[0]
                S["rc_shown"] += 1; S["rc_weak"] += k != "strong"; S["rc_air"] += k == "nopair"
    return S

def pc(a, b): return 100.0 * a / b if b else float("nan")
def line(S):
    return [("VPIP", pc(S["vpip"], S["hands"]), S["hands"]), ("PFR", pc(S["pfr"], S["hands"]), S["hands"]), ("3-bet", pc(S["tb"], S["tb_o"]), S["tb_o"]),
            ("overbets", pc(S["over"], S["bets"]), S["bets"]), ("fold to our flop bet", pc(S["fb_flop"], S["fb_o_flop"]), S["fb_o_flop"]),
            ("fold to our turn bet", pc(S["fb_turn"], S["fb_o_turn"]), S["fb_o_turn"]), ("fold to our river bet", pc(S["fb_river"], S["fb_o_river"]), S["fb_o_river"]),
            ("bets river after our check", pc(S["rc"], S["rc_o"]), S["rc_o"])]

base = stats(sorted(glob.glob(os.path.join(os.path.dirname(HERE), "hands", "sunday_s1_r00[2-9].json")) + glob.glob(os.path.join(os.path.dirname(HERE), "hands", "sunday_s1_r01*.json")) + glob.glob(os.path.join(os.path.dirname(HERE), "hands", "sunday_s1_r020.json"))))
cur = stats(sys.argv[1:])
out = []; flags = []
for (n, v, k), (_, bv, bk) in zip(line(cur), line(base)):
    out.append("%s %.0f%% (n=%d; base %.0f%%)" % (n, v, k, bv))
    if k >= 8 and abs(v - bv) > 8: flags.append("%s %+.0f" % (n, v - bv))
out.insert(3, "open %.2fbb (n=%d; base %.2f)" % (cur["open_bb"] / max(1, cur["open_n"]), cur["open_n"], base["open_bb"] / max(1, base["open_n"])))
out.append("river bets after our check shown: %d, one pair or less %d, no pair %d (base shown %d, one pair or less %d, no pair %d)" % (cur["rc_shown"], cur["rc_weak"], cur["rc_air"], base["rc_shown"], base["rc_weak"], base["rc_air"]))
print("ANKER CHECK (%d round(s)): " % len(sys.argv[1:]) + "; ".join(out))
print("ANKER FLAGS (moves over 8 points, n>=8): " + (", ".join(flags) or "none"))
