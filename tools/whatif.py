"""What would another bot build have done at each of our real postflop CALLS?
    python3 tools/whatif.py bots/av17.py hands/saturday_r012.json [min_call_chips]
Replays the round so the build has the same per-seat knowledge, and at every call we actually
made after the flop of at least min_call_chips, asks the build for its action (7 votes)."""
import importlib.util, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("botmod", os.path.join(ROOT, sys.argv[1]))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
MINC = int(sys.argv[3]) if len(sys.argv) > 3 else 200
START, BB = 2000, 20
tot = {"n": 0, "veto": 0, "saved": 0.0, "lost": 0.0}
for f in sys.argv[2:3]:
    d = json.load(open(f)); n = len(d["players"]); me = d["seat"]; A = M.Agent(); P = d["players"]
    A.on_table_start({"seat": me, "num_players": n, "hands": 1000, "starting_stack": START, "big_blind": BB, "small_blind": 10})
    for h in d["hands"]:
        hist = []; street = "preflop"; board = []; posted = 0
        stacks = [START] * n; bets = [0] * n; folded = [False] * n; pot = 0; cur = 0; min_inc = BB
        invested = 0; vetoed = None
        for ev in h["events"]:
            if ev[0] == "post":
                s, amt = ev[1], ev[2]
                hist.append({"seat": s, "street": "preflop", "action": "small_blind" if posted == 0 else "big_blind", "amount": amt}); posted += 1
                stacks[s] -= amt; bets[s] += amt; pot += amt; cur = max(cur, bets[s])
                if s == me: invested += amt
            elif ev[0] == "board":
                street = ev[1]; board = ev[2]; bets = [0] * n; cur = 0; min_inc = BB
            elif ev[0] == "refund":
                stacks[ev[1]] += ev[2]; pot -= ev[2]
                if ev[1] == me: invested -= ev[2]
            elif ev[0] == "act":
                s, a, amt = ev[1], ev[2], ev[3]
                if s == me and street != "preflop" and a == "call" and amt >= MINC and vetoed is None:
                    to_call = min(cur - bets[s], stacks[s]); max_to = bets[s] + stacks[s]
                    others = any((not folded[j]) and stacks[j] > 0 for j in range(n) if j != s)
                    can_raise = max_to > cur and others
                    state = {"type": "act", "hand_number": h["n"], "street": street, "seat": s, "button": h["button"],
                             "hole_cards": h["hole"][str(me)], "board": list(board), "small_blind": 10, "big_blind": BB, "blind_level": 0,
                             "pot": pot, "stacks": list(stacks), "bets": list(bets), "folded": list(folded), "to_call": to_call,
                             "min_raise_to": min(cur + min_inc, max_to) if can_raise else None, "max_raise_to": max_to if can_raise else None,
                             "legal_actions": ["fold", "call"] + (["raise"] if can_raise else []),
                             "betting": "no_limit", "raise_cap": None, "raises_this_street": 0, "history": list(hist)}
                    votes = {}
                    for _ in range(7):
                        r = A.act(state)["action"]; votes[r] = votes.get(r, 0) + 1
                    tot["n"] += 1
                    if votes.get("fold", 0) >= 5:
                        vetoed = (street, amt, pot, invested)
                hist.append({"seat": s, "street": street, "action": a, "amount": amt})
                if a == "raise":
                    inc = amt - cur
                    if inc >= min_inc: min_inc = inc
                    if s == me: invested += amt - bets[s]
                    stacks[s] -= amt - bets[s]; pot += amt - bets[s]; bets[s] = amt; cur = amt
                elif a == "call":
                    if s == me: invested += amt
                    stacks[s] -= amt; pot += amt; bets[s] += amt
                elif a == "fold":
                    folded[s] = True
        if vetoed:
            r = h["results"][me]; alt = -vetoed[3]          # result if we had folded at that call
            tot["veto"] += 1
            if alt > r: tot["saved"] += alt - r
            else: tot["lost"] += r - alt
            print("  #%-4d %s board [%s] %s call %d into %d: build says FOLD | actual result %+d, folding there %+d" % (
                h["n"], "".join(h["hole"][str(me)]), " ".join(h["board"]), vetoed[0], vetoed[1], vetoed[2], r, alt))
        shown = {k: v for k, v in h["hole"].items() if k in (h.get("showdown") or {})}
        A.on_hand_end({"type": "hand_end", "hand_number": h["n"], "history": hist, "board": h["board"], "shown": shown, "winners": [], "stacks": [START] * n})
print("%s: %d postflop calls of %d+ chips; the build would have folded %d of them: saves %.0f bb, gives up %.0f bb -> net %+.1f bb/100" % (
    os.path.basename(sys.argv[2]), tot["n"], MINC, tot["veto"], tot["saved"] / 20, tot["lost"] / 20, (tot["saved"] - tot["lost"]) / 20 / 10))
