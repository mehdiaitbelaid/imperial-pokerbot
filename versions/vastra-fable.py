"""AlgoSoc pokerbot, team build v1.

Cash game style: 100 bb every hand, 7 or 8 seats, scored in bb/100.
Preflop plays position aware ranges from an embedded equity table; postflop
runs a time boxed Monte Carlo against ranges narrowed by each opponent's
preflop action, postflop line and the stats we keep on that seat this round.

Everything a teammate may want to tune sits in the PARAMETERS block below.
Standard library only, no file or network access.
"""
import bisect
import gc
import random
import time

# ============================== PARAMETERS ==============================
# Hand strength is a percentile q: 0.0 is AA, 1.0 is the worst hand.
# Open raise thresholds keyed by how many players still act behind us
# preflop (7 = UTG at 8 max, 2 = button, 1 = small blind).
OPEN_Q = {7: 0.10, 6: 0.12, 5: 0.14, 4: 0.17, 3: 0.22, 2: 0.38, 1: 0.32, 0: 0.0}
OPEN_BB = 3.0              # open size in big blinds
OPEN_BTN_BB = 2.5          # button and small blind open size
OPEN_LIMPER_BB = 1.0       # added per limper when isolating
OPEN_LOOSE_BB = 1.0        # added when the players behind call too much
ISO_TIGHTEN = 0.75         # open threshold multiplier when limpers are in
OVERLIMP_Q = 0.30          # call behind limpers in late position with q under this
SB_COMPLETE_Q = 0.45       # small blind completes a limped pot under this
STEAL_WIDEN = 1.3          # widen opens when players behind fold a lot
STEAL_ALL_FOLD = (0.65, 0.60, 0.50, 0.42)  # if P(all behind fold) >= a open top b, else if >= c open top d
LOOSE_VPIP = 0.45          # players behind looser than this on average: open wider for value
LOOSE_OPEN_Q = 0.28        # open threshold at LOOSE_VPIP, rising 0.3 per unit of extra looseness
SPAMMER_OPEN_CAP = 0.22    # with an all in spammer behind only open hands that can call a shove
THREEBET_Q = 0.035         # always 3 bet for value under this
THREEBET_VS_WIDE = 0.40    # also 3 bet hands in the top share of a wide opener's range
CALL_RAISE_BASE = 0.85     # call a raise with q under raiser_range * this (scaled by size)
BB_DEFEND_BONUS = 0.10     # extra q the big blind defends against small raises
FOURBET_Q = 0.020          # 4 bet or jam under this
CALL_3BET_Q = 0.050        # call a 3 bet under this when we opened
COLD_4BET_CALL_Q = 0.020   # cold call anything bigger than a 3 bet only under this
JAM_MARGIN = 0.03          # equity edge needed over pot odds to call an all in
JAM_MARGIN_PER_BEHIND = 0.015  # extra edge per player still to act behind us
BIG_RAISE_BB = 25          # raises at least this big are treated as commitment decisions

# Postflop
VALUE_EQ = {1: 0.60, 2: 0.48, 3: 0.40}      # bet for value when equity is above, by opponents
VALUE_EQ_RIVER = {1: 0.64, 2: 0.55, 3: 0.48}
STATION_VALUE_CUT = 0.06   # bet thinner against calling stations
RAISE_EQ = {1: 0.80, 2: 0.70, 3: 0.65}      # raise a bet for value above this
CALL_MARGIN = 0.02         # equity edge over pot odds needed to call
DRAW_IMPLIED = 0.04        # equity allowance for draws on flop and turn when stacks are deep
BET_FRAC = {"flop": 0.60, "turn": 0.65, "river": 0.70}
BET_FRAC_STRONG = 0.85     # size with very strong hands or against stations
WET_BONUS = 0.10           # extra pot fraction on wet boards
CBET_FREQ = 0.60           # heads up flop c bet frequency as preflop raiser
CBET_SIZE = 0.50
SEMI_BLUFF_FREQ = 0.40
BARREL_FREQ = 0.25         # turn bluff as aggressor against folders
RIVER_BLUFF_FREQ = 0.30    # river bluff against players who overfold
AIR_FOLD_BET = 0.5         # heads up on flop or turn, fold air with no draw to bets this big (pot share)
WEAK_PAIR_MARGIN = 0.04    # extra equity a weak pair needs against big bets from non maniacs
TRAP_FREQ = 0.50           # slow play strong hands against maniacs before the river

# Opponent model
PRIOR_N = 10               # pseudo hands used to smooth every stat
# Population priors from the live practice field: mostly tight, fairly passive bots.
PRIOR = {"vpip": 0.24, "pfr": 0.15, "tb": 0.06, "shv": 0.02, "agg": 0.30,
         "fbet": 0.45, "frv": 0.45}
BLUFF_BASE = 0.25          # share of air an average bettor keeps betting
RANGE_BLUR = 0.35          # postflop share of samples drawn from a wider range than our read
RANGE_BLUR_MULT = 3.0      # how much wider; guards against reads that are too tight
BARREL_DECAY = 0.7         # air and weak pair weights shrink by this per extra street bet
MIN_HANDS_CLASSIFY = 25

# Time control (seconds). The round bank is 10 s; we aim well under it.
ROUND_TARGET = 1.3         # total think time we allow ourselves per round
MC_MAX = 0.0009            # max Monte Carlo time per decision
MC_TRIALS_MAX = 600
MC_COMMIT = 0.0006         # Monte Carlo time kept for stack committing decisions when the budget is spent
COMMIT_BANK = 5.0          # but only while total think time this round is under this
TRANSPORT_EST = 0.0002     # transport cost per decision we do not see but the bank does
# ========================================================================

R = "23456789TJQKA"
CARD = {}
for _i, _r in enumerate(R):
    for _j, _s in enumerate("cdhs"):
        CARD[_r + _s] = _i * 4 + _j

