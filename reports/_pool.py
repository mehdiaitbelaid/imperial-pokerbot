"""Throwaway pooled checks for the round tracker (reads hands/saturday_rNNN.json only).

    python3 -I reports/_pool.py 3 4 5 6 7 8        # rounds to pool
    python3 -I reports/_pool.py 9 --detail         # also list each big spot we faced

Prints: (1) how we respond when raised postflop / facing a bet >= pot, and what happens;
(2) our river calls by bet size; (3) per opponent: what they show down after raising
postflop or betting >= pot (all hands at the table, not only ours); (4) our fold to 3-bet.
"""
import json, sys, collections

HERE = __file__.rsplit('/', 2)[0]
WEAK = {'High Card', 'Pair'}


RK = '23456789TJQKA'


def cat(cards):
    """0 high card, 1 pair, 2 two pair, 3 trips, 4 straight, 5 flush, 6 full house+ (5-7 cards)."""
    rs = [RK.index(c[0]) for c in cards]
    cnt = sorted(collections.Counter(rs).values(), reverse=True)
    fl = max(collections.Counter(c[1] for c in cards).values()) >= 5
    u = set(rs) | ({-1} if 12 in rs else set())
    st = any(all(x + i in u for i in range(5)) for x in range(-1, 9))
    if cnt[0] == 4 or (cnt[0] == 3 and len(cnt) > 1 and cnt[1] >= 2):
        return 6
    if fl:
        return 5
    if st:
        return 4
    if cnt[0] == 3:
        return 3
    if cnt[0] == 2 and len(cnt) > 1 and cnt[1] == 2:
        return 2
    return 1 if cnt[0] == 2 else 0


def ours(hole, board):
    """Our made hand at decision time: 'weak' = one pair or less, or a hand no better than the board's."""
    c = cat(hole + board)
    cb = cat(board)
    if c <= 1 or c == cb or (c == 2 and cb == 1):
        return 'weak'
    return 'two pair+'


