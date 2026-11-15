"""Avengers pokerbot (Resonance Qt).

Preflop: position charts (instant), widened or tightened by what each seat has
shown this round (fold-to-3-bet, shove frequency, looseness).
Postflop: every opponent gets a range from his preflop line, re-ranked on the
actual board and narrowed by his postflop actions and stats; our equity against
those ranges (exact on the river, Monte Carlo before) feeds an expected-value
comparison of check / bet sizes / call / raise that uses each seat's measured
fold frequency.
Standard library only. Everything heavy is built once at import.
"""
import gc
import json
import random
import time

DEBUG = False
BIG_CALL = 300          # chips to call from which a decision counts as big
BIG_BUDGET = 0.0035    # seconds of simulation for a big decision (about 400 samples on the server)
WEAK_PAIR_BET = 0.5     # bet size (share of the pot before it) from which the weak-pair rule applies
RAISE_SMALL = True      # V21: raise small bets heads up when the bettor's folds pay for it
# V22: what each seat's bet sizes mean. Sizes are bucketed in pots; per seat and bucket we count
# (a) how often he gives up when that bet is raised, (b) how strong the hands he showed down were.
ZR_FIELD = (0.79, 0.69, 0.53, 0.41, 0.36, 0.31)   # field: folds when his own bet of that size is raised
ZR_MIN = 4              # observations of this seat needed before raising a bet of 0.42-0.90 pot
ZR_PRIOR = 4.0
ZS_MIN = 3              # shown hands needed before a seat's own size record reshapes his range
ZS_PRIOR = 3.0
ZW_MIN = 6              # shown hands needed before a size is treated as weaker than the model says
ZW_MAXB = 3             # ... and only for bets under 0.90 pot
SIZE_LEARN = True
VERSION = "3.0"
# Time for a long game (the 5,000-hand final). FINAL_BANK_S is the time bank we assume for the whole
# game; the bot paces itself to use about two thirds of it, measured on its own clock.
FINAL_BANK_S = 50.0     # set to 10 x (hands / 1000) if the organisers scale the bank with the game length
IPC_S = 0.0009          # time per decision the server counts that we cannot see (sending us the state)
LONG_GAME = 1500        # games longer than this many hands are paced
# End of a long game: only the top two places pay. In the last quarter the bot follows every seat's
# chips: outside the top two and far behind, it takes more gambles; far ahead of third, it avoids them.
RANK_PLAY = True
RANK_PHASE = 0.25
RANK_HANDICAP = 0.0     # test only: chips per hand taken off our own count


# Seat fingerprints for Sunday's table: a seat is recognised from its own open sizes and bet sizes
# during the round, then starts from what that team did on Saturday (per size bucket: times its bet
# was raised / folded, hands shown / strong). At most 12 pseudo-observations, so live play corrects it.
FINGERPRINTS = False     # v3.0: nothing specific to one table; every rule is learned during the game
THREEBET_ANY = True     # 3-bet any two cards against an opener who folds to 3-bets 4 times in 5 (8+ cases)
MANIAC_RULES = True     # against the recognised 3-bet maniac: 4-bet instead of calling, raise his bets instead of calling
SEED = {
    "ANKER": ([0, 12, 12, 10, 12, 8], [0, 5.76, 0.86, 5, 8.64, 3], [0, 12, 12, 12, 12, 12], [0, 10.24, 11.17, 9.26, 8.21, 9]),
    "CPF": ([0, 12, 0, 0, 12, 0], [0, 9.62, 0, 0, 2.4, 0], [10, 12, 0, 12, 12, 0], [8, 4.12, 0, 10, 11.22, 0]),
    "WBOT": ([12, 12, 12, 12, 12, 0], [9.65, 5.51, 4, 1.85, 3.82, 0], [12, 12, 12, 12, 12, 12], [4.68, 6.1, 5.8, 9.76, 8.38, 11.56]),
    "GG": ([0, 0, 12, 0, 12, 0], [0, 0, 8.93, 0, 3.69, 0], [0, 12, 12, 0, 12, 0], [0, 7, 4.43, 0, 10.55, 0]),
    "POKE": ([0, 12, 12, 12, 12, 12], [0, 7.1, 6.62, 8.5, 9, 3.6], [0, 12, 12, 12, 12, 12], [0, 7.84, 7.38, 5.35, 9, 11.02]),
    "ANTON": ([0, 12, 12, 12, 0, 0], [0, 11, 10.29, 10.11, 0, 0], [0, 12, 12, 12, 0, 12], [0, 8.7, 6.46, 6.4, 0, 11.48]),
    "YSL": ([0, 0, 12, 9, 0, 0], [0, 0, 0, 0, 0, 0], [0, 12, 12, 12, 0, 0], [0, 6.5, 12, 12, 0, 0]),
}


def seat_label(S):
    """Which of the known profiles this seat's own actions match, or 0."""
    op = S.opn
    if S.tb_o >= 25 and S.tb >= 0.18 * S.tb_o and not (op >= 6 and S.o25 >= 0.9 * op):
        return "ANTON"                         # 3-bets one hand in five or more, with mixed open sizes
    if S.rfi_o >= 25 and S.limp >= 0.15 * S.rfi_o:
        return "POKE"                          # limps
    bn = S.bn
    if bn >= 8 and S.b15 >= 0.35 * bn:
        return "WBOT"                          # bets a sixth of the pot again and again
    if op >= 6:
        nolimp = S.limp <= 0.02 * S.rfi_o
        folds3 = S.f3_o < 4 or S.f3 >= 0.6 * S.f3_o      # the profiles below fold to 3-bets
        if S.o22 >= 0.8 * op and (bn < 5 or S.b50 + S.b100 >= 0.7 * bn):
            return "GG"                        # opens 2.2bb, bets half pot or pot
        if S.o28 >= 0.55 * op and bn >= 3 and S.b15 == 0 and S.bov == 0 and folds3:
            return "YSL"                       # opens 2.8bb, never bets tiny or over the pot
        if S.o25 >= 0.85 * op and nolimp and bn >= 5:
            if S.b33 >= 2 and S.b33 + S.b100 >= 0.8 * bn and S.bov == 0 and folds3:
                return "CPF"                   # opens 2.5bb, bets a third of the pot or the pot
            if S.o25 >= 0.95 * op and S.b33 == 0 and S.bov >= 0.25 * bn:
                return "ANKER"                 # opens 2.5bb, overbets, never bets a third
    return 0


def zbucket(x):
    if x < 0.42:
        return 0 if x < 0.24 else 1
    if x < 0.90:
        return 2 if x < 0.65 else 3
    return 4 if x < 1.30 else 5

WEAK_PAIR_MARGIN = 0.10 # extra equity a pair below top pair needs on flop and turn against such bets
_now = time.perf_counter

# ----------------------------------------------------------------- evaluator
PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
RANKS = "23456789TJQKA"
SUITS = "cdhs"


def _enc(cat, ks):
    v = cat
    ks = list(ks) + [0] * (5 - len(ks))
    for k in ks[:5]:
        v = v * 16 + k
    return v


def _straight_high(mask):
    m = (mask << 1) | ((mask >> 12) & 1)
    for top in range(13, 3, -1):
        if (m >> (top - 4)) & 31 == 31:
            return top - 1
    return -1


def _score_counts(counts):
    mask = 0
    for r in range(13):
        if counts[r]:
            mask |= 1 << r
    groups = sorted(((n, r) for r, n in enumerate(counts) if n), reverse=True)
    top_n, top_r = groups[0]
    if top_n == 4:
        kicker = max(r for r in range(13) if counts[r] and r != top_r)
        return _enc(7, (top_r, kicker))
    if top_n == 3 and len(groups) > 1 and groups[1][0] >= 2:
        return _enc(6, (top_r, groups[1][1]))
    sh = _straight_high(mask)
    if sh >= 0:
        return _enc(4, (sh,))
    singles = sorted((r for r in range(13) if counts[r] == 1), reverse=True)
    if top_n == 3:
        return _enc(3, [top_r] + singles[:2])
    if top_n == 2:
        pairs = sorted((r for r in range(13) if counts[r] == 2), reverse=True)
        if len(pairs) >= 2:
            rest = max(r for r in range(13) if counts[r] and r not in pairs[:2])
            return _enc(2, (pairs[0], pairs[1], rest))
        return _enc(1, [pairs[0]] + singles[:3])
    return _enc(0, singles[:5])


RANK = {}  # prime product of 5, 6 or 7 card ranks -> score ignoring flushes


def _gen(r, left, counts, prod):
    if r == 13:
        if left == 0:
            RANK[prod] = _score_counts(counts)
        return
    if (13 - r) * 4 < left:
        return
    p = PRIMES[r]
    for c in range(min(4, left) + 1):
        counts[r] = c
        _gen(r + 1, left - c, counts, prod * p ** c)
    counts[r] = 0


for _n in (5, 6, 7):
    _gen(0, _n, [0] * 13, 1)

FLUSH = {}
for _m in range(1 << 13):
    if bin(_m).count("1") >= 5:
        _sh = _straight_high(_m)
        if _sh >= 0:
            FLUSH[_m] = _enc(8, (_sh,))
        else:
            FLUSH[_m] = _enc(5, [r for r in range(12, -1, -1) if _m >> r & 1][:5])

# 4 of a 5-rank window present (open-ender or gutshot), wheel included.
DRAW4 = [False] * (1 << 13)
for _m in range(1 << 13):
    _mm = (_m << 1) | ((_m >> 12) & 1)
    for _lo in range(0, 10):
        if bin((_mm >> _lo) & 31).count("1") >= 4:
            DRAW4[_m] = True
            break

CP = [PRIMES[c >> 2] for c in range(52)]
CARD = {RANKS[r] + SUITS[s]: r * 4 + s for r in range(13) for s in range(4)}
DRAWB = 1 << 20          # ranking bonus for a draw: one hand category
TWO_PAIR = 2 << 20

