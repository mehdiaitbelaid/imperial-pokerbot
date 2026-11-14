"""Measure how often the field folds to pressure, spot by spot.

    python3 tools/fold_analysis.py ../hands-data/hands
    python3 tools/fold_analysis.py ../hands-data/hands --min-opp 20

Reads the round files fetch_hands.py writes ({ref, seat, players, hands,
round}) and prints:

  1. per responder fold, call and raise rates for each pressure spot,
     population of opponents only;
  2. per attempt fold through (every responder folded) with the break even
     fold rate of a pure bluff at the size used and its EV in bb, assuming
     zero equity when called, flagged when the fold rate beats break even by
     10 points or more over at least 30 attempts;
  3. the same fold rates per opponent team, plus how much each team fights
     back (3-bets, raises against bets, check raises);
  4. what the field does to us;
  5. hand classes opponents show down after calling or making a big bet;
  6. shrinkage pseudo counts estimated from the spread between teams;
  7. our own opportunities per 100 hands for each pressure spot.

Stdlib only. Spot definitions are in the comments next to the code that
records them. Postflop "raise" events with nothing to call are bets.
"""
import argparse
import glob
import json
import os
import sys
from collections import defaultdict

RANKS = "23456789TJQKA"
LATE = ("CO", "BTN", "SB")
BLINDS = ("SB", "BB")


def pos_label(seat, button, n):
    rel = (seat - button) % n
    if rel == 0:
        return "BTN"
    if rel == 1:
        return "SB"
    if rel == 2:
        return "BB"
    if rel == n - 1:
        return "CO"
    if rel == n - 2:
        return "HJ"
    return "EP"


def size_bucket(frac):
    if frac < 0.40:
        return "<40%"
    if frac < 0.70:
        return "40..70%"
    if frac <= 1.10:
        return "70..110%"
    return ">110%"


def open_bucket(raise_to, bb):
    x = raise_to / float(bb)
    if x <= 2.5:
        return "<=2.5bb"
    if x <= 3.5:
        return "2.5..3.5bb"
    if x <= 5:
        return "3.5..5bb"
    return ">5bb"


def shove_pot_bucket(pot, bb):
    x = pot / float(bb)
    if x <= 3:
        return "pot<=3bb"
    if x <= 10:
        return "pot 3..10bb"
    if x <= 30:
        return "pot 10..30bb"
    return "pot>30bb"


# Hand classes for showdown evidence. Classified on the board as it was when
# the bet was made or called, by what the hole cards add to it.
def classify(hole, board):
    try:
        hr = [RANKS.index(c[0]) for c in hole]
        hs = [c[1] for c in hole]
        br = [RANKS.index(c[0]) for c in board]
        bs = [c[1] for c in board]
    except (ValueError, IndexError, TypeError):
        return None
    if len(hr) != 2 or len(br) < 3:
        return None
    allr = hr + br
    suits = hs + bs
    for s in set(hs):
        if suits.count(s) >= 5 and bs.count(s) < 5:
            return "monster"
    if has_straight(set(allr)) and not (len(br) >= 5 and has_straight(set(br))):
        if not has_straight(set(br)):
            return "monster"
    bcount = defaultdict(int)
    for r in br:
        bcount[r] += 1
    pocket = hr[0] == hr[1]
    if pocket and bcount[hr[0]] >= 1:
        return "monster"  # set or quads
    for r in hr:
        if bcount[r] >= 2:
            return "monster"  # trips or better with the board pair
    paired = [r for r in hr if bcount[r] >= 1]
    if not pocket and len(set(paired)) == 2:
        return "monster"  # two pair using both hole cards
    top = max(br)
    if pocket and hr[0] > top:
        return "top/overpair"
    if top in paired:
        return "top/overpair"
    if pocket or paired:
        return "weak pair"
    if len(br) < 5 and draw(hr, hs, br, bs):
        return "draw"
    return "air"


def has_straight(rs):
    rs = set(rs)
    if 12 in rs:
        rs.add(-1)
    for lo in range(-1, 9):
        if all(r in rs for r in range(lo, lo + 5)):
            return True
    return False


def draw(hr, hs, br, bs):
    suits = hs + bs
    for s in set(hs):
        if suits.count(s) == 4:
            return True
    rs = set(hr + br)
    if 12 in rs:
        rs.add(-1)
    hset = set(hr) | ({-1} if 12 in hr else set())
    # any four of five consecutive ranks using a hole card, gutshots included
    for lo in range(-1, 9):
        win = set(range(lo, lo + 5))
        if len(win & rs) >= 4 and win & hset:
            return True
    return False


