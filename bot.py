"""Equity + opponent-model pokerbot.

Core: precomputed 7-card rank lookup (fast evaluator), Monte Carlo equity
against per-opponent ranges inferred from their actions and their observed
stats (VPIP / PFR / fold-to-bet / bluff rate), then pot-odds and value
thresholds. Exploits drift from a solid baseline but are capped.
Standard library only. Everything heavy is built once at import.
"""
import json
import random
import time

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


RANK7 = {}


def _gen(r, left, counts, prod):
    if r == 13:
        if left == 0:
            RANK7[prod] = _score_counts(counts)
        return
    if (13 - r) * 4 < left:
        return
    p = PRIMES[r]
    for c in range(min(4, left) + 1):
        counts[r] = c
        _gen(r + 1, left - c, counts, prod * p ** c)
    counts[r] = 0


_gen(0, 7, [0] * 13, 1)

FLUSH = {}
for _m in range(1 << 13):
    if bin(_m).count("1") >= 5:
        _sh = _straight_high(_m)
        if _sh >= 0:
            FLUSH[_m] = _enc(8, (_sh,))
        else:
            FLUSH[_m] = _enc(5, [r for r in range(12, -1, -1) if _m >> r & 1][:5])

# 4 of a 5-rank window present (open-ender / gutshot-ish), wheel included.
DRAW4 = [False] * (1 << 13)
for _m in range(1 << 13):
    mm = (_m << 1) | ((_m >> 12) & 1)
    for lo in range(0, 10):
        if bin((mm >> lo) & 31).count("1") >= 4:
            DRAW4[_m] = True
            break

CP = [PRIMES[c >> 2] for c in range(52)]


def card_int(s):
    return RANKS.index(s[0]) * 4 + SUITS.index(s[1])


def eval7(cards):
    p = 1
    sc = [0, 0, 0, 0]
    sm = [0, 0, 0, 0]
    for c in cards:
        p *= CP[c]
        s = c & 3
        sc[s] += 1
        sm[s] |= 1 << (c >> 2)
    for s in range(4):
        if sc[s] >= 5:
            return FLUSH[sm[s]]
    return RANK7[p]


