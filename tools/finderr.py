"""Replay bucket_sim rounds of one bot and print the first error text.  python3 tools/finderr.py BOT.py SEED ROUNDS field..."""
import os, random, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from engine import FixedHandsTable
from engine.players import SubprocessPlayer
def play(job):
    bots, seed, r = job
    rng = random.Random(seed); order = list(range(len(bots))); rng.shuffle(order)
    ps = [SubprocessPlayer(os.path.join(ROOT, bots[i]), timeout_ms=300, bank_ms=1e9) for i in order]
    try:
        FixedHandsTable(ps, hands=1000, config={"betting": "no_limit", "raise_cap": 0}, seed=rng.random()).play()
    finally:
        for p in ps: p.close()
    me = order.index(0)
    return r, ps[me].stats.errors, ps[me].stats.error_samples
if __name__ == "__main__":
    bot, seed, rounds = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); field = sys.argv[4:]
    with Pool(5) as p:
        for r, e, s in p.imap_unordered(play, [([bot] + field, seed * 100000 + r, r) for r in range(rounds)]):
            if e:
                print("round", r, "errors", e); print("\n".join(s)); p.terminate(); break
        else:
            print("no error in", rounds, "rounds")