# Preflop equity per class: (vs 1 random hand, vs 3, vs 6)
PRE = {
    "AA": (0.8482, 0.6275, 0.4405), "AKs": (0.6768, 0.4113, 0.2756), "AKo": (0.6677, 0.3926, 0.2475), "AQs": (0.6582, 0.3976, 0.2561), "AQo": (0.6406, 0.3629, 0.2257),
    "AJs": (0.6555, 0.3882, 0.2437), "AJo": (0.6448, 0.3522, 0.2108), "ATs": (0.6383, 0.3600, 0.2388), "ATo": (0.6298, 0.3367, 0.2066), "A9s": (0.6319, 0.3437, 0.2051),
    "A9o": (0.5998, 0.3176, 0.1791), "A8s": (0.6289, 0.3332, 0.2032), "A8o": (0.5920, 0.2957, 0.1587), "A7s": (0.6115, 0.3183, 0.1950), "A7o": (0.5843, 0.2875, 0.1565),
    "A6s": (0.6062, 0.3196, 0.1907), "A6o": (0.5768, 0.2730, 0.1403), "A5s": (0.5909, 0.3064, 0.1986), "A5o": (0.5850, 0.2838, 0.1550), "A4s": (0.5925, 0.3184, 0.1972),
    "A4o": (0.5648, 0.2680, 0.1511), "A3s": (0.5793, 0.2936, 0.1925), "A3o": (0.5601, 0.2609, 0.1413), "A2s": (0.5710, 0.2962, 0.1740), "A2o": (0.5549, 0.2501, 0.1399),
    "KK": (0.8269, 0.5935, 0.3672), "KQs": (0.6404, 0.3810, 0.2609), "KQo": (0.6063, 0.3461, 0.2193), "KJs": (0.6414, 0.3798, 0.2427), "KJo": (0.6022, 0.3300, 0.2006),
    "KTs": (0.6199, 0.3572, 0.2173), "KTo": (0.5887, 0.3143, 0.1972), "K9s": (0.6093, 0.3307, 0.2067), "K9o": (0.5914, 0.2869, 0.1655), "K8s": (0.5727, 0.3069, 0.1944),
    "K8o": (0.5698, 0.2748, 0.1403), "K7s": (0.5780, 0.2973, 0.1853), "K7o": (0.5437, 0.2740, 0.1466), "K6s": (0.5671, 0.2794, 0.1810), "K6o": (0.5400, 0.2545, 0.1331),
    "K5s": (0.5572, 0.2823, 0.1696), "K5o": (0.5373, 0.2436, 0.1308), "K4s": (0.5382, 0.2714, 0.1629), "K4o": (0.5261, 0.2273, 0.1223), "K3s": (0.5317, 0.2634, 0.1682),
    "K3o": (0.5012, 0.2241, 0.1148), "K2s": (0.5278, 0.2596, 0.1652), "K2o": (0.5065, 0.2212, 0.1105), "QQ": (0.7932, 0.5294, 0.3304), "QJs": (0.6068, 0.3650, 0.2305),
    "QJo": (0.5711, 0.3183, 0.1941), "QTs": (0.5995, 0.3441, 0.2299), "QTo": (0.5590, 0.3030, 0.1864), "Q9s": (0.5781, 0.3138, 0.1950), "Q9o": (0.5507, 0.2809, 0.1552),
    "Q8s": (0.5613, 0.2970, 0.1756), "Q8o": (0.5299, 0.2650, 0.1388), "Q7s": (0.5443, 0.2876, 0.1546), "Q7o": (0.5129, 0.2417, 0.1201), "Q6s": (0.5273, 0.2751, 0.1597),
    "Q6o": (0.5225, 0.2327, 0.1152), "Q5s": (0.5253, 0.2604, 0.1438), "Q5o": (0.4894, 0.2290, 0.1185), "Q4s": (0.5202, 0.2523, 0.1495), "Q4o": (0.4990, 0.2228, 0.1126),
    "Q3s": (0.5002, 0.2426, 0.1529), "Q3o": (0.4826, 0.2052, 0.1090), "Q2s": (0.5049, 0.2453, 0.1472), "Q2o": (0.4760, 0.1974, 0.1058), "JJ": (0.7699, 0.4798, 0.2909),
    "JTs": (0.5707, 0.3391, 0.2231), "JTo": (0.5556, 0.3060, 0.1905), "J9s": (0.5499, 0.3028, 0.1972), "J9o": (0.5292, 0.2750, 0.1652), "J8s": (0.5363, 0.3044, 0.1830),
    "J8o": (0.5187, 0.2602, 0.1370), "J7s": (0.5222, 0.2736, 0.1553), "J7o": (0.5023, 0.2325, 0.1234), "J6s": (0.5022, 0.2508, 0.1518), "J6o": (0.4893, 0.2102, 0.1130),
    "J5s": (0.4980, 0.2389, 0.1467), "J5o": (0.4662, 0.2102, 0.1051), "J4s": (0.4858, 0.2258, 0.1350), "J4o": (0.4620, 0.1944, 0.0946), "J3s": (0.4771, 0.2268, 0.1346),
    "J3o": (0.4632, 0.1893, 0.1055), "J2s": (0.4846, 0.2233, 0.1360), "J2o": (0.4470, 0.1913, 0.0916), "TT": (0.7456, 0.4511, 0.2546), "T9s": (0.5407, 0.3032, 0.1966),
    "T9o": (0.5181, 0.2851, 0.1631), "T8s": (0.5234, 0.2894, 0.1693), "T8o": (0.4925, 0.2474, 0.1447), "T7s": (0.5074, 0.2790, 0.1613), "T7o": (0.4707, 0.2403, 0.1268),
    "T6s": (0.4878, 0.2510, 0.1560), "T6o": (0.4586, 0.2159, 0.1092), "T5s": (0.4629, 0.2238, 0.1459), "T5o": (0.4407, 0.1894, 0.0996), "T4s": (0.4733, 0.2202, 0.1426),
    "T4o": (0.4381, 0.1797, 0.0966), "T3s": (0.4572, 0.2288, 0.1333), "T3o": (0.4326, 0.1786, 0.0937), "T2s": (0.4671, 0.2142, 0.1272), "T2o": (0.4178, 0.1755, 0.0870),
    "99": (0.7183, 0.4116, 0.2241), "98s": (0.5116, 0.2822, 0.1779), "98o": (0.4770, 0.2563, 0.1426), "97s": (0.4939, 0.2743, 0.1701), "97o": (0.4680, 0.2254, 0.1284),
    "96s": (0.4720, 0.2467, 0.1572), "96o": (0.4487, 0.2120, 0.1115), "95s": (0.4502, 0.2289, 0.1433), "95o": (0.4146, 0.1936, 0.0941), "94s": (0.4375, 0.2214, 0.1307),
    "94o": (0.4006, 0.1828, 0.0873), "93s": (0.4233, 0.2082, 0.1221), "93o": (0.3906, 0.1730, 0.0798), "92s": (0.4294, 0.2004, 0.1178), "92o": (0.3832, 0.1588, 0.0776),
    "88": (0.6848, 0.3738, 0.2067), "87s": (0.4794, 0.2696, 0.1677), "87o": (0.4482, 0.2370, 0.1310), "86s": (0.4608, 0.2584, 0.1570), "86o": (0.4360, 0.2274, 0.1116),
    "85s": (0.4303, 0.2379, 0.1455), "85o": (0.4114, 0.2022, 0.1090), "84s": (0.4302, 0.2149, 0.1284), "84o": (0.3932, 0.1644, 0.0932), "83s": (0.3954, 0.1998, 0.1154),
    "83o": (0.3730, 0.1591, 0.0747), "82s": (0.3938, 0.1879, 0.1198), "82o": (0.3782, 0.1548, 0.0791), "77": (0.6676, 0.3474, 0.1801), "76s": (0.4644, 0.2434, 0.1534),
    "76o": (0.4183, 0.2206, 0.1146), "75s": (0.4292, 0.2403, 0.1505), "75o": (0.4055, 0.2018, 0.1094), "74s": (0.4248, 0.2146, 0.1376), "74o": (0.3902, 0.1756, 0.1032),
    "73s": (0.3927, 0.2001, 0.1234), "73o": (0.3673, 0.1587, 0.0867), "72s": (0.3886, 0.1799, 0.1154), "72o": (0.3445, 0.1388, 0.0725), "66": (0.6251, 0.3153, 0.1645),
    "65s": (0.4249, 0.2415, 0.1584), "65o": (0.3967, 0.1923, 0.1180), "64s": (0.4158, 0.2152, 0.1388), "64o": (0.3828, 0.1872, 0.1042), "63s": (0.3985, 0.2008, 0.1269),
    "63o": (0.3730, 0.1672, 0.0873), "62s": (0.3817, 0.1828, 0.1166), "62o": (0.3407, 0.1531, 0.0781), "55": (0.5911, 0.2905, 0.1589), "54s": (0.4150, 0.2327, 0.1462),
    "54o": (0.3806, 0.1761, 0.1178), "53s": (0.3987, 0.2161, 0.1405), "53o": (0.3817, 0.1700, 0.1008), "52s": (0.3796, 0.1918, 0.1254), "52o": (0.3500, 0.1533, 0.0869),
    "44": (0.5689, 0.2531, 0.1518), "43s": (0.3912, 0.2079, 0.1288), "43o": (0.3438, 0.1637, 0.0891), "42s": (0.3648, 0.1909, 0.1230), "42o": (0.3210, 0.1517, 0.0891),
    "33": (0.5443, 0.2274, 0.1451), "32s": (0.3584, 0.1822, 0.1146), "32o": (0.3327, 0.1470, 0.0770), "22": (0.4976, 0.2162, 0.1374),
}

