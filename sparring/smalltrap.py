"""Adversarial sparring for the 'raise small bets' rule: bets a quarter of the pot with strong
hands as often as with nothing, then re-raises all-in when raised with a strong hand."""
import random
R = "23456789TJQKA"


def strength(hole, board):
    hr = [R.index(c[0]) for c in hole]; br = [R.index(c[0]) for c in board]
    if hr[0] == hr[1] and hr[0] > max(br):
        return 3
    hits = sum(1 for x in hr if x in br)
    if hits >= 2 or (hr[0] == hr[1] and hr[0] in br):
        return 4
    if hits == 1 and max(br) in hr:
        return 2
    if hits == 1 or hr[0] == hr[1]:
        return 1
    return 0


class Agent:
    def __init__(self):
        self.r = random.Random()

    def act(self, s):
        L = s["legal_actions"]
        hole = s["hole_cards"]; board = s["board"]
        a, b = sorted((R.index(c[0]) for c in hole), reverse=True)
        if not board:
            good = a == b or a >= 10 or (a >= 8 and hole[0][1] == hole[1][1])
            if good and "raise" in L and s["to_call"] <= 3 * s["big_blind"]:
                return {"action": "raise", "amount": max(s["min_raise_to"], 3 * s["big_blind"])}
            if good and s["to_call"] <= 10 * s["big_blind"]:
                return {"action": "call" if "call" in L else "check"}
            return {"action": "check" if "check" in L else "fold"}
        st = strength(hole, board)
        if s["to_call"] == 0:
            if "raise" in L and (st >= 2 or self.r.random() < 0.45):
                return {"action": "raise", "amount": max(s["min_raise_to"], s["pot"] // 4)}
            return {"action": "check"}
        if st >= 3 and "raise" in L:
            return {"action": "all_in"}
        if st >= 2 or s["to_call"] <= s["pot"] * 0.25:
            return {"action": "call"}
        return {"action": "fold"}