class Tally:
    """fold, call, raise counts per (spot, team)."""

    def __init__(self):
        self.d = defaultdict(lambda: [0, 0, 0])

    def add(self, spot, team, resp):
        i = {"fold": 0, "call": 1, "raise": 2}[resp]
        self.d[(spot, team)][i] += 1
        if team != "*us":
            self.d[(spot, "*field")][i] += 1

    def get(self, spot, team):
        return self.d.get((spot, team), [0, 0, 0])


def fmt_rate(k, n, min_n):
    if n == 0:
        return "    -   "
    r = "%.2f(%d)" % (k / float(n), n)
    return r + ("!" if n < min_n else " ")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default="hands")
    ap.add_argument("--min-opp", type=int, default=30, help="opportunities below this are marked unreliable with !")
    ap.add_argument("--min-hands", type=int, default=300, help="hide teams seen fewer hands in the per team tables")
    args = ap.parse_args()
    files = sorted(glob.glob(os.path.join(args.path, "*.json"))) if os.path.isdir(args.path) else [args.path]
    if not files:
        sys.exit("no round files in %s" % args.path)

    resp = Tally()
    attempts = defaultdict(list)       # key -> [(pot_bb, risk_bb, success, by_us)]
    attempts_us_resp = defaultdict(list)
    team_hands = defaultdict(int)
    team_rounds = defaultdict(set)
    vpip = defaultdict(int)
    pfr = defaultdict(int)
    chk = defaultdict(lambda: [0, 0])  # team -> [checks with nothing to call, then bet into]
    chk_hu = defaultdict(lambda: [0, 0])
    xr = defaultdict(lambda: [0, 0])   # team -> [checked then faced bet, raised]
    our_bets = defaultdict(lambda: [0, 0])  # spot -> [our bets, raised by someone]
    opps_us = defaultdict(lambda: [0, 0, 0])  # spot -> [opportunities, attempts, successes]
    sd_call = defaultdict(lambda: defaultdict(int))
    sd_bet = defaultdict(lambda: defaultdict(int))
    spot_obs_by_teamround = defaultdict(lambda: defaultdict(int))
    opps_cls = defaultdict(lambda: [0, 0])
    call_log = defaultdict(list)
    total_hands = 0
    rounds = 0
    skipped = 0

    for path in files:
        try:
            with open(path) as fh:
                data = json.load(fh)
        except (OSError, ValueError) as e:
            print("skipping %s: %s" % (path, e))
            continue
        if not isinstance(data, dict) or not isinstance(data.get("hands"), list):
            continue
        me = data.get("seat")
        if not isinstance(me, int):
            me = (data.get("round") or {}).get("seat")
        players = data.get("players") or []
        ref = str(data.get("ref") or os.path.basename(path))
        rounds += 1

        def team(s):
            if s == me:
                return "*us"
            if isinstance(players, list) and 0 <= s < len(players) and isinstance(players[s], str):
                return players[s]
            return "%s seat %d" % (ref, s)

        for h in data["hands"]:
            if not isinstance(h, dict) or not isinstance(h.get("events"), list):
                skipped += 1
                continue
            try:
                walk(h, me, team, ref, args, resp, attempts, attempts_us_resp, team_hands, team_rounds,
                     vpip, pfr, chk, chk_hu, xr, our_bets, opps_us, sd_call, sd_bet, spot_obs_by_teamround,
                     len(players) if isinstance(players, list) else 0, opps_cls, call_log)
                total_hands += 1
            except (KeyError, IndexError, TypeError, ValueError) as e:
                skipped += 1
                if skipped <= 3:
                    print("skipped hand %s in %s: %r" % (h.get("n"), ref, e))

    report(args, resp, attempts, attempts_us_resp, team_hands, team_rounds, vpip, pfr, chk, chk_hu, xr,
           our_bets, opps_us, sd_call, sd_bet, spot_obs_by_teamround, total_hands, rounds, skipped, opps_cls,
           call_log)


