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
PF = json.loads('__PF__')
_RE = json.loads('__RE__')
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
                 "limp", "rfi_o", "lf_o", "lf_f", "sd_r", "sd_ok", "bx_n", "bx_s", "cb_o", "cb")

    def __init__(self):
        for k in self.__slots__:
            setattr(self, k, 0)
        self.fo = [0, 0, 0, 0, 0]   # faced a bet of 35%+ of the pot, by line (see line_cat)
        self.ff = [0, 0, 0, 0, 0]   # ... and folded

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
        self.total_hands = 1000
        self.hands_seen = 0
        self.errors = 0
        self.cap = 200

    def on_table_start(self, info):
        self.total_hands = info.get("hands", 1000) or 1000

    # ------------------------------------------------------------- learning
    def on_hand_end(self, summary):
        try:
            self._learn(summary)
        except Exception:
            if DEBUG:
                import traceback
                traceback.print_exc()
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
        for h in hist:
            s = h["seat"]
            a = h["action"]
            amt = h.get("amount") or 0
            seats.add(s)
            if a == "small_blind":
                sbs = s
            elif a == "big_blind":
                bbs = s
            if h["street"] != street:
                street = h["street"]
                bets = {}
                cur = 0
                checked = set()
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
                if a == "raise":
                    pr.add(s)
                    vp.add(s)
                    if raises == 0:
                        first_raiser = s
                    raises += 1
                    if amt >= 800:
                        S.shove += 1
                elif a == "call":
                    vp.add(s)
            else:
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

    def _act(self, state, t0):
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
                if n3 >= 3 and f3 >= 0.78:
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
            if e >= (0.40 if ip else 0.43) and price <= 10:
                return CALL
            if pair and price <= 6:
                return CALL
            if cls in ("KQs", "AJs", "ATs", "JTs", "QJs", "T9s") and ip and price <= 6:
                return CALL
            return fold_or_check()

        # 4-bets and beyond, or a 3-bet in front of us before we acted
        if cls in ("AA", "KK"):
            if can_raise:
                if my_raises >= 1 or R >= 12 * bb:
                    return {"action": "all_in"}
                return self._raise_to(state, R * 2.4, commit=0.4)
            return call_or_check()
        if my_raises >= 1:
            if e >= 0.56 and can_raise:
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
            eq = self._mc(h0, h1, board, dead, tiers, t0 + self._budget(state), bp, sc, sm)

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
        if can_raise and eq >= (0.52 if nofold else 0.62) and hi is not None:
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
        if not river and c < mystack:
            margin += 0.03
            if mydraw and c <= 0.25 * mystack:
                margin -= 0.05
        if eq >= need + margin:
            return CALL
        return FOLD

    def _budget(self, state):
        left = 8.0 - self.used
        hands_left = max(1, self.total_hands - state.get("hand_number", 1) + 1)
        b = left / (hands_left * 0.45)
        return 0.0003 if b < 0.0003 else (0.0016 if b > 0.0016 else b)

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
