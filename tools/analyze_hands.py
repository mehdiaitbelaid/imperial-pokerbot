"""Summarise the hand histories that fetch_hands.py downloads.

    python3 fetch_hands.py --token YOUR-DATA-TOKEN      # fills hands/
    python3 tools/analyze_hands.py                      # reads hands/*.json
    python3 tools/analyze_hands.py hands/ --min-hands 50

Prints per opponent stats (hands, VPIP, PFR, aggression, fold to bet,
showdowns and the hands they showed) and our own result by position and by
the street the pot ended on.

Format assumptions, coded defensively because only the event list is
documented in fetch_hands.py:
  * a round file is {"hands": [...], "round": {...}}; a bare list of hands is
    also accepted.
  * each hand has "events" in the documented shape, plus optionally "button",
    "hole" or "cards" (seat -> two cards; our seat is the one whose cards
    appear in every hand), "results" (per seat chip result, list or dict),
    "players"/"names"/"seats" (seat -> team name) and "seat"/"you"/"our_seat".
  * when no names are given, an opponent is keyed by round and seat, since
    seats are reshuffled every round.
Anything missing is skipped rather than guessed.
"""
import argparse
import glob
import json
import os
import sys
from collections import defaultdict

BB_DEFAULT = 20
POS_NAMES = {0: "BTN", 1: "SB", 2: "BB"}


def pos_name(rel, n):
    if rel in POS_NAMES:
        return POS_NAMES[rel]
    from_end = n - rel
    return {1: "CO", 2: "HJ", 3: "MP"}.get(from_end, "UTG+%d" % (rel - 3) if rel > 3 else "UTG")


def as_seat_map(obj):
    """Turn a list or a dict keyed by seat strings into {int seat: value}."""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            try:
                out[int(k)] = v
            except (TypeError, ValueError):
                continue
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out[i] = v
    return out


def name_map(*sources):
    for src in sources:
        if not isinstance(src, dict):
            continue
        for key in ("players", "names", "seats", "teams", "table"):
            m = src.get(key)
            if isinstance(m, (dict, list)) and m:
                mm = as_seat_map(m)
                clean = {}
                for s, v in mm.items():
                    if isinstance(v, dict):
                        v = v.get("name") or v.get("team") or v.get("bot")
                    if isinstance(v, str):
                        clean[s] = v
                if clean:
                    return clean
    return {}


def find_our_seat(hands, data):
    for src in [data, data.get("round") if isinstance(data, dict) else None]:
        if isinstance(src, dict):
            for key in ("seat", "you", "our_seat", "my_seat"):
                if isinstance(src.get(key), int):
                    return src[key]
    # Our cards are the only ones visible in hands that ended without a
    # showdown, so count seats whose cards show while they did not show down.
    votes = defaultdict(int)
    for h in hands:
        if not isinstance(h, dict):
            continue
        for key in ("seat", "you", "our_seat", "my_seat"):
            if isinstance(h.get(key), int):
                return h[key]
        hole = as_seat_map(h.get("hole") or h.get("cards") or {})
        shown = replay(h)[4]
        for s, c in hole.items():
            if c and s not in shown:
                votes[s] += 1
    if votes:
        best = max(votes.values())
        top = [s for s, v in votes.items() if v == best]
        if len(top) == 1:
            return top[0]
    return None