# ------------------------------------------------------------ preflop ranking
PF = json.loads('{"AA":[0.8482,0.6275,0.4405],"AKs":[0.6768,0.4113,0.2756],"AKo":[0.6677,0.3926,0.2475],"AQs":[0.6582,0.3976,0.2561],"AQo":[0.6406,0.3629,0.2257],"AJs":[0.6555,0.3882,0.2437],"AJo":[0.6448,0.3522,0.2108],"ATs":[0.6383,0.36,0.2388],"ATo":[0.6298,0.3367,0.2066],"A9s":[0.6319,0.3437,0.2051],"A9o":[0.5998,0.3176,0.1791],"A8s":[0.6289,0.3332,0.2032],"A8o":[0.592,0.2957,0.1587],"A7s":[0.6115,0.3183,0.195],"A7o":[0.5843,0.2875,0.1565],"A6s":[0.6062,0.3196,0.1907],"A6o":[0.5768,0.273,0.1403],"A5s":[0.5909,0.3064,0.1986],"A5o":[0.585,0.2838,0.155],"A4s":[0.5925,0.3184,0.1972],"A4o":[0.5648,0.268,0.1511],"A3s":[0.5793,0.2936,0.1925],"A3o":[0.5601,0.2609,0.1413],"A2s":[0.571,0.2962,0.174],"A2o":[0.5549,0.2501,0.1399],"KK":[0.8269,0.5935,0.3672],"KQs":[0.6404,0.381,0.2609],"KQo":[0.6063,0.3461,0.2193],"KJs":[0.6414,0.3798,0.2427],"KJo":[0.6022,0.33,0.2006],"KTs":[0.6199,0.3572,0.2173],"KTo":[0.5887,0.3143,0.1972],"K9s":[0.6093,0.3307,0.2067],"K9o":[0.5914,0.2869,0.1655],"K8s":[0.5727,0.3069,0.1944],"K8o":[0.5698,0.2748,0.1403],"K7s":[0.578,0.2973,0.1853],"K7o":[0.5437,0.274,0.1466],"K6s":[0.5671,0.2794,0.181],"K6o":[0.54,0.2545,0.1331],"K5s":[0.5572,0.2823,0.1696],"K5o":[0.5373,0.2436,0.1308],"K4s":[0.5382,0.2714,0.1629],"K4o":[0.5261,0.2273,0.1223],"K3s":[0.5317,0.2634,0.1682],"K3o":[0.5012,0.2241,0.1148],"K2s":[0.5278,0.2596,0.1652],"K2o":[0.5065,0.2212,0.1105],"QQ":[0.7932,0.5294,0.3304],"QJs":[0.6068,0.365,0.2305],"QJo":[0.5711,0.3183,0.1941],"QTs":[0.5995,0.3441,0.2299],"QTo":[0.559,0.303,0.1864],"Q9s":[0.5781,0.3138,0.195],"Q9o":[0.5507,0.2809,0.1552],"Q8s":[0.5613,0.297,0.1756],"Q8o":[0.5299,0.265,0.1388],"Q7s":[0.5443,0.2876,0.1546],"Q7o":[0.5129,0.2417,0.1201],"Q6s":[0.5273,0.2751,0.1597],"Q6o":[0.5225,0.2327,0.1152],"Q5s":[0.5253,0.2604,0.1438],"Q5o":[0.4894,0.229,0.1185],"Q4s":[0.5202,0.2523,0.1495],"Q4o":[0.499,0.2228,0.1126],"Q3s":[0.5002,0.2426,0.1529],"Q3o":[0.4826,0.2052,0.109],"Q2s":[0.5049,0.2453,0.1472],"Q2o":[0.476,0.1974,0.1058],"JJ":[0.7699,0.4798,0.2909],"JTs":[0.5707,0.3391,0.2231],"JTo":[0.5556,0.306,0.1905],"J9s":[0.5499,0.3028,0.1972],"J9o":[0.5292,0.275,0.1652],"J8s":[0.5363,0.3044,0.183],"J8o":[0.5187,0.2602,0.137],"J7s":[0.5222,0.2736,0.1553],"J7o":[0.5023,0.2325,0.1234],"J6s":[0.5022,0.2508,0.1518],"J6o":[0.4893,0.2102,0.113],"J5s":[0.498,0.2389,0.1467],"J5o":[0.4662,0.2102,0.1051],"J4s":[0.4858,0.2258,0.135],"J4o":[0.462,0.1944,0.0946],"J3s":[0.4771,0.2268,0.1346],"J3o":[0.4632,0.1893,0.1055],"J2s":[0.4846,0.2233,0.136],"J2o":[0.447,0.1913,0.0916],"TT":[0.7456,0.4511,0.2546],"T9s":[0.5407,0.3032,0.1966],"T9o":[0.5181,0.2851,0.1631],"T8s":[0.5234,0.2894,0.1693],"T8o":[0.4925,0.2474,0.1447],"T7s":[0.5074,0.279,0.1613],"T7o":[0.4707,0.2403,0.1268],"T6s":[0.4878,0.251,0.156],"T6o":[0.4586,0.2159,0.1092],"T5s":[0.4629,0.2238,0.1459],"T5o":[0.4407,0.1894,0.0996],"T4s":[0.4733,0.2202,0.1426],"T4o":[0.4381,0.1797,0.0966],"T3s":[0.4572,0.2288,0.1333],"T3o":[0.4326,0.1786,0.0937],"T2s":[0.4671,0.2142,0.1272],"T2o":[0.4178,0.1755,0.087],"99":[0.7183,0.4116,0.2241],"98s":[0.5116,0.2822,0.1779],"98o":[0.477,0.2563,0.1426],"97s":[0.4939,0.2743,0.1701],"97o":[0.468,0.2254,0.1284],"96s":[0.472,0.2467,0.1572],"96o":[0.4487,0.212,0.1115],"95s":[0.4502,0.2289,0.1433],"95o":[0.4146,0.1936,0.0941],"94s":[0.4375,0.2214,0.1307],"94o":[0.4006,0.1828,0.0873],"93s":[0.4233,0.2082,0.1221],"93o":[0.3906,0.173,0.0798],"92s":[0.4294,0.2004,0.1178],"92o":[0.3832,0.1588,0.0776],"88":[0.6848,0.3738,0.2067],"87s":[0.4794,0.2696,0.1677],"87o":[0.4482,0.237,0.131],"86s":[0.4608,0.2584,0.157],"86o":[0.436,0.2274,0.1116],"85s":[0.4303,0.2379,0.1455],"85o":[0.4114,0.2022,0.109],"84s":[0.4302,0.2149,0.1284],"84o":[0.3932,0.1644,0.0932],"83s":[0.3954,0.1998,0.1154],"83o":[0.373,0.1591,0.0747],"82s":[0.3938,0.1879,0.1198],"82o":[0.3782,0.1548,0.0791],"77":[0.6676,0.3474,0.1801],"76s":[0.4644,0.2434,0.1534],"76o":[0.4183,0.2206,0.1146],"75s":[0.4292,0.2403,0.1505],"75o":[0.4055,0.2018,0.1094],"74s":[0.4248,0.2146,0.1376],"74o":[0.3902,0.1756,0.1032],"73s":[0.3927,0.2001,0.1234],"73o":[0.3673,0.1587,0.0867],"72s":[0.3886,0.1799,0.1154],"72o":[0.3445,0.1388,0.0725],"66":[0.6251,0.3153,0.1645],"65s":[0.4249,0.2415,0.1584],"65o":[0.3967,0.1923,0.118],"64s":[0.4158,0.2152,0.1388],"64o":[0.3828,0.1872,0.1042],"63s":[0.3985,0.2008,0.1269],"63o":[0.373,0.1672,0.0873],"62s":[0.3817,0.1828,0.1166],"62o":[0.3407,0.1531,0.0781],"55":[0.5911,0.2905,0.1589],"54s":[0.415,0.2327,0.1462],"54o":[0.3806,0.1761,0.1178],"53s":[0.3987,0.2161,0.1405],"53o":[0.3817,0.17,0.1008],"52s":[0.3796,0.1918,0.1254],"52o":[0.35,0.1533,0.0869],"44":[0.5689,0.2531,0.1518],"43s":[0.3912,0.2079,0.1288],"43o":[0.3438,0.1637,0.0891],"42s":[0.3648,0.1909,0.123],"42o":[0.321,0.1517,0.0891],"33":[0.5443,0.2274,0.1451],"32s":[0.3584,0.1822,0.1146],"32o":[0.3327,0.147,0.077],"22":[0.4976,0.2162,0.1374]}')


