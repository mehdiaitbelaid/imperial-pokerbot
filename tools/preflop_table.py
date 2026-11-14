"""Heads-up and 3-way equity for the 169 starting hand classes, by simulation.
Writes tools/preflop.json: {"AKs": [eq_vs1, eq_vs3, eq_vs6], ...}"""
import json, os, random, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.cards import evaluate

R = "23456789TJQKA"
SIMS = 6000

def classes():
    out = []
    for i in range(12, -1, -1):
        for j in range(i, -1, -1):
            if i == j: out.append(R[i] + R[j])
            else: out += [R[i] + R[j] + "s", R[i] + R[j] + "o"]
    return out

def hole_for(cls):
    a, b = R.index(cls[0]), R.index(cls[1])
    if a == b: return [a * 4, b * 4 + 1]
    if cls[2] == "s": return [a * 4, b * 4]
    return [a * 4, b * 4 + 1]

def equity(args):
    cls, nopp = args
    rng = random.Random(hash((cls, nopp)) & 0xffffffff)
    hole = hole_for(cls)
    deck = [c for c in range(52) if c not in hole]
    tot = 0.0
    for _ in range(SIMS):
        cards = rng.sample(deck, 5 + 2 * nopp)
        board = cards[:5]
        me = evaluate(hole + board)
        best, ties, win = True, 0, True
        for k in range(nopp):
            s = evaluate(cards[5 + 2 * k: 7 + 2 * k] + board)
            if s > me: win = False; break
            if s == me: ties += 1
        if win: tot += 1.0 / (ties + 1)
    return cls, nopp, tot / SIMS

if __name__ == "__main__":
    jobs = [(c, n) for c in classes() for n in (1, 3, 6)]
    with Pool() as p:
        res = p.map(equity, jobs, chunksize=4)
    table = {}
    for cls, n, e in res:
        table.setdefault(cls, [0, 0, 0])[(1, 3, 6).index(n)] = round(e, 4)
    json.dump(table, open(os.path.join(os.path.dirname(__file__), "preflop.json"), "w"))
    print(len(table), table["AA"], table["72o"], table["T9s"])
