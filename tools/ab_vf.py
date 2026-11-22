"""Paired A/B on Mehdi's 'field' line-up, in-process, with variance reduction:
 1. identical deals (same seed) and seating for A and B;
 2. common random numbers: every bot's RNG is reseeded from the game state before
    each decision, so opponents act identically whenever they face the same spot;
 3. all-in luck adjustment: all-in-before-the-river pots scored at equity.
usage: python3 tools/ab_vf.py A.py B.py N_SEEDS [field|tight]
Needs sparring/ from branch v1 or fable-bot (maniac, calling_station_plus, field_like, nit, tag_basic, pot_odds_bot)."""
import sys, os, random, importlib.util, statistics as stt, math
from multiprocessing import Pool
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from engine import FixedHandsTable
from engine.players import LocalPlayer
from engine.cards import evaluate, to_int
SP = os.path.join(HERE, 'sparring') + os.sep; EX = os.path.join(HERE, 'examples') + os.sep
_cache = {}
def load(p):
    if p not in _cache:
        s = importlib.util.spec_from_file_location('m%d' % len(_cache), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
        _cache[p] = m
    return _cache[p]
def crn(cls, tag, table_seed):
    class W(cls):
        def act(self, state):
            if hasattr(self, 'rng'):
                self.rng.seed(hash((table_seed, tag, state.get('hand_number'), state.get('seat'), state.get('street'), len(state.get('history') or []))))
            return super().act(state)
    return W
def share(hands, board, me_idx, rng, sims=300):
    dead = set(c for h in hands for c in h) | set(board); deck = [c for c in range(52) if c not in dead]; tot = 0.0
    need = 5 - len(board)
    for _ in range(sims):
        b = board + rng.sample(deck, need); sc = [evaluate(h + b) for h in hands]; m = max(sc)
        if sc[me_idx] == m: tot += 1.0 / sc.count(m)
    return tot / sims
def job(args):
    cand, seed, field = args
    r = random.Random(seed)
    n = r.choice((6, 7, 8))
    if field == 'field':
        fill = [SP + 'maniac.py', SP + 'calling_station_plus.py'] + [SP + 'field_like.py'] * (n - 3)
    else:
        pool = [SP + 'nit.py', SP + 'tag_basic.py', SP + 'pot_odds_bot.py', EX + 'tight_aggressive.py', SP + 'tag_basic.py']
        fill = [SP + 'maniac.py'] + [r.choice(pool) for _ in range(n - 2)]
    seat = r.randrange(n)
    line = fill[:seat] + [cand] + fill[seat:]
    players = [LocalPlayer(crn(load(p).Agent, i, seed)) for i, p in enumerate(line)]
    log = FixedHandsTable(players, hands=1000, seed=seed, record=True).play()['log']
    er = random.Random(seed * 7 + 1)
    raw, adj = [], []
    for h in log:
        res = (h['end'][seat] - h['stacks'][seat]) / 20.0; a = res
        sd = h.get('showdown')
        if sd and str(seat) in sd:
            ev = h['events']; last = max(i for i, e in enumerate(ev) if e[0] == 'act'); b = []
            for e in ev[:last + 1]:
                if e[0] == 'board': b = e[2]
            if len(b) < 5:
                won = {}
                for e in ev:
                    if e[0] == 'win': won[e[1]] = won.get(e[1], 0) + e[2]
                live = [int(x) for x in sd]
                inv = {i: h['stacks'][i] - h['end'][i] + won.get(i, 0) for i in live}
                if len(set(inv.values())) == 1:
                    hands = [[to_int(c) for c in h['hole'][str(i)]] for i in live]
                    eqs = share(hands, [to_int(c) for c in b], live.index(seat), er)
                    a = (eqs * sum(won.values()) - inv[seat]) / 20.0
        raw.append(res); adj.append(a)
    return raw, adj
if __name__ == '__main__':
    A, B, N = sys.argv[1], sys.argv[2], int(sys.argv[3]); field = sys.argv[4] if len(sys.argv) > 4 else 'field'
    seeds = [910000 + i for i in range(N)]
    with Pool(2) as pool:
        ra = pool.map(job, [(A, s, field) for s in seeds]); rb = pool.map(job, [(B, s, field) for s in seeds])
    for k, name in ((0, 'raw'), (1, 'all-in adjusted')):
        a = [x for t in ra for x in t[k]]; b = [x for t in rb for x in t[k]]; d = [y - x for x, y in zip(b, a)]
        n = len(d); sd = stt.pstdev(d)
        print("%-16s A %+7.1f  B %+7.1f  A-B %+6.1f bb/100  se %4.1f  95%% [%+.1f, %+.1f]  (%d paired hands)" % (
            name, 100 * stt.mean(a), 100 * stt.mean(b), 100 * stt.mean(d), 100 * sd / math.sqrt(n),
            100 * (stt.mean(d) - 1.96 * sd / math.sqrt(n)), 100 * (stt.mean(d) + 1.96 * sd / math.sqrt(n)), n))
    per = [100 * (stt.mean(x[1]) - stt.mean(y[1])) for x, y in zip(ra, rb)]
    print("per-table A-B (adjusted): mean %+.1f, sd %.1f, tables won by A %d/%d" % (stt.mean(per), stt.pstdev(per), sum(1 for p in per if p > 0), len(per)))