def walk(h, me, team, ref, args, resp, attempts, attempts_us_resp, team_hands, team_rounds, vpip, pfr,
         chk, chk_hu, xr, our_bets, opps_us, sd_call, sd_bet, obs_tr, n_players, opps_cls, call_log):
    start = h.get("start_stacks") or []
    n = len(start) or n_players
    if n < 2:
        raise ValueError("table size unknown")
    if not start:
        start = [2000] * n
    bb = h.get("bb") or 20
    button = h.get("button")
    if not isinstance(button, int):
        raise ValueError("no button")
    pos = [pos_label(s, button, n) for s in range(n)]
    hole = {}
    for k, v in (h.get("hole") or {}).items():
        try:
            hole[int(k)] = v
        except ValueError:
            pass

    put = [0] * n
    sbet = [0] * n
    folded = [False] * n
    allin = [False] * n
    street = "preflop"
    board = []
    top = 0
    pf_raises = 0
    pf_raisers = []   # seats in raise order
    limpers = 0
    limp_seats = set()
    pf_aggr = None
    voluntary = False  # any voluntary preflop action yet
    first_bet = {}     # street -> bettor seat
    checked = []       # seats that checked this street with nothing to call
    checked_set = set()
    xr_pending = set()
    cur = None         # current attempt: dict
    street_start_active = n
    big_calls = {}     # seat -> (street, board snapshot)
    big_bets = {}
    seen = set()
    our_calls = []
    pf_vol = set()
    pf_raise_set = set()

    def close(att):
        if not att or not att["resps"]:
            return
        success = all(r == "fold" for r in att["resps"])
        rec = (att["pot"] / float(bb), att["risk"] / float(bb), success, att["bettor"] == me)
        if att["us_resp"]:
            for k in att["akeys"]:
                attempts_us_resp[k].append(rec)
        else:
            for k in att["akeys"]:
                attempts[k].append(rec)
        if att["bettor"] == me and att["okey"]:
            our_bets[att["okey"]][0] += 1
            our_bets[att["okey"]][1] += any(r == "raise" for r in att["resps"])

    for ev in h["events"]:
        if not isinstance(ev, list) or not ev:
            continue
        kind = ev[0]
        if kind == "post" and len(ev) >= 3:
            s, amt = ev[1], ev[2] or 0
            put[s] += amt
            sbet[s] += amt
            top = max(top, sbet[s])
            seen.add(s)
            continue
        if kind == "board" and len(ev) >= 3:
            close(cur)
            cur = None
            flush_checks(checked, team, chk, chk_hu, street_start_active)
            checked = []
            checked_set = set()
            xr_pending = set()
            street = ev[1]
            board = list(ev[2]) if isinstance(ev[2], list) else board
            sbet = [0] * n
            top = 0
            street_start_active = sum(1 for s in range(n) if not folded[s])
            continue
        if kind != "act" or len(ev) < 3:
            continue
        s, a = ev[1], ev[2]
        amt = ev[3] if len(ev) >= 4 and ev[3] is not None else 0
        seen.add(s)
        to_call = top - sbet[s]
        pot_before = sum(put)
        tm = team(s)
        if a == "all_in":
            # not seen in the data so far; treat as a raise to the whole stack
            a = "raise"
            amt = start[s] - (put[s] - sbet[s])
            if amt <= top:
                a, amt = "call", min(to_call, start[s] - put[s])

        # our opportunities, recorded before the action is applied
        if s == me:
            our_opportunity(street, a, to_call, pos[s], pf_raises, limpers, voluntary, pf_aggr, me,
                            first_bet, street_start_active, opps_us, opps_cls, hole.get(me), board, checked_set,
                            team(pf_raisers[0]) if pf_raisers else "")

        if a in ("call", "raise") and street == "preflop":
            pf_vol.add(s)
            voluntary = True
            if a == "raise":
                pf_raise_set.add(s)

        # a response to the current bet
        if cur is not None and s != cur["bettor"] and to_call > 0 and a in ("fold", "call", "raise"):
            r = a
            keys = cur["rkeys"](s)
            for k in keys:
                resp.add(k, tm, r)
                obs_tr[(ref, tm)][k] += 1
            cur["resps"].append(r)
            if s == me:
                cur["us_resp"] = True
            if s in xr_pending:
                xr[tm][0] += 1
                xr[tm][1] += a == "raise"
                xr_pending.discard(s)
            if a == "call" and street != "preflop" and cur["risk"] > 0.6 * cur["pot"]:
                big_calls[s] = (street, list(board))
            if s == me and a == "call" and street != "preflop":
                frac = cur["risk"] / float(cur["pot"]) if cur["pot"] else 0
                our_calls.append((street, "big" if frac > 0.6 else "small", to_call / float(pot_before + to_call)))

        if a == "fold":
            folded[s] = True
        elif a == "check":
            if to_call == 0 and street != "preflop":
                checked.append(s)
                checked_set.add(s)
        elif a == "call":
            put[s] += amt
            sbet[s] += amt
            if street == "preflop" and pf_raises == 0:
                limpers += 1
                limp_seats.add(s)
        elif a == "raise":
            risk = amt - sbet[s]
            prev_top = top
            prev_bettor = cur["bettor"] if cur else None
            close(cur)
            put[s] += risk
            sbet[s] = amt
            top = max(top, amt)
            if put[s] >= start[s]:
                allin[s] = True
            cur = make_attempt(s, street, amt, risk, pot_before, prev_top, prev_bettor, pos, pf_raises,
                               pf_raisers, limp_seats, pf_aggr, first_bet, checked_set, street_start_active,
                               allin[s], bb, me)
            if street == "preflop":
                if pf_raises == 1 and pf_raisers:
                    cur["akeys"].append("pf 3bet vs opener %s" % team(pf_raisers[0]))
                pf_raises += 1
                pf_raisers.append(s)
                pf_aggr = s
            else:
                if prev_top == 0:
                    first_bet.setdefault(street, s)
                    # everyone who checked earlier on this street was bet into
                    for c in checked:
                        if c != s:
                            k = team(c)
                            chk[k][0] += 1
                            chk[k][1] += 1
                            if street_start_active == 2:
                                chk_hu[k][0] += 1
                                chk_hu[k][1] += 1
                            xr_pending.add(c)
                    checked = []
                if street in ("turn", "river") and risk > 0.6 * pot_before:
                    big_bets[s] = (street, list(board))
        if a == "call" and put[s] >= start[s]:
            allin[s] = True
    close(cur)
    flush_checks(checked, team, chk, chk_hu, street_start_active)
    winners = set(ev[1] for ev in h["events"] if isinstance(ev, list) and len(ev) >= 3 and ev[0] == "win")
    res = h.get("results")
    net = res[me] / float(bb) if isinstance(res, list) and isinstance(me, int) and me < len(res) else 0.0
    # one record per street and size, so a hand with two calls counts twice
    for st, sz, req in our_calls:
        call_log[(st, sz)].append((req, me in winners, net))
    for s in seen:
        k = team(s)
        team_hands[k] += 1
        team_rounds[k].add(ref)
        vpip[k] += s in pf_vol
        pfr[k] += s in pf_raise_set
    for s, (st, bd) in big_calls.items():
        if s != me and s in hole:
            c = classify(hole[s], bd)
            if c:
                sd_call[team(s)][c] += 1
                sd_call["*field"][c] += 1
    for s, (st, bd) in big_bets.items():
        if s != me and s in hole:
            c = classify(hole[s], bd)
            if c:
                sd_bet[team(s)][c] += 1
                sd_bet["*field"][c] += 1