def replay(hand):
    """Walk the events. Returns per seat put in, won, actions, end street, showdown seats."""
    put = defaultdict(int)
    won = defaultdict(int)
    acts = []
    street = "preflop"
    street_bet = defaultdict(int)
    for ev in hand.get("events") or []:
        if not isinstance(ev, list) or not ev:
            continue
        kind = ev[0]
        if kind == "post" and len(ev) >= 3:
            put[ev[1]] += ev[2]
            street_bet[ev[1]] += ev[2]
        elif kind == "board" and len(ev) >= 2:
            street = ev[1]
            street_bet = defaultdict(int)
        elif kind == "act" and len(ev) >= 4:
            seat, a, amt = ev[1], ev[2], ev[3] or 0
            if a == "call":
                put[seat] += amt
                street_bet[seat] += amt
            elif a == "raise":
                put[seat] += amt - street_bet[seat]
                street_bet[seat] = amt
            acts.append((street, seat, a, amt, dict(street_bet)))
        elif kind == "refund" and len(ev) >= 3:
            put[ev[1]] -= ev[2]
        elif kind == "win" and len(ev) >= 3:
            won[ev[1]] += ev[2]
    shown = set()
    for ev in hand.get("events") or []:
        if isinstance(ev, list) and ev and ev[0] == "win" and len(ev) >= 4 and ev[3]:
            shown.add(ev[1])
    if isinstance(hand.get("showdown"), dict):
        shown |= set(as_seat_map(hand["showdown"]))
    return put, won, acts, street, shown


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default="hands")
    ap.add_argument("--min-hands", type=int, default=30, help="hide opponents seen fewer hands")
    args = ap.parse_args()
    files = sorted(glob.glob(os.path.join(args.path, "*.json"))) if os.path.isdir(args.path) else [args.path]
    if not files:
        sys.exit("No round files in %s. Run fetch_hands.py first." % args.path)

    opp = defaultdict(lambda: defaultdict(int))
    shown_cards = defaultdict(list)
    by_pos = defaultdict(lambda: [0, 0])
    by_street = defaultdict(lambda: [0, 0])
    total_chips = total_hands = 0
    unknown_seat_rounds = 0

    for path in files:
        try:
            data = json.load(open(path))
        except Exception as e:
            print("skipping %s: %s" % (path, e))
            continue
        hands = data.get("hands") if isinstance(data, dict) else data
        if not isinstance(hands, list):
            continue
        rd = data.get("round", {}) if isinstance(data, dict) else {}
        ref = str(rd.get("ref") or os.path.basename(path))
        me = find_our_seat(hands, data)
        if me is None:
            unknown_seat_rounds += 1
        names = name_map(data if isinstance(data, dict) else {}, rd)
        for h in hands:
            if not isinstance(h, dict):
                continue
            bb = h.get("bb") or BB_DEFAULT
            put, won, acts, end_street, shown = replay(h)
            seats = set(put) | set(s for _, s, _, _, _ in acts)
            n = len(h.get("stacks") or []) or (max(seats) + 1 if seats else 8)
            hnames = name_map(h) or names
            key = lambda s: "us (all rounds)" if s == me else (hnames.get(s) or "%s seat %d" % (ref, s))  # noqa: E731

            # per opponent counters
            vpip, pfr, raised_pre = set(), set(), 0
            for st, s, a, amt, _ in acts:
                d = opp[key(s)]
                if st == "preflop":
                    if a in ("call", "raise"):
                        vpip.add(s)
                    if a == "raise":
                        pfr.add(s)
                        raised_pre += 1
                else:
                    if a == "raise":
                        d["agg"] += 1
                    elif a == "call":
                        d["calls"] += 1
                    elif a == "check":
                        d["checks"] += 1
            # fold to bet postflop: track the street's top bet
            cur = {}
            for st, s, a, amt, sb in acts:
                if st == "preflop":
                    continue
                top = max([v for v in sb.values()] + [0])
                if a == "fold":
                    opp[key(s)]["fold_bet"] += 1
                    opp[key(s)]["faced_bet"] += 1
                elif a == "call":
                    opp[key(s)]["faced_bet"] += 1
                elif a == "raise" and cur.get(st, 0) > 0:
                    opp[key(s)]["faced_bet"] += 1
                if a == "raise":
                    cur[st] = top
            for s in seats:
                d = opp[key(s)]
                d["hands"] += 1
                d["vpip"] += s in vpip
                d["pfr"] += s in pfr
                d["sd"] += s in shown
            hole = as_seat_map(h.get("hole") or h.get("cards") or {})
            for s in shown:
                if s != me and hole.get(s):
                    shown_cards[key(s)].append("".join(hole[s]))

            if me is None:
                continue
            res = as_seat_map(h.get("results") or {})
            if me in res and isinstance(res[me], (int, float)):
                net = res[me]
            else:
                net = won.get(me, 0) - put.get(me, 0)
            total_chips += net
            total_hands += 1
            button = h.get("button")
            if isinstance(button, int):
                p = pos_name((me - button) % n, n)
                by_pos[p][0] += 1
                by_pos[p][1] += net / float(bb)
            by_street[end_street][0] += 1
            by_street[end_street][1] += net / float(bb)

    print("opponents (seen at least %d hands)" % args.min_hands)
    print("%-34s %6s %5s %5s %6s %8s %5s  shown" % ("player", "hands", "vpip", "pfr", "agg", "fold bet", "sd"))
    rows = sorted(opp.items(), key=lambda kv: -kv[1]["hands"])
    for name, d in rows:
        if d["hands"] < args.min_hands:
            continue
        acts = d["agg"] + d["calls"] + d["checks"]
        print("%-34s %6d %5.2f %5.2f %6.2f %8s %5d  %s" % (
            name[:34], d["hands"], d["vpip"] / d["hands"], d["pfr"] / d["hands"],
            d["agg"] / acts if acts else 0.0,
            "%.2f" % (d["fold_bet"] / d["faced_bet"]) if d["faced_bet"] else "n/a",
            d["sd"], " ".join(shown_cards[name][:8])))
    if total_hands:
        print("\nour result: %d hands, %+.1f bb/100" % (total_hands, total_chips / float(BB_DEFAULT) / total_hands * 100))
        print("\nby position          hands   bb/100")
        for p, (k, bbs) in sorted(by_pos.items(), key=lambda kv: kv[0]):
            print("  %-16s %7d %+8.1f" % (p, k, bbs / k * 100))
        print("\nby street pot ended  hands   bb/100")
        for s in ("preflop", "flop", "turn", "river"):
            if s in by_street:
                k, bbs = by_street[s]
                print("  %-16s %7d %+8.1f" % (s, k, bbs / k * 100))
    if unknown_seat_rounds:
        print("\n%d round(s) where our seat could not be identified; our win rate skips them." % unknown_seat_rounds)


if __name__ == "__main__":
    main()