# Tables over 13 bit rank masks
POPC = [0] * 8192
STRAIGHT = [-1] * 8192
TOP5 = [0] * 8192
SDRAW = [False] * 8192
for _m in range(8192):
    POPC[_m] = bin(_m).count("1")
    _mm = (_m << 1) | (1 if _m & 4096 else 0)
    for _t in range(13, 3, -1):
        _w = (_mm >> (_t - 4)) & 31
        if _w == 31:
            STRAIGHT[_m] = _t - 1
            break
    for _t in range(13, 3, -1):
        _w = (_mm >> (_t - 4)) & 31
        if bin(_w).count("1") >= 4:
            SDRAW[_m] = True
            break
    _v = 0
    _k = 0
    for _r in range(12, -1, -1):
        if (_m >> _r) & 1:
            _v = _v * 16 + _r
            _k += 1
            if _k == 5:
                break
    while _k < 5:
        _v *= 16
        _k += 1
    TOP5[_m] = _v


def ev(cards):
    """Score the best five card hand from 5 to 7 int cards; bigger wins."""
    cnt = [0] * 13
    sm = [0, 0, 0, 0]
    for c in cards:
        r = c >> 2
        cnt[r] += 1
        sm[c & 3] |= 1 << r
    mask = sm[0] | sm[1] | sm[2] | sm[3]
    fl = 0
    for f in sm:
        if POPC[f] >= 5:
            sh = STRAIGHT[f]
            if sh >= 0:
                return 0x800000 | sh
            fl = 0x500000 | TOP5[f]
            break
    if POPC[mask] == len(cards):
        if fl:
            return fl
        sh = STRAIGHT[mask]
        if sh >= 0:
            return 0x400000 | sh
        return TOP5[mask]
    quad = trip = p1 = p2 = -1
    for r in range(12, -1, -1):
        k = cnt[r]
        if k < 2:
            continue
        if k == 4:
            quad = r
        elif k == 3:
            if trip < 0:
                trip = r
            elif p1 < 0:
                p1 = r
        elif p1 < 0:
            p1 = r
        elif p2 < 0:
            p2 = r
    if quad >= 0:
        return 0x700000 | (quad << 4) | (TOP5[mask & ~(1 << quad)] >> 16)
    if trip >= 0 and p1 >= 0:
        return 0x600000 | (trip << 4) | p1
    if fl:
        return fl
    sh = STRAIGHT[mask]
    if sh >= 0:
        return 0x400000 | sh
    if trip >= 0:
        return 0x300000 | (trip << 8) | (TOP5[mask & ~(1 << trip)] >> 12)
    if p2 >= 0:
        return 0x200000 | (p1 << 8) | (p2 << 4) | (TOP5[mask & ~(1 << p1) & ~(1 << p2)] >> 16)
    return 0x100000 | (p1 << 12) | (TOP5[mask & ~(1 << p1)] >> 8)


def hand_class(a, b):
    ra, rb = a >> 2, b >> 2
    if ra < rb:
        ra, rb = rb, ra
    if ra == rb:
        return R[ra] * 2
    return R[ra] + R[rb] + ("s" if (a & 3) == (b & 3) else "o")


# Percentile of every class, ranked by a blend that favours hands which play
# well both heads up and multiway. PCT[a*52+b] is the same for card ints.
def _rank_classes():
    order = sorted(PRE, key=lambda k: -(0.45 * PRE[k][0] + 0.35 * PRE[k][1] + 0.2 * PRE[k][2]))
    pct, cum = {}, 0
    for k in order:
        cum += 6 if len(k) == 2 else (4 if k[2] == "s" else 12)
        pct[k] = cum / 1326.0
    return pct


CLASS_PCT = _rank_classes()
PCT = [1.0] * 2704
for _a in range(52):
    for _b in range(52):
        if _a != _b:
            PCT[_a * 52 + _b] = CLASS_PCT[hand_class(_a, _b)]


COMBOS = []
for _a in range(52):
    for _b in range(_a + 1, 52):
        COMBOS.append((PCT[_a * 52 + _b], _a, _b))
COMBOS.sort()
COMBO_PCT = [c[0] for c in COMBOS]
COMBOS = [(c[1], c[2]) for c in COMBOS]


def range_size(width):
    """Number of combos in the top `width` share of hands."""
    return max(6, min(1326, bisect.bisect_right(COMBO_PCT, width + 1e-9)))


def board_info(board):
    cnt = [0] * 13
    suit = [0, 0, 0, 0]
    mask = 0
    top = -1
    for c in board:
        r = c >> 2
        cnt[r] += 1
        suit[c & 3] += 1
        mask |= 1 << r
        if r > top:
            top = r
    return cnt, suit, top, mask, len(board)


def cat_of(a, b, bi):
    """0 air, 1 draw, 2 weak pair, 3 top pair or overpair, 4 two pair or better."""
    bcnt, bsuit, btop, bmask, nb = bi
    r1, r2 = a >> 2, b >> 2
    s1, s2 = a & 3, b & 3
    if s1 == s2:
        fl = bsuit[s1] + 2
    else:
        fl = max(bsuit[s1], bsuit[s2]) + 1
    if fl >= 5:
        return 4
    m = bmask | (1 << r1) | (1 << r2)
    if STRAIGHT[m] > STRAIGHT[bmask]:
        return 4
    if r1 == r2:
        if bcnt[r1]:
            return 4
        return 3 if r1 > btop else 2
    h1, h2 = bcnt[r1], bcnt[r2]
    if h1 and h2:
        return 4
    if h1 or h2:
        hr = r1 if h1 else r2
        if bcnt[hr] >= 2:
            return 4
        return 3 if hr == btop else 2
    if nb < 5:
        if fl == 4 or (SDRAW[m] and not SDRAW[bmask]):
            return 1
        if nb == 3 and r1 > btop and r2 > btop:
            return 1
    return 0