# ------------------------------------------------------------ preflop tables
PF = json.loads('{"AA":[0.8482,0.6275,0.4405],"AKs":[0.6768,0.4113,0.2756],"AKo":[0.6677,0.3926,0.2475],"AQs":[0.6582,0.3976,0.2561],"AQo":[0.6406,0.3629,0.2257],"AJs":[0.6555,0.3882,0.2437],"AJo":[0.6448,0.3522,0.2108],"ATs":[0.6383,0.36,0.2388],"ATo":[0.6298,0.3367,0.2066],"A9s":[0.6319,0.3437,0.2051],"A9o":[0.5998,0.3176,0.1791],"A8s":[0.6289,0.3332,0.2032],"A8o":[0.592,0.2957,0.1587],"A7s":[0.6115,0.3183,0.195],"A7o":[0.5843,0.2875,0.1565],"A6s":[0.6062,0.3196,0.1907],"A6o":[0.5768,0.273,0.1403],"A5s":[0.5909,0.3064,0.1986],"A5o":[0.585,0.2838,0.155],"A4s":[0.5925,0.3184,0.1972],"A4o":[0.5648,0.268,0.1511],"A3s":[0.5793,0.2936,0.1925],"A3o":[0.5601,0.2609,0.1413],"A2s":[0.571,0.2962,0.174],"A2o":[0.5549,0.2501,0.1399],"KK":[0.8269,0.5935,0.3672],"KQs":[0.6404,0.381,0.2609],"KQo":[0.6063,0.3461,0.2193],"KJs":[0.6414,0.3798,0.2427],"KJo":[0.6022,0.33,0.2006],"KTs":[0.6199,0.3572,0.2173],"KTo":[0.5887,0.3143,0.1972],"K9s":[0.6093,0.3307,0.2067],"K9o":[0.5914,0.2869,0.1655],"K8s":[0.5727,0.3069,0.1944],"K8o":[0.5698,0.2748,0.1403],"K7s":[0.578,0.2973,0.1853],"K7o":[0.5437,0.274,0.1466],"K6s":[0.5671,0.2794,0.181],"K6o":[0.54,0.2545,0.1331],"K5s":[0.5572,0.2823,0.1696],"K5o":[0.5373,0.2436,0.1308],"K4s":[0.5382,0.2714,0.1629],"K4o":[0.5261,0.2273,0.1223],"K3s":[0.5317,0.2634,0.1682],"K3o":[0.5012,0.2241,0.1148],"K2s":[0.5278,0.2596,0.1652],"K2o":[0.5065,0.2212,0.1105],"QQ":[0.7932,0.5294,0.3304],"QJs":[0.6068,0.365,0.2305],"QJo":[0.5711,0.3183,0.1941],"QTs":[0.5995,0.3441,0.2299],"QTo":[0.559,0.303,0.1864],"Q9s":[0.5781,0.3138,0.195],"Q9o":[0.5507,0.2809,0.1552],"Q8s":[0.5613,0.297,0.1756],"Q8o":[0.5299,0.265,0.1388],"Q7s":[0.5443,0.2876,0.1546],"Q7o":[0.5129,0.2417,0.1201],"Q6s":[0.5273,0.2751,0.1597],"Q6o":[0.5225,0.2327,0.1152],"Q5s":[0.5253,0.2604,0.1438],"Q5o":[0.4894,0.229,0.1185],"Q4s":[0.5202,0.2523,0.1495],"Q4o":[0.499,0.2228,0.1126],"Q3s":[0.5002,0.2426,0.1529],"Q3o":[0.4826,0.2052,0.109],"Q2s":[0.5049,0.2453,0.1472],"Q2o":[0.476,0.1974,0.1058],"JJ":[0.7699,0.4798,0.2909],"JTs":[0.5707,0.3391,0.2231],"JTo":[0.5556,0.306,0.1905],"J9s":[0.5499,0.3028,0.1972],"J9o":[0.5292,0.275,0.1652],"J8s":[0.5363,0.3044,0.183],"J8o":[0.5187,0.2602,0.137],"J7s":[0.5222,0.2736,0.1553],"J7o":[0.5023,0.2325,0.1234],"J6s":[0.5022,0.2508,0.1518],"J6o":[0.4893,0.2102,0.113],"J5s":[0.498,0.2389,0.1467],"J5o":[0.4662,0.2102,0.1051],"J4s":[0.4858,0.2258,0.135],"J4o":[0.462,0.1944,0.0946],"J3s":[0.4771,0.2268,0.1346],"J3o":[0.4632,0.1893,0.1055],"J2s":[0.4846,0.2233,0.136],"J2o":[0.447,0.1913,0.0916],"TT":[0.7456,0.4511,0.2546],"T9s":[0.5407,0.3032,0.1966],"T9o":[0.5181,0.2851,0.1631],"T8s":[0.5234,0.2894,0.1693],"T8o":[0.4925,0.2474,0.1447],"T7s":[0.5074,0.279,0.1613],"T7o":[0.4707,0.2403,0.1268],"T6s":[0.4878,0.251,0.156],"T6o":[0.4586,0.2159,0.1092],"T5s":[0.4629,0.2238,0.1459],"T5o":[0.4407,0.1894,0.0996],"T4s":[0.4733,0.2202,0.1426],"T4o":[0.4381,0.1797,0.0966],"T3s":[0.4572,0.2288,0.1333],"T3o":[0.4326,0.1786,0.0937],"T2s":[0.4671,0.2142,0.1272],"T2o":[0.4178,0.1755,0.087],"99":[0.7183,0.4116,0.2241],"98s":[0.5116,0.2822,0.1779],"98o":[0.477,0.2563,0.1426],"97s":[0.4939,0.2743,0.1701],"97o":[0.468,0.2254,0.1284],"96s":[0.472,0.2467,0.1572],"96o":[0.4487,0.212,0.1115],"95s":[0.4502,0.2289,0.1433],"95o":[0.4146,0.1936,0.0941],"94s":[0.4375,0.2214,0.1307],"94o":[0.4006,0.1828,0.0873],"93s":[0.4233,0.2082,0.1221],"93o":[0.3906,0.173,0.0798],"92s":[0.4294,0.2004,0.1178],"92o":[0.3832,0.1588,0.0776],"88":[0.6848,0.3738,0.2067],"87s":[0.4794,0.2696,0.1677],"87o":[0.4482,0.237,0.131],"86s":[0.4608,0.2584,0.157],"86o":[0.436,0.2274,0.1116],"85s":[0.4303,0.2379,0.1455],"85o":[0.4114,0.2022,0.109],"84s":[0.4302,0.2149,0.1284],"84o":[0.3932,0.1644,0.0932],"83s":[0.3954,0.1998,0.1154],"83o":[0.373,0.1591,0.0747],"82s":[0.3938,0.1879,0.1198],"82o":[0.3782,0.1548,0.0791],"77":[0.6676,0.3474,0.1801],"76s":[0.4644,0.2434,0.1534],"76o":[0.4183,0.2206,0.1146],"75s":[0.4292,0.2403,0.1505],"75o":[0.4055,0.2018,0.1094],"74s":[0.4248,0.2146,0.1376],"74o":[0.3902,0.1756,0.1032],"73s":[0.3927,0.2001,0.1234],"73o":[0.3673,0.1587,0.0867],"72s":[0.3886,0.1799,0.1154],"72o":[0.3445,0.1388,0.0725],"66":[0.6251,0.3153,0.1645],"65s":[0.4249,0.2415,0.1584],"65o":[0.3967,0.1923,0.118],"64s":[0.4158,0.2152,0.1388],"64o":[0.3828,0.1872,0.1042],"63s":[0.3985,0.2008,0.1269],"63o":[0.373,0.1672,0.0873],"62s":[0.3817,0.1828,0.1166],"62o":[0.3407,0.1531,0.0781],"55":[0.5911,0.2905,0.1589],"54s":[0.415,0.2327,0.1462],"54o":[0.3806,0.1761,0.1178],"53s":[0.3987,0.2161,0.1405],"53o":[0.3817,0.17,0.1008],"52s":[0.3796,0.1918,0.1254],"52o":[0.35,0.1533,0.0869],"44":[0.5689,0.2531,0.1518],"43s":[0.3912,0.2079,0.1288],"43o":[0.3438,0.1637,0.0891],"42s":[0.3648,0.1909,0.123],"42o":[0.321,0.1517,0.0891],"33":[0.5443,0.2274,0.1451],"32s":[0.3584,0.1822,0.1146],"32o":[0.3327,0.147,0.077],"22":[0.4976,0.2162,0.1374]}')
_RE = json.loads('{"buckets":[0.015,0.025,0.04,0.06,0.09,0.13,0.18,0.25,0.35,0.5,0.7,1.0],"eq":{"AA":[794,801,827,825,840,847,851,854,853,852,850,852],"AKs":[360,411,445,499,573,614,638,654,664,670,670,670],"AQs":[301,380,364,435,502,559,597,621,637,650,657,662],"AJs":[287,351,343,403,438,511,561,593,616,631,643,654],"ATs":[291,322,326,381,398,463,522,567,596,616,630,646],"A9s":[282,297,298,358,369,426,475,522,563,588,607,628],"A8s":[284,300,302,348,358,412,451,496,537,574,596,619],"A7s":[286,302,303,338,350,404,439,476,517,555,584,610],"A6s":[284,299,301,336,348,399,430,463,500,540,572,599],"A5s":[298,313,315,348,361,408,435,463,499,536,566,599],"A4s":[295,310,311,345,357,406,432,457,490,527,557,590],"A3s":[290,307,308,342,354,403,430,455,485,521,549,582],"A2s":[287,304,304,339,351,401,428,452,482,516,544,574],"AKo":[326,379,416,473,551,596,621,637,648,653,653,653],"KK":[541,668,682,716,720,742,750,759,773,794,811,824],"KQs":[242,351,342,393,410,453,485,511,542,583,614,634],"KJs":[234,321,326,361,386,408,453,487,523,567,600,625],"KTs":[242,294,309,346,375,381,419,464,506,553,588,618],"K9s":[234,270,277,322,350,362,387,424,474,526,565,600],"K8s":[224,263,274,303,337,345,373,402,444,503,545,583],"K7s":[225,265,276,294,332,345,373,395,431,488,535,575],"K6s":[228,268,278,297,333,342,370,395,423,475,524,566],"K5s":[227,267,277,297,332,341,368,386,417,464,511,558],"K4s":[223,264,272,293,329,338,364,385,410,456,502,549],"K3s":[219,261,270,290,326,335,363,383,406,451,495,541],"K2s":[216,257,265,285,322,331,359,379,406,447,489,532],"AQo":[262,345,328,403,476,536,576,601,618,631,639,644],"KQo":[203,318,306,359,378,425,459,486,518,562,593,614],"QQ":[285,535,562,620,647,669,688,706,724,748,773,799],"QJs":[190,300,339,358,362,376,407,443,477,520,564,602],"QTs":[199,270,324,357,359,368,387,421,460,507,552,595],"Q9s":[192,247,294,333,340,352,366,390,429,481,529,577],"Q8s":[183,242,286,313,327,340,355,376,406,458,509,560],"Q7s":[173,235,279,294,311,328,344,361,389,434,488,543],"Q6s":[176,238,282,298,315,328,344,367,391,426,480,536],"Q5s":[176,238,282,298,314,328,342,358,386,418,468,528],"Q4s":[172,234,277,294,310,324,338,357,379,411,459,519],"Q3s":[169,231,275,291,308,321,337,354,376,408,451,510],"Q2s":[164,227,271,288,304,317,333,350,375,403,445,502],"AJo":[248,315,306,369,407,484,537,571,596,612,624,636],"KJo":[193,285,288,323,351,376,423,459,497,543,579,606],"QJo":[147,262,303,323,325,341,375,412,447,494,540,581],"JJ":[190,402,483,551,579,608,635,661,687,710,738,775],"JTs":[196,249,317,351,355,363,379,402,441,478,521,575],"J9s":[193,228,289,329,338,353,362,379,412,452,499,556],"J8s":[186,225,283,309,326,341,354,368,393,429,479,540],"J7s":[176,217,274,290,308,329,342,355,378,407,459,523],"J6s":[163,206,264,282,300,316,330,348,369,391,440,506],"J5s":[167,210,267,284,302,318,330,342,366,389,431,500],"J4s":[164,207,264,281,298,314,327,342,360,383,423,491],"J3s":[160,203,260,277,294,310,325,338,357,379,417,482],"J2s":[156,199,256,274,291,307,322,335,356,375,411,474],"ATo":[252,286,289,347,363,433,496,544,575,595,611,627],"KTo":[200,254,270,310,339,345,387,434,478,528,566,597],"QTo":[158,232,286,323,323,333,353,389,430,480,528,573],"JTo":[157,211,282,318,320,328,344,369,410,449,495,553],"TT":[187,268,405,495,526,556,587,619,650,678,708,750],"T9s":[207,210,283,334,349,359,367,383,403,437,479,540],"T8s":[203,210,278,315,336,348,360,372,388,415,459,523],"T7s":[194,201,270,295,320,335,348,359,374,397,440,507],"T6s":[183,193,261,288,311,322,335,352,364,383,422,490],"T5s":[169,180,249,278,300,311,323,333,350,370,404,472],"T4s":[169,179,248,276,299,311,322,336,347,367,399,465],"T3s":[165,176,245,273,296,307,320,332,343,364,394,457],"T2s":[160,172,240,269,292,304,317,328,342,359,388,448],"A9o":[244,259,259,323,332,392,446,495,539,566,585,608],"K9o":[192,229,236,284,313,325,352,392,445,500,541,578],"Q9o":[150,207,256,297,304,316,330,355,397,452,503,554],"J9o":[151,187,251,293,301,317,326,344,378,421,471,532],"T9o":[167,170,245,300,314,324,332,348,370,406,450,515],"99":[190,193,321,439,478,512,540,574,607,641,674,721],"98s":[213,204,266,311,339,357,367,379,389,408,447,508],"97s":[208,199,264,295,325,346,356,367,377,393,429,491],"96s":[196,190,254,287,315,334,343,360,368,381,411,474],"95s":[183,179,243,277,305,323,331,341,353,368,395,457],"94s":[166,162,228,264,292,310,317,330,337,353,379,439],"93s":[165,161,227,262,291,309,319,330,336,352,376,433],"92s":[162,159,223,259,288,306,315,326,335,348,370,424],"A8o":[245,262,263,311,320,377,419,468,511,550,574,599],"K8o":[184,225,235,265,300,308,338,368,413,475,520,560],"Q8o":[140,202,248,276,291,303,319,341,373,428,482,536],"J8o":[145,185,244,272,289,304,318,333,358,397,450,515],"T8o":[162,168,239,280,300,312,324,337,353,382,429,497],"98o":[175,164,228,275,304,322,331,345,354,375,417,481],"88":[192,189,302,387,442,481,511,544,573,607,642,692],"87s":[221,212,272,294,330,352,366,376,386,396,423,479],"86s":[209,204,265,287,322,341,354,369,378,384,406,463],"85s":[197,195,255,278,312,331,343,351,363,372,392,446],"84s":[182,180,240,264,298,317,329,340,347,356,375,427],"83s":[165,164,225,249,285,304,317,327,333,342,360,409],"82s":[163,161,225,249,284,303,316,325,334,340,357,403],"A7o":[246,263,264,301,313,370,408,447,491,530,560,588],"K7o":[186,228,237,256,295,307,337,360,398,459,508,552],"Q7o":[129,195,241,257,274,292,307,326,355,403,460,518],"J7o":[136,177,237,252,271,292,306,319,342,374,428,497],"T7o":[155,162,231,259,283,298,312,323,338,362,409,479],"97o":[168,159,226,259,289,311,321,333,342,359,397,463],"87o":[182,172,235,258,295,317,331,341,352,361,391,450],"77":[193,190,303,338,405,454,487,518,546,575,611,662],"76s":[223,218,279,288,325,348,361,375,384,390,405,454],"75s":[211,209,268,279,315,337,350,357,370,379,392,437],"74s":[194,193,253,264,302,325,337,347,354,363,376,419],"73s":[178,177,239,251,288,312,325,334,340,349,362,401],"72s":[161,160,223,236,274,297,311,319,329,335,345,382],"A6o":[244,261,262,298,310,363,396,431,471,513,547,577],"K6o":[186,227,237,258,295,304,333,360,390,445,497,542],"Q6o":[133,197,244,261,277,290,306,330,355,393,450,510],"J6o":[123,167,227,245,263,279,293,312,333,356,408,478],"T6o":[141,150,222,251,274,285,298,315,328,348,389,461],"96o":[155,149,216,251,280,298,307,324,332,345,378,445],"86o":[170,165,227,250,286,305,319,334,342,349,372,432],"76o":[184,178,240,251,289,312,326,340,349,356,371,423],"66":[195,193,304,326,393,433,466,500,526,550,581,633],"65s":[225,221,280,287,324,344,358,368,379,386,396,431],"64s":[209,207,267,275,312,333,345,358,364,371,380,413],"63s":[191,190,251,261,298,319,333,345,350,357,365,395],"62s":[176,174,236,247,285,306,320,332,339,343,349,377],"A5o":[259,276,276,311,323,374,403,433,470,509,541,577],"K5o":[187,229,237,258,296,304,332,351,383,434,483,533],"Q5o":[133,198,243,261,277,290,305,321,350,384,437,501],"J5o":[126,168,227,246,263,280,293,305,330,354,399,472],"T5o":[127,137,208,239,262,273,285,295,313,334,370,442],"95o":[141,137,203,239,269,286,295,304,317,332,361,427],"85o":[156,153,215,240,274,293,306,314,327,336,357,414],"75o":[171,169,230,242,279,302,315,322,335,343,358,405],"65o":[187,184,244,252,289,309,322,334,345,352,361,399],"55":[193,192,302,325,391,424,452,478,507,530,554,603],"54s":[222,222,280,289,325,343,355,364,373,382,390,415],"53s":[205,205,265,276,312,330,343,351,359,368,376,397],"52s":[188,189,251,262,299,317,331,337,349,354,360,379],"A4o":[256,274,274,309,321,371,399,426,461,500,532,567],"K4o":[183,226,233,255,292,301,328,351,376,425,474,523],"Q4o":[129,195,240,257,274,287,301,321,344,377,428,491],"J4o":[120,165,225,243,260,277,290,305,324,348,390,462],"T4o":[127,137,208,239,261,273,284,298,309,331,364,435],"94o":[123,119,186,225,254,272,279,292,298,315,342,407],"84o":[139,137,200,225,261,280,292,303,310,319,339,395],"74o":[154,153,215,227,266,288,301,311,318,327,340,386],"64o":[169,168,229,239,276,296,309,323,328,336,345,380],"54o":[182,183,243,253,290,309,320,329,338,347,356,382],"44":[190,189,299,322,387,419,445,465,487,509,530,570],"43s":[201,202,261,272,308,327,340,348,353,362,369,386],"42s":[184,186,246,258,295,314,327,335,342,348,354,368],"A3o":[252,270,269,305,317,368,397,423,455,493,523,558],"K3o":[178,222,229,251,288,297,326,348,372,419,465,514],"Q3o":[124,191,236,253,269,283,299,318,340,373,419,482],"J3o":[116,161,220,239,256,273,287,301,320,344,383,453],"T3o":[124,134,205,236,258,269,283,294,306,327,359,426],"93o":[124,120,186,224,253,271,280,292,298,314,340,400],"83o":[122,120,185,211,246,266,279,288,295,304,323,375],"73o":[136,135,198,212,251,274,288,296,303,312,325,366],"63o":[151,150,213,225,262,282,296,308,314,321,329,361],"53o":[165,166,227,239,276,295,308,315,324,333,341,363],"43o":[161,163,224,236,273,292,305,313,317,327,334,352],"33":[186,185,295,317,382,414,439,457,470,489,507,537],"32s":[180,182,242,254,291,310,324,331,337,343,349,360],"A2o":[249,267,265,302,313,365,393,420,451,488,517,550],"K2o":[174,217,224,246,283,293,322,344,371,414,458,505],"Q2o":[120,186,231,249,266,279,296,314,339,369,413,473],"J2o":[112,157,216,235,252,269,284,297,319,339,376,444],"T2o":[119,129,200,232,254,265,279,290,305,322,352,417],"92o":[120,116,183,221,250,268,277,288,297,310,334,391],"82o":[122,120,185,210,247,266,279,288,297,303,320,368],"72o":[118,117,182,196,235,259,274,281,291,296,307,346],"62o":[134,132,196,209,247,268,282,294,302,305,312,341],"52o":[147,149,212,225,262,281,294,301,312,317,323,343],"42o":[143,145,207,221,258,277,290,298,305,312,317,332],"32o":[139,141,203,216,255,274,288,294,300,306,312,323],"22":[180,180,289,312,376,408,433,448,461,474,486,503]},"starter":{"AA":868,"AKs":681,"AQs":628,"AJs":610,"ATs":592,"A9s":562,"A8s":543,"A7s":526,"A6s":510,"A5s":507,"A4s":497,"A3s":489,"A2s":482,"AKo":666,"KK":767,"KQs":528,"KJs":510,"KTs":493,"K9s":462,"K8s":435,"K7s":420,"K6s":405,"K5s":391,"K4s":380,"K3s":372,"K2s":364,"AQo":608,"KQo":503,"QQ":700,"QJs":434,"QTs":432,"Q9s":413,"Q8s":398,"Q7s":384,"Q6s":383,"Q5s":376,"Q4s":368,"Q3s":361,"Q2s":354,"AJo":589,"KJo":484,"QJo":402,"JJ":681,"JTs":439,"J9s":420,"J8s":406,"J7s":391,"J6s":377,"J5s":373,"J4s":366,"J3s":359,"J2s":351,"ATo":570,"KTo":465,"QTo":400,"JTo":408,"TT":662,"T9s":428,"T8s":414,"T7s":399,"T6s":385,"T5s":368,"T4s":364,"T3s":356,"T2s":349,"A9o":538,"K9o":432,"Q9o":380,"J9o":387,"T9o":396,"99":635,"98s":417,"97s":405,"96s":390,"95s":374,"94s":356,"93s":352,"92s":345,"A8o":518,"K8o":404,"Q8o":365,"J8o":372,"T8o":380,"98o":385,"88":611,"87s":410,"86s":397,"85s":380,"84s":362,"83s":345,"82s":340,"A7o":500,"K7o":387,"Q7o":349,"J7o":357,"T7o":365,"97o":371,"87o":377,"77":589,"76s":403,"75s":386,"74s":369,"73s":351,"72s":333,"A6o":482,"K6o":371,"Q6o":347,"J6o":342,"T6o":350,"96o":356,"86o":362,"76o":369,"66":568,"65s":392,"64s":375,"63s":357,"62s":339,"A5o":480,"K5o":356,"Q5o":340,"J5o":338,"T5o":332,"95o":338,"85o":345,"75o":351,"65o":358,"55":545,"54s":382,"53s":364,"52s":346,"A4o":468,"K4o":345,"Q4o":333,"J4o":330,"T4o":327,"94o":319,"84o":326,"74o":333,"64o":339,"54o":347,"44":519,"43s":356,"42s":338,"A3o":460,"K3o":336,"Q3o":324,"J3o":322,"T3o":320,"93o":314,"83o":307,"73o":314,"63o":320,"53o":328,"43o":320,"33":493,"32s":331,"A2o":452,"K2o":327,"Q2o":317,"J2o":314,"T2o":312,"92o":307,"82o":302,"72o":294,"62o":301,"52o":309,"42o":301,"32o":292,"22":466}}')
RE_B = _RE["buckets"]
RE = _RE["eq"]
ES = _RE["starter"]      # equity (per mille) against any pair / ace / king