def walk(h):
    """Yield (street, seat, action, amt, to_call, pot_before, had_bet_this_street, n_raises_street)."""
    street = 'preflop'
    com = collections.Counter()
    tot = collections.Counter()
    h['_tot'] = tot
    pot = 0
    cur = 0
    nr = 0
    for e in h['events']:
        if e[0] == 'post':
            com[e[1]] += e[2]; pot += e[2]; cur = max(cur, com[e[1]]); tot[e[1]] += e[2]
        elif e[0] == 'board':
            street = e[1]; com = collections.Counter(); cur = 0; nr = 0; h['_board'] = list(e[2])
        elif e[0] == 'act':
            _, s, a, amt = e
            to_call = cur - com[s]
            yield street, s, a, amt, to_call, pot, com[s] > 0, nr
            if a == 'raise':
                pot += amt - com[s]; tot[s] += amt - com[s]; com[s] = amt; cur = amt; nr += 1
            elif a == 'call':
                pot += amt; com[s] += amt; tot[s] += amt


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    detail = '--detail' in sys.argv
    spots = collections.defaultdict(list)      # kind -> rows
    rivcall = collections.defaultdict(lambda: [0, 0, 0, 0])
    oppshow = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    f3b = [0, 0]
    f3b_by = collections.defaultdict(lambda: [0, 0])
    for r in args:
        d = json.load(open('%s/hands/saturday_r%03d.json' % (HERE, int(r))))
        me = d['seat']; names = d['players']
        for h in d['hands']:
            sd = h.get('showdown') or {}
            seen = set()
            bst = collections.defaultdict(set)
            last_agg = None
            we_opened = False
            for street, s, a, amt, to_call, pot, had, nr in walk(h):
                if street == 'preflop':
                    if s == me and a == 'raise' and nr == 0:
                        we_opened = True
                    elif s == me and we_opened and nr == 2 and to_call > 0:
                        f3b[1] += 1; f3b_by[names[last_agg]][1] += 1
                        if a == 'fold':
                            f3b[0] += 1; f3b_by[names[last_agg]][0] += 1
                        we_opened = False
                    if a == 'raise':
                        last_agg = s
                    continue
                ratio = to_call / max(1, pot - to_call) if to_call > 0 else 0
                if s == me and to_call > 0:
                    kind = 'raised' if had else ('bet>=pot' if ratio >= 0.95 else None)
                    if kind and (h['n'], kind) not in seen:
                        seen.add((h['n'], kind))
                        opp = names[last_agg] if last_agg is not None else '?'
                        won = h['result'] > 0
                        spots[kind].append((r, h['n'], street, opp, a, to_call, pot, h['result'],
                                            str(me) in sd, won, ''.join(h['hole'].get(str(me), [])),
                                            ''.join(h['hole'].get(str(last_agg), [])) if last_agg is not None else '',
                                            h['result'] + h['_tot'][me],
                                            ours(h['hole'][str(me)], h['_board'])))
                    if street == 'river' and a == 'call':
                        b = '<0.5' if ratio < 0.5 else ('0.5-0.95' if ratio < 0.95 else '>=0.95')
                        rivcall[b][0] += 1; rivcall[b][1] += h['result'] > 0; rivcall[b][2] += h['result']; rivcall[b][3] += h['result'] + h['_tot'][me]
                if a == 'raise' and s != me and to_call == 0 and amt >= 0.5 * pot:
                    bst[s].add(street)
                if a == 'raise':
                    if s != me and str(s) in sd:
                        k = None
                        if to_call > 0:
                            k = 'raise'
                        elif amt >= 0.95 * pot:
                            k = 'bet>=pot'
                        if k:
                            o = oppshow[names[s]][k]
                            o[1] += 1; o[0] += sd[str(s)] in WEAK
                    last_agg = s
            for s2, sts in bst.items():
                if len(sts) >= 2 and str(s2) in sd:
                    o = oppshow[names[s2]]['barrel2']
                    o[1] += 1; o[0] += sd[str(s2)] in WEAK
    print('== WHEN WE ARE RAISED POSTFLOP / FACE A BET >= POT (first such spot per hand) ==')
    for kind, rows in spots.items():
        acts = collections.Counter(x[4] for x in rows)
        cont = [x for x in rows if x[4] != 'fold']
        sdn = [x for x in cont if x[8]]
        print('%-9s n=%d  fold %d call %d reraise %d | continued: %d, net %+.0f bb, vs folding there %+.0f bb, showdown %d won %d' % (
            kind, len(rows), acts['fold'], acts['call'], acts['raise'], len(cont),
            sum(x[7] for x in cont) / 20, sum(x[12] for x in cont) / 20, len(sdn), sum(x[9] for x in sdn)))
        for w in ('weak', 'two pair+'):
            v = [x for x in cont if x[13] == w]
            print('   holding %-9s at that moment: continued %d, won %d, vs folding there %+.0f bb' % (
                w, len(v), sum(x[9] for x in v), sum(x[12] for x in v) / 20))
        by = collections.defaultdict(list)
        for x in cont:
            by[x[3]].append(x)
        print('   continued by opp: ' + '; '.join('%s %d/%d won %+.0fbb' % (
            k[:12], sum(x[9] for x in v), len(v), sum(x[7] for x in v) / 20) for k, v in sorted(by.items(), key=lambda kv: sum(x[7] for x in kv[1]))))
        if detail:
            for x in rows:
                print('     r%s #%d %s vs %s: %s to_call %d pot %d -> %+d  we=%s (%s) opp=%s' % (x[0], x[1], x[2], x[3][:12], x[4], x[5], x[6], x[7], x[10], x[13], x[11]))
    print('== OUR RIVER CALLS by bet/pot ==')
    for b, v in sorted(rivcall.items()):
        print('  %-9s n=%d won %d net %+.0f bb, vs folding the river %+.0f bb' % (b, v[0], v[1], v[2] / 20, v[3] / 20))
    print('== OUR FOLD TO 3-BET == %d/%d' % tuple(f3b), '; '.join('%s %d/%d' % (k[:12], v[0], v[1]) for k, v in f3b_by.items() if v[1] >= 3))
    print('== OPPONENTS: shown down after a postflop raise / a bet >= pot: weak (one pair or less) / shown ==')
    for t, v in sorted(oppshow.items()):
        print('  %-26s raise %d/%d   bet>=pot %d/%d   2+ street barrels (>=0.5 pot) %d/%d' % (t, v['raise'][0], v['raise'][1], v['bet>=pot'][0], v['bet>=pot'][1], v['barrel2'][0], v['barrel2'][1]))


main()