def equity(hole, board, opps, deadline, rng, blur=0.0):
    """Monte Carlo share of the pot against opponents described by
    (range_width, weights or None). Returns (equity, trials)."""
    dead = [False] * 52
    for c in hole:
        dead[c] = True
    for c in board:
        dead[c] = True
    deck = [c for c in range(52) if not dead[c]]
    n = len(deck)
    need = 5 - len(board)
    bi = board_info(board)
    rnd = rng.random
    clock = time.perf_counter
    sizes = [range_size(rw) for rw, _ in opps]
    wide = [range_size(min(1.0, rw * RANGE_BLUR_MULT)) for rw, _ in opps]
    mine_fixed = ev(hole + board) if need == 0 else 0
    won = 0.0
    trials = 0
    attempts = 0
    while trials < MC_TRIALS_MAX and attempts < 4 * MC_TRIALS_MAX:
        # the clock is checked on attempts, so failed deals cannot run past the deadline
        if clock() > deadline:
            break
        attempts += 1
        used = list(dead)
        hands = []
        ok = True
        for (rw, w), k, kw in zip(opps, sizes, wide):
            if blur and rnd() < blur:
                k = kw
            pick = None
            for _ in range(24):
                a, b = COMBOS[int(rnd() * k)]
                if used[a] or used[b]:
                    continue
                if w is not None and rnd() > w[cat_of(a, b, bi)]:
                    continue
                pick = (a, b)
                break
            if pick is None:
                ok = False
                break
            used[pick[0]] = used[pick[1]] = True
            hands.append(pick)
        if not ok:
            continue
        if need:
            full = list(board)
            for _ in range(64):
                c = deck[int(rnd() * n)]
                if not used[c]:
                    used[c] = True
                    full.append(c)
                    if len(full) == 5:
                        break
            if len(full) < 5:
                continue
            mine = ev(hole + full)
        else:
            full = board
            mine = mine_fixed
        best = True
        ties = 0
        for a, b in hands:
            s = ev([a, b] + full)
            if s > mine:
                best = False
                break
            if s == mine:
                ties += 1
        if best:
            won += 1.0 / (ties + 1)
        trials += 1
    if trials == 0:
        return None, 0
    return won / trials, trials


def has_draw(a, b, bi):
    """Flush draw or open ended straight draw that uses a hole card, before the river."""
    bcnt, bsuit, btop, bmask, nb = bi
    if nb >= 5:
        return False
    s1, s2 = a & 3, b & 3
    if (bsuit[s1] + (2 if s1 == s2 else 1)) == 4 or (s1 != s2 and bsuit[s2] + 1 == 4):
        return True
    m = bmask | (1 << (a >> 2)) | (1 << (b >> 2))
    return SDRAW[m] and not SDRAW[bmask] and STRAIGHT[m] < 0


def quick_equity(hole, board, nopp, widths=None):
    """Cheap fallback when Monte Carlo is out of time. Preflop it compares our
    percentile with the tightest opponent range, never with a random hand;
    postflop it uses absolute made hand strength, so board made hands and
    kickers count."""
    if not board:
        q = PCT[hole[0] * 52 + hole[1]]
        r = min(widths) if widths else 1.0
        if r >= 0.99:
            e = PRE.get(hand_class(hole[0], hole[1]), (0.5, 0.3, 0.2))
            return e[0] if nopp <= 1 else (e[1] if nopp <= 3 else e[2])
        # conservative table against a range of width r
        if q <= 0.35 * r:
            e = 0.60
        elif q <= 0.7 * r:
            e = 0.48
        elif q <= r:
            e = 0.40
        else:
            e = 0.30
        return e ** (1.0 + 0.6 * (max(1, nopp) - 1))
    bi = board_info(board)
    cat = cat_of(hole[0], hole[1], bi)
    base = (0.15, 0.35, 0.50, 0.70, 0.88)[cat]
    score = ev(hole + board)
    kind = score >> 20
    bscore = ev(board)
    if kind >= 4:
        if kind > bscore >> 20:
            # our cards make the category: full house or better, straight or flush
            base = max(base, 0.92 if kind >= 6 else 0.85)
        elif score == bscore:
            base = 0.40              # we play the board: a chop at best
        else:
            # the board makes the category and our cards only add a kicker or a
            # higher card, so strength follows our best hole card
            base = 0.25 + 0.6 * max(hole[0] >> 2, hole[1] >> 2) / 12.0
    if cat in (2, 3) and has_draw(hole[0], hole[1], bi):
        base += 0.08
    return base ** (1.0 + 0.6 * (max(1, nopp) - 1))


LINE_RANK = {"check": 0, "call": 1, "bet": 2, "raise": 3}


def _mark(line, seat, street, kind):
    """Keep each player's most aggressive action on their latest street."""
    old = line.get(seat)
    if old is None or old[0] != street or LINE_RANK[kind] > LINE_RANK[old[1]]:
        line[seat] = (street, kind)


def _new_stats():
    return {"h": 0, "vpip": 0, "pfr": 0, "tb": 0, "tb_opp": 0, "shv": 0,
            "rn": 0, "minr": 0, "rsz": 0.0, "agg": 0, "pas": 0, "chk": 0,
            "fbet": 0, "fbet_opp": 0, "frv": 0, "frv_opp": 0, "sd": 0,
            "sd_raise": [], "sd_call": [], "sd_shove": []}