def req(cls, f):
    """Equity (0..1) of hand class cls all-in preflop against the top fraction f of hands."""
    row = RE[cls]
    if f <= RE_B[0]:
        return row[0] / 1000.0
    for i in range(1, len(RE_B)):
        if f <= RE_B[i]:
            lo = RE_B[i - 1]
            t = (f - lo) / (RE_B[i] - lo)
            return (row[i - 1] + t * (row[i] - row[i - 1])) / 1000.0
    return row[-1] / 1000.0


def _cls(a, b):
    ra, rb = a >> 2, b >> 2
    if ra < rb:
        ra, rb = rb, ra
    if ra == rb:
        return RANKS[ra] * 2
    return RANKS[ra] + RANKS[rb] + ("s" if (a & 3) == (b & 3) else "o")


CLS = {}
_all = []
for _a in range(52):
    for _b in range(_a + 1, 52):
        _c = _cls(_a, _b)
        CLS[(_a, _b)] = CLS[(_b, _a)] = _c
        _e = PF[_c]
        _all.append((_e[0] + _e[1] * 1.6, _a, _b))
_all.sort(reverse=True)
COMBOS = [(_a, _b) for _s, _a, _b in _all]   # strongest first
NC = len(COMBOS)
# The starter kit's example bot raises every time it holds a pair, an ace or a
# king and gives up everything else to any bet above two big blinds.
STARTER_S = [(_a, _b) for _a, _b in COMBOS if (_a >> 2) == (_b >> 2) or (_a >> 2) >= 11 or (_b >> 2) >= 11]
STARTER_W = [(_a, _b) for _a, _b in COMBOS if not ((_a >> 2) == (_b >> 2) or (_a >> 2) >= 11 or (_b >> 2) >= 11)]


def expand(spec):
    """'66+,A5s-A2s,KTs+,AJo+' -> set of hand classes."""
    out = set()
    for tok in spec.replace(" ", "").split(","):
        if not tok:
            continue
        if "-" in tok:
            hi, lo = tok.split("-")
            if len(hi) == 2:
                a, b = RANKS.index(hi[0]), RANKS.index(lo[0])
                for r in range(min(a, b), max(a, b) + 1):
                    out.add(RANKS[r] * 2)
            else:
                a, b = RANKS.index(hi[1]), RANKS.index(lo[1])
                for r in range(min(a, b), max(a, b) + 1):
                    out.add(hi[0] + RANKS[r] + hi[2])
        elif tok.endswith("+"):
            t = tok[:-1]
            if len(t) == 2:
                for r in range(RANKS.index(t[0]), 13):
                    out.add(RANKS[r] * 2)
            else:
                for r in range(RANKS.index(t[1]), RANKS.index(t[0])):
                    out.add(t[0] + RANKS[r] + t[2])
        else:
            out.add(tok)
    return out


