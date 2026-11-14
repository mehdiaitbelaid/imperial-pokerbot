"""Sparring: loose aggressive, opens wide in position, barrels."""
import random

RANKS = "23456789TJQKA"


def pf(hole):
    """Rough preflop score: 22 is about 0.55, AA about 1.0, 72o about 0.1."""
    a, b = sorted((RANKS.index(c[0]) for c in hole), reverse=True)
    if a == b:
        return 0.55 + a / 26.0
    v = (a + b) / 26.0 - 0.02 * max(0, a - b - 1)
    return v + (0.06 if hole[0][1] == hole[1][1] else 0.0)


def made(hole, board):
    """0 nothing, 1 weak pair, 2 top pair or overpair, 3 two pair or better."""
    hr = [RANKS.index(c[0]) for c in hole]
    br = [RANKS.index(c[0]) for c in board]
    if not br:
        return 0
    top = max(br)
    hits = [r for r in hr if r in br]
    suits = [c[1] for c in hole + board]
    if max(suits.count(s) for s in "cdhs") >= 5:
        return 3
    if hr[0] == hr[1]:
        if hr[0] in br:
            return 3
        return 2 if hr[0] > top else 1
    if len(hits) == 2:
        return 3
    if hits:
        if br.count(hits[0]) >= 2:
            return 3
        return 2 if hits[0] == top else 1
    return 0


def draw(hole, board):
    suits = [c[1] for c in hole + board]
    if len(board) < 5 and any(suits.count(s) == 4 and s in (hole[0][1], hole[1][1]) for s in "cdhs"):
        return True
    return False


def legal_raise(state, amount):
    if "raise" not in state["legal_actions"] or state.get("min_raise_to") is None:
        return {"action": "call"} if "call" in state["legal_actions"] else {"action": "check"}
    return {"action": "raise", "amount": int(max(state["min_raise_to"], min(state["max_raise_to"], amount)))}


def passive(state):
    return {"action": "check"} if "check" in state["legal_actions"] else {"action": "call"}


def fold(state):
    return {"action": "check"} if "check" in state["legal_actions"] else {"action": "fold"}


class Agent:
    def __init__(self):
        self.rng = random.Random()
        self.aggressor = False

    def act(self, state):
        hole, board = state["hole_cards"], state["board"]
        bb, pot, to_call = state["big_blind"], state["pot"], state["to_call"]
        n = len(state["stacks"])
        late = (state["seat"] - state["button"]) % n in (0, n - 1, n - 2)
        r = self.rng.random()
        if state["street"] == "preflop":
            s = pf(hole)
            raised = max(state["bets"]) > bb
            self.aggressor = False
            if s >= 0.9 or (raised and s >= 0.8 and r < 0.5):
                self.aggressor = True
                return legal_raise(state, 3 * max(state["bets"]))
            if not raised and (s >= 0.55 or (late and s >= 0.40)):
                self.aggressor = True
                return legal_raise(state, 2.5 * bb)
            if raised and (s >= 0.62 or (late and s >= 0.5)) and to_call <= 6 * bb:
                return passive(state)
            return fold(state)
        m = made(hole, board)
        d = draw(hole, board)
        if to_call == 0:
            if m >= 1 or d or (self.aggressor and r < 0.7):
                return legal_raise(state, 0.7 * pot)
            return passive(state)
        if m == 3 or (m == 2 and r < 0.3) or (d and r < 0.25):
            return legal_raise(state, max(state["bets"]) * 2.5 + pot * 0.3)
        if m >= 1 or d or (to_call <= 0.3 * pot and r < 0.4):
            return passive(state)
        return fold(state)