class Agent:
    def __init__(self):
        self.rng = random.Random()
        self.stats = {}
        self.types = {}
        self.used = 0.0
        self.start_stack = 2000
        self.bb = 20
        self.cache = {}

    # ------------------------------------------------------------ hooks
    def on_table_start(self, info):
        try:
            self.start_stack = int(info.get("starting_stack") or 2000)
            self.bb = int(info.get("big_blind") or 20)
        except Exception:
            pass

    def on_hand_end(self, summary):
        try:
            self._learn(summary)
        except Exception:
            pass
        self.cache = {}
        self._ends = getattr(self, "_ends", 0) + 1
        if self._ends % 100 == 0:
            # collection is switched off during play; this sweep (about 0.01 ms) can
            # still delay the next act, since hand end messages are not acknowledged
            gc.collect()

    def act(self, state):
        t0 = time.perf_counter()
        try:
            out = self._decide(state, t0)
        except Exception:
            out = None
        try:
            out = self._legalise(out, state)
        except Exception:
            out = {"action": "fold"}
        self.used += time.perf_counter() - t0 + TRANSPORT_EST
        return out

    # ------------------------------------------------------- safety net
    def _legalise(self, d, st):
        try:
            legal = st.get("legal_actions") or []
            a = (d or {}).get("action")
            if a == "all_in":
                a = "raise"
                d = {"action": "raise", "amount": st.get("max_raise_to")}
            if a == "raise":
                lo, hi = st.get("min_raise_to"), st.get("max_raise_to")
                if "raise" in legal and lo is not None and hi is not None:
                    try:
                        amt = int(d.get("amount"))
                    except Exception:
                        amt = int(lo)
                    return {"action": "raise", "amount": int(max(lo, min(hi, amt)))}
                a = "call"
            if a == "call":
                if "call" in legal:
                    return {"action": "call"}
                a = "check"
            if "check" in legal:
                return {"action": "check"}
            if a != "fold" and "call" in legal:
                to_call = st.get("to_call") or 0
                if to_call <= 0.1 * (st.get("pot") or 0):
                    return {"action": "call"}
            if "fold" in legal:
                return {"action": "fold"}
        except Exception:
            pass
        return {"action": "check"} if "check" in (st.get("legal_actions") or []) else {"action": "fold"}

    # ------------------------------------------------------ opponent model
    def _st(self, seat):
        s = self.stats.get(seat)
        if s is None:
            s = self.stats[seat] = _new_stats()
        return s

    def _rate(self, seat, num, den, prior):
        s = self.stats.get(seat)
        if s is None:
            return PRIOR[prior]
        n, d = s[num], (s[den] if isinstance(den, str) else den)
        return (n + PRIOR[prior] * PRIOR_N) / (d + PRIOR_N)

    def _learn(self, sm):
        hist = sm.get("history") or []
        bb = self.bb
        seen = set()
        street = None
        cur = 0
        sb = {}
        total = {}
        nraise = 0
        last_inc = bb
        pre_role = {}
        shovers = set()
        for h in hist:
            seat = h.get("seat")
            act = h.get("action")
            amt = h.get("amount") or 0
            stt = h.get("street")
            if seat is None:
                continue
            seen.add(seat)
            if stt != street:
                street = stt
                sb = {}
                cur = 0
                last_inc = bb
            if act in ("small_blind", "big_blind"):
                sb[seat] = amt
                total[seat] = total.get(seat, 0) + amt
                cur = max(cur, amt)
                continue
            s = self._st(seat)
            mine = sb.get(seat, 0)
            facing = cur > mine
            if act == "raise":
                added = amt - mine
                total[seat] = total.get(seat, 0) + added
                sb[seat] = amt
                inc = amt - cur
                s["rn"] += 1
                if inc <= last_inc:
                    s["minr"] += 1
                if inc > last_inc:
                    last_inc = inc
                cur = amt
                allin = total[seat] >= self.start_stack
                if stt == "preflop":
                    if nraise >= 1:
                        s["tb_opp"] += 1
                        if nraise == 1:
                            s["tb"] += 1
                    nraise += 1
                    pre_role[seat] = "r"
                    s["rsz"] += amt / float(bb)
                    if allin:
                        s["shv"] += 1
                        shovers.add(seat)
                else:
                    s["agg"] += 1
                    if facing:
                        s["fbet_opp"] += 1
                        if stt == "river":
                            s["frv_opp"] += 1
            elif act == "call":
                total[seat] = total.get(seat, 0) + amt
                sb[seat] = mine + amt
                if stt == "preflop":
                    if nraise == 1:
                        s["tb_opp"] += 1
                    pre_role.setdefault(seat, "c")
                else:
                    s["pas"] += 1
                    s["fbet_opp"] += 1
                    if stt == "river":
                        s["frv_opp"] += 1
            elif act == "fold":
                if stt == "preflop":
                    if nraise == 1:
                        s["tb_opp"] += 1
                elif facing:
                    s["fbet"] += 1
                    s["fbet_opp"] += 1
                    if stt == "river":
                        s["frv"] += 1
                        s["frv_opp"] += 1
            elif act == "check":
                if stt != "preflop":
                    s["chk"] += 1
        for seat in seen:
            s = self._st(seat)
            s["h"] += 1
            role = pre_role.get(seat)
            if role:
                s["vpip"] += 1
                if role == "r":
                    s["pfr"] += 1
        shown = sm.get("shown") or {}
        for k, cards in shown.items():
            try:
                seat = int(k)
                a, b = CARD[cards[0]], CARD[cards[1]]
            except Exception:
                continue
            s = self._st(seat)
            s["sd"] += 1
            role = pre_role.get(seat)
            if seat in shovers:
                s["sd_shove"].append(PCT[a * 52 + b])
            if role == "r":
                s["sd_raise"].append(PCT[a * 52 + b])
            elif role == "c":
                s["sd_call"].append(PCT[a * 52 + b])
        for seat in seen:
            self.types[seat] = self._classify(seat)

    def _classify(self, seat):
        s = self.stats.get(seat)
        if not s:
            return "unknown"
        h = s["h"]
        if h >= 12 and s["shv"] / float(h) > 0.20:
            return "spammer"
        if h < MIN_HANDS_CLASSIFY:
            return "unknown"
        vpip = s["vpip"] / float(h)
        pfr = s["pfr"] / float(h)
        acts = s["agg"] + s["pas"] + s["chk"]
        aggf = s["agg"] / float(acts) if acts else 0.3
        fb = s["fbet"] / float(s["fbet_opp"]) if s["fbet_opp"] >= 6 else None
        if pfr > 0.35 or (aggf > 0.55 and vpip > 0.45):
            return "maniac"
        if vpip > 0.45 and aggf < 0.40 and (fb is None or fb < 0.30) and pfr < 0.20:
            return "station"
        if vpip < 0.15:
            return "nit"
        if s["rn"] >= 8 and s["minr"] / float(s["rn"]) > 0.60:
            return "minraiser"
        return "unknown"

    def _type(self, seat):
        return self.types.get(seat, "unknown")

    def _open_range(self, seat):
        r = self._rate(seat, "pfr", "h", "pfr")
        s = self.stats.get(seat)
        if s and len(s["sd_raise"]) >= 3:
            obs = min(1.0, 2.0 * sum(s["sd_raise"]) / len(s["sd_raise"]))
            r = 0.5 * r + 0.5 * obs
        return min(1.0, max(0.04, r))

    def _call_range(self, seat):
        r = self._rate(seat, "vpip", "h", "vpip")
        s = self.stats.get(seat)
        if s and len(s["sd_call"]) >= 3:
            obs = min(1.0, 2.0 * sum(s["sd_call"]) / len(s["sd_call"]))
            r = 0.5 * r + 0.5 * obs
        return min(1.0, max(0.10, r))

    def _threebet_range(self, seat):
        return min(1.0, max(0.025, self._rate(seat, "tb", "tb_opp", "tb")))

    def _shove_range(self, seat):
        s = self.stats.get(seat)
        r = PRIOR["shv"]
        if s and s["h"]:
            r = (s["shv"] + PRIOR["shv"] * PRIOR_N) / (s["h"] + PRIOR_N)
            if len(s["sd_shove"]) >= 2:
                r = max(r, min(1.0, 2.0 * sum(s["sd_shove"]) / len(s["sd_shove"])))
            if len(s["sd_raise"]) >= 3 and self._type(seat) == "spammer":
                r = max(r, min(1.0, 2.0 * sum(s["sd_raise"]) / len(s["sd_raise"])))
        return min(1.0, max(0.03, r))

    def _bluffiness(self, seat):
        t = self._type(seat)
        if t == "spammer":
            return 0.95
        s = self.stats.get(seat)
        aggf, vpip = 0.3, 0.35
        if s and s["h"]:
            acts = s["agg"] + s["pas"] + s["chk"]
            aggf = (s["agg"] + 0.3 * PRIOR_N) / (acts + PRIOR_N)
            vpip = self._rate(seat, "vpip", "h", "vpip")
        b = BLUFF_BASE + 0.6 * (aggf - 0.3) + 0.4 * (vpip - 0.30)
        if t == "maniac":
            b = max(b, 0.70)
        elif t == "nit":
            b = min(b, 0.10)
        elif t == "station":
            b = min(b, 0.20)
        return min(0.95, max(0.05, b))

    # ------------------------------------------------------------ decide
    def _decide(self, st, t0):
        legal = st.get("legal_actions") or []
        if not legal:
            return None
        hole = [CARD[c] for c in st["hole_cards"]]
        board = [CARD[c] for c in (st.get("board") or [])]
        me = st.get("seat", 0)
        stacks = st.get("stacks") or []
        n = len(stacks) or 8
        bets = st.get("bets") or [0] * n
        folded = st.get("folded") or [False] * n
        button = st.get("button", 0) or 0
        bb = st.get("big_blind") or self.bb or 20
        self.bb = bb
        if stacks and st.get("street") == "preflop":
            self.start_stack = max(self.start_stack, max(stacks[i] + bets[i] for i in range(n)))
        street = st.get("street") or ("preflop" if not board else ("flop", "turn", "river")[min(2, len(board) - 3)])
        hist = st.get("history") or []
        self._hn = st.get("hand_number") or 0
        ctx = self._context(st, hist, me, n, button, folded, stacks)
        ctx.update(legal=legal, hole=hole, board=board, me=me, n=n, bb=bb, street=street,
                   stacks=stacks, bets=bets, folded=folded, button=button, t0=t0,
                   to_call=st.get("to_call") or 0, pot=st.get("pot") or 0,
                   lo=st.get("min_raise_to"), hi=st.get("max_raise_to"),
                   betting=st.get("betting") or "no_limit")
        ctx["my_stack"] = stacks[me] if me < len(stacks) else self.start_stack
        ctx["my_bet"] = bets[me] if me < len(bets) else 0
        ctx["can_raise"] = "raise" in legal and ctx["lo"] is not None and ctx["hi"] is not None
        if street == "preflop":
            return self._preflop(ctx)
        return self._postflop(ctx)

    def _context(self, st, hist, me, n, button, folded, stacks):
        """Who raised, who called, and each player's line this hand."""
        pre_raises = []
        limpers = []
        callers_after = []
        line = {}
        level = {}
        allin = {}
        street = None
        cur = 0
        sbet = {}
        pre_put = {}
        last_aggr = None
        barrels = {}
        for h in hist:
            seat = h.get("seat")
            act = h.get("action")
            amt = h.get("amount") or 0
            stt = h.get("street")
            if stt != street:
                street = stt
                cur = 0
                sbet = {}
            if act in ("small_blind", "big_blind"):
                sbet[seat] = amt
                cur = max(cur, amt)
                pre_put[seat] = amt
                continue
            if stt == "preflop" and act in ("raise", "call"):
                pre_put[seat] = amt if act == "raise" else pre_put.get(seat, 0) + amt
            if act == "raise":
                if stt == "preflop":
                    pre_raises.append((seat, amt))
                    level[seat] = len(pre_raises)
                    callers_after = []
                    last_aggr = seat
                else:
                    kind = "raise" if cur > sbet.get(seat, 0) and cur > 0 else "bet"
                    _mark(line, seat, stt, kind)
                    barrels.setdefault(seat, set()).add(stt)
                    last_aggr = seat
                cur = max(cur, amt)
                sbet[seat] = amt
            elif act == "call":
                sbet[seat] = sbet.get(seat, 0) + amt
                if stt == "preflop":
                    if pre_raises:
                        callers_after.append(seat)
                    else:
                        limpers.append(seat)
                else:
                    _mark(line, seat, stt, "call")
            elif act == "check":
                if stt != "preflop":
                    _mark(line, seat, stt, "check")
        pre_allin = {}
        for i in range(n):
            if i < len(stacks) and stacks[i] == 0 and not folded[i]:
                allin[i] = True
                if pre_put.get(i, 0) >= self.start_stack:
                    pre_allin[i] = True
        line = dict((k, v[1]) for k, v in line.items())
        return {"pre_raises": pre_raises, "limpers": limpers, "callers_after": callers_after,
                "line": line, "barrels": barrels, "level": level, "allin": allin, "pre_allin": pre_allin, "last_aggr": last_aggr}

    def _pre_range(self, seat, ctx):
        """Range width implied by a seat's preflop action this hand."""
        lv = ctx["level"].get(seat)
        if lv is None:
            if seat in ctx["limpers"] or seat in ctx["callers_after"] or ctx["pre_raises"]:
                r = self._call_range(seat)
                if ctx["pre_raises"] and seat not in ctx["limpers"]:
                    r = min(r, 0.45)
                return r
            return 1.0
        t = self._type(seat)
        if lv == 1:
            r = self._open_range(seat)
        elif lv == 2:
            r = self._threebet_range(seat)
        else:
            r = max(0.025, 0.4 * self._threebet_range(seat))
        wild = t in ("maniac", "spammer")
        if wild:
            r = max(r, 0.8 * self._open_range(seat))
        if ctx["pre_allin"].get(seat):
            sr = self._shove_range(seat)
            r = max(sr, 0.8 * self._open_range(seat)) if wild else max(min(r, sr), 0.03)
        return min(1.0, r)

    def _budget(self, hand_no):
        left = ROUND_TARGET - self.used
        if left <= 0.3:
            return 0.0
        hands_left = max(60, 1001 - (hand_no or 1))
        return max(0.0, min(MC_MAX, 1.6 * left / hands_left))

    def _eq(self, ctx, opps, key, commit=False):
        hit = self.cache.get(key)
        # a stack committing decision never reuses an equity that came from the fallback
        if hit is not None and (hit[1] or not commit):
            return hit[0]
        hole, board = ctx["hole"], ctx["board"]
        b = self._budget(self._hand_no)
        if commit and b < MC_COMMIT and self.used < COMMIT_BANK:
            b = MC_COMMIT
        eq = None
        if b > 0.0002 and opps:
            eq, n = equity(hole, board, opps, ctx["t0"] + b, self.rng, RANGE_BLUR if board else 0.0)
            if n < 12:
                eq = None
        mc = eq is not None
        if eq is None:
            eq = quick_equity(hole, board, len(opps), [o[0] for o in opps])
        self.cache[key] = (eq, mc)
        return eq

    # ------------------------------------------------------------ preflop
    def _raise_to(self, ctx, amount):
        if not ctx["can_raise"]:
            return {"action": "call"} if "call" in ctx["legal"] else {"action": "check"}
        amount = int(amount)
        hi = ctx["hi"]
        # if the raise leaves us with little behind, just go all in
        if hi - amount < 0.25 * amount and ctx["betting"] == "no_limit":
            amount = hi
        return {"action": "raise", "amount": max(ctx["lo"], min(hi, amount))}

    def _behind(self, ctx):
        """Players still to act after us this preflop round, not folded."""
        n, me, button, folded = ctx["n"], ctx["me"], ctx["button"], ctx["folded"]
        out = []
        bb_seat = (button + 2) % n if n > 2 else (button + 1) % n
        k = (me + 1) % n
        while k != (bb_seat + 1) % n:
            if not folded[k] and k != me:
                out.append(k)
            k = (k + 1) % n
            if len(out) > n:
                break
        return out

    def _preflop(self, ctx):
        n, me, button, bb = ctx["n"], ctx["me"], ctx["button"], ctx["bb"]
        hole = ctx["hole"]
        q = PCT[hole[0] * 52 + hole[1]]
        cls = hand_class(hole[0], hole[1])
        to_call = ctx["to_call"]
        pot = ctx["pot"]
        legal = ctx["legal"]
        raises = ctx["pre_raises"]
        limpers = ctx["limpers"]
        rel = (me - button) % n
        behind = self._behind(ctx) if rel != 2 else []
        nbehind = len(behind)
        is_bb = rel == 2 or (n == 2 and rel == 1)
        is_sb = rel == 1 and n > 2
        stack_total = ctx["my_stack"] + ctx["my_bet"]
        types_behind = [self._type(s) for s in behind]
        loose_behind = 0.0
        if behind:
            loose_behind = sum(self._rate(s, "vpip", "h", "vpip") for s in behind) / len(behind)
        fixed = ctx["betting"] == "fixed_limit"

        if not raises:
            # Unopened or limped pot
            thr = OPEN_Q.get(min(7, nbehind), 0.10)
            if rel == 1:
                thr = OPEN_Q[1]
            if nbehind <= 2 and behind and loose_behind < 0.25:
                thr *= STEAL_WIDEN
            if limpers:
                thr *= ISO_TIGHTEN
            if is_bb:
                thr = 0.14 if limpers else 0.0
            pool = behind + [s for s in limpers if s != me]
            if pool:
                vp = [self._rate(s, "vpip", "h", "vpip") for s in pool]
                loose = sum(vp) / len(vp)
                if loose >= LOOSE_VPIP:
                    thr = max(thr, LOOSE_OPEN_Q + 0.3 * (loose - LOOSE_VPIP))
            if behind and not limpers:
                p_fold = 1.0
                for s in behind:
                    p_fold *= 1.0 - self._rate(s, "vpip", "h", "vpip")
                a, b, c, d = STEAL_ALL_FOLD
                if p_fold >= a:
                    thr = max(thr, b)
                elif p_fold >= c:
                    thr = max(thr, d)
            if any(t == "spammer" for t in types_behind):
                thr = min(thr, SPAMMER_OPEN_CAP)
            if q <= thr:
                size = OPEN_BTN_BB if rel in (0, 1) else OPEN_BB
                size += OPEN_LIMPER_BB * len(limpers)
                if loose_behind > 0.45 or any(t == "station" for t in types_behind):
                    size += OPEN_LOOSE_BB
                return self._raise_to(ctx, size * bb)
            if to_call == 0:
                return {"action": "check"}
            if limpers and to_call <= bb:
                if is_sb and q <= SB_COMPLETE_Q:
                    return {"action": "call"}
                if nbehind <= 3 and q <= OVERLIMP_Q:
                    return {"action": "call"}
                if cls[0] == cls[1] and nbehind <= 5:
                    return {"action": "call"}
            return {"action": "fold"}

        last_seat, last_to = raises[-1]
        r_bb = last_to / float(bb)
        nraises = len(raises)
        villains = [s for s, _ in raises]
        callers = ctx["callers_after"]
        opener_allin = ctx["allin"].get(last_seat, False)
        live_opps = [i for i in range(n) if i != me and not ctx["folded"][i]]
        call_amt = min(to_call, ctx["my_stack"])
        pot_odds = call_amt / float(pot + call_amt) if call_amt > 0 else 0.0

        # Commitment decisions: an all in, or a raise so big we play for stacks.
        big = opener_allin or (not fixed and last_to >= BIG_RAISE_BB * bb) or call_amt >= 0.35 * stack_total
        if big:
            opps = []
            for s in live_opps:
                if s in villains or s in callers or ctx["allin"].get(s):
                    opps.append((self._pre_range(s, ctx), None))
            if not opps:
                opps = [(self._pre_range(last_seat, ctx), None)]
            opps = opps[:4]
            key = ("pre", tuple(round(o[0], 3) for o in opps))
            eq = self._eq(ctx, opps, key, True)
            need = pot_odds + JAM_MARGIN + JAM_MARGIN_PER_BEHIND * len(behind)
            if q <= FOURBET_Q:
                need = min(need, pot_odds)
            if eq >= need:
                if opener_allin or not ctx["can_raise"]:
                    return {"action": "call"}
                if eq >= need + 0.08 or q <= FOURBET_Q:
                    return self._raise_to(ctx, ctx["hi"])
                return {"action": "call"}
            return {"action": "fold"}

        r_villain = self._pre_range(last_seat, ctx)
        vtype = self._type(last_seat)
        if nraises == 1:
            if q <= THREEBET_Q or (q <= THREEBET_VS_WIDE * r_villain and r_villain >= 0.25):
                mult = 3.0 if rel in (0, 3) or nbehind == 0 else 3.6
                size = last_to * mult + last_to * len(callers)
                return self._raise_to(ctx, size)
            size_factor = (3.0 / max(2.0, r_bb)) ** 0.7
            thr = r_villain * CALL_RAISE_BASE * size_factor
            if vtype == "nit":
                thr *= 0.6
            if is_bb and r_bb <= 4:
                thr += BB_DEFEND_BONUS * (3.0 / max(2.0, r_bb))
            if vtype == "minraiser" or r_bb <= 2.01:
                thr = max(thr, 0.45 if is_bb else 0.22)
            thr = max(0.02, min(0.55, thr))
            pair = cls[0] == cls[1]
            setmine = pair and to_call * 15 <= ctx["my_stack"] and r_bb <= 4.5
            if q <= thr or setmine:
                return {"action": "call"}
            if to_call == 0:
                return {"action": "check"}
            return {"action": "fold"}

        # Facing a 3 bet or more
        we_opened = ctx["level"].get(me) is not None
        r3 = r_villain
        if q <= FOURBET_Q or (q <= 0.6 * r3 and r3 >= 0.10):
            return self._raise_to(ctx, max(last_to * 2.4, 0) if not fixed else last_to * 2)
        if we_opened and (q <= CALL_3BET_Q or q <= r3) and to_call <= 0.25 * stack_total:
            return {"action": "call"}
        if q <= COLD_4BET_CALL_Q:
            return {"action": "call"}
        if fixed and q <= 0.08:
            return {"action": "call"}
        if to_call == 0:
            return {"action": "check"}
        return {"action": "fold"}

    # ------------------------------------------------------------ postflop
    def _weights(self, seat, ctx):
        lk = ctx["line"].get(seat)
        if lk is None:
            return None
        bl = self._bluffiness(seat)
        t = self._type(seat)
        if lk == "raise":
            w = [bl * 0.6, 0.6, 0.3, 0.8, 1.0]
        elif lk == "bet":
            w = [bl, 0.75, 0.55, 0.95, 1.0]
        elif lk == "call":
            air = 0.8 if t == "station" else (0.6 if t in ("maniac", "spammer") else 0.3)
            w = [air, 0.9, 0.9, 1.0, 1.0]
        else:
            w = [1.0, 1.0, 1.0, 0.75, 0.5]
        if lk in ("bet", "raise") and t not in ("maniac", "spammer"):
            pot = ctx["pot"]
            vb = ctx["bets"][seat] if seat < len(ctx["bets"]) else 0
            if pot and vb >= 0.5 * pot:
                w[0] *= 0.7
                w[2] *= 0.7
            extra = len(ctx["barrels"].get(seat, ())) - 1
            if extra > 0:
                f = BARREL_DECAY ** extra
                w[0] *= f
                w[1] *= f
                w[2] *= f
        return w

    def _postflop(self, ctx):
        me, n = ctx["me"], ctx["n"]
        legal = ctx["legal"]
        folded = ctx["folded"]
        street = ctx["street"]
        pot = ctx["pot"]
        to_call = ctx["to_call"]
        board = ctx["board"]
        hole = ctx["hole"]
        live = [i for i in range(n) if i != me and not folded[i]]
        if not live:
            return {"action": "check"} if "check" in legal else {"action": "call"}
        opps = []
        for s in live:
            opps.append((self._pre_range(s, ctx), self._weights(s, ctx)))
        if len(opps) > 5:
            opps = sorted(opps, key=lambda o: o[0])[:5]
        key = (street, tuple((round(o[0], 3), tuple(o[1]) if o[1] else None) for o in opps))
        commit = to_call >= 0.35 * ctx["my_stack"] or any(ctx["allin"].get(s) for s in live)
        eq = self._eq(ctx, opps, key, commit)
        nopp = len(live)
        k = min(3, nopp)
        types = [self._type(s) for s in live]
        stations = all(t == "station" for t in types)
        any_station = any(t == "station" for t in types)
        maniac_in = any(t in ("maniac", "spammer") for t in types)
        bi = board_info(board)
        mycat = cat_of(hole[0], hole[1], bi)
        draw = mycat == 1 or (mycat in (2, 3) and has_draw(hole[0], hole[1], bi))
        wet = max(bi[1]) >= 2 or self._connected(bi[3])
        rng = self.rng.random
        my_stack = ctx["my_stack"]
        bb = ctx["bb"]
        aggressor = ctx["last_aggr"] == me or (ctx["pre_raises"] and ctx["pre_raises"][-1][0] == me)

        if to_call == 0:
            thr = (VALUE_EQ_RIVER if street == "river" else VALUE_EQ)[k]
            if any_station:
                thr -= STATION_VALUE_CUT
            if eq >= thr:
                frac = BET_FRAC.get(street, 0.65)
                if eq >= 0.80 or any_station:
                    frac = BET_FRAC_STRONG
                if wet and street != "river":
                    frac += WET_BONUS
                return self._bet(ctx, frac * pot)
            if nopp == 1 and not stations:
                v = live[0]
                fold_rate = self._rate(v, "fbet", "fbet_opp", "fbet")
                if street == "flop" and ctx["pre_raises"] and ctx["pre_raises"][-1][0] == me:
                    f = CBET_FREQ * (0.6 + fold_rate) * (0.8 if wet else 1.1)
                    if rng() < f:
                        return self._bet(ctx, CBET_SIZE * pot)
                if street != "river" and mycat == 1 and rng() < SEMI_BLUFF_FREQ * (0.5 + fold_rate):
                    return self._bet(ctx, 0.6 * pot)
                if street == "turn" and aggressor and fold_rate > 0.45 and eq < 0.35 and rng() < BARREL_FREQ:
                    return self._bet(ctx, 0.6 * pot)
                if street == "river":
                    s = self.stats.get(v)
                    frv = s["frv"] / float(s["frv_opp"]) if s and s["frv_opp"] >= 8 else 0.0
                    if frv > 0.55 and eq < 0.20 and rng() < RIVER_BLUFF_FREQ:
                        return self._bet(ctx, 0.7 * pot)
            return {"action": "check"}

        # Facing a bet
        call_amt = min(to_call, my_stack)
        po = call_amt / float(pot + call_amt)
        need = po + CALL_MARGIN
        allin_faced = any(ctx["allin"].get(s) for s in live)
        if street != "river" and not allin_faced and draw and my_stack > 4 * call_amt:
            need -= DRAW_IMPLIED
        if nopp >= 2:
            need += 0.02
        if nopp == 1 and street != "river" and not maniac_in and to_call >= AIR_FOLD_BET * (pot - to_call):
            if mycat == 0 and eq < RAISE_EQ[1]:
                return {"action": "fold"}
            if mycat == 2 and not draw:
                need += WEAK_PAIR_MARGIN
        raise_thr = RAISE_EQ[k]
        if eq >= raise_thr and ctx["can_raise"]:
            if maniac_in and street != "river" and rng() < TRAP_FREQ and eq < 0.95:
                return {"action": "call"}
            cur = max(ctx["bets"])
            target = cur + 0.85 * (pot + to_call)
            return self._raise_to(ctx, target)
        if eq >= need:
            return {"action": "call"}
        return {"action": "fold"}

    def _connected(self, bmask):
        for t in range(9):
            w = (bmask >> t) & 31
            if POPC[w] >= 3:
                return True
        return False

    def _bet(self, ctx, amount):
        amount = max(ctx["bb"], int(amount))
        if not ctx["can_raise"]:
            return {"action": "check"}
        return self._raise_to(ctx, ctx["my_bet"] + amount)

    @property
    def _hand_no(self):
        return getattr(self, "_hn", 0)