# Open-raise level: 0 = UTG (8-handed) ... 5 = button, 6 = extra-wide steals.
_LEVELS = [
    "66+,ATs+,A5s-A4s,KTs+,QTs+,JTs,T9s,AJo+,KQo",
    "55,A9s,A8s,A3s,K9s,Q9s,98s,KJo",
    "44,33,22,A7s,A6s,A2s,J9s,87s,76s,ATo,QJo",
    "K8s,K7s,T8s,65s,54s,KTo,QTo,JTo",
    "K6s,K5s,K4s,Q8s,J8s,97s,86s,75s,A9o,A8o",
    "K3s,K2s,Q7s-Q4s,J7s,T7s,96s,85s,64s,53s,43s,A7o-A2o,K9o,K8o,Q9o,J9o,T9o,98o",
    "Q3s,Q2s,J6s-J4s,T6s,95s,74s,63s,52s,K7o-K5o,Q8o,J8o,T8o,87o,97o",
]
LEVEL = {}
for _i, _spec in enumerate(_LEVELS):
    for _c in expand(_spec):
        LEVEL.setdefault(_c, _i)

V3_CORE = expand("QQ+,AKs,AKo")
V3_LOOSE = expand("JJ,TT,AQs")
V3_MANIAC = expand("99,88,AJs,KQs,AQo")
BLUFF3 = expand("A5s-A2s,KTs,K9s,QTs,Q9s,J9s,AJo,ATo,KQo,KJo")
PAIRS = expand("22+")
FLAT_SUITED = expand("AQs,AJs,ATs,KQs,KJs,QJs,JTs,T9s,98s,87s,76s")
FLAT_SUITED_IP = expand("KTs,QTs,A9s,A5s-A2s,65s,54s,J9s,T8s,97s")
FLAT_OFF = expand("AQo,KQo")
BB_OFF = expand("AJo,ATo,KJo,QJo,KTo,QTo,JTo,A9o")
CALL3 = expand("JJ,TT,AQs,AKs,AKo,QQ")

# Calling-a-shove order: cumulative fraction of all hands, best first.
_SH_TOP = ["AA", "KK", "QQ", "AKs", "JJ", "AKo", "TT", "AQs", "99", "AQo", "AJs", "88", "KQs",
           "ATs", "77", "AJo", "KJs", "66", "ATo", "KQo", "A9s", "55"]
_rest = sorted((c for c in PF if c not in _SH_TOP), key=lambda c: -(PF[c][0] + PF[c][1]))
SHOVE = {}
_cum = 0
for _c in _SH_TOP + _rest:
    _cum += 6 if len(_c) == 2 else (4 if _c[2] == "s" else 12)
    SHOVE[_c] = _cum / 1326.0


# ------------------------------------------------------------ opponent stats
class St:
    __slots__ = ("hands", "vpip", "pfr", "tb_o", "tb", "f3_o", "f3", "shove",
                 "bet_o", "bet", "fb_o", "fb_f", "fb_r", "sd_agg", "sd_air", "st_o", "st_f", "fo", "ff", "ro", "rf",
                 "limp", "rfi_o", "lf_o", "lf_f", "sd_r", "sd_ok", "bx_n", "bx_s", "cb_o", "cb", "sr_o", "sr_f",
                 "zo", "zf", "zn", "zs", "opn", "o22", "o25", "o28", "bn", "b15", "b33", "b50", "b100", "bov", "lab", "f4_o", "f4")

    def __init__(self):
        for k in self.__slots__:
            setattr(self, k, 0)
        self.fo = [0, 0, 0, 0, 0]   # faced a bet of 35%+ of the pot, by line (see line_cat)
        self.ff = [0, 0, 0, 0, 0]   # ... and folded
        self.zo = [0, 0, 0, 0, 0, 0]   # his bet of this size bucket was raised ...
        self.zf = [0, 0, 0, 0, 0, 0]   # ... and he folded
        self.zn = [0, 0, 0, 0, 0, 0]   # hands shown down after a bet of this size bucket ...
        self.zs = [0, 0, 0, 0, 0, 0]   # ... that were top pair or better (or a strong draw) when he bet

    def limp_folder(self):
        """Limps, then gives up every time someone raises."""
        return self.lf_o >= 3 and self.lf_f >= 0.9 * self.lf_o

    def limp_suspect(self):
        """Limps so often that it is worth raising him to find out."""
        return self.lf_o == self.lf_f and self.rfi_o >= 8 and self.limp >= 0.45 * self.rfi_o

    def starter(self):
        """Plays like the starter kit's example bot (see STARTER_S)."""
        return (self.lf_o >= 3 and self.lf_f >= 0.9 * self.lf_o and self.hands >= 15
                and self.limp >= 0.35 * self.rfi_o and self.sd_r == self.sd_ok
                and self.pfr >= 0.2 * self.hands and self.f3 == 0)

    # Priors are the field averages measured on the practice rounds.
    def r_vpip(self):
        return (self.vpip + 0.25 * 12) / (self.hands + 12)

    def r_pfr(self):
        return (self.pfr + 0.16 * 12) / (self.hands + 12)

    def r_3bet(self):
        return (self.tb + 0.045 * 20) / (self.tb_o + 20)

    def r_f3(self):
        return (self.f3 + 0.58 * 3) / (self.f3_o + 3)

    def r_sf(self):
        """How often he gives up his blind to a late-position raise."""
        return (self.st_f + 0.7 * 6) / (self.st_o + 6)

    def r_shove(self):
        return (self.shove + 0.2) / (self.hands + 40)

    def r_fold(self):
        return (self.fb_f + 0.48 * 8) / (self.fb_o + 8)

    def r_cb(self):
        """How often he bets the flop after raising preflop (field: about 70%)."""
        return (self.cb + 0.70 * 6) / (self.cb_o + 6)

    def r_smallraise(self, river):
        """How often he gives up when his own small bet (under 40% of the pot) is raised.
        Field: 71% on the flop, 72% on the turn, 63% on the river (279 real cases)."""
        return (self.sr_f + 5 * (0.63 if river else 0.70)) / (self.sr_o + 5)

    def r_bx(self):
        """His usual bet size, in pots."""
        return (self.bx_s + 0.65 * 4) / (self.bx_n + 4)

    def r_bet(self):
        return (self.bet + 0.40 * 10) / (self.bet_o + 10)

    def r_raise(self):
        return (self.fb_r + 0.12 * 10) / (self.fb_o + 10)

    def r_air(self):
        return min(0.6, 1.3 * (self.sd_air + 0.14 * 6) / (self.sd_agg + 6))


_PREV = {"flop": "preflop", "turn": "flop", "river": "turn"}


def line_cat(s, street, agg_by, callers_by, checked):
    """Where seat s stands when someone bets on `street`:
    0 led into (he made the last raise or bet of the previous street and has not checked),
    1 gave up (same, but he checked), 2 called a bet on the previous street,
    3 the previous street was checked through, 4 anything else (a preflop caller on the flop)."""
    prev = _PREV.get(street)
    if s == agg_by.get(prev, -1):
        return 1 if s in checked else 0
    if street != "flop":
        if s in callers_by.get(prev, ()):
            return 2
        if prev not in agg_by:
            return 3
    return 4


# Field, measured on the practice hands: how often a player folds to the first bet of a
# street, by line, as (heads-up, multiway) for flop / turn / river.
FOLD_CAT = (
    ((0.29, 0.33), (0.17, 0.25), (0.21, 0.25)),   # 0 led into
    ((0.70, 0.75), (0.71, 0.75), (0.70, 0.75)),   # 1 gave up
    ((0.45, 0.60), (0.33, 0.55), (0.39, 0.55)),   # 2 called the previous street
    ((0.55, 0.80), (0.58, 0.79), (0.64, 0.88)),   # 3 previous street checked through
    ((0.57, 0.69), (0.45, 0.60), (0.50, 0.60)),   # 4 other
)
FOLD_LIMPED = (0.55, 0.86)                         # flop of an unraised pot
# A bet tells how strong its author is only relative to his own habit: (value share, bluff
# weight) multipliers for a bet smaller than usual, usual, bigger than usual.
SIZE_MULT = ((1.7, 3.5), (1.35, 2.2), (0.5, 0.35))
WIDE_CALLS = False      # defend the big blind and flat in position more widely


def size_class(S, x):
    m = S.r_bx()
    if x >= 0.8 and x >= 1.3 * m:
        return 2
    return 0 if x <= 0.8 * m else 1


def fold_prob(S, cat, si, multi, limped, x, is_raise):
    """Probability that the opponent with stats S folds to a bet of x pots (or to a raise):
    his own measured frequency in this line, shrunk towards the field's, scaled by how
    much he folds overall."""
    if is_raise:
        p = (S.rf + 6 * 0.28) / (S.ro + 6)
        if x < 0.4:
            p *= 0.35
        return 0.02 if p < 0.02 else (0.9 if p > 0.9 else p)
    k = S.r_fold() / 0.48
    k = 0.5 if k < 0.5 else (1.7 if k > 1.7 else k)
    prior = (FOLD_LIMPED[multi] if (limped and si == 0 and cat == 4) else FOLD_CAT[cat][si][multi]) * k
    if prior > 0.95:
        prior = 0.95
    p = (S.ff[cat] + 5 * prior) / (S.fo[cat] + 5)
    if x < 0.35:
        p *= 0.6
    elif x < 0.7:
        p *= 0.93
    elif x <= 1.1:
        p *= 1.15
    elif x <= 2.5:
        p *= 1.2
    else:
        p *= 1.3
    return 0.02 if p < 0.02 else (0.93 if p > 0.93 else p)


CHECK = {"action": "check"}
FOLD = {"action": "fold"}
CALL = {"action": "call"}