def _cls(a, b):
    ra, rb = a >> 2, b >> 2
    if ra < rb:
        ra, rb = rb, ra
    if ra == rb:
        return RANKS[ra] * 2
    return RANKS[ra] + RANKS[rb] + ("s" if (a & 3) == (b & 3) else "o")


ALL = []  # (score, a, b)
for _a in range(52):
    for _b in range(_a + 1, 52):
        e = PF[_cls(_a, _b)]
        ALL.append((e[0] + e[1] * 1.6, _a, _b))
ALL.sort(reverse=True)
PCT = {}
COMBOS = []  # strongest first
for _i, (_s, _a, _b) in enumerate(ALL):
    PCT[(_a, _b)] = PCT[(_b, _a)] = (_i + 0.5) / len(ALL)
    COMBOS.append((_a, _b))
NC = len(COMBOS)


# ------------------------------------------------------------ opponent stats
class Stats:
    __slots__ = ("hands", "vpip", "pfr", "pf_raise_opps", "ftb_faced", "ftb_fold",
                 "pf_agg", "pf_pass", "agg_sd", "agg_sd_bluff", "allin")

    def __init__(self):
        self.hands = 0
        self.vpip = 0
        self.pfr = 0
        self.pf_raise_opps = 0
        self.ftb_faced = 0
        self.ftb_fold = 0
        self.pf_agg = 0     # postflop bets/raises
        self.pf_pass = 0    # postflop checks/calls
        self.agg_sd = 0
        self.agg_sd_bluff = 0
        self.allin = 0

    def r_vpip(self):
        return (self.vpip + 0.35 * 12) / (self.hands + 12)

    def r_pfr(self):
        return (self.pfr + 0.17 * 12) / (self.hands + 12)

    def r_ftb(self):
        return (self.ftb_fold + 0.45 * 8) / (self.ftb_faced + 8)

    def r_agg(self):
        return (self.pf_agg + 0.35 * 10) / (self.pf_agg + self.pf_pass + 10)

    def r_bluff(self):
        return (self.agg_sd_bluff + 0.3 * 5) / (self.agg_sd + 5)


