"""Fuzz a bot's act() with random but plausible states and check every reply.

    python3 tools/fuzz_act.py              # bot.py, 20,000 synthetic states plus captured real ones
    python3 tools/fuzz_act.py versions/v1.py --states 50000

Synthetic states cover every betting mode, raise caps, null raise bounds,
empty or random history and missing optional keys. Real states come from
in process tables against the house and sparring bots. A fresh Agent is made
every 1,000 decisions, like a new round. Exits non zero on any illegal reply
or exception.
"""
import argparse
import importlib.util
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from engine import FixedHandsTable  # noqa: E402
from engine.players import LocalPlayer  # noqa: E402

RANKS = "23456789TJQKA"
DECK = [r + s for r in RANKS for s in "cdhs"]
STREETS = ["preflop", "flop", "turn", "river"]
OPTIONAL = ["history", "raise_cap", "raises_this_street", "betting", "button", "bets", "folded",
            "small_blind", "big_blind", "blind_level", "hand_number", "pot", "stacks", "street",
            "board", "to_call", "seat"]


def load(path):
    spec = importlib.util.spec_from_file_location("fuzzbot%d" % random.randrange(1 << 30), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Agent


def synth(rng):
    n = rng.choice([7, 8, 8])
    cards = rng.sample(DECK, 7)
    street = rng.choice(STREETS)
    nb = {"preflop": 0, "flop": 3, "turn": 4, "river": 5}[street]
    seat = rng.randrange(n)
    button = rng.randrange(n)
    stacks = [rng.choice([2000, rng.randrange(0, 2001)]) for _ in range(n)]
    bets = [rng.choice([0, 0, 10, 20, rng.randrange(0, 600)]) for _ in range(n)]
    folded = [rng.random() < 0.4 for _ in range(n)]
    folded[seat] = False
    betting = rng.choice(["no_limit", "pot_limit", "fixed_limit"])
    cap = rng.choice([None, None, 1, 2, 3, 4])
    to_call = rng.choice([0, 0, 10, 20, 40, rng.randrange(1, 2001)])
    to_call = min(to_call, stacks[seat]) if stacks[seat] else to_call
    legal = ["fold", "call"] if to_call > 0 else ["check"]
    lo = hi = None
    if rng.random() < 0.7:
        legal.append("raise")
        lo = rng.randrange(20, 2001)
        hi = rng.randrange(lo, 2001) if rng.random() < 0.8 else lo
    if rng.random() < 0.03:
        lo, hi = None, None  # raise listed but bounds missing: must still be safe
    hist = []
    if rng.random() < 0.8:
        hist.append({"seat": (button + 1) % n, "street": "preflop", "action": "small_blind", "amount": 10})
        hist.append({"seat": (button + 2) % n, "street": "preflop", "action": "big_blind", "amount": 20})
        for k in range(rng.randrange(0, 14)):
            st = STREETS[min(STREETS.index(street), k // 4)]
            a = rng.choice(["fold", "check", "call", "raise", "raise", "call"])
            amt = {"fold": 0, "check": 0}.get(a, rng.randrange(10, 2001))
            hist.append({"seat": rng.randrange(n), "street": st, "action": a, "amount": amt})
    state = {
        "hole_cards": cards[:2], "board": cards[2:2 + nb], "street": street, "seat": seat,
        "button": button, "stacks": stacks, "bets": bets, "folded": folded,
        "pot": sum(bets) + rng.randrange(0, 3000), "to_call": to_call,
        "min_raise_to": lo, "max_raise_to": hi, "legal_actions": legal,
        "small_blind": 10, "big_blind": 20, "blind_level": 0,
        "hand_number": rng.randrange(1, 1001), "betting": betting, "raise_cap": cap,
        "raises_this_street": rng.randrange(0, 5), "history": hist,
    }
    for key in OPTIONAL:
        if rng.random() < 0.04:
            state.pop(key, None)
    if rng.random() < 0.02:
        state["history"] = []
    return state


def check(reply, state):
    legal = state.get("legal_actions") or []
    if not isinstance(reply, dict):
        return "reply is not a dict: %r" % (reply,)
    a = reply.get("action")
    if a not in legal:
        return "action %r not in %r" % (a, legal)
    if a == "raise":
        amt = reply.get("amount")
        lo, hi = state.get("min_raise_to"), state.get("max_raise_to")
        if not isinstance(amt, int) or lo is None or hi is None or not lo <= amt <= hi:
            return "raise amount %r outside %r..%r" % (amt, lo, hi)
    return None


class Recorder(LocalPlayer):
    """In process seat that checks every reply the bot gives in a real game."""

    def __init__(self, agent_cls, log):
        super().__init__(agent_cls)
        self.log = log

    def act(self, state):
        t0 = time.perf_counter()
        reply = self.agent.act(state)
        self.log.append((time.perf_counter() - t0, check(reply, state), state))
        return reply


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bot", nargs="?", default="bot.py")
    ap.add_argument("--states", type=int, default=20000)
    ap.add_argument("--tables", type=int, default=3, help="in process tables for real states")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    path = args.bot if os.path.isfile(args.bot) else os.path.join(HERE, args.bot)
    Agent = load(path)
    rng = random.Random(args.seed)
    times, fails = [], []

    agent = None
    for i in range(args.states):
        if i % 1000 == 0:
            agent = Agent()
            if rng.random() < 0.5:
                info = {"seat": 0, "num_players": 8, "big_blind": 20, "starting_stack": 2000}
                for k in list(info):
                    if rng.random() < 0.3:
                        info.pop(k)
                agent.on_table_start(info)
        st = synth(rng)
        t0 = time.perf_counter()
        try:
            reply = agent.act(st)
        except Exception as e:
            fails.append("exception %r" % e)
            continue
        times.append(time.perf_counter() - t0)
        err = check(reply, st)
        if err:
            fails.append(err)
        if rng.random() < 0.05 and hasattr(agent, "on_hand_end"):
            summary = {"hand_number": 1, "board": st.get("board", []), "history": st.get("history", []),
                       "shown": rng.choice([{}, {"1": ["As", "Kd"]}, {"x": None}]), "winners": [], "stacks": []}
            try:
                agent.on_hand_end(summary)
            except Exception as e:
                fails.append("on_hand_end exception %r" % e)

    real = []
    pool = ["examples/calling_station.py", "examples/random_bot.py", "examples/tight_aggressive.py",
            "sparring/maniac.py", "sparring/allin_spammer.py", "sparring/nit.py", "sparring/minraiser.py",
            "sparring/lag_basic.py"]
    pool = [p for p in pool if os.path.isfile(os.path.join(HERE, p))]
    for t, betting in zip(range(args.tables), ["no_limit", "pot_limit", "fixed_limit", "no_limit"] * 9):
        seats = [Recorder(Agent, real)] + [LocalPlayer(load(os.path.join(HERE, rng.choice(pool)))) for _ in range(7)]
        cfg = {"betting": betting, "raise_cap": 3 if t == 3 else 0}
        FixedHandsTable(seats, hands=1000, config=cfg, seed=rng.random()).play()
    for dt, err, st in real:
        times.append(dt)
        if err:
            fails.append("real state: " + err)

    times.sort()
    n = len(times)
    p50 = times[n // 2] * 1000
    p99 = times[int(n * 0.99)] * 1000
    print("decisions checked: %d (%d synthetic, %d from real tables)" % (n + len([f for f in fails if f.startswith("exception")]), args.states, len(real)))
    print("illegal replies or exceptions: %d" % len(fails))
    for f in fails[:10]:
        print("  ", f)
    print("decision time in process: median %.3f ms, p99 %.3f ms, max %.3f ms" % (p50, p99, times[-1] * 1000))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