def flush_checks(checked, team, chk, chk_hu, active):
    # checks nobody bet into before the street ended
    for c in checked:
        k = team(c)
        chk[k][0] += 1
        if active == 2:
            chk_hu[k][0] += 1


def make_attempt(s, street, amt, risk, pot, prev_top, prev_bettor, pos, pf_raises, pf_raisers, limp_seats,
                 pf_aggr, first_bet, checked_set, active, is_allin, bb, me):
    """Build the spot keys for responders (rkeys) and for the attempt (akeys)."""
    akeys = []
    okey = None
    frac = risk / float(pot) if pot else 0.0
    hu = active == 2
    hw = "HU" if hu else "MW"

    if street == "preflop":
        if pf_raises == 0 and not limp_seats:
            opener_pos = pos[s]
            bucket = open_bucket(amt, bb)
            akeys.append("pf open from %s" % opener_pos)
            if opener_pos in LATE:
                akeys.append("pf steal from %s" % opener_pos)
                akeys.append("pf steal from %s size %s" % (opener_pos, bucket))
            okey = "pf open"

            def rkeys(r):
                ks = ["pf fold to open: folder %s" % pos[r], "pf fold to open: size %s" % bucket]
                if opener_pos in LATE and pos[r] in BLINDS:
                    ks.append("pf blind vs steal: %s vs %s" % (pos[r], opener_pos))
                if is_allin:
                    ks.append("pf vs shove: %s" % shove_pot_bucket(pot, bb))
                return ks
        else:
            opener = pf_raisers[0] if pf_raisers else None
            three = pf_raisers[1] if len(pf_raisers) > 1 else None
            level = pf_raises + 1
            if pf_raises == 0:
                akeys.append("pf iso over limpers")
                okey = "pf iso"
            elif level == 2:
                akeys.append("pf 3bet")
                okey = "pf 3bet"
            elif level == 3:
                akeys.append("pf 4bet")
                okey = "pf 4bet"
            else:
                akeys.append("pf 5bet+")
            if is_allin:
                akeys.append("pf shove %s" % shove_pot_bucket(pot, bb))

            def rkeys(r):
                ks = []
                if level == 2 and r == opener:
                    ks.append("pf opener vs 3bet")
                elif level == 3 and r == three:
                    ks.append("pf 3bettor vs 4bet")
                elif pf_raises == 0 and r in limp_seats:
                    ks.append("pf limper vs iso")
                if is_allin:
                    ks.append("pf vs shove: %s" % shove_pot_bucket(pot, bb))
                return ks
        return {"bettor": s, "pot": pot, "risk": risk, "rkeys": rkeys, "akeys": akeys, "resps": [],
                "us_resp": False, "okey": okey}

    bucket = size_bucket(frac)
    if prev_top == 0:
        line = line_of(street, s, pf_aggr, first_bet, checked_set)
        akeys = ["%s %s" % (line, hw), "%s %s %s" % (line, hw, bucket)]
        LINE_KEYS.add(akeys[0])
        if street == "river":
            # all river first bets together, for the size table
            akeys += ["river bet %s" % hw, "river bet %s %s" % (hw, bucket)]
        if is_allin:
            akeys.append("%s shove" % street)
        okey = "%s first bet" % street

        def rkeys(r):
            ks = list(akeys)
            if is_allin:
                ks.append("post vs shove")
            return ks
    else:
        how = "check raise" if s in checked_set else "bet raise"
        akeys = ["%s raise vs bettor (%s)" % (street, how)]
        if is_allin:
            akeys.append("%s raise all in" % street)
        okey = "%s raise" % street

        def rkeys(r):
            ks = []
            if r == prev_bettor:
                ks.append("%s bettor vs %s" % (street, how))
                ks.append("%s bettor vs raise" % street)
            if is_allin:
                ks.append("post vs shove")
            return ks
    return {"bettor": s, "pot": pot, "risk": risk, "rkeys": rkeys, "akeys": akeys, "resps": [],
            "us_resp": False, "okey": okey}