def _warm_up():
    """Run one decision of each kind at import so the first real ones are not slow."""
    base = {"hand_number": 1, "seat": 3, "button": 0, "small_blind": 10, "big_blind": 20,
            "stacks": [2000, 1990, 1980, 2000, 2000, 2000, 2000, 2000],
            "bets": [0, 10, 20, 0, 0, 0, 0, 0], "folded": [False] * 8, "pot": 30,
            "to_call": 20, "min_raise_to": 40, "max_raise_to": 2000,
            "legal_actions": ["fold", "call", "raise"], "betting": "no_limit",
            "raise_cap": None, "raises_this_street": 0, "street": "preflop", "board": [],
            "hole_cards": ["As", "Kd"],
            "history": [{"seat": 1, "street": "preflop", "action": "small_blind", "amount": 10},
                        {"seat": 2, "street": "preflop", "action": "big_blind", "amount": 20}]}
    flop = dict(base, street="flop", board=["Ah", "7c", "2d"], to_call=0, pot=130,
                bets=[0] * 8, legal_actions=["check", "raise"], min_raise_to=20,
                history=base["history"] + [{"seat": 3, "street": "preflop", "action": "raise", "amount": 60},
                                           {"seat": 2, "street": "preflop", "action": "call", "amount": 40}],
                folded=[True, True, False, False, True, True, True, True])
    shove = dict(base, history=base["history"] + [{"seat": 4, "street": "preflop", "action": "raise", "amount": 2000}])
    try:
        a = Agent()
        a.used = -1.0
        for st in (base, flop, shove, base, flop):
            a.act(st)
            a.cache = {}
    except Exception:
        pass


_warm_up()
gc.collect()
gc.freeze()
gc.disable()
