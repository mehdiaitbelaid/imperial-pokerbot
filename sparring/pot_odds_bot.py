"""Sparring: estimates equity against random hands by a short Monte Carlo
and calls or folds on pot odds; raises with clearly strong equity."""
import random
import time

RANKS = "23456789TJQKA"


def to_int(c):
    return RANKS.index(c[0]) * 4 + "cdhs".index(c[1])


def score(cards):
    counts = {}
    suits = {}
    for c in cards:
        counts[c >> 2] = counts.get(c >> 2, 0) + 1
        suits.setdefault(c & 3, []).append(c >> 2)
    ranks = sorted(counts, reverse=True)
    flush = None
    for s in suits.values():
        if len(s) >= 5:
            flush = sorted(s, reverse=True)
    def straight(rs):
        rs = set(rs)
        if 12 in rs:
            rs.add(-1)
        for top in range(12, 2, -1):
            if all(t in rs for t in range(top - 4, top + 1)):
                return top
        return -1
    if flush:
        sf = straight(flush)
        if sf >= 0:
            return (8, sf)
    groups = sorted(((n, r) for r, n in counts.items()), reverse=True)
    if groups[0][0] == 4:
        return (7, groups[0][1])
    if groups[0][0] == 3 and len(groups) > 1 and groups[1][0] >= 2:
        return (6, groups[0][1], groups[1][1])
    if flush:
        return (5,) + tuple(flush[:5])
    st = straight(ranks)
    if st >= 0:
        return (4, st)
    kick = [r for n, r in groups]
    return (groups[0][0] if groups[0][0] < 3 else 3, (1 if len(groups) > 1 and groups[1][0] == 2 else 0)) + tuple(kick[:5])


class Agent:
    def __init__(self):
        self.rng = random.Random()
        self.used = 0.0

    def equity(self, hole, board, nopp, budget):
        dead = set(hole + board)
        deck = [c for c in range(52) if c not in dead]
        end = time.perf_counter() + budget
        won = n = 0
        while time.perf_counter() < end and n < 150:
            draw = self.rng.sample(deck, 5 - len(board) + 2 * nopp)
            full = board + draw[:5 - len(board)]
            me = score(hole + full)
            rest = draw[5 - len(board):]
            if all(score(rest[2 * k:2 * k + 2] + full) <= me for k in range(nopp)):
                won += 1
            n += 1
        return won / n if n else 0.5

    def act(self, state):
        t0 = time.perf_counter()
        try:
            hole = [to_int(c) for c in state["hole_cards"]]
            board = [to_int(c) for c in state["board"]]
            nopp = min(3, sum(1 for f in state["folded"] if not f) - 1)
            budget = 0.0015 if self.used < 5.0 else 0.0002
            eq = self.equity(hole, board, max(1, nopp), budget)
            pot, to_call = state["pot"], state["to_call"]
            odds = to_call / float(pot + to_call) if to_call else 0.0
            if eq > 0.7 or (nopp == 1 and eq > 0.6):
                out = {"action": "raise", "amount": max(state["bets"]) + pot} if "raise" in state["legal_actions"] else {"action": "call"}
            elif to_call == 0:
                out = {"action": "check"}
            elif eq > odds:
                out = {"action": "call"}
            else:
                out = {"action": "fold"}
            if out["action"] == "raise":
                out["amount"] = int(max(state["min_raise_to"], min(state["max_raise_to"], out["amount"])))
            if out["action"] == "call" and "call" not in state["legal_actions"]:
                out = {"action": "check"}
        except Exception:
            out = {"action": "check"} if "check" in state.get("legal_actions", []) else {"action": "fold"}
        self.used += time.perf_counter() - t0
        return out