LINE_KEYS = set()


def line_of(street, s, pf_aggr, first_bet, checked_set):
    """Name the betting line of a first bet on a postflop street by seat s."""
    if street == "flop":
        if s == pf_aggr:
            return "flop cbet"
        if pf_aggr is None:
            return "flop bet in limped pot"
        if pf_aggr in checked_set:
            return "flop stab after aggressor checked"
        return "flop lead into aggressor"
    prev = "flop" if street == "turn" else "turn"
    fb = first_bet.get(prev)
    if fb == s:
        return "turn barrel" if street == "turn" else "river barrel"
    if fb is None:
        return "%s bet after %s checked through" % (street, prev)
    if fb in checked_set:
        return "%s stab after %s bettor checked" % (street, prev)
    return "%s lead into %s bettor" % (street, prev)


def our_opportunity(street, a, to_call, p, pf_raises, limpers, voluntary, pf_aggr, me, first_bet, active,
                    opps, opps_cls, cards, board, checked_set, opener_team):
    bet = a == "raise"
    if street == "preflop":
        if not voluntary and pf_raises == 0:
            key = "steal from %s (folded to us)" % p if p in LATE else "open from %s (folded to us)" % p
            opps[key][0] += 1
            opps[key][1] += bet
        elif pf_raises == 0 and to_call >= 0:
            opps["facing limpers"][0] += 1
            opps["facing limpers"][1] += bet
        elif pf_raises == 1 and to_call > 0:
            for key in ("facing one open", "facing one open from %s" % opener_team):
                opps[key][0] += 1
                opps[key][1] += bet
        return
    if to_call != 0:
        return
    hw = "HU" if active == 2 else "MW"
    key = "%s %s" % (line_of(street, me, pf_aggr, first_bet, checked_set), hw)
    opps[key][0] += 1
    opps[key][1] += bet
    c = classify(cards, board) if cards else None
    if c:
        opps_cls[(key, c)][0] += 1
        opps_cls[(key, c)][1] += bet


