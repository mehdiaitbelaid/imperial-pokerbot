"""Where does build B decide differently from build A on our REAL decisions?

    python3 tools/diffreplay.py A.py B.py hands/saturday_r003.json ...

Rebuilds every state the dealer sent us, lets both builds learn from the same hands, and asks
each for its action (5 votes postflop, since both simulate). A decision counts as different only
when both builds are consistent (4 of 5 votes) and disagree. For B folding where we called, the
cost or saving is exact (the hand result is known); other differences are listed by type."""
import importlib.util, json, os, sys
from collections import Counter, defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


MA = load(sys.argv[1], "botA"); MB = load(sys.argv[2], "botB")
START, BB = 2000, 20
total = 0; diff = Counter(); money = defaultdict(float); examples = defaultdict(list)


def vote(agent, state, k):
    c = Counter(agent.act(state)["action"] for _ in range(k))
    a, n = c.most_common(1)[0]
    return a if n >= (k * 4 + 4) // 5 else None


for f in sys.argv[3:]:
    d = json.load(open(f)); n = len(d["players"]); me = d["seat"]
    A = MA.Agent(); B = MB.Agent()
    info = {"seat": me, "num_players": n, "hands": 1000, "starting_stack": START, "big_blind": BB, "small_blind": 10}
    for ag in (A, B):
        ag.on_table_start(info)
    for h in d["hands"]:
        hist = []; street = "preflop"; board = []; posted = 0
        stacks = [START] * n; bets = [0] * n; folded = [False] * n; pot = 0; cur = 0; min_inc = BB; inv = 0
        for ev in h["events"]:
            if ev[0] == "post":
                s, amt = ev[1], ev[2]
                hist.append({"seat": s, "street": "preflop", "action": "small_blind" if posted == 0 else "big_blind", "amount": amt}); posted += 1
                stacks[s] -= amt; bets[s] += amt; pot += amt; cur = max(cur, bets[s])
                if s == me: inv += amt
            elif ev[0] == "board":
                street = ev[1]; board = ev[2]; bets = [0] * n; cur = 0; min_inc = BB
            elif ev[0] == "refund":
                stacks[ev[1]] += ev[2]; pot -= ev[2]
                if ev[1] == me: inv -= ev[2]
            elif ev[0] == "act":
                s, a, amt = ev[1], ev[2], ev[3]
                if s == me:
                    to_call = min(cur - bets[s], stacks[s]); max_to = bets[s] + stacks[s]
                    others = any((not folded[j]) and stacks[j] > 0 for j in range(n) if j != s)
                    can_raise = max_to > cur and others
                    st = {"type": "act", "hand_number": h["n"], "street": street, "seat": s, "button": h["button"],
                          "hole_cards": h["hole"][str(me)], "board": list(board), "small_blind": 10, "big_blind": BB, "blind_level": 0,
                          "pot": pot, "stacks": list(stacks), "bets": list(bets), "folded": list(folded), "to_call": to_call,
                          "min_raise_to": min(cur + min_inc, max_to) if can_raise else None, "max_raise_to": max_to if can_raise else None,
                          "legal_actions": (["fold", "call"] if to_call > 0 else ["check"]) + (["raise"] if can_raise else []),
                          "betting": "no_limit", "raise_cap": None, "raises_this_street": 0, "history": list(hist)}
                    k = 1 if street == "preflop" else 5
                    va = vote(A, st, k); vb = vote(B, st, k)
                    total += 1
                    if va and vb and va != vb:
                        key = (street, va + " -> " + vb)
                        diff[key] += 1
                        if vb == "fold" and a == va and a in ("call", "raise"):
                            money[key] += -inv - h["results"][me]     # folding instead: lose only what was in
                            if len(sys.argv) > 0 and key == ("preflop", "raise -> fold"):
                                det = [hh for hh in hist if hh["action"] == "raise"]
                                print("   pf raise->fold %s#%d %s pos_rel=%d raises_before=%d to_call=%d result_if_raise %+d fold %+d" % (
                                    os.path.basename(f)[9:13], h["n"], "".join(h["hole"][str(me)]), (me - h["button"]) % n, len(det), to_call, h["results"][me], -inv))
                        if len(examples[key]) < 3:
                            examples[key].append("%s#%d %s [%s]" % (os.path.basename(f)[9:13], h["n"], "".join(h["hole"][str(me)]), " ".join(board)))
                hist.append({"seat": s, "street": street, "action": a, "amount": amt})
                if a == "raise":
                    inc = amt - cur
                    if inc >= min_inc: min_inc = inc
                    if s == me: inv += amt - bets[s]
                    stacks[s] -= amt - bets[s]; pot += amt - bets[s]; bets[s] = amt; cur = amt
                elif a == "call":
                    if s == me: inv += amt
                    stacks[s] -= amt; pot += amt; bets[s] += amt
                elif a == "fold":
                    folded[s] = True
        shown = {k2: v for k2, v in h["hole"].items() if k2 in (h.get("showdown") or {})}
        summ = {"type": "hand_end", "hand_number": h["n"], "history": hist, "board": h["board"], "shown": shown, "winners": [], "stacks": [START] * n}
        for ag in (A, B):
            ag.on_hand_end(summ)
nd = sum(diff.values())
print("%d real decisions replayed; B decides differently from A in %d (%.1f%%)" % (total, nd, 100.0 * nd / max(1, total)))
for key, c in diff.most_common():
    extra = ("   folding there instead of calling: %+.0f bb" % (money[key] / 20)) if key in money else ""
    print("  %-8s %-18s %4d  e.g. %s%s" % (key[0], key[1], c, ", ".join(examples[key]), extra))
