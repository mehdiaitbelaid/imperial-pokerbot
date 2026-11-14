"""Replica of the real 'ediz_slow': the starter kit bot before the flop (raises any pair, ace or
king every time, limps the rest, folds a limp to any raise above 2 big blinds), but after the
flop it only keeps betting with a made hand and gives up to real bets otherwise."""
R = "23456789TJQKA"


class Agent:
    def act(self, state):
        legal = state["legal_actions"]
        hole = state["hole_cards"]
        ranks = sorted(R.index(c[0]) for c in hole)
        strong = ranks[0] == ranks[1] or ranks[1] >= 11
        board = [R.index(c[0]) for c in state["board"]]
        cheap = state["to_call"] <= state["big_blind"] * 2
        if not board:
            if strong and "raise" in legal:
                return {"action": "raise", "amount": min(state["min_raise_to"] + state["pot"] // 2, state["max_raise_to"])}
            if "check" in legal:
                return {"action": "check"}
            return {"action": "call"} if (cheap or strong) else {"action": "fold"}
        made = ranks[0] == ranks[1] or ranks[0] in board or ranks[1] in board
        if strong and made and "raise" in legal:
            return {"action": "raise", "amount": min(state["min_raise_to"] + state["pot"] // 2, state["max_raise_to"])}
        if "check" in legal:
            return {"action": "check"}
        return {"action": "call"} if (cheap or (strong and made)) else {"action": "fold"}