# ------------------------------------------------------------------- agent
class Agent:
    def __init__(self):
        self.rng = random.Random()
        self.st = [St() for _ in range(10)]
        self.used = 0.0
        self.tot = []          # chips won so far by every seat
        self.start_stack = 2000
        self.risk = 0.0
        self.used_mc = 0.0     # time spent inside the simulations
        self.n_mc = 0
        self.n_dec = 0         # decisions asked of us
        self.total_hands = 1000
        self.hands_seen = 0
        self.errors = 0
        self.cap = 200
        self.zcur = ()
        self.zweak = False
        self.me_seat = -1

    def on_table_start(self, info):
        self.total_hands = info.get("hands", 1000) or 1000
        self.start_stack = info.get("starting_stack", 2000) or 2000
        self.tot = [0.0] * (info.get("num_players", 0) or 0)
        self.me_seat = info.get("seat", -1)

    # ------------------------------------------------------------- learning
    def on_hand_end(self, summary):
        t0 = _now()
        try:
            self._learn(summary)
        except Exception:
            if DEBUG:
                import traceback
                traceback.print_exc()
        self.used += _now() - t0
        self.hands_seen += 1
        if (self.hands_seen & 63) == 0:
            gc.collect(0)

    def _learn(self, summary):
        hist = summary.get("history") or []
        st = self.st
        street = "preflop"
        bets = {}
        cur = 0
        pot = 0
        raises = 0
        first_raiser = -1
        acted = set()
        faced3 = set()
        vp = set()
        pr = set()
        agg_post = set()
        seats = set()
        n = len(summary.get("stacks") or ()) or 8
        sbs = bbs = -1
        last_x = 0.0
        last_raise = False
        limped = set()
        lf_seen = set()
        steal = False          # a late-position open with nobody else in yet
        others_in = 0
        agg_by = {}            # street -> seat that made its last bet or raise
        callers_by = {}        # street -> seats that called on it
        checked = set()        # seats that checked on the current street
        first_bet = None       # (seat, size in pots) of the first bet of the current street
        small_raised = -1      # seat whose small bet has just been raised
        zraised = None         # (seat, size bucket) of a first bet that has just been raised
        bbv = 20
        tb_seat = -1           # seat that made the 3-bet
        faced4 = False
        betlog = []            # (seat, street, size bucket) of every first bet of a street
        for h in hist:
            s = h["seat"]
            a = h["action"]
            amt = h.get("amount") or 0
            seats.add(s)
            if a == "small_blind":
                sbs = s
            elif a == "big_blind":
                bbs = s
                if amt > 0:
                    bbv = amt
            if h["street"] != street:
                street = h["street"]
                bets = {}
                cur = 0
                checked = set()
                first_bet = None
                small_raised = -1
                zraised = None
            if a == "small_blind" or a == "big_blind":
                bets[s] = amt
                if amt > cur:
                    cur = amt
                pot += amt
                continue
            S = st[s]
            mine = bets.get(s, 0)
            if street == "preflop":
                if s in limped and cur - mine > 40 and s not in lf_seen:
                    lf_seen.add(s)
                    S.lf_o += 1
                    if a == "fold":
                        S.lf_f += 1
                if s not in acted:
                    acted.add(s)
                    if raises == 0:
                        S.rfi_o += 1
                        if a == "call":
                            S.limp += 1
                            limped.add(s)
                        elif a == "raise" and not limped:
                            S.opn += 1
                            ob = amt / float(bbv)
                            if 2.14 < ob < 2.26:
                                S.o22 += 1
                            elif 2.44 < ob < 2.56:
                                S.o25 += 1
                            elif 2.74 < ob < 2.86:
                                S.o28 += 1
                    if raises == 1:
                        S.tb_o += 1
                        if a == "raise":
                            S.tb += 1
                        if steal and others_in == 0 and (s == sbs or s == bbs):
                            S.st_o += 1
                            if a == "fold":
                                S.st_f += 1
                    elif raises == 0 and a == "raise" and others_in == 0 and sbs >= 0:
                        steal = ((sbs - s) % n) <= 2          # cutoff, button or small blind
                    if a != "fold" and not (raises == 0 and a == "raise"):
                        if s != sbs and s != bbs:
                            others_in += 1
                elif s == first_raiser and raises == 2 and s not in faced3:
                    faced3.add(s)
                    S.f3_o += 1
                    if a == "fold":
                        S.f3 += 1
                elif s == tb_seat and raises == 3 and not faced4:
                    faced4 = True              # he 3-bet and now faces a 4-bet
                    S.f4_o += 1
                    if a == "fold":
                        S.f4 += 1
                if a == "raise":
                    pr.add(s)
                    vp.add(s)
                    if raises == 0:
                        first_raiser = s
                    elif raises == 1:
                        tb_seat = s
                    raises += 1
                    if amt >= 800:
                        S.shove += 1
                elif a == "call":
                    vp.add(s)
            else:
                if s == small_raised:
                    small_raised = -1
                    S.sr_o += 1
                    if a == "fold":
                        S.sr_f += 1
                if zraised is not None and s == zraised[0]:
                    S.zo[zraised[1]] += 1
                    if a == "fold":
                        S.zf[zraised[1]] += 1
                    zraised = None
                if cur > mine:
                    S.fb_o += 1
                    if a == "fold":
                        S.fb_f += 1
                    elif a == "raise":
                        S.fb_r += 1
                    if last_raise:
                        S.ro += 1
                        if a == "fold":
                            S.rf += 1
                    elif last_x >= 0.35:
                        c = line_cat(s, street, agg_by, callers_by, checked)
                        S.fo[c] += 1
                        if a == "fold":
                            S.ff[c] += 1
                else:
                    S.bet_o += 1
                    if street == "flop" and s == agg_by.get("preflop", -1) and s not in checked:
                        S.cb_o += 1
                        if a == "raise":
                            S.cb += 1
                    if a == "raise":
                        S.bet += 1
                        S.bx_n += 1
                        S.bx_s += amt / float(pot or 1)
                    elif a == "check":
                        checked.add(s)
                if a == "raise":
                    agg_post.add(s)
            if a == "raise":
                if street != "preflop":
                    last_raise = cur > 0
                    last_x = (amt - cur) / float(pot + cur - mine) if cur > 0 else amt / float(pot or 1)
                    if cur == 0:
                        first_bet = (s, last_x)
                        betlog.append((s, street, zbucket(last_x)))
                        S.bn += 1
                        if last_x <= 0.20:
                            S.b15 += 1
                        elif 0.30 <= last_x <= 0.36:
                            S.b33 += 1
                        elif 0.46 <= last_x <= 0.53:
                            S.b50 += 1
                        elif 0.95 <= last_x <= 1.05:
                            S.b100 += 1
                        elif last_x >= 1.06:
                            S.bov += 1
                    elif first_bet is not None and s != first_bet[0]:
                        if first_bet[1] < 0.4:
                            small_raised = first_bet[0]
                        zraised = (first_bet[0], zbucket(first_bet[1]))
                        first_bet = None
                pot += amt - mine
                bets[s] = amt
                cur = amt
                agg_by[street] = s
            elif a == "call":
                pot += amt
                bets[s] = mine + amt
                callers_by.setdefault(street, set()).add(s)
        for s in range(n):
            S = st[s]
            S.hands += 1
            if s in vp:
                S.vpip += 1
            if s in pr:
                S.pfr += 1
        shown = summary.get("shown")
        if shown:
            for k, cards in shown.items():
                if int(k) in pr:
                    S = st[int(k)]
                    S.sd_r += 1
                    r0 = CARD[cards[0]] >> 2
                    r1 = CARD[cards[1]] >> 2
                    if r0 == r1 or r0 >= 11 or r1 >= 11:
                        S.sd_ok += 1
        stx = summary.get("stacks")
        if stx:
            if len(self.tot) != len(stx):
                self.tot = [0.0] * len(stx)
            for i in range(len(stx)):
                self.tot[i] += stx[i] - self.start_stack
        if FINGERPRINTS:
            for s in seats:
                S = st[s]
                if not S.lab and S.hands >= 20 and s != self.me_seat:
                    code = seat_label(S)
                    if code:
                        S.lab = code
                        if code == "CPF" or code == "YSL":
                            S.f3_o += 12            # Saturday: folded 84% and 85% of 337 and 184 of our 3-bets
                            S.f3 += 10
                        elif code == "ANTON":
                            S.f4_o += 6             # Saturday: folded 59 to 66% of 4-bets after 3-betting
                            S.f4 += 3.7
                        zo, zf, zn, zs = SEED[code]
                        for b in range(6):
                            S.zo[b] += zo[b]
                            S.zf[b] += zf[b]
                            S.zn[b] += zn[b]
                            S.zs[b] += zs[b]
        if shown and betlog:
            bd_all = [CARD[c] for c in summary.get("board") or ()]
            seen_cards = {}
            for k, cards in shown.items():
                seen_cards[int(k)] = cards
            for s, stt, b in betlog:
                cards = seen_cards.get(s)
                nbd = 3 if stt == "flop" else (4 if stt == "turn" else 5)
                if cards and len(bd_all) >= nbd:
                    S = st[s]
                    S.zn[b] += 1
                    if self._zstrong(CARD[cards[0]], CARD[cards[1]], bd_all[:nbd]):
                        S.zs[b] += 1
        if shown and agg_post:
            board = [CARD[c] for c in summary.get("board") or ()]
            if len(board) == 5:
                bp = 1
                for c in board:
                    bp *= CP[c]
                bcat = RANK[bp] >> 20
                for k, cards in shown.items():
                    s = int(k)
                    if s not in agg_post:
                        continue
                    S = st[s]
                    S.sd_agg += 1
                    cat = RANK[bp * CP[CARD[cards[0]]] * CP[CARD[cards[1]]]] >> 20
                    if cat <= bcat and cat <= 2 and not self._flushy(board, cards):
                        S.sd_air += 1

    def _zstrong(self, a, b, bd):
        """Was this hand top pair or better (or a draw with an overcard) on this board?
        Same yardstick as the range model's `nge`."""
        bp, sc, sm, bmask, thr, fs, scf, smf, d4b, paired, tb = self._board_ctx(bd)
        v = RANK[bp * CP[a] * CP[b]]
        sa = a & 3
        sb = b & 3
        if fs >= 0 and scf + (sa == fs) + (sb == fs) >= 5:
            m = smf
            if sa == fs:
                m |= 1 << (a >> 2)
            if sb == fs:
                m |= 1 << (b >> 2)
            f = FLUSH[m]
            if f > v:
                v = f
        if len(bd) < 5 and v < TWO_PAIR:
            c4 = sc[sa] + 2 if sa == sb else max(sc[sa], sc[sb]) + 1
            if c4 == 4 or (not d4b and DRAW4[bmask | (1 << (a >> 2)) | (1 << (b >> 2))]):
                v += DRAWB
        return v >= thr

    @staticmethod
    def _flushy(board, cards):
        sc = [0, 0, 0, 0]
        for c in board:
            sc[c & 3] += 1
        for c in cards:
            sc[CARD[c] & 3] += 1
        return max(sc) >= 5

    # ------------------------------------------------------------ entry
    def act(self, state):
        t0 = _now()
        self.n_dec += 1
        try:
            out = self._act(state, t0)
        except Exception:
            self.errors += 1
            if DEBUG:
                import traceback
                traceback.print_exc()
            out = None
        self.used += _now() - t0
        # Whatever was decided, only ever answer with an action the dealer lists.
        legal = state.get("legal_actions") or ()
        a = out.get("action") if out else None
        if a == "all_in":
            a = "raise"
            out = {"action": "raise", "amount": state.get("max_raise_to")}
        if a == "raise":
            lo = state.get("min_raise_to")
            hi = state.get("max_raise_to")
            if "raise" in legal and lo is not None and hi is not None:
                try:
                    amt = int(out.get("amount"))
                except (TypeError, ValueError):
                    amt = lo
                return {"action": "raise", "amount": lo if amt < lo else (hi if amt > hi else amt)}
            a = "call"
        if a == "call":
            if "call" in legal:
                return CALL
            a = "check"
        if a == "check":
            if "check" in legal:
                return CHECK
            return CALL if ("call" in legal and not state.get("to_call")) else FOLD
        return CHECK if "check" in legal else FOLD

    def _risk(self, state):
        """+1 = gamble (outside the top two, far behind), -1 = protect (far ahead of third), 0 = normal."""
        tot = self.tot
        total = self.total_hands
        if not RANK_PLAY or total <= LONG_GAME or not tot:
            return 0.0
        hn = state.get("hand_number", 1) or 1
        left = total - hn
        if left < 0 or left > RANK_PHASE * total:
            return 0.0
        me = state["seat"]
        if me >= len(tot):
            return 0.0
        mine = tot[me] - RANK_HANDICAP * (hn - 1)
        others = sorted((tot[i] for i in range(len(tot)) if i != me), reverse=True)
        if len(others) < 2:
            return 0.0
        sd = 280.0 * (left + 1) ** 0.5            # one hand swings about 14 big blinds
        if mine < others[1]:                      # outside the top two: gamble to get back in
            r = (others[1] - mine) / sd - 0.5
            return 0.0 if r < 0 else (1.0 if r > 1 else r)
        r = ((mine - others[1]) / sd - 1.5) / 1.5  # inside: protect once far ahead of third place
        return 0.0 if r < 0 else -(1.0 if r > 1 else r)

    def _act(self, state, t0):
        self.risk = self._risk(state)
        hc = state["hole_cards"]
        hole = (CARD[hc[0]], CARD[hc[1]])
        if state["street"] == "preflop":
            return self._preflop(state, hole)
        board = [CARD[c] for c in state["board"]]
        return self._postflop(state, hole, board, t0)

    @staticmethod
    def _raise_to(state, target, commit=0.62):
        lo, hi = state["min_raise_to"], state["max_raise_to"]
        if lo is None:
            return None
        target = int(target)
        if target >= hi * commit:
            target = hi
        if target < lo:
            target = lo
        if target > hi:
            target = hi
        return {"action": "raise", "amount": target}

    # ------------------------------------------------------------ preflop
    def _preflop(self, state, hole):
        legal = state["legal_actions"]
        me = state["seat"]
        stacks = state["stacks"]
        bets = state["bets"]
        n = len(stacks)
        button = state["button"]
        bb = state["big_blind"] or 20
        to_call = state["to_call"]
        pot = state["pot"]
        cur = max(bets)
        mybet = bets[me]
        mytotal = stacks[me] + mybet
        can_raise = "raise" in legal
        cls = CLS[hole]
        lvl = LEVEL.get(cls, 9)
        pair = len(cls) == 2
        suited = (not pair) and cls[2] == "s"
        rel = (me - button) % n            # 0 button, 1 small blind, 2 big blind
        d = (button - me) % n              # seats between us and the button
        st = self.st

        raises = 0
        last_raiser = -1
        my_raises = 0
        limpers = 0
        whale_limp = False                 # a limper who plays almost every hand
        all_lf = True                      # every limper gives up to a raise
        all_sus = True                     # ... or limps so much that we should test him
        other_raiser = False               # a raise from someone who is not a starter-kit bot
        callers = 0                        # callers of the last raise
        for h in state["history"]:
            a = h["action"]
            if a == "raise":
                raises += 1
                last_raiser = h["seat"]
                callers = 0
                if h["seat"] == me:
                    my_raises += 1
                elif not st[h["seat"]].starter():
                    other_raiser = True
            elif a == "call":
                if raises:
                    callers += 1
                else:
                    limpers += 1
                    W = st[h["seat"]]
                    if W.hands >= 25 and W.r_vpip() >= 0.45:
                        whale_limp = True
                    if not W.limp_folder():
                        all_lf = False
                        if not W.limp_suspect():
                            all_sus = False

        def call_or_check():
            return CALL if to_call > 0 else CHECK

        def fold_or_check():
            return CHECK if to_call == 0 else FOLD

        # ---------------------------------------------- nobody has raised
        if raises == 0:
            if rel == 1:
                plvl = 5 if (pair or suited) else 4
            elif rel == 2:
                plvl = 1
            else:
                plvl = max(0, 5 - d)
            if limpers == 0:
                if not can_raise:
                    return call_or_check() if lvl <= plvl else fold_or_check()
                # steal wider from blinds that have shown they give up
                adj = 0
                late = rel in (0, 1) or d == 1
                if late:
                    if rel == 1:
                        p_fold = st[(button + 2) % n].r_sf()
                    else:
                        p_fold = st[(button + 1) % n].r_sf() * st[(button + 2) % n].r_sf()
                        if d == 1:
                            p_fold *= 1.0 - min(0.6, st[button].r_vpip() * 1.2)
                    # a 2.2bb steal with nothing needs the rest to fold about 45% of the time
                    if p_fold >= (0.74 if rel == 1 else 0.62):
                        adj = 9
                    elif p_fold >= (0.60 if rel == 1 else 0.46):
                        adj = 1
                if lvl <= plvl + adj:
                    size = bb * (2.5 if rel == 1 else (2.2 if late else 3.0))
                    if st[(button + 2) % n].limp_folder() or st[(button + 1) % n].limp_folder():
                        size = max(size, 3.25 * bb)     # above his two-big-blind calling limit
                    return self._raise_to(state, size)
                return fold_or_check()
            # limped pot
            if can_raise and all_lf:
                k = 0 if rel == 2 else (1 if rel == 1 else d + 2)     # players still to act
                if k <= 2 or (k == 3 and lvl <= 6) or lvl <= 5:
                    return self._raise_to(state, bb * (3.5 + limpers - 1))
            if can_raise and all_sus and lvl <= 5:
                return self._raise_to(state, bb * (3.5 + limpers - 1))
            iso = 1 if rel == 2 else (2 if rel == 1 else min(plvl, 3))
            if whale_limp:
                iso = min(iso + 2, 4)      # he calls and pays off: raise wider and bigger
            if can_raise and lvl <= iso:
                return self._raise_to(state, bb * (4 + limpers + (1 if rel in (1, 2) else 0) + (1 if whale_limp else 0)))
            if rel == 2:
                return CHECK
            if rel == 1 and lvl <= 6:
                return CALL
            if (pair or suited) and lvl <= 5 and d <= 1:
                return CALL
            return fold_or_check()

        # ---------------------------------------------- facing a raise
        R = cur
        S = st[last_raiser]
        need = to_call / float(pot + to_call) if to_call > 0 else 0.0
        pfr = S.r_pfr()
        tb = S.r_3bet()
        shv = S.r_shove()
        if S.starter() and not other_raiser:
            # his range is exactly pair / ace / king and he never folds it
            es = ES[cls] / 1000.0
            if to_call >= 0.4 * mytotal:
                if es >= need + 0.01:
                    return {"action": "all_in"} if can_raise else CALL
                return fold_or_check()
            if es >= 0.53:
                if not can_raise:
                    return call_or_check()
                if raises >= 2 or R >= 8 * bb:
                    return {"action": "all_in"}
                return self._raise_to(state, R * 3.0 + R * callers)
            # see a flop cheaply: he will keep betting the same range on any board
            if to_call <= 5 * bb and (callers == 0 or lvl <= 5):
                return call_or_check()
            return fold_or_check()
        # all-in or close to it: call when our equity against his shoving range pays
        if to_call >= 0.4 * mytotal or R >= 800:
            if raises == 1:
                f = max(0.015, min(0.9, shv * 1.3))
            else:
                f = max(0.012, tb * 0.45, shv)
            margin = 0.02 + (0.04 if callers else 0.0)
            margin -= 0.06 * self.risk if self.risk > 0 else 0.04 * self.risk
            if cls == "AA" or req(cls, f) >= need + margin:
                return {"action": "all_in"} if can_raise else CALL
            return fold_or_check()

        # how wide the raiser's range is for this action
        if raises == 1:
            dr = (button - last_raiser) % n
            relr = (last_raiser - button) % n
            late = dr <= 1 or relr == 1
            f = pfr * (1.4 if late else (0.75 if dr >= 4 and relr > 2 else 1.0))
            f = 0.06 if f < 0.06 else (0.85 if f > 0.85 else f)
        elif raises == 2:
            f = 0.02 if tb < 0.02 else (0.6 if tb > 0.6 else tb)
        else:
            f = max(0.015, tb * 0.4, shv)
        e = req(cls, f)
        pos_me = (me - button - 1) % n
        pos_r = (last_raiser - button - 1) % n
        ip = pos_me > pos_r
        price = to_call / float(bb)

        if raises == 1 and my_raises == 0:
            loose = f >= 0.25
            sticky = S.f3_o >= 3 and S.r_f3() < 0.35      # does not fold to 3-bets
            if can_raise and (cls in ("AA", "KK") or e >= (0.60 if ip else 0.62)):
                mult = (3.0 if ip else 3.7) + (0.8 if (sticky or pfr >= 0.3) else 0.0)
                return self._raise_to(state, R * mult + R * callers)
            # bluff 3-bet the openers who give up to 3-bets
            f3 = S.r_f3()
            if can_raise and callers == 0 and R <= 4.5 * bb:
                n3 = S.f3_o
                hot = False                      # a frequent 3-bettor still to act behind us
                left = 0                         # players still to act behind us
                for i in range(1, n):
                    t = (me + i) % n
                    if t == last_raiser:
                        break
                    T = st[t]
                    if not state["folded"][t]:
                        left += 1
                        if T.tb_o >= 20 and T.tb >= 0.18 * T.tb_o:
                            hot = True
                if THREEBET_ANY and n3 >= 8 and S.f3 >= 0.80 * n3 and not hot and left <= 3:
                    bluff = True                 # V22: any two cards
                elif n3 >= 3 and f3 >= 0.78:
                    bluff = lvl <= 6
                elif n3 >= 2 and f3 >= 0.70:
                    bluff = lvl <= 5
                elif f3 >= 0.55:
                    bluff = cls in BLUFF3      # most of the field folds: try, then learn
                else:
                    bluff = False
                if bluff:
                    return self._raise_to(state, R * (2.8 if ip else 3.4))
            if pair and price <= 6.5:
                return CALL
            if cls in ("AKs", "AKo") and price <= 8:
                return CALL
            if cls in FLAT_SUITED and price <= 5 and (ip or rel == 2):
                return CALL
            if cls in FLAT_SUITED_IP and price <= 4 and ip and rel != 1:
                return CALL
            if cls in FLAT_OFF and price <= 4.5 and (ip or rel == 2) and (loose or pfr >= 0.12):
                return CALL
            if loose and e >= 0.5 and price <= 6 and (ip or rel == 2):
                return CALL
            if WIDE_CALLS:
                # in position against a late open: the hands that flop well
                if ip and rel != 1 and late and price <= 3.2 and callers <= 1 and (lvl <= 3 or (suited and lvl <= 5)):
                    return CALL
            if rel == 2:
                if price <= 1.5 and lvl <= 5:
                    return CALL
                if WIDE_CALLS and price <= 2.5 and callers <= 1 and lvl <= (5 if late else 4):
                    return CALL
                if price <= 2.5 and (lvl <= 2 or cls in BB_OFF or (suited and lvl <= 4)):
                    return CALL
            return fold_or_check()

        if my_raises >= 1 and raises == 2:
            # we raised and got re-raised
            if cls in ("AA", "KK") or e >= 0.62:
                if can_raise:
                    if tb >= 0.15 or R >= 14 * bb:
                        return {"action": "all_in"}
                    return self._raise_to(state, R * (2.3 if ip else 2.6), commit=0.45)
                return call_or_check()
            if S.lab == "ANTON":
                maniac = MANIAC_RULES and can_raise and R <= 13 * bb and S.f4 >= 0.45 * S.f4_o
            else:
                # v3.0: any seat that 3-bets one hand in five and has folded most of the 4-bets it faced
                maniac = (MANIAC_RULES and can_raise and R <= 13 * bb and S.tb_o >= 25 and S.tb >= 0.18 * S.tb_o
                          and S.f4_o >= 4 and S.f4 >= 0.55 * S.f4_o)
            if e >= (0.40 if ip else 0.43) and price <= 10:
                return self._raise_to(state, R * 2.3, commit=0.45) if maniac else CALL
            if pair and price <= 6:
                return self._raise_to(state, R * 2.3, commit=0.45) if maniac else CALL
            if cls in ("KQs", "AJs", "ATs", "JTs", "QJs", "T9s") and ip and price <= 6:
                return self._raise_to(state, R * 2.3, commit=0.45) if maniac else CALL
            return fold_or_check()

        # 4-bets and beyond, or a 3-bet in front of us before we acted
        if cls in ("AA", "KK"):
            if can_raise:
                if my_raises >= 1 or R >= 12 * bb:
                    return {"action": "all_in"}
                return self._raise_to(state, R * 2.4, commit=0.4)
            return call_or_check()
        if my_raises >= 1:
            if e >= 0.56 - (0.05 * self.risk if self.risk > 0 else 0.0) and can_raise:
                return {"action": "all_in"}
            if e >= 0.47 and to_call <= 0.2 * mytotal:
                return CALL
            return fold_or_check()
        if e >= 0.60 and can_raise:
            if f >= 0.12:
                return {"action": "all_in"}
            return self._raise_to(state, R * 2.4, commit=0.4)
        if e >= 0.50 and to_call <= 0.15 * mytotal:
            return CALL
        return fold_or_check()

    # ------------------------------------------------------------ postflop
    def _lines(self, hist, n, street):
        pfr = [0] * n      # preflop raises by seat
        pfi = [0] * n      # which raise of the hand his last one was (1 = open)
        pcall = [0] * n    # 1 limped, 2 called a raise
        agg = [0] * n      # postflop bets and raises
        rais = [0] * n     # postflop raises over a bet
        called = [0] * n   # postflop calls
        lastx = [0.0] * n  # size of his last postflop bet or raise, in pots
        raises = 0
        cur_st = "preflop"
        curbet = 0
        pot = 0
        front = [0] * n    # chips in front of each seat this street
        agg_by = {}
        callers_by = {}
        checked = set()
        for h in hist:
            a = h["action"]
            s = h["seat"]
            stt = h["street"]
            if stt != cur_st:
                cur_st = stt
                curbet = 0
                front = [0] * n
                checked = set()
            if a == "raise":
                amt = h["amount"]
                if stt == "preflop":
                    raises += 1
                    pfr[s] += 1
                    pfi[s] = raises
                else:
                    agg[s] += 1
                    if curbet > 0:
                        rais[s] += 1
                        lastx[s] = (amt - curbet) / float((pot + curbet - front[s]) or 1)
                    else:
                        lastx[s] = amt / float(pot or 1)
                pot += amt - front[s]
                front[s] = amt
                curbet = amt
                agg_by[stt] = s
            elif a == "call":
                amt = h["amount"]
                if stt == "preflop":
                    pcall[s] = 2 if raises else 1
                else:
                    called[s] += 1
                pot += amt
                front[s] += amt
                callers_by.setdefault(stt, set()).add(s)
            elif a == "check":
                checked.add(s)
            elif a == "small_blind" or a == "big_blind":
                amt = h["amount"]
                pot += amt
                front[s] = amt
                if amt > curbet:
                    curbet = amt
        if cur_st != street:
            checked = set()
        cat = [line_cat(i, street, agg_by, callers_by, checked) for i in range(n)]
        return pfr, pfi, pcall, agg, rais, called, lastx, cat, raises == 0

    def _tier(self, s, L, dead, bp, fs, scf, smf, sc, bmask, d4b, nb, thr):
        """Seat s's range on this board as (strong, weak, keep, sfrac): lists of
        (score, a, b); a weak combo is `keep` times as likely as a strong one;
        sfrac is the share of the range holding top pair or better, or a draw."""
        S = self.st[s]
        pfr, pfi, pcall, agg, rais, called, lastx = L[:7]
        lo = 0.0
        plain = S.starter()
        if plain:
            hi = 1.0
        elif pfr[s]:
            i = pfi[s]
            if i >= 3 or pfr[s] >= 2:
                hi = max(0.03, min(0.3, S.r_3bet() * 0.5, S.r_pfr() * 0.5))
            elif i == 2:
                hi = max(0.03, min(0.5, S.r_3bet()))
            else:
                hi = max(0.06, min(0.7, S.r_pfr() * 1.15))
        elif pcall[s] == 2:
            hi = max(0.10, min(0.7, S.r_vpip() * 0.85))
        elif pcall[s] == 1:
            hi = max(0.2, min(0.9, S.r_vpip()))
            lo = min(S.r_pfr() * 0.6, hi * 0.5)
        else:
            hi = 1.0
        i0 = int(lo * NC)
        i1 = max(i0 + 12, int(hi * NC))
        if plain:
            src = STARTER_S if (pfr[s] or agg[s]) else STARTER_W
        else:
            src = COMBOS[i0:i1]
        cap = self.cap
        if len(src) > cap + 20:
            src = src[::len(src) // cap]
        out = []
        nge = 0
        drawok = nb < 5
        for a, b in src:
            if a in dead or b in dead:
                continue
            v = RANK[bp * CP[a] * CP[b]]
            sa = a & 3
            sb = b & 3
            if fs >= 0:
                cnt = scf + (sa == fs) + (sb == fs)
                if cnt >= 5:
                    m = smf
                    if sa == fs:
                        m |= 1 << (a >> 2)
                    if sb == fs:
                        m |= 1 << (b >> 2)
                    f = FLUSH[m]
                    if f > v:
                        v = f
            if drawok and v < TWO_PAIR:
                c4 = sc[sa] + 2 if sa == sb else max(sc[sa], sc[sb]) + 1
                if c4 == 4 or (not d4b and DRAW4[bmask | (1 << (a >> 2)) | (1 << (b >> 2))]):
                    v += DRAWB
            if v >= thr:
                nge += 1
            out.append((v, a, b))
        N = len(out)
        if not N:
            return [(0, a, b) for a, b in COMBOS[:60] if a not in dead and b not in dead], None, 0.0, 0.5
        if plain or not (agg[s] or called[s]):
            return out, None, 0.0, nge / float(N)
        out.sort(reverse=True)
        if agg[s]:
            air = S.r_air()
            if rais[s]:
                vf = max(0.04, S.r_raise() * 1.2)
                keep = max(0.02, min(0.5, air * 0.5))
            else:
                b = S.r_cb() if (pfr[s] and pfi[s] == max(pfi)) else S.r_bet()
                vf = b * (1.0 - air)
                keep = max(0.03, min(0.6, b * air / max(0.05, 1.0 - vf)))
                # measured at the river; applied at half strength earlier
                h = 1.0 if nb == 5 else 0.5
                mv, mk = SIZE_MULT[size_class(S, lastx[s])]
                vf *= 1.0 + (mv - 1.0) * h
                keep *= 1.0 + (mk - 1.0) * h
            vf *= 0.8 ** (agg[s] - 1)
            if nb == 5:
                keep *= 0.8
            vf = max(0.04, min(0.9, vf))
        else:
            vf = max(0.15, min(0.95, 1.0 - S.r_fold()))
            keep = 0.06
        k = max(3, int(vf * N))
        if k > N:
            k = N
        sfrac = (min(k, nge) + keep * max(0, nge - k)) / (k + keep * (N - k))
        if SIZE_LEARN and agg[s] and not rais[s] and s in self.zcur and 0 < nge < N:
            zb = zbucket(lastx[s])
            zn = S.zn[zb]
            if zn >= ZS_MIN:
                # share of top pair or better in what he showed after this size, shrunk to the model's
                q = (S.zs[zb] + ZS_PRIOR * sfrac) / (zn + ZS_PRIOR)
                q = max(0.03, min(0.97, q))
                if q >= sfrac:
                    return out[:nge], out[nge:], (1.0 - q) / q * nge / float(N - nge), q
                if zb <= ZW_MAXB and zn >= ZW_MIN:
                    self.zweak = True          # his bet of this size is weaker than the model thinks
                    return out[:nge], out[nge:], (1.0 - q) / q * nge / float(N - nge), q
        return out[:k], out[k:], keep, sfrac

    @staticmethod
    def _board_ctx(board):
        bp = 1
        sc = [0, 0, 0, 0]
        sm = [0, 0, 0, 0]
        bmask = 0
        top = 0
        paired = False
        trips_board = False
        seen = {}
        for x in board:
            bp *= CP[x]
            s = x & 3
            r = x >> 2
            sc[s] += 1
            sm[s] |= 1 << r
            bmask |= 1 << r
            if r > top:
                top = r
            k = seen.get(r, 0) + 1
            seen[r] = k
            if k == 2:
                paired = True
            elif k == 3:
                trips_board = True
        # what counts as a hand an opponent will not fold: top pair or better
        # (two pair or better on a paired board), or a draw
        thr = TWO_PAIR if paired else ((1 << 20) | (top << 16))
        fs = -1
        for s in range(4):
            if sc[s] >= 3:
                fs = s
        scf = sc[fs] if fs >= 0 else 0
        smf = sm[fs] if fs >= 0 else 0
        return bp, sc, sm, bmask, thr, fs, scf, smf, DRAW4[bmask], paired, trips_board

    def _postflop(self, state, hole, board, t0):
        legal = state["legal_actions"]
        me = state["seat"]
        stacks = state["stacks"]
        bets = state["bets"]
        folded = state["folded"]
        n = len(stacks)
        pot = state["pot"]
        c = state["to_call"]
        street = state["street"]
        cur = max(bets)
        mybet = bets[me]
        mystack = stacks[me]
        can_raise = "raise" in legal
        live = [i for i in range(n) if not folded[i] and i != me]
        if not live:
            return CHECK if c == 0 else CALL
        L = self._lines(state["history"], n, street)
        nb = len(board)
        river = nb == 5

        bp, sc, sm, bmask, thr, fs, scf, smf, d4b, paired, trips_board = self._board_ctx(board)
        h0, h1 = hole
        myv = RANK[bp * CP[h0] * CP[h1]]
        s0 = h0 & 3
        s1 = h1 & 3
        if fs >= 0 and scf + (s0 == fs) + (s1 == fs) >= 5:
            m = smf
            if s0 == fs:
                m |= 1 << (h0 >> 2)
            if s1 == fs:
                m |= 1 << (h1 >> 2)
            if FLUSH[m] > myv:
                myv = FLUSH[m]
        mydraw = False
        if not river and myv < TWO_PAIR:
            c4 = sc[s0] + 2 if s0 == s1 else max(sc[s0], sc[s1]) + 1
            mydraw = c4 == 4 or (not d4b and DRAW4[bmask | (1 << (h0 >> 2)) | (1 << (h1 >> 2))])
        dead = set(board)
        dead.add(h0)
        dead.add(h1)

        k = len(live)
        self.cap = 200 if k <= 2 else (130 if k == 3 else 90)     # keep multiway decisions fast
        self.zcur = set(s for s in live if cur > 0 and bets[s] == cur)     # seats whose bet we face now
        self.zweak = False
        tiers = [self._tier(s, L, dead, bp, fs, scf, smf, sc, bmask, d4b, nb, thr) for s in live]
        if river:
            eq = 1.0
            for strong, weak, keep, _sf in tiers:
                w = 0.0
                for t in strong:
                    v = t[0]
                    if myv > v:
                        w += 1.0
                    elif myv == v:
                        w += 0.5
                tot = float(len(strong))
                if weak:
                    ww = 0.0
                    for t in weak:
                        v = t[0]
                        if myv > v:
                            ww += 1.0
                        elif myv == v:
                            ww += 0.5
                    w += keep * ww
                    tot += keep * len(weak)
                eq *= w / tot if tot > 0 else 0.5
        else:
            # Big calls get a fixed time to simulate: the tournament server is 4-5 times slower
            # than a laptop, so a short budget gives few samples and noisy big decisions.
            # This is the only change from v14 (same decisions when samples are plentiful).
            budget = self._budget(state)
            if c >= BIG_CALL:
                # big calls get a fixed time, shortened only when a long game is short of time
                budget = BIG_BUDGET if (self.total_hands <= LONG_GAME or budget >= 0.0012) else max(0.0008, 2.5 * budget)
            t_mc = _now()
            eq = self._mc(h0, h1, board, dead, tiers, t_mc + budget, bp, sc, sm)
            self.used_mc += _now() - t_mc
            self.n_mc += 1

        # Very strong made hands are never folded on a board that is not scary:
        # paying off sometimes costs less than being pushed off a set.
        mycat = myv >> 20
        if mycat >= 3 and not (mycat == 3 and trips_board):
            scary = (scf >= 4 and mycat < 5) or (d4b and mycat < 4)
            if not scary:
                semi = (scf >= 3 and mycat < 5) or (scf >= 4 and mycat == 5) or (paired and mycat <= 5)
                fl = 0.52 if semi else 0.64
                if eq < fl:
                    eq = fl

        # Opponents who can still act: (how often his weak hands fold to a
        # normal bet, share of his range that will not fold).
        opp = []
        allin = False
        pfi = L[1]
        probe = False          # someone folds everything to any bet above two big blinds
        nofold = False         # a starter-kit bot holding its raising range: never folds
        for s, t in zip(live, tiers):
            if stacks[s] > 0:
                S = self.st[s]
                ov = None
                hot = L[0][s] or L[3][s]            # raised preflop or bet postflop this hand
                if S.starter():
                    ov = 0.0 if hot else 0.97
                elif S.limp_folder() and L[2][s] == 1 and not hot:
                    ov = 0.85
                if ov is not None:
                    if ov:
                        probe = True
                    else:
                        nofold = True
                # ranges built by re-raising preflop fold half as often
                opp.append((S, L[7][s], 0.5 if pfi[s] >= 2 else 1.0, ov))
            else:
                allin = True
        floor = 0.0 if river else (0.6 if nb == 3 else 0.5)
        si = nb - 3
        multi = 1 if len(live) >= 2 else 0
        limped = L[8]
        lo = state["min_raise_to"]
        hi = state["max_raise_to"]

        if c == 0:
            if not can_raise:
                return CHECK
            best = None
            best_ev = eq * pot * (1.0 if river else 0.9) + 0.03 * pot
            cands = [mybet + x * pot for x in (0.5, 0.8, 1.1, 1.6)]
            if probe:
                cands.insert(0, mybet + 45)
            if nofold and eq >= 0.52:
                cands.append(hi)
            for tgt in cands:
                if tgt >= 0.62 * hi:
                    tgt = hi
                elif tgt < lo:
                    tgt = lo
                size = tgt - mybet
                xx = size / float(pot)
                pf_all = 0.0 if allin else 1.0
                for S, cat, w, ov in opp:
                    if ov is None:
                        pf_all *= fold_prob(S, cat, si, multi, limped, xx, False) * w
                    else:
                        pf_all *= ov if size > 40 else 0.0
                cfa = 1.0 - pf_all
                eqc = max(floor * eq, (eq - pf_all) / cfa) if cfa > 1e-9 else eq
                ev = pf_all * pot + cfa * (eqc * (pot + 2 * size) - size)
                if ev > best_ev:
                    best_ev = ev
                    best = tgt
                if tgt >= hi:
                    break
            if best is None:
                return CHECK
            return {"action": "raise", "amount": int(best)}

        need = c / float(pot + c)
        behind = 0
        for s in live:
            if bets[s] < cur and stacks[s] > 0:
                behind += 1
        ev_call = eq * (pot + c) - c
        # V21, only change from V20: heads up, raise a bet under 40% of the pot to 3 times its
        # size when the bettor's measured folds pay for it. Field: authors of such bets give up
        # about 7 times in 10 when raised; each seat's own rate takes over as it is observed.
        if RAISE_SMALL and can_raise and hi is not None and len(live) == 1 and behind == 0 and not allin and not nofold:
            v = live[0]
            xb0 = L[6][v]
            if 0 < xb0 < 0.4 and L[4][v] == 0 and L[3][v] >= 1 and bets[v] == cur and not self.st[v].starter():
                r_to = max(lo, 3 * cur)
                if r_to <= 0.35 * (mystack + mybet) and r_to < hi:
                    Sv = self.st[v]
                    zb0 = zbucket(xb0)
                    pfr_ = (Sv.zf[zb0] + 5.0 * ((0.68 if river else 0.75) if zb0 == 0 else (0.63 if river else 0.70))) / (Sv.zo[zb0] + 5.0)
                    a_ = r_to - mybet
                    eqc_ = max(floor * eq, (eq - pfr_) / (1.0 - pfr_)) if pfr_ < 0.999 else eq
                    ev_r = pfr_ * pot + (1.0 - pfr_) * (eqc_ * (pot + a_ + (r_to - cur)) - a_)
                    if ev_r > max(ev_call, 0.0) + 0.05 * pot:
                        return {"action": "raise", "amount": int(r_to)}
        if MANIAC_RULES and can_raise and hi is not None and len(live) == 1 and behind == 0 and not allin and not nofold:
            v = live[0]
            xb0 = L[6][v]
            Sv = self.st[v]
            zb = zbucket(xb0)
            if ((Sv.lab == "ANTON" or (Sv.zo[zb] >= 8 and Sv.zf[zb] >= 0.8 * Sv.zo[zb]))
                    and 0.4 <= xb0 < 0.9 and L[4][v] == 0 and L[3][v] >= 1 and bets[v] == cur and mycat < 2):
                r_to = max(lo, (3.0 if zb <= 2 else 2.6) * cur)
                if r_to <= 0.35 * (mystack + mybet) and r_to < hi:
                    pfr_ = (Sv.zf[zb] + ZR_PRIOR * ZR_FIELD[zb]) / (Sv.zo[zb] + ZR_PRIOR)
                    a_ = r_to - mybet
                    ev_r = pfr_ * pot + (1.0 - pfr_) * (floor * eq * (pot + a_ + (r_to - cur)) - a_)
                    if pfr_ >= 0.7 and ev_r > max(ev_call, 0.0) + 0.05 * pot:
                        return {"action": "raise", "amount": int(r_to)}
        if can_raise and eq >= (0.52 if nofold else 0.62) and hi is not None and not (self.zweak and (mycat < 2 or (mycat == 2 and paired))):
            r_to = hi if nofold else cur + 0.9 * (pot + c)
            if r_to >= 0.62 * hi:
                r_to = hi
            elif r_to < lo:
                r_to = lo
            a = r_to - mybet
            add = r_to - cur
            pf_all = 0.0 if allin else 1.0
            xr = add / float(pot + c)
            for S, cat, w, ov in opp:
                pf_all *= (fold_prob(S, cat, si, multi, limped, xr, True) * w) if ov is None else ov
            cfa = 1.0 - pf_all
            eqc = max(floor * eq, (eq - pf_all) / cfa) if cfa > 1e-9 else eq
            ev_raise = pf_all * pot + cfa * (eqc * (pot + a + add) - a)
            if eqc >= 0.5 and ev_raise > ev_call + 0.02 * pot:
                return {"action": "raise", "amount": int(r_to)}
        margin = 0.03 * behind
        # V20, only change from v14p: on the flop and turn, a pair below top pair (no draw)
        # facing a bet of half the pot or more needs more equity. On 35 real rounds these calls
        # lost 1,957 big blinds (flop and turn, 244 calls) while the same calls against smaller
        # bets won 3,833. Not applied against seats that bet with anything (kit-like, VPIP 50%+).
        if not river and not mydraw and c >= WEAK_PAIR_BET * (pot - c):
            r0 = h0 >> 2
            r1 = h1 >> 2
            top = 0
            for x in board:
                if (x >> 2) > top:
                    top = x >> 2
            hit0 = False
            hit1 = False
            for x in board:
                if (x >> 2) == r0:
                    hit0 = True
                if (x >> 2) == r1:
                    hit1 = True
            pr = -1
            if r0 == r1 and not hit0:
                pr = r0                                  # pocket pair
            elif hit0 != hit1:
                pr = r0 if hit0 else r1                  # one hole card pairs the board
            cat_ok = (myv >> 20) == 1 or ((myv >> 20) == 2 and paired)
            if cat_ok and 0 <= pr < top:
                loose = False
                for s in live:
                    if bets[s] == cur:
                        S = self.st[s]
                        if S.starter() or S.r_vpip() >= 0.5:
                            loose = True
                if not loose:
                    margin += WEAK_PAIR_MARGIN
        if not river and c < mystack:
            margin += 0.03
            if mydraw and c <= 0.25 * mystack:
                margin -= 0.05
        if self.risk > 0:
            margin -= 0.07 * self.risk            # outside the top two late in the game: take the gamble
        elif self.risk < 0 and c >= BIG_CALL:
            margin -= 0.05 * self.risk            # far ahead of third: pass on big marginal calls
        if eq >= need + margin:
            return CALL
        # V22: about to fold. Heads up against a bet of 0.42-0.90 pot from a seat whose bets of that
        # size have been folding to raises (his own record only), raise as a bluff instead.
        if SIZE_LEARN and can_raise and hi is not None and len(live) == 1 and behind == 0 and not allin and not nofold:
            v = live[0]
            xb0 = L[6][v]
            if 0.4 <= xb0 < 0.9 and L[4][v] == 0 and L[3][v] >= 1 and bets[v] == cur and not self.st[v].starter():
                Sv = self.st[v]
                zb = zbucket(xb0)
                if Sv.zo[zb] >= ZR_MIN:
                    r_to = max(lo, (3.0 if zb <= 2 else 2.6) * cur)
                    if r_to <= 0.35 * (mystack + mybet) and r_to < hi:
                        pfr_ = (Sv.zf[zb] + ZR_PRIOR * ZR_FIELD[zb]) / (Sv.zo[zb] + ZR_PRIOR)
                        a_ = r_to - mybet
                        ev_r = pfr_ * pot + (1.0 - pfr_) * (floor * eq * (pot + a_ + (r_to - cur)) - a_)
                        if ev_r > 0.08 * pot:
                            return {"action": "raise", "amount": int(r_to)}
        return FOLD

    def _budget(self, state):
        hn = state.get("hand_number", 1) or 1
        total = self.total_hands
        if total <= LONG_GAME and hn <= total:
            left = 8.0 - self.used                       # a 1,000-hand round: unchanged
            hands_left = max(1, total - hn + 1)
            b = left / (hands_left * 0.45)
            return 0.0003 if b < 0.0003 else (0.0016 if b > 0.0016 else b)
        # a long game (or one longer than announced): spread the time evenly over the hands left
        if hn > total:
            total = hn + 500
        hands_left = max(1, total - hn + 1)
        # what the server has probably counted so far: our own clock plus its cost per decision
        spent = self.used + self.n_dec * IPC_S
        left = 0.9 * FINAL_BANK_S * max(1.0, total / 5000.0) - spent
        done = self.hands_seen
        if done >= 30:
            fixed = (self.used - self.used_mc) / done + (self.n_dec / float(done)) * IPC_S   # per hand, outside the simulations
            per = self.n_mc / float(done)                                                     # simulations per hand
            b = (left / hands_left - fixed) / (per if per > 0.2 else 0.2)
        else:
            b = left / hands_left - 1.7 * IPC_S
        return 0.0001 if b < 0.0001 else (0.0016 if b > 0.0016 else b)

    def _mc(self, h0, h1, board, dead, tiers, t_end, bp0, sc0, sm0):
        rnd = self.rng.random
        deck = [x for x in range(52) if x not in dead]
        Ld = len(deck)
        nb = len(board)
        hp = CP[h0] * CP[h1]
        s0 = h0 & 3
        s1 = h1 & 3
        r0 = 1 << (h0 >> 2)
        r1 = 1 << (h1 >> 2)
        plans = []
        for strong, weak, keep, _sf in tiers:
            ls = len(strong)
            lw = len(weak) if weak else 0
            pw = keep * lw / (keep * lw + ls) if lw else 0.0
            plans.append((strong, ls, weak, lw, pw))
        wins = 0.0
        n = 0
        while n < 400:
            if (n & 7) == 7 and n >= 23 and _now() > t_end:
                break
            used = set(dead)
            opp = []
            ok = True
            for strong, ls, weak, lw, pw in plans:
                for _ in range(10):
                    if lw and rnd() < pw:
                        t = weak[int(rnd() * lw)]
                    else:
                        t = strong[int(rnd() * ls)]
                    a = t[1]
                    b = t[2]
                    if a not in used and b not in used:
                        break
                else:
                    ok = False
                    break
                used.add(a)
                used.add(b)
                opp.append((a, b))
            n += 1
            if not ok:
                wins += 0.5
                continue
            bp = bp0
            sc = sc0[:]
            sm = sm0[:]
            k = nb
            while k < 5:
                x = deck[int(rnd() * Ld)]
                if x not in used:
                    used.add(x)
                    bp *= CP[x]
                    s = x & 3
                    sc[s] += 1
                    sm[s] |= 1 << (x >> 2)
                    k += 1
            fs = -1
            if sc[0] >= 3:
                fs = 0
            elif sc[1] >= 3:
                fs = 1
            elif sc[2] >= 3:
                fs = 2
            elif sc[3] >= 3:
                fs = 3
            me = RANK[bp * hp]
            if fs >= 0:
                scf = sc[fs]
                smf = sm[fs]
                if scf + (s0 == fs) + (s1 == fs) >= 5:
                    m = smf
                    if s0 == fs:
                        m |= r0
                    if s1 == fs:
                        m |= r1
                    f = FLUSH[m]
                    if f > me:
                        me = f
                best = True
                ties = 0
                for a, b in opp:
                    v = RANK[bp * CP[a] * CP[b]]
                    sa = a & 3
                    sb = b & 3
                    if scf + (sa == fs) + (sb == fs) >= 5:
                        m = smf
                        if sa == fs:
                            m |= 1 << (a >> 2)
                        if sb == fs:
                            m |= 1 << (b >> 2)
                        f = FLUSH[m]
                        if f > v:
                            v = f
                    if v > me:
                        best = False
                        break
                    if v == me:
                        ties += 1
            else:
                best = True
                ties = 0
                for a, b in opp:
                    v = RANK[bp * CP[a] * CP[b]]
                    if v > me:
                        best = False
                        break
                    if v == me:
                        ties += 1
            if best:
                wins += 1.0 / (ties + 1)
        return wins / n if n else 0.5


gc.collect()
gc.freeze()
gc.disable()