def _connects(a, b, branks, bsuit, bmask):
    ra, rb = a >> 2, b >> 2
    if ra == rb or ra in branks or rb in branks:
        return True
    sa, sb = a & 3, b & 3
    if sa == sb and bsuit[sa] >= 2:
        return True
    if bsuit[sa] >= 3 or bsuit[sb] >= 3:
        return True
    if DRAW4[bmask | (1 << ra) | (1 << rb)] and not DRAW4[bmask]:
        return True
    return False


# ------------------------------------------------------------------- agent
class Agent:
    def __init__(self):
        self.rng = random.Random()
        self.stats = {}
        self.seat = None
        self.used = 0.0
        self.n = 8

    def on_table_start(self, info):
        self.seat = info.get("seat")
        self.n = info.get("num_players", 8)
        self.total_hands = info.get("hands", 1000)

    # ------------------------------------------------------------- tracking
    def _st(self, seat):
        st = self.stats.get(seat)
        if st is None:
            st = self.stats[seat] = Stats()
        return st

    def on_hand_end(self, summary):
        try:
            self._learn(summary)
        except Exception:
            pass

    def _learn(self, summary):
        hist = summary.get("history") or []
        seats = set(h["seat"] for h in hist)
        bets = {}
        street = "preflop"
        cur = 0
        pf_raised = False
        vp, pr, agg_post = set(), set(), set()
        for h in hist:
            s, a, amt = h["seat"], h["action"], h.get("amount") or 0
            if h["street"] != street:
                street = h["street"]
                bets = {}
                cur = 0
            mine = bets.get(s, 0)
            facing = cur > mine
            if a in ("small_blind", "big_blind"):
                bets[s] = amt
                cur = max(cur, amt)
                continue
            st = self._st(s)
            if street == "preflop":
                if a in ("call", "raise"):
                    vp.add(s)
                if a == "raise":
                    pr.add(s)
                    pf_raised = True
            else:
                if facing:
                    st.ftb_faced += 1
                    if a == "fold":
                        st.ftb_fold += 1
                if a == "raise":
                    st.pf_agg += 1
                    agg_post.add(s)
                elif a in ("check", "call"):
                    st.pf_pass += 1
            if a == "raise":
                bets[s] = amt
                cur = max(cur, amt)
                if amt >= 1900:
                    st.allin += 1
            elif a == "call":
                bets[s] = mine + amt
        for s in seats:
            st = self._st(s)
            st.hands += 1
            if s in vp:
                st.vpip += 1
            if s in pr:
                st.pfr += 1
        shown = summary.get("shown") or {}
        board = [card_int(c) for c in summary.get("board") or []]
        if len(board) == 5:
            branks = set(c >> 2 for c in board)
            for k, cards in shown.items():
                s = int(k)
                if s not in agg_post:
                    continue
                hc = [card_int(c) for c in cards]
                st = self._st(s)
                st.agg_sd += 1
                score = eval7(hc + board)
                cat = score >> 20
                conn = cat >= 4 or (hc[0] >> 2) == (hc[1] >> 2) or (hc[0] >> 2) in branks or (hc[1] >> 2) in branks
                if not conn:
                    st.agg_sd_bluff += 1

    # ------------------------------------------------------------ ranges
    def _range_for(self, seat, hist, board, bctx):
        """Return (combos_strong, combos_weak, weak_weight) describing seat's range."""
        st = self._st(seat)
        vpip, pfr = st.r_vpip(), st.r_pfr()
        raises_before = 0
        my_raises = 0
        called_raise = False
        limped = False
        post_agg = False
        post_agg_this = False
        post_called = False
        street = board_street(len(board))
        for h in hist:
            a = h["action"]
            if h["street"] == "preflop":
                if a == "raise":
                    if h["seat"] == seat:
                        my_raises += 1
                        if raises_before >= 1:
                            my_raises += 1
                    raises_before += 1
                elif a == "call" and h["seat"] == seat:
                    if raises_before:
                        called_raise = True
                    else:
                        limped = True
            elif h["seat"] == seat:
                if a == "raise":
                    post_agg = True
                    if h["street"] == street:
                        post_agg_this = True
                elif a == "call":
                    post_called = True
        if my_raises >= 3:
            thr = pfr * 0.22
        elif my_raises == 2:
            thr = pfr * 0.4
        elif my_raises == 1:
            thr = pfr
        elif called_raise:
            thr = min(vpip * 0.75, 0.45)
        elif limped:
            thr = vpip
        else:
            thr = 1.0
        thr = max(0.025, min(1.0, thr))
        k = max(8, int(thr * NC))
        rng = COMBOS[:k]
        if not board or not (post_agg or post_called):
            return rng, None, 0.0
        branks, bsuit, bmask = bctx
        strong, weak = [], []
        for ab in rng:
            if _connects(ab[0], ab[1], branks, bsuit, bmask):
                strong.append(ab)
            else:
                weak.append(ab)
        if post_agg:
            keep = st.r_bluff() * (0.6 if post_agg_this and street != "flop" else 1.0)
            keep = max(0.05, min(1.0, keep * 1.2))
        else:
            keep = max(0.12, min(1.0, 1.0 - st.r_ftb() * 1.2))
        if not strong:
            return weak, None, 0.0
        return strong, weak, keep

    # ------------------------------------------------------------ equity
    def equity(self, hole, board, ranges, budget):
        rng = self.rng.random
        dead = set(hole) | set(board)
        deck = [c for c in range(52) if c not in dead]
        L = len(deck)
        need = 5 - len(board)
        hp = CP[hole[0]] * CP[hole[1]]
        bp0 = 1
        for c in board:
            bp0 *= CP[c]
        plans = []
        for strong, weak, keep in ranges:
            if weak:
                pw = keep * len(weak) / (keep * len(weak) + len(strong))
            else:
                pw = 0.0
            plans.append((strong, len(strong), weak, len(weak) if weak else 0, pw))
        t_end = time.perf_counter() + budget
        wins = 0.0
        n = 0
        while True:
            if (n & 7) == 0 and n >= 24 and time.perf_counter() > t_end:
                break
            if n >= 3000:
                break
            used = set(dead)
            opp = []
            ok = True
            for strong, ls, weak, lw, pw in plans:
                for _ in range(12):
                    if lw and rng() < pw:
                        a, b = weak[int(rng() * lw)]
                    else:
                        a, b = strong[int(rng() * ls)]
                    if a not in used and b not in used:
                        break
                else:
                    ok = False
                    break
                used.add(a)
                used.add(b)
                opp.append((a, b))
            if not ok:
                n += 1
                continue
            bd = list(board)
            while len(bd) < 5:
                c = deck[int(rng() * L)]
                if c not in used:
                    used.add(c)
                    bd.append(c)
            bp = bp0
            for c in bd[len(board):]:
                bp *= CP[c]
            sc = [0, 0, 0, 0]
            sm = [0, 0, 0, 0]
            for c in bd:
                s = c & 3
                sc[s] += 1
                sm[s] |= 1 << (c >> 2)
            fs = -1
            for s in range(4):
                if sc[s] >= 3:
                    fs = s
            me = RANK7[bp * hp]
            if fs >= 0:
                cnt = sc[fs] + ((hole[0] & 3) == fs) + ((hole[1] & 3) == fs)
                if cnt >= 5:
                    m = sm[fs]
                    if (hole[0] & 3) == fs:
                        m |= 1 << (hole[0] >> 2)
                    if (hole[1] & 3) == fs:
                        m |= 1 << (hole[1] >> 2)
                    me = FLUSH[m]
            best = True
            ties = 0
            for a, b in opp:
                s2 = RANK7[bp * CP[a] * CP[b]]
                if fs >= 0:
                    cnt = sc[fs] + ((a & 3) == fs) + ((b & 3) == fs)
                    if cnt >= 5:
                        m = sm[fs]
                        if (a & 3) == fs:
                            m |= 1 << (a >> 2)
                        if (b & 3) == fs:
                            m |= 1 << (b >> 2)
                        s2 = FLUSH[m]
                if s2 > me:
                    best = False
                    break
                if s2 == me:
                    ties += 1
            if best:
                wins += 1.0 / (ties + 1)
            n += 1
        return wins / max(n, 1), n

    # ------------------------------------------------------------ act
    def act(self, state):
        t0 = time.perf_counter()
        try:
            out = self._act(state)
        except Exception:
            out = None
        self.used += time.perf_counter() - t0
        if out is None:
            return {"action": "check" if "check" in state["legal_actions"] else "fold"}
        return out

    def table_vpip(self, seats):
        if not seats:
            return 0.35
        return sum(self._st(s).r_vpip() for s in seats) / len(seats)

    def _budget(self, hand_no):
        left = 8.0 - self.used
        hands_left = max(1, self.total_hands - hand_no + 1) if hasattr(self, "total_hands") else 500
        b = left / (hands_left * 0.9)
        return max(0.0006, min(0.0028, b))

    def _raise(self, state, target):
        lo, hi = state["min_raise_to"], state["max_raise_to"]
        if lo is None:
            return None
        me = state["seat"]
        total = state["stacks"][me] + state["bets"][me]
        target = int(target)
        if target >= hi * 0.72 or target >= total * 0.72:
            target = hi
        target = max(lo, min(hi, target))
        return {"action": "raise", "amount": target}

    def _act(self, state):
        legal = state["legal_actions"]
        me = state["seat"]
        if self.seat is None:
            self.seat = me
        n = len(state["stacks"])
        self.n = n
        hole = [card_int(c) for c in state["hole_cards"]]
        board = [card_int(c) for c in state["board"]]
        pot = state["pot"]
        to_call = state["to_call"]
        bb = state["big_blind"] or 20
        bets = state["bets"]
        cur = max(bets)
        folded = state["folded"]
        hist = state["history"]
        live = [i for i in range(n) if not folded[i] and i != me]
        can_raise = "raise" in legal
        budget = self._budget(state.get("hand_number", 1))

        bctx = None
        if board:
            branks = set(c >> 2 for c in board)
            bsuit = [0, 0, 0, 0]
            bmask = 0
            for c in board:
                bsuit[c & 3] += 1
                bmask |= 1 << (c >> 2)
            bctx = (branks, bsuit, bmask)

        if not board:
            return self._preflop(state, hole, live, hist, budget, bb, pot, to_call, cur, can_raise, legal)

        ranges = [self._range_for(s, hist, board, bctx) for s in live]
        eq, _ = self.equity(hole, board, ranges, budget)
        return self._postflop(state, eq, live, hist, bb, pot, to_call, cur, can_raise, legal)

    # ------------------------------------------------------------ preflop
    def _preflop(self, state, hole, live, hist, budget, bb, pot, to_call, cur, can_raise, legal):
        me = state["seat"]
        n = len(state["stacks"])
        button = state["button"]
        pct = PCT[(hole[0], hole[1])]
        raises = [h for h in hist if h["action"] == "raise"]
        limpers = len(set(h["seat"] for h in hist if h["action"] == "call")) if not raises else 0
        rel = (me - button) % n
        if n == 2:
            behind = 1 if rel == 0 else 0
        elif rel == 0:
            behind = 2
        elif rel == 1:
            behind = 1
        elif rel == 2:
            behind = 0
        else:
            behind = n - rel + 2
        acted = set(h["seat"] for h in hist if h["action"] not in ("small_blind", "big_blind"))
        behind_seats = [s for s in live if s not in acted]

        if not raises:
            base = {0: 0.0, 1: 0.48, 2: 0.50, 3: 0.34, 4: 0.26, 5: 0.22, 6: 0.19}.get(behind, 0.17)
            size = 3.0
            av = self.table_vpip(live)
            if behind_seats:
                avb = sum(self._st(s).r_vpip() for s in behind_seats) / len(behind_seats)
                if avb < 0.22:
                    base *= 1.4
            if av > 0.42:
                base *= 1.2
                size = 4.0
            if av > 0.55:
                size = 5.0
            if limpers:
                base *= 0.9
            base = min(base, 0.6)
            if to_call == 0:  # big blind, limped pot
                if can_raise and pct <= 0.18:
                    return self._raise(state, cur + bb * (size + limpers))
                return {"action": "check"}
            if pct <= base and can_raise:
                return self._raise(state, bb * (size + limpers))
            if limpers == 0 and rel == 1 and pct <= 0.55 and not can_raise:
                return {"action": "call"}
            return {"action": "fold"}

        # facing a raise: equity vs the ranges of everyone who put money in
        involved = [s for s in live if s in acted or any(h["seat"] == s and h["action"] in ("raise", "call") for h in hist)]
        if not involved:
            involved = live[:1]
        ranges = [self._range_for(s, hist, [], None) for s in involved]
        # quick prune: very weak hands facing a raise fold without simulation
        if pct > 0.55 and to_call > bb:
            return {"action": "fold"} if "fold" in legal else {"action": "check"}
        eq, _ = self.equity(hole, [], ranges, budget)
        k = len(involved)
        po = to_call / float(pot + to_call)
        margin = 0.03 + 0.02 * len([s for s in behind_seats if s not in involved])
        if rel in (1, 2):
            margin += 0.02
        val = 0.60 / (k ** 0.55)
        if can_raise and eq >= val:
            n_raises = len(raises)
            mult = 3.0 if n_raises == 1 else 2.4
            target = cur * mult + 10 * len([h for h in hist if h["action"] == "call"])
            return self._raise(state, target)
        if eq >= po + margin:
            return {"action": "call"}
        return {"action": "fold"}

    # ------------------------------------------------------------ postflop
    def _postflop(self, state, eq, live, hist, bb, pot, to_call, cur, can_raise, legal):
        me = state["seat"]
        k = max(1, len(live))
        street = state["street"]
        sts = [self._st(s) for s in live]
        avg_ftb = sum(s.r_ftb() for s in sts) / k
        avg_vpip = sum(s.r_vpip() for s in sts) / k
        station = avg_ftb < 0.28 and avg_vpip > 0.45
        # did we take the initiative preflop?
        pf_aggr = False
        for h in hist:
            if h["street"] == "preflop" and h["action"] == "raise":
                pf_aggr = h["seat"] == me
        vt = 0.54 / (k ** 0.62)
        if station:
            vt -= 0.06
        if street == "river":
            vt += 0.03
        if to_call == 0:
            if not can_raise:
                return {"action": "check"}
            hu_strength = eq ** (1.0 / k) if k > 1 else eq
            if eq >= vt:
                frac = 0.6
                if hu_strength > 0.82:
                    frac = 0.85
                if station:
                    frac *= 1.35
                return self._raise(state, max(bb, pot * frac))
            # bluff / semi-bluff only heads-up against folders, capped
            if k == 1 and avg_ftb > 0.52 and not station:
                p = 0.35 + (avg_ftb - 0.52) * 1.5
                if pf_aggr and street == "flop":
                    p += 0.25
                if street == "river":
                    p -= 0.15
                if self.rng.random() < min(0.8, p):
                    return self._raise(state, max(bb, pot * 0.5))
            return {"action": "check"}

        po = to_call / float(pot + to_call)
        # players still to act behind us this street
        acted_this = set(h["seat"] for h in hist if h["street"] == street)
        behind = len([s for s in live if s not in acted_this])
        margin = 0.02 + 0.03 * behind
        rt = 0.74 / (k ** 0.5)
        if station:
            rt -= 0.05
        if street == "river":
            rt += 0.03
        if can_raise and eq >= rt:
            return self._raise(state, cur + (pot + to_call) * 0.9)
        if eq >= po + margin:
            return {"action": "call"}
        return {"action": "fold"}


def board_street(n):
    return {0: "preflop", 3: "flop", 4: "turn", 5: "river"}.get(n, "flop")
