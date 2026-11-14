"""Replay our own decisions from real hand histories through a bot build.

    python3 tools/replay.py upload/bot.py hands/saturday_r003.json

For every decision we faced, rebuilds the state the dealer sent, asks the bot again and compares
with what was actually played. A real "fold" or "check" where the bot answers something else is
most likely a timeout (the dealer plays check, else fold, for us). Preflop is deterministic, so
those are certain; postflop uses Monte Carlo, so only clear cases are listed.
"""
import importlib.util, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("botmod", os.path.join(ROOT, sys.argv[1]))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
START, BB = 2000, 20
tot = {"decisions": 0, "pre_mismatch": 0, "post_mismatch": 0}
for f in sys.argv[2:]:
    d = json.load(open(f)); n = len(d["players"]); me = d["seat"]; A = M.Agent()
    A.on_table_start({"seat": me, "num_players": n, "hands": 1000})
    susp = []; dec = 0; by_street = {}
    for h in d["hands"]:
        hist = []; street = "preflop"; board = []; posted = 0
        stacks = [START] * n; bets = [0] * n; folded = [False] * n; pot = 0; cur = 0; min_inc = BB; raises_st = 0
        for ev in h["events"]:
            if ev[0] == "post":
                s, amt = ev[1], ev[2]
                hist.append({"seat": s, "street": "preflop", "action": "small_blind" if posted == 0 else "big_blind", "amount": amt}); posted += 1
                stacks[s] -= amt; bets[s] += amt; pot += amt; cur = max(cur, bets[s])
            elif ev[0] == "board":
                street = ev[1]; board = ev[2]; bets = [0] * n; cur = 0; min_inc = BB; raises_st = 0
            elif ev[0] == "refund":
                stacks[ev[1]] += ev[2]; pot -= ev[2]
            elif ev[0] == "act":
                s, a, amt = ev[1], ev[2], ev[3]
                if s == me:
                    to_call = min(cur - bets[s], stacks[s])
                    others = any((not folded[j]) and stacks[j] > 0 for j in range(n) if j != s)
                    max_to = bets[s] + stacks[s]
                    can_raise = max_to > cur and others
                    state = {"type": "act", "hand_number": h["n"], "street": street, "seat": s, "button": h["button"],
                             "hole_cards": h["hole"][str(me)], "board": list(board), "small_blind": 10, "big_blind": BB,
                             "blind_level": 0, "pot": pot, "stacks": list(stacks), "bets": list(bets), "folded": list(folded),
                             "to_call": to_call, "min_raise_to": min(cur + min_inc, max_to) if can_raise else None,
                             "max_raise_to": max_to if can_raise else None,
                             "legal_actions": (["fold", "call"] if to_call > 0 else ["check"]) + (["raise"] if can_raise else []),
                             "betting": "no_limit", "raise_cap": None, "raises_this_street": raises_st, "history": list(hist)}
                    votes = {}
                    for _ in range(1 if street == "preflop" else 7):
                        r = A.act(state)["action"]; votes[r] = votes.get(r, 0) + 1
                    best = max(votes, key=votes.get); share = votes[best] / float(sum(votes.values()))
                    dec += 1; by_street[street] = by_street.get(street, 0) + 1
                    passive = (a == "fold") or (a == "check" and to_call == 0)
                    if passive and best not in ("fold", "check") and share >= (1.0 if street == "preflop" else 0.85):
                        susp.append((h["n"], street, "".join(h["hole"][str(me)]), " ".join(board), a, best, to_call, pot, h["results"][me]))
                hist.append({"seat": s, "street": street, "action": a, "amount": amt})
                if a == "raise":
                    inc = amt - cur
                    if inc >= min_inc: min_inc = inc
                    stacks[s] -= amt - bets[s]; pot += amt - bets[s]; bets[s] = amt; cur = amt; raises_st += 1
                elif a == "call":
                    stacks[s] -= amt; pot += amt; bets[s] += amt
                elif a == "fold":
                    folded[s] = True
        shown = {k: v for k, v in h["hole"].items() if k in (h.get("showdown") or {})}
        A._learn({"history": hist, "board": h["board"], "shown": shown, "stacks": [0] * n})
    rd = d.get("round", {})
    print("%s: %d decisions %s | platform says %s timeouts, think %ss | replay finds %d passive plays the bot would not make" % (
        os.path.basename(f), dec, by_street, rd.get("timeouts"), rd.get("think_s"), len(susp)))
    for x in susp:
        print("   hand %4d %-7s we=%s board=[%s] played %-5s, bot says %-5s (to call %d, pot %d) -> hand result %+d" % x)