def report(args, resp, attempts, attempts_us_resp, team_hands, team_rounds, vpip, pfr, chk, chk_hu, xr,
           our_bets, opps_us, sd_call, sd_bet, obs_tr, total_hands, rounds, skipped, opps_cls, call_log):
    m = args.min_opp
    print("rounds %d, hands %d, skipped hands %d. '!' marks fewer than %d opportunities (unreliable)."
          % (rounds, total_hands, skipped, m))

    spots = sorted(set(k for k, t in resp.d))
    print("\n1. FIELD (opponents only) response to pressure, per responder")
    print("%-52s %6s %6s %6s %6s %8s" % ("spot", "n", "fold", "call", "raise", "obs/100h"))
    for sp in spots:
        f, c, r = resp.get(sp, "*field")
        n = f + c + r
        if not n:
            continue
        # observations per opponent per 100 hands, averaged over team rounds
        tot_obs = sum(v.get(sp, 0) for (rf, tm), v in obs_tr.items() if tm != "*us")
        opp_hands = sum(hn for tm, hn in team_hands.items() if tm != "*us")
        rate = 100.0 * tot_obs / opp_hands if opp_hands else 0
        print("%-52s %5d%s %6.2f %6.2f %6.2f %8.2f" % (sp[:52], n, "!" if n < m else " ", f / float(n),
                                                       c / float(n), r / float(n), rate))

    print("\n2. PURE BLUFF EV per attempt (every responder an opponent; zero equity when called)")
    print("   fold = share of attempts where every responder folded; BE = risk/(pot+risk); "
          "EV = fold*pot - (1-fold)*risk in bb")
    print("%-50s %5s %6s %6s %5s %5s %5s %6s %6s  %s" % ("attempt", "n", "pot", "risk", "size", "fold", "BE",
                                                     "edge", "EV bb", "flag"))
    for k in sorted(attempts):
        rows = attempts[k]
        n = len(rows)
        if n < 5:
            continue
        pot = sum(r[0] for r in rows) / n
        risk = sum(r[1] for r in rows) / n
        f = sum(1 for r in rows if r[2]) / float(n)
        be = risk / (pot + risk) if pot + risk else 0
        ev = f * pot - (1 - f) * risk
        flag = ""
        if f - be >= 0.10 and n >= 30:
            flag = "PRESSURE"
        elif f - be <= -0.10 and n >= 30:
            flag = "LOSES"
        elif n < m:
            flag = "unreliable"
        print("%-50s %5d %6.1f %6.1f %5.2f %5.2f %5.2f %+6.2f %+6.2f  %s" % (
            k[:50], n, pot, risk, risk / pot if pot else 0, f, be, f - be, ev, flag))

    print("\n   our own attempts only (subset of table 2: bettor is us)")
    print("%-50s %5s %5s %5s %6s" % ("attempt", "n", "fold", "BE", "EV bb"))
    for k in sorted(attempts):
        rows = [r for r in attempts[k] if r[3]]
        n = len(rows)
        if n < 5:
            continue
        pot = sum(r[0] for r in rows) / n
        risk = sum(r[1] for r in rows) / n
        f = sum(1 for r in rows if r[2]) / float(n)
        be = risk / (pot + risk) if pot + risk else 0
        print("%-50s %4d%s %5.2f %5.2f %+6.2f" % (k[:50], n, "!" if n < m else " ", f, be, f * pot - (1 - f) * risk))

    teams = sorted([t for t in team_hands if team_hands[t] >= args.min_hands],
                   key=lambda t: (t != "*us", -team_hands[t]))
    cols = [
        ("stealdef", ["pf blind vs steal: SB vs CO", "pf blind vs steal: SB vs BTN", "pf blind vs steal: BB vs CO",
                      "pf blind vs steal: BB vs BTN", "pf blind vs steal: BB vs SB"]),
        ("vs3bet", ["pf opener vs 3bet"]),
        ("vs4bet", ["pf 3bettor vs 4bet"]),
        ("vsshove", [k for k in spots if k.startswith("pf vs shove")]),
        ("cbetHU", ["flop cbet HU"]),
        ("cbetMW", ["flop cbet MW"]),
        ("barrel", ["turn barrel HU", "turn barrel MW"]),
        ("delayed", ["turn bet after flop checked through HU", "turn bet after flop checked through MW"]),
        ("riverbet", ["river bet HU", "river bet MW"]),
        ("vsraise", ["flop bettor vs raise", "turn bettor vs raise", "river bettor vs raise"]),
        ("anybet", sorted(LINE_KEYS)),
    ]
    print("\n3a. FOLD RATE per team, fold(n). '*us' is our bot. Teams with fewer than %d hands hidden." % args.min_hands)
    print("%-26s %5s %4s " % ("team", "hands", "rds") + " ".join("%-10s" % c for c, _ in cols))
    for t in teams:
        cells = []
        for c, keys in cols:
            f = n = 0
            for k in keys:
                a = resp.get(k, t)
                f += a[0]
                n += sum(a)
            cells.append("%-10s" % fmt_rate(f, n, m))
        print("%-26s %5d %4d " % (t[:26], team_hands[t], len(team_rounds[t])) + " ".join(cells))
    cells = []
    for c, keys in cols:
        f = n = 0
        for k in keys:
            a = resp.get(k, "*field")
            f += a[0]
            n += sum(a)
        cells.append("%-10s" % fmt_rate(f, n, m))
    print("%-26s %5s %4s " % ("*field (opponents)", "", "") + " ".join(cells))

    print("\n3b. FIGHT BACK and looseness per team: rate(n)")
    fcols = [
        ("vpip", None), ("pfr", None),
        ("3bet vs open", ["pf fold to open: folder %s" % p for p in ("EP", "HJ", "CO", "BTN", "SB", "BB")], 2),
        ("call vs cbet", ["flop cbet HU", "flop cbet MW"], 1),
        ("raise vs cbet", ["flop cbet HU", "flop cbet MW"], 2),
        ("raise vs bet", sorted(LINE_KEYS), 2),
        ("check raise", None),
    ]
    print("%-26s " % "team" + " ".join("%-13s" % c[0] for c in fcols))
    for t in teams:
        cells = ["%-13s" % ("%.2f(%d)" % (vpip[t] / float(team_hands[t]), team_hands[t])),
                 "%-13s" % ("%.2f(%d)" % (pfr[t] / float(team_hands[t]), team_hands[t]))]
        for c in fcols[2:6]:
            k = n = 0
            for key in c[1]:
                a = resp.get(key, t)
                k += a[c[2]]
                n += sum(a)
            cells.append("%-13s" % fmt_rate(k, n, m))
        x = xr[t]
        cells.append("%-13s" % fmt_rate(x[1], x[0], m))
        print("%-26s " % t[:26] + " ".join(cells))

    print("\n4. WHAT THE FIELD DOES TO US")
    print("   our bets that got raised (raised by any responder)")
    for k in sorted(our_bets):
        b, r = our_bets[k]
        print("   %-30s %s" % (k, fmt_rate(r, b, m)))
    print("   bet into after a check with nothing to call (postflop), all pots and heads up")
    print("   %-26s %-12s %-12s" % ("who checked", "all", "HU"))
    fa = [0, 0]
    fh = [0, 0]
    for t, v in chk.items():
        if t != "*us":
            fa[0] += v[0]
            fa[1] += v[1]
            fh[0] += chk_hu[t][0]
            fh[1] += chk_hu[t][1]
    us = chk.get("*us", [0, 0])
    ush = chk_hu.get("*us", [0, 0])
    print("   %-26s %-12s %-12s" % ("us", fmt_rate(us[1], us[0], m), fmt_rate(ush[1], ush[0], m)))
    print("   %-26s %-12s %-12s" % ("opponents", fmt_rate(fa[1], fa[0], m), fmt_rate(fh[1], fh[0], m)))
    print("   our fold rates in each spot: row '*us' in table 3a; full detail below")
    print("%-52s %6s %6s %6s %6s" % ("spot (us responding)", "n", "fold", "call", "raise"))
    for sp in spots:
        f, c, r = resp.get(sp, "*us")
        n = f + c + r
        if n >= 10:
            print("%-52s %5d%s %6.2f %6.2f %6.2f" % (sp[:52], n, "!" if n < m else " ", f / float(n), c / float(n),
                                                     r / float(n)))

    print("\n5. SHOWDOWN EVIDENCE (board at the time of the bet or call)")
    classes = ["monster", "top/overpair", "weak pair", "draw", "air"]
    for title, src in (("a) opponents who called a bet over 60% pot postflop and showed down", sd_call),
                       ("b) opponents who bet over 60% pot on turn or river and showed down", sd_bet)):
        print("   " + title)
        print("   %-26s %5s " % ("team", "n") + " ".join("%-13s" % c for c in classes))
        for t in ["*field"] + [x for x in teams if x != "*us"]:
            d = src.get(t)
            if not d:
                continue
            n = sum(d.values())
            print("   %-26s %4d%s " % (t[:26], n, "!" if n < m else " ") +
                  " ".join("%-13s" % ("%.2f(%d)" % (d[c] / float(n), d[c])) for c in classes))

    print("\n6. SHRINKAGE PRIOR from the spread between opponent teams (method of moments, beta binomial)")
    print("   pseudo count = p(1-p)/var_between - 1; small = teams differ a lot, trust per seat data early")
    print("%-28s %6s %6s %6s %6s %10s" % ("stat", "teams", "p", "sd", "N0", "team range"))
    stats = [("fold any postflop 1st bet", cols[10][1]), ("fold vs steal (blinds)", cols[0][1]), ("fold cbet HU", ["flop cbet HU"]),
             ("fold cbet MW", ["flop cbet MW"]), ("fold opener vs 3bet", ["pf opener vs 3bet"]),
             ("fold turn barrel", cols[6][1]), ("fold river bet", cols[8][1])]
    for name, keys in stats:
        pts = []
        for t in team_hands:
            if t == "*us":
                continue
            f = n = 0
            for k in keys:
                a = resp.get(k, t)
                f += a[0]
                n += sum(a)
            if n >= 15:
                pts.append((f / float(n), n))
        if len(pts) < 3:
            print("%-28s %6d   too few teams" % (name, len(pts)))
            continue
        tot = sum(n for _, n in pts)
        p = sum(r * n for r, n in pts) / tot
        var_obs = sum(n * (r - p) ** 2 for r, n in pts) / tot
        # expected binomial noise in the n weighted spread: sum n * p(1-p)/n over total n
        noise = len(pts) * p * (1 - p) / tot
        var_b = var_obs - noise
        if var_b <= 0:
            n0 = "inf"
            sd = 0.0
        else:
            n0 = "%.0f" % max(0.0, p * (1 - p) / var_b - 1)
            sd = var_b ** 0.5
        print("%-28s %6d %6.2f %6.2f %6s %4.2f..%4.2f" % (name, len(pts), p, sd, n0, min(r for r, _ in pts),
                                                        max(r for r, _ in pts)))

    print("\n7. OUR OPPORTUNITIES per 100 of our hands (attempt = we bet or raised)")
    our_n = team_hands.get("*us", 0)
    print("   our hands: %d" % our_n)
    print("   facing one open from X: per100 counts only hands of rounds where X sat at our table")
    print("%-44s %6s %8s %8s" % ("spot", "n", "per100", "we bet"))
    for k in sorted(opps_us):
        o, a, _ = opps_us[k]
        base = our_n
        if k.startswith("facing one open from "):
            base = team_hands.get(k[len("facing one open from "):], our_n)
        print("%-44s %6d %8.2f %8.2f" % (k[:44], o, 100.0 * o / base if base else 0, a / float(o) if o else 0))

    print("\n   our hand class in each postflop spot: share of spots, and how often we bet it")
    classes = ["monster", "top/overpair", "weak pair", "draw", "air"]
    print("%-44s %5s " % ("spot", "n") + " ".join("%-15s" % c for c in classes))
    for k in sorted(opps_us):
        o = opps_us[k][0]
        if o < 15 or not any((k, c) in opps_cls for c in classes):
            continue
        cells = []
        for c in classes:
            n, b = opps_cls.get((k, c), [0, 0])
            cells.append("%-15s" % ("%.2f(%d) b%.2f" % (n / float(o), n, b / float(n)) if n else "-"))
        print("%-44s %5d " % (k[:44], o) + " ".join(cells))

    print("\n8. OUR CALLS facing a postflop bet: how often we end up winning the pot")
    print("   req = call/(pot after call), the equity a call needs; net = our whole hand result in bb")
    print("%-22s %5s %7s %7s %8s" % ("street, bet size", "n", "won", "req", "net bb"))
    for st in ("flop", "turn", "river"):
        for sz in ("small", "big"):
            rows = call_log.get((st, sz), [])
            if not rows:
                continue
            n = len(rows)
            print("%-22s %4d%s %7.2f %7.2f %+8.2f" % ("%s %s" % (st, "<=60%" if sz == "small" else ">60%"), n,
                                                      "!" if n < m else " ", sum(r[1] for r in rows) / float(n),
                                                      sum(r[0] for r in rows) / n, sum(r[2] for r in rows) / n))


if __name__ == "__main__":
    main()
