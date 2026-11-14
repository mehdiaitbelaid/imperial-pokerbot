"""Shared parametric agent for the Table D sparring replicas.

A replica is `class Agent(Base)` with a parameter dict `P`; DEFAULTS below documents every key.
The strategy is FIXED: no opponent modelling and no learning during a round, only randomness
(one exception by design: a replica may draw one of several `variants` per round, as WBot's open
size did from round to round).

How a decision is made
  preflop   The hand's percentile among the 169 starting hands (plus a small jitter) is compared
            with the measured frequencies of the spot: first-in raise / limp by position, reply
            to limpers, reply to one raise by own position (blind defence by open size, squeeze
            spot, other), reply to a 3-bet after opening, to a 4-bet after 3-betting, to a 5-bet.
            The best hands of the current range raise, the next ones call; `*_rand` parameters
            give a share of the raises to random hands (Anton's 3-bets).  Sizes are the measured
            ones.  A raise that puts the stack in needs a premium hand (`shove_max`).
  postflop  The hand is put in one of the profiles' classes: value = two pair or better made
            with the hole cards, medium = top pair / overpair, weak = lower pair, draw = flush
            draw or four to a straight, air (split in "ace high or two overcards" and the rest).
            Nothing to call: the line's measured bet frequency (A c-bet / barrel, D donk, S bet
              when checked to, L lead; heads up or multiway) and the measured table "classes
              shown down after each bet size" give P(bet | class) and P(size | class).
            Facing a bet: measured fold / call / raise of the node (first bet, second barrel,
              third barrel, river bet after a checked turn, stab after it missed a c-bet; having
              checked first or not; heads up or multiway), moved by the size bucket of the bet.
              Folds come from the weakest classes (`fw`), raises follow the measured class mix of
              its raises; no check-raise on streets where the profile has none.
            Raised after its own bet: measured fold / call / re-raise for the size it bet.
  A target frequency becomes per-class probabilities through the class mix of the replica's own
  range at that node: tabled/_nodes.py, counted once in self-play by tabled/measure.py --nodes
  and then frozen (without the file built-in priors are used).

Stdlib only; a decision takes a few tens of microseconds; act() always returns a legal action.
"""
import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
try:
    from _nodes import NODES as _NODES          # frozen class mixes of each replica's nodes
except Exception:                               # file absent: priors only
    _NODES = {}

RANKS = "23456789TJQKA"
_RV = {r: i for i, r in enumerate(RANKS)}
CLS5 = ("air", "draw", "weak", "medium", "value")
# fine classes used internally: 0 air (low) 1 air (ace high / two overcards) 2 draw 3 weak 4 medium 5 value
K = 6
FINE_OF = {"air": (0, 1), "draw": (2,), "weak": (3,), "medium": (4,), "value": (5,)}
CLS5_OF_FINE = ("air", "air", "draw", "weak", "medium", "value")

# 169 starting hands, best first (equity against 1, 3 and 6 random hands blended, small pairs lifted)
ORDER = ("AA KK QQ JJ TT AKs AQs AKo 99 AJs KQs KJs 88 AQo ATs AJo QJs KTs A9s KQo QTs ATo A8s K9s 77 "
         "KJo A7s JTs 66 A4s A6s A5s KTo A9o Q9s QJo 55 K8s A3s K7s J9s JTo QTo T9s A2s 44 K9o A8o Q8s J8s "
         "K6s A7o K5s 33 A5o T8s Q7s 98s Q9o J9o K4s 22 K3s T9o Q6s A4o K2s T7s A6o K8o 97s K7o J7s A3o 87s "
         "Q5s A2o Q8o Q4s J6s T6s K6o Q2s Q3s J8o 96s 86s K5o T8o J5s 98o 76s 65s Q7o K4o 75s J7o Q6o T5s "
         "85s J4s 95s T4s J3s J2s T7o 54s Q5o 87o T3s 97o K3o K2o Q4o T2s 94s 74s 53s 64s J6o 84s 86o Q3o "
         "T6o 96o 93s J5o 76o Q2o 43s 92s 63s 73s J3o J4o 65o 83s 75o 85o 82s 52s T5o J2o 42s T4o 95o 62s "
         "T3o 72s 54o 94o 64o 32s T2o 74o 84o 53o 93o 63o 92o 43o 82o 73o 83o 52o 42o 62o 72o 32o").split()


def _build_pct():
    out, cum = {}, 0
    for name in ORDER:
        hi, lo = _RV[name[0]], _RV[name[1]]
        if hi == lo:
            n, key = 6, (hi, lo, False)
        elif name[2] == "s":
            n, key = 4, (hi, lo, True)
        else:
            n, key = 12, (hi, lo, False)
        out[key] = (cum + n / 2.0) / 1326.0
        cum += n
    return out


PCT = _build_pct()            # (high rank, low rank, suited) -> share of hands that are better


def hand_pct(hole):
    a, b = _RV[hole[0][0]], _RV[hole[1][0]]
    if a < b:
        a, b = b, a
    return PCT[(a, b, a != b and hole[0][1] == hole[1][1])]


def pos_name(rel, n):
    """Seat name from (seat - button) % n, as in the profiles."""
    if rel == 0:
        return "BTN"
    if rel == 1:
        return "SB"
    if rel == 2:
        return "BB"
    fe = n - rel
    return {1: "CO", 2: "HJ", 3: "MP"}.get(fe, "UTG" if rel == 3 else "UTG+1")


# ------------------------------------------------------------------ hand classes
def _mk_straight():
    t = bytearray(8192)
    for m in range(8192):
        x = (m << 1) | ((m >> 12) & 1)
        for lo in range(10):
            if (x >> lo) & 31 == 31:
                t[m] = 1
                break
    return bytes(t)


_STRAIGHT = _mk_straight()
_POP = bytes(bin(i).count("1") for i in range(32))


def _cat(cards):
    """Hand category of up to 7 cards: 0 high card .. 8 straight flush."""
    cnt = [0] * 13
    mask = 0
    sm = {}
    sc = {}
    for c in cards:
        r = _RV[c[0]]
        s = c[1]
        cnt[r] += 1
        mask |= 1 << r
        sm[s] = sm.get(s, 0) | (1 << r)
        sc[s] = sc.get(s, 0) + 1
    fl = None
    for s in sc:
        if sc[s] >= 5:
            fl = s
    if fl is not None and _STRAIGHT[sm[fl]]:
        return 8
    mx = max(cnt)
    if mx == 4:
        return 7
    if mx == 3 and (cnt.count(3) >= 2 or 2 in cnt):
        return 6
    if fl is not None:
        return 5
    if _STRAIGHT[mask]:
        return 4
    if mx == 3:
        return 3
    if mx == 2:
        return 2 if cnt.count(2) >= 2 else 1
    return 0


def _has_draw(hole, board):
    """Flush draw or four to a straight (gutshots count) that uses a hole card."""
    sc = {}
    m = hm = 0
    for c in board:
        sc[c[1]] = sc.get(c[1], 0) + 1
        m |= 1 << _RV[c[0]]
    for c in hole:
        sc[c[1]] = sc.get(c[1], 0) + 1
        hm |= 1 << _RV[c[0]]
    for c in hole:
        if sc[c[1]] == 4:
            return True
    m |= hm
    m = (m << 1) | ((m >> 12) & 1)
    hm = (hm << 1) | ((hm >> 12) & 1)
    for lo in range(10):
        if _POP[(m >> lo) & 31] == 4 and (hm >> lo) & 31:
            return True
    return False


def classify(hole, board):
    """Fine class 0..5 of a hand on a board, with the profiles' definitions."""
    mine = _cat(hole + board)
    bc = _cat(board)
    if (mine >= 4 and mine > bc) or (mine == 3 and bc < 3) or (mine == 2 and bc < 1):
        return 5
    h0, h1 = _RV[hole[0][0]], _RV[hole[1][0]]
    btop = 0
    for c in board:
        r = _RV[c[0]]
        if r > btop:
            btop = r
    if (mine == 1 and bc == 0) or (mine == 2 and bc == 1):
        if h0 == h1:
            return 4 if h0 > btop else 3
        return 4 if (h0 == btop or h1 == btop) else 3
    if len(board) < 5 and _has_draw(hole, board):
        return 2
    if h0 == 12 or h1 == 12 or (h0 > btop and h1 > btop):
        return 1
    return 0


def texture(flop):
    rs = sorted((_RV[c[0]] for c in flop), reverse=True)
    if len(set(rs)) < 3:
        return "paired"
    if len(set(c[1] for c in flop)) == 1:
        return "monotone"
    if rs[0] <= 7 and rs[0] - rs[2] <= 4:
        return "low connected"
    if rs[0] >= 10:
        return "high card"
    return "other"


def bucket(x):
    """Size bucket of a bet as a share of the pot before it."""
    if x < 0.4:
        return "<40%"
    if x <= 0.75:
        return "40-75%"
    if x <= 1.12:
        return "75-110%"
    return "overbet"


BUCKETS = ("<40%", "40-75%", "75-110%", "overbet")
_PREV = {"flop": "preflop", "turn": "flop", "river": "turn"}


# ------------------------------------------------------------------ reading the hand so far
def pre_ctx(hist, me):
    """Preflop situation before `me` acts: (raises, limpers, callers since the last raise,
    opener seat, open raise-to, my voluntary actions as (action, raises before it))."""
    raises = limpers = callers = 0
    opener = -1
    open_amt = 0
    mine = []
    for e in hist:
        if e.get("street") != "preflop":
            continue
        a = e.get("action")
        s = e.get("seat")
        if a == "raise":
            if s == me:
                mine.append(("raise", raises))
            if raises == 0:
                opener = s
                open_amt = e.get("amount") or 0
            raises += 1
            callers = 0
        elif a == "call":
            if s == me:
                mine.append(("call", raises))
            if raises == 0:
                limpers += 1
            else:
                callers += 1
        elif a == "check" and s == me:
            mine.append(("check", raises))
    return raises, limpers, callers, opener, open_amt, mine


def post_ctx(hist, me, street):
    """Postflop situation before `me` acts on `street`.

    Returns a dict:
      role        line when there is nothing to call: "A" I made the last bet or raise of the
                  previous street (c-bet / barrel), "D" that aggressor is another seat still to
                  act behind me (donk), "S" somebody already checked to me, "L" I am first
      checked     I already checked on this street
      my_raises   bets or raises I made on this street; my_first: I made the street's first bet
      nraises     bets and raises on this street so far; bettor: the last one's seat
      ms          I was the previous street's aggressor, checked, and now face a bet
      node        key of the facing-a-single-bet node: flop, turn_b2 (second barrel: I called the
                  flop bet of the same seat), turn, river_b3 (third barrel), river_ct (river bet
                  after a turn without a bet), river, each with _x (I checked first on this
                  street) or _n, or <street>_ms (I was the aggressor, checked, and face a stab)
      folds_now   seats that folded on this street
      my_bet      (amount, pot before, current bet before, my chips in before) of my last bet or
                  raise on this street
      pa          seat that made the last bet or raise of the previous street (None: nobody)
    """
    prev = _PREV.get(street, "turn")
    pa = None
    out = set()
    cf = {}
    turn_raise = False
    cur = None
    rs = 0
    lr = None
    checked = False
    my_raises = 0
    my_first = False
    others_first = False
    i_acted = False
    acted = set()
    folds_now = 0
    pot = 0
    sbet = {}
    top = 0
    my_bet = None
    for e in hist:
        a = e.get("action")
        s = e.get("seat")
        es = e.get("street")
        amt = e.get("amount") or 0
        if es != cur:
            cur = es
            rs = 0
            lr = None
            sbet = {}
            top = 0
        if a == "raise":
            if es == prev:
                pa = s
            if es == "turn":
                turn_raise = True
            if es == street and s == me:
                my_raises += 1
                if rs == 0:
                    my_first = True
                my_bet = (amt, pot, top, sbet.get(s, 0))
            pot += amt - sbet.get(s, 0)
            sbet[s] = amt
            top = amt
        elif a == "call":
            if s == me and rs == 1 and es not in cf and lr != me:
                cf[es] = lr
            pot += amt
            sbet[s] = sbet.get(s, 0) + amt
        elif a == "fold":
            out.add(s)
            if s == me and rs == 1 and es not in cf:
                cf[es] = None
            if es == street:
                folds_now += 1
        elif a in ("small_blind", "big_blind"):
            pot += amt
            sbet[s] = sbet.get(s, 0) + amt
            if sbet[s] > top:
                top = sbet[s]
        if es == street:
            if s == me:
                i_acted = True
                if a == "check":
                    checked = True
            else:
                if not i_acted:
                    others_first = True
            acted.add(s)
        if a == "raise":
            if s == me and rs == 1 and es not in cf:
                cf[es] = None                     # I raised the first bet: not a call
            rs += 1
            lr = s
    if cur != street:
        rs = 0
        lr = None
    if pa == me:
        role = "A"
    elif pa is not None and pa not in out and pa not in acted:
        role = "D"
    else:
        role = "S" if others_first else "L"
    ms = pa == me and checked
    if street == "flop":
        node = "flop"
    elif street == "turn":
        node = "turn_b2" if lr is not None and cf.get("flop") == lr else "turn"
    else:
        if lr is not None and cf.get("flop") == lr and cf.get("turn") == lr:
            node = "river_b3"
        elif not turn_raise:
            node = "river_ct"
        else:
            node = "river"
    if ms:
        node = street + "_ms"
    else:
        node += "_x" if checked else "_n"
    return {"role": role, "checked": checked, "my_raises": my_raises, "my_first": my_first,
            "nraises": rs, "bettor": lr, "ms": ms, "node": node, "folds_now": folds_now,
            "my_bet": my_bet, "pa": pa}


# ------------------------------------------------------------------ frequency -> per class
def solve(pi, g, f, cap=None):
    """Per-class probabilities p with sum(pi*p) = f and p proportional to g/pi, capped."""
    n = len(pi)
    if cap is None:
        cap = [1.0] * n
    top = sum(pi[c] * cap[c] for c in range(n))
    if f <= 0.0 or top <= 0.0:
        return [0.0] * n
    if f >= top - 1e-9:
        return list(cap)
    r = [(g[c] / pi[c]) if pi[c] > 1e-9 else 0.0 for c in range(n)]
    if max(r) <= 0.0:
        return [cap[c] * f / top for c in range(n)]

    def tot(lam):
        return sum(pi[c] * min(cap[c], lam * r[c]) for c in range(n))

    hi = 1.0
    k = 0
    while tot(hi) < f and k < 60:
        hi *= 2.0
        k += 1
    lo = 0.0
    for _ in range(48):
        mid = 0.5 * (lo + hi)
        if tot(mid) < f:
            lo = mid
        else:
            hi = mid
    return [min(cap[c], hi * r[c]) for c in range(n)]


def _logit(p):
    p = 0.01 if p < 0.01 else 0.99 if p > 0.99 else p
    return p / (1.0 - p)


def _shift(p, num, den):
    """p moved by the odds ratio num/den."""
    o = _logit(p) * _logit(num) / _logit(den)
    return o / (1.0 + o)


_PRIOR = {
    "B|flop": [0.24, 0.20, 0.12, 0.20, 0.17, 0.07],
    "B|turn": [0.20, 0.15, 0.14, 0.22, 0.19, 0.10],
    "B|river": [0.27, 0.14, 0.0, 0.25, 0.21, 0.13],
    "F|flop": [0.24, 0.20, 0.12, 0.21, 0.16, 0.07],
    "F|turn": [0.14, 0.12, 0.14, 0.27, 0.22, 0.11],
    "F|river": [0.17, 0.12, 0.0, 0.29, 0.26, 0.16],
}

# ------------------------------------------------------------------ preflop range bookkeeping
# A range is a piecewise constant density over the hand percentile: [(upper bound, density), ...]
_FULL = [(1.0, 1.0)]


def _rank_of(rng, p):
    """Share of the range that is better than percentile p."""
    tot = below = lo = 0.0
    for b, d in rng:
        tot += (b - lo) * d
        if p >= b:
            below += (b - lo) * d
        elif p > lo:
            below += (p - lo) * d
        lo = b
    return below / tot if tot > 0 else p


def _inv(rng, u):
    tot = lo = 0.0
    for b, d in rng:
        tot += (b - lo) * d
        lo = b
    target = u * tot
    acc = lo = 0.0
    for b, d in rng:
        seg = (b - lo) * d
        if d > 0 and acc + seg >= target:
            return lo + (target - acc) / d
        acc += seg
        lo = b
    return 1.0


def _narrow(rng, u0, u1, d_above):
    """Keep the hands ranked between u0 and u1 of the range, plus a share d_above of the worse ones."""
    p0, p1 = _inv(rng, u0), _inv(rng, u1)
    out = []
    lo = 0.0
    for b, d in rng:
        for cut in (p0, p1):
            if lo < cut < b:
                out.append((cut, d * (0.0 if lo < p0 else 1.0 if lo < p1 else d_above)))
                lo = cut
        if b > lo:
            out.append((b, d * (0.0 if lo < p0 else 1.0 if lo < p1 else d_above)))
            lo = b
    return out or _FULL


# ------------------------------------------------------------------ parameters
ALLIN = 99.0          # bet "size" meaning all-in

DEFAULTS = dict(
    # ---- preflop ---------------------------------------------------------------------------
    # first in (nobody has entered): position -> (raise, limp) frequencies
    fi={"UTG": (0.15, 0.0), "UTG+1": (0.16, 0.0), "MP": (0.20, 0.0), "HJ": (0.25, 0.0),
        "CO": (0.36, 0.0), "BTN": (0.54, 0.0), "SB": (0.56, 0.05)},
    # open sizes in big blinds: position (or "*") -> [(size, weight)]; a dict {"top": share of
    # the opening range (strongest first), "top_sizes": [...], "rest": [...]} makes the size
    # depend on the hand
    open_bb={"*": [(2.5, 1.0)]},
    open_scale={},                       # position -> multiplier on the chosen size
    vs_limp=(0.07, 0.28),                # facing limpers, first action: (call, raise)
    bb_iso=0.15,                         # big blind raises limpers this often (else checks)
    iso=("open", 1.0),                   # iso raise = base bb ("open" = own open size) + x per limper
    limp_fold=0.60,                      # limped, then raised: fold ...
    limp_rr=0.0,                         # ... or re-raise (to 3x)
    # facing ONE raise, first action: (call, 3-bet)
    # blinds against a CO / BTN / SB open with no caller, by open size <=2.25 ("s"), <=3 ("m"), more ("l")
    bd={"SB": {"s": (0.20, 0.10), "m": (0.14, 0.11), "l": (0.10, 0.09)},
        "BB": {"s": (0.42, 0.10), "m": (0.32, 0.11), "l": (0.24, 0.09)}},
    sq={"IP": (0.15, 0.05), "SB": (0.15, 0.05), "BB": (0.30, 0.05)},     # at least one caller already
    # other opens, by own position ("IP" = any seat outside the blinds without its own entry)
    vs1={"IP": (0.10, 0.07), "SB": (0.08, 0.06), "BB": (0.20, 0.06)},
    big_open=((0.8, 0.5), (0.4, 0.3)),   # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
    tb_rand=0.15,                        # share of 3-bets made with a random hand instead of the best ones
    tb_mult={"ip": [((3.0, 0.0), 1.0)], "oop": [((3.0, 0.0), 1.0)]},   # (multiple of the raise, + bb)
    f3b=(0.61, 0.25, 0.14),              # opened and was 3-bet: fold, call, 4-bet
    fb_rand=0.0,                         # share of those 4-bets made with a random hand of the opening range
    fourbet=[(2.3, 1.0)],                # 4-bet sizes: multiple of the 3-bet, or "allin"
    cold3=(0.04, 0.03),                  # facing a 3-bet without having opened: (call, 4-bet), of all hands
    cold_rand=0.0,                       # share of those cold 4-bets made with a random hand
    call_then_3b=0.22,                   # called (or limped), then a re-raise behind: continue this often
    f4b=(0.41, 0.32, 0.27),              # 3-bet and was 4-bet (not all-in): fold, call, 5-bet
    f4b_shove=0.60,                      # 3-bet and was shoved on: fold
    fivebet=[("allin", 1.0)],
    f5b=(0.25, 0.70, 0.05),              # 4-bet and was raised again: fold, call, raise
    shove_call=0.045,                    # other spots: percentile of the hands that call a preflop all-in
    shove_max=0.038,                     # only hands better than this percentile (TT+, AK, AQs) move all-in preflop themselves
    pre_noise=0.02,                      # sd of the per-hand jitter of the percentile
    # ---- postflop: betting -------------------------------------------------------------------
    # bet frequency by street and line (A c-bet/barrel, D donk, S checked to, L lead) x hu/mw
    betf={
        "flop": {"A_hu": 0.80, "A_mw": 0.44, "D_hu": 0.40, "D_mw": 0.25, "S_hu": 0.50, "S_mw": 0.35, "L_hu": 0.45, "L_mw": 0.30},
        "turn": {"A_hu": 0.78, "A_mw": 0.63, "D_hu": 0.33, "D_mw": 0.20, "S_hu": 0.45, "S_mw": 0.30, "L_hu": 0.40, "L_mw": 0.25},
        "river": {"A_hu": 0.76, "A_mw": 0.56, "D_hu": 0.24, "D_mw": 0.15, "S_hu": 0.40, "S_mw": 0.25, "L_hu": 0.35, "L_mw": 0.20},
    },
    # per street: "sizes" {size: {class: hands shown down after a bet of that size}} and "share"
    # {line_hu/mw (or "*"): {size: share of its bets}}.  Together: P(bet | class), P(size | class).
    J={
        "flop": {"sizes": {0.33: dict(air=44, weak=28, medium=18, draw=12, value=2),
                           0.5: dict(air=54, weak=41, medium=62, draw=21, value=15),
                           1.0: dict(air=14, weak=11, medium=36, draw=10, value=20)},
                 "share": {"*": {0.33: 0.3, 0.5: 0.4, 1.0: 0.3}}},
        "turn": {"sizes": {0.33: dict(air=32, weak=38, medium=22, draw=23, value=5),
                           0.5: dict(air=22, weak=37, medium=44, draw=21, value=22),
                           1.0: dict(air=2, weak=8, medium=26, draw=3, value=25)},
                 "share": {"*": {0.33: 0.3, 0.5: 0.4, 1.0: 0.3}}},
        "river": {"sizes": {0.33: dict(air=39, weak=34, medium=19, value=14),
                            0.5: dict(air=24, weak=25, medium=22, value=27),
                            1.0: dict(air=2, weak=3, medium=10, value=22)},
                  "share": {"*": {0.33: 0.3, 0.5: 0.4, 1.0: 0.3}}},
    },
    round_bets=False,                    # bet = size x pot rounded to the nearest chip (default: rounded down)
    jam=None,                            # {"spr": x, "p": {street: prob}}: a bet becomes all-in when stack/pot <= x
    air_hi_bet=1.0,                      # betting propensity of ace-high air relative to other air
    # replies when raised after betting, by the size it bet: size -> (fold, call, re-raise), or
    # size -> {"*": (...), street: (...)}
    raised={"default": (0.52, 0.39, 0.09)},
    rw=[1.0, 0.9, 0.45, 0.6, 0.15, 0.0],          # fold weights by fine class when raised after betting
    rrw=[0.02, 0.02, 0.12, 0.03, 0.25, 1.0],      # re-raise weights
    # ---- postflop: facing a bet ----------------------------------------------------------------
    # per street, for spots where it has not checked first ("nx") and where it has ("xr"): "all"
    # (fold, call, raise) and the same by size bucket of the bet; "cells": node + "_hu"/"_mw" ->
    # (fold, call, raise) (nodes: see post_ctx); "no_xr": it never check-raises on this street
    face={
        "flop": {"nx": {"all": (0.45, 0.42, 0.13), "<40%": (0.27, 0.56, 0.17), "40-75%": (0.44, 0.43, 0.13),
                        "75-110%": (0.57, 0.33, 0.10), "overbet": (0.70, 0.23, 0.07)},
                 "xr": {"all": (0.58, 0.39, 0.03), "<40%": (0.37, 0.58, 0.05), "40-75%": (0.57, 0.40, 0.03),
                        "75-110%": (0.70, 0.28, 0.02), "overbet": (0.78, 0.20, 0.02)},
                 "cells": {}, "no_xr": False},
        "turn": {"nx": {"all": (0.42, 0.48, 0.10), "<40%": (0.19, 0.69, 0.12), "40-75%": (0.43, 0.46, 0.11),
                        "75-110%": (0.58, 0.34, 0.08), "overbet": (0.65, 0.32, 0.03)},
                 "xr": {"all": (0.55, 0.43, 0.02), "<40%": (0.27, 0.70, 0.03), "40-75%": (0.56, 0.42, 0.02),
                        "75-110%": (0.70, 0.29, 0.01), "overbet": (0.75, 0.24, 0.01)},
                 "cells": {}, "no_xr": False},
        "river": {"nx": {"all": (0.50, 0.42, 0.08), "<40%": (0.31, 0.61, 0.08), "40-75%": (0.52, 0.39, 0.09),
                         "75-110%": (0.64, 0.29, 0.07), "overbet": (0.67, 0.30, 0.03)},
                  "xr": {"all": (0.62, 0.37, 0.01), "<40%": (0.41, 0.58, 0.01), "40-75%": (0.63, 0.36, 0.01),
                         "75-110%": (0.75, 0.24, 0.01), "overbet": (0.77, 0.22, 0.01)},
                  "cells": {}, "no_xr": False},
    },
    fw={"flop": [1.0, 0.75, 0.48, 0.38, 0.12, 0.0],     # fold weights by fine class
        "turn": [1.0, 0.80, 0.55, 0.42, 0.14, 0.0],
        "river": [1.0, 0.95, 1.0, 0.46, 0.17, 0.004]},
    # class mix of its raises (hands shown down after a raise)
    raise_comp={"flop": dict(air=8, draw=10, weak=6, medium=30, value=30),
                "turn": dict(air=2, draw=4, weak=4, medium=18, value=45),
                "river": dict(air=2, draw=0, weak=2, medium=8, value=50)},
    # raise sizes as a share of the pot after calling: street -> {class or "*": [(size, weight)]}
    rsize={"flop": {"*": [(0.75, 1.0)]}, "turn": {"*": [(0.75, 1.0)]}, "river": {"*": [(0.75, 1.0)]}},
    # facing a bet and a raise, or re-raised after raising: per fine class (fold, raise)
    face2=([1.0, 1.0, 0.75, 0.95, 0.62, 0.04], [0.0, 0.0, 0.02, 0.0, 0.03, 0.40]),
    commit=0.75,                         # a raise for this share of the stack or more becomes all-in
    variants=None,                       # [(weight, {parameter overrides})]: one drawn per round
)

_WHOLE = ("J", "open_bb", "raised", "fi", "tb_mult", "vs1", "sq", "rsize", "raise_comp", "betf", "face", "fw", "bd")


def _merge(a, b):
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict) and k not in _WHOLE:
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def _cum(pairs):
    """[(value, weight)] -> [(value, cumulative share)]"""
    tot = float(sum(w for _, w in pairs)) or 1.0
    out, c = [], 0.0
    for v, w in pairs:
        c += w / tot
        out.append((v, c))
    out[-1] = (out[-1][0], 1.0)
    return out


def _pick(cum, u):
    for v, c in cum:
        if u < c:
            return v
    return cum[-1][0]


class _Compiled:
    """Parameters of one replica variant plus the tables derived from them."""

    def __init__(self, name, P):
        self.name = name
        self.P = P
        self.nodes = _NODES.get(name, {})
        self._pi = {}
        self._joint = {}
        self._bet = {}
        self._face = {}
        self._raised = {}
        self.cum = {}

    def pi(self, key, hu=None):
        """Class mix of a node (heads up or multiway when `hu` is given): frozen self-play counts
        shrunk towards the node's overall mix, itself shrunk towards a prior."""
        k2 = key if hu is None else key + ("|hu" if hu else "|mw")
        v = self._pi.get(k2)
        if v is None:
            if hu is None:
                prior = _PRIOR[key[:key.index("|", 2)]]
                m = 40.0
            else:
                prior = self.pi(key)
                m = 60.0
            cnt = self.nodes.get(k2)
            if cnt:
                n = float(sum(cnt))
                v = [(cnt[c] + m * prior[c]) / (n + m) for c in range(K)]
            else:
                v = list(prior)
            v = [max(x, 1e-4) for x in v]
            if "|river" in key:
                v[2] = 0.0
            s = sum(v)
            v = self._pi[k2] = [x / s for x in v]
        return v

    def joint(self, street, grp):
        """Size shares of a line and classes shown per size -> class mix of the line's bets (g) and,
        per class, the size distribution (psz cumulative, prob plain)."""
        key = (street, grp)
        v = self._joint.get(key)
        if v is None:
            T = self.P["J"][street]
            share = T["share"].get(grp) or T["share"]["*"]
            sizes = sorted(s for s in share if share[s] > 0)
            tot = float(sum(share[s] for s in sizes)) or 1.0
            q = {}
            g = dict.fromkeys(CLS5, 0.0)
            for s in sizes:
                comp = T["sizes"].get(s) or {}
                n = float(sum(comp.values()))
                q[s] = dict((c, (comp.get(c, 0) / n) if n else 0.2) for c in CLS5)
                for c in CLS5:
                    g[c] += share[s] / tot * q[s][c]
            if street == "river":
                g["draw"] = 0.0
            psz = {}
            prob = {}
            for c in CLS5:
                w = [(s, share[s] / tot * q[s][c]) for s in sizes]
                if sum(x[1] for x in w) <= 0:
                    w = [(s, share[s] / tot) for s in sizes]
                t = float(sum(x[1] for x in w))
                psz[c] = _cum(w)
                prob[c] = dict((s, x / t) for s, x in w)
            v = self._joint[key] = {"g": g, "psz": psz, "prob": prob, "sizes": sizes}
        return v

    @staticmethod
    def six(pi, g5, air_hi=1.0):
        """5-class mix -> 6 fine classes (air split like the node's own air)."""
        a0, a1 = pi[0], pi[1] * air_hi
        t = (a0 + a1) or 1.0
        g = g5.get
        return [g("air", 0.0) * a0 / t, g("air", 0.0) * a1 / t, g("draw", 0.0), g("weak", 0.0), g("medium", 0.0),
                g("value", 0.0)]

    def pi_street(self, street):
        """Class mix over all of the street's betting nodes together (weighted by how often each occurs)."""
        key = "B*" + street
        v = self._pi.get(key)
        if v is None:
            tot = [0.0] * K
            for role in "ADSL":
                cnt = self.nodes.get("B|%s|%s" % (street, role))
                if cnt:
                    for c in range(K):
                        tot[c] += cnt[c]
            prior = _PRIOR["B|" + street]
            n = sum(tot)
            v = [(tot[c] + 40.0 * prior[c]) / (n + 40.0) for c in range(K)]
            v = self._pi[key] = [max(x, 1e-4) for x in v]
        return v

    def pbet(self, street, role, hu):
        """(P(bet | fine class), joint table) at a betting node.  The joint table gives the class
        mix of the bets; divided by the street's overall class mix it is a betting propensity per
        class, which is scaled so that this line bets at its measured frequency."""
        key = (street, role, hu)
        v = self._bet.get(key)
        if v is None:
            grp = role + ("_hu" if hu else "_mw")
            J = self.joint(street, grp)
            f = self.P["betf"][street][grp]
            pi = self.pi("B|%s|%s" % (street, role), hu)
            ps = self.pi_street(street)
            g = self.six(ps, J["g"], self.P["air_hi_bet"])
            v = self._bet[key] = (solve(pi, [g[c] / ps[c] * pi[c] for c in range(K)], f), J)
        return v

    def pface(self, street, node, bkt, hu):
        """(P(fold | class), P(raise | class)) facing a single bet."""
        key = (node, bkt, hu)
        v = self._face.get(key)
        if v is None:
            S = self.P["face"][street]
            chk = not node.endswith("_n")
            T = S["xr" if chk else "nx"]
            allf, allc, allr = T["all"][:3]
            cell = S["cells"].get(node + ("_hu" if hu else "_mw")) or T["all"]
            b = T.get(bkt) or T["all"]
            f = _shift(cell[0], b[0], allf)
            ratio = (b[2] / allr) if allr > 0 else 1.0
            r = cell[2] * (0.33 if ratio < 0.33 else 3.0 if ratio > 3.0 else ratio)
            if S["no_xr"] and chk:
                r = 0.0
            r = min(r, 0.9)
            if f + r > 1.0:
                f = 1.0 - r
            pi = self.pi("F|%s|%s" % (street, node), hu)
            pr = solve(pi, self.six(pi, self.P["raise_comp"][street]), r)
            fw = self.P["fw"][street]
            pf = solve(pi, [fw[c] * pi[c] for c in range(K)], f, [1.0 - x for x in pr])
            v = self._face[key] = (pf, pr)
        return v

    def praised(self, street, role, hu, size):
        """(P(fold | class), P(re-raise | class)) when raised after betting `size`."""
        key = (street, role, hu, size)
        v = self._raised.get(key)
        if v is None:
            R = self.P["raised"]
            tgt = None
            best = 0.031
            for s in R:
                if s != "default" and abs(s - size) < best:
                    best = abs(s - size)
                    tgt = R[s]
            if tgt is None:
                tgt = R["default"]
            if isinstance(tgt, dict):
                tgt = tgt.get(street) or tgt["*"]
            # class mix of its own bets of this size on this line: range x P(bet | class) x P(size | class)
            pb, J = self.pbet(street, role, hu)
            near = min(J["sizes"], key=lambda s: abs(s - size))
            pi = self.pi("B|%s|%s" % (street, role), hu)
            q = [pi[c] * pb[c] * J["prob"][CLS5_OF_FINE[c]].get(near, 0.0) for c in range(K)]
            t = sum(q)
            q = [x / t for x in q] if t > 0 else list(pi)
            rw, rrw = self.P["rw"], self.P["rrw"]
            pf = solve(q, [rw[c] * q[c] for c in range(K)], tgt[0])
            pr = solve(q, [rrw[c] * q[c] for c in range(K)], tgt[2], [1.0 - x for x in pf])
            v = self._raised[key] = (pf, pr)
        return v


_CACHE = {}


def _compiled(cls, variant):
    key = (cls, variant)
    c = _CACHE.get(key)
    if c is None:
        P = _merge(DEFAULTS, cls.P)
        if variant is not None:
            P = _merge(P, P["variants"][variant][1])
        c = _CACHE[key] = _Compiled(cls.NAME or cls.__module__, P)
    return c


def _safe(action, st):
    """Turn the wanted action into a legal one: clamp raises, else call / check, else fold."""
    la = st.get("legal_actions") or ()
    want = action.get("action") if isinstance(action, dict) else None
    if want == "raise":
        mn, mx = st.get("min_raise_to"), st.get("max_raise_to")
        if "raise" in la and isinstance(mn, int) and isinstance(mx, int) and mn <= mx:
            try:
                amt = int(action.get("amount"))
            except Exception:
                amt = mn
            return {"action": "raise", "amount": mn if amt < mn else mx if amt > mx else amt}
        want = "call"
    if want == "call":
        if "call" in la:
            return {"action": "call"}
        want = "check"
    if want == "check" and "check" in la:
        return {"action": "check"}
    if want == "fold" and "fold" in la:
        return {"action": "fold"}
    for a in ("check", "fold", "call"):
        if a in la:
            return {"action": a}
    return {"action": "fold"}


class Base:
    NAME = None
    P = {}

    def __init__(self):
        cls = type(self)
        var = cls.P.get("variants")
        self.variant = None
        if var:
            u = random.random() * sum(w for w, _ in var)
            for i, (w, _) in enumerate(var):
                u -= w
                if u < 0:
                    break
            self.variant = i
        self.C = _compiled(cls, self.variant)
        self.hkey = None
        self.mem = {}

    def on_table_start(self, info):
        pass

    def on_hand_end(self, summary):
        pass

    # ------------------------------------------------------------------ entry point
    def act(self, state):
        try:
            a = self._act(state)
        except Exception:
            a = None
        return _safe(a, state)

    def _act(self, st):
        hole = st["hole_cards"]
        hkey = (st.get("hand_number"), hole[0], hole[1])
        if hkey != self.hkey:
            self.hkey = hkey
            self.mem = {}
        board = st.get("board") or []
        street = st.get("street") or {0: "preflop", 3: "flop", 4: "turn"}.get(len(board), "river")
        hist = st.get("history") or []
        me = st.get("seat") or 0
        if street == "preflop" or len(board) < 3:
            return self._preflop(st, hist, me, hole)
        return self._postflop(st, hist, me, hole, board, street)

    # ------------------------------------------------------------------ preflop
    def _cumof(self, key, pairs):
        c = self.C.cum.get(key)
        if c is None:
            c = self.C.cum[key] = _cum(pairs)
        return c

    def _open_size(self, pos, q):
        P = self.C.P
        ob = P["open_bb"]
        spec = ob.get(pos) or ob["*"]
        if isinstance(spec, dict):
            spec = spec["top_sizes"] if q < spec["top"] else spec["rest"]
        return _pick(self._cumof(("open", id(spec)), spec), random.random()) * P["open_scale"].get(pos, 1.0)

    def _iso_bb(self, pos, limpers):
        base, per = self.C.P["iso"]
        if base == "open":
            base = self._open_size(pos, 1.0)
        return base + per * limpers

    def _raise_to(self, st, amt):
        """Preflop raise; one that puts the stack in is only made with a premium hand (else a call)."""
        mx = st.get("max_raise_to")
        if amt == "allin" or (isinstance(mx, int) and amt >= self.C.P["commit"] * mx):
            if self.mem.get("p0", 0.0) >= self.C.P["shove_max"]:
                return {"action": "call"}
            amt = mx or 0
        return {"action": "raise", "amount": int(amt)}

    def _resize(self, key):
        """4-bet / 5-bet size; without a premium hand an all-in pick falls back to the list's sized raise."""
        spec = self.C.P[key]
        size = _pick(self._cumof(key, spec), random.random())
        if size == "allin" and self.mem.get("p0", 0.0) >= self.C.P["shove_max"]:
            for s, _ in spec:
                if s != "allin":
                    return s
        return size

    def _split(self, u, call, rais, rho, can_raise):
        """Raise the top `rais` of my range (a share rho of those raises with random hands of the
        range instead), call the next `call`, fold the rest; remember the narrowed range."""
        mem = self.mem
        rng = mem.get("rng") or _FULL
        if not can_raise:
            call, rais = call + rais * (1.0 - rho), 0.0
        v = rais * (1.0 - rho)
        dens = (rais * rho / (1.0 - v)) if v < 1.0 else 0.0
        if can_raise and (u < v or (dens > 0.0 and random.random() < dens)):
            mem["rng"] = _narrow(rng, 0.0, v, dens)
            return "raise"
        hi = v + (call / (1.0 - dens) if dens < 1.0 else 0.0)
        if u < hi:
            mem["rng"] = _narrow(rng, v, hi, 0.0)
            return "call"
        return "fold"

    def _preflop(self, st, hist, me, hole):
        P = self.C.P
        mem = self.mem
        la = st.get("legal_actions") or ()
        bb = st.get("big_blind") or 20
        bets = st.get("bets") or []
        stacks = st.get("stacks") or []
        n = len(stacks or bets) or 8
        button = st.get("button") or 0
        pos = pos_name((me - button) % n, n)
        to_call = st.get("to_call") or 0
        cur = max(bets) if bets else to_call
        stack = stacks[me] if 0 <= me < len(stacks) else 2000
        raises, limpers, callers, opener, open_amt, mine = pre_ctx(hist, me)
        if not hist:
            raises = st.get("raises_this_street") or 0
        p = mem.get("p")
        if p is None:
            p0 = mem["p0"] = hand_pct(hole)
            p = p0 + random.gauss(0.0, P["pre_noise"])
            p = mem["p"] = 0.0005 if p < 0.0005 else 0.9995 if p > 0.9995 else p
        shove = to_call >= 0.4 * (stack + to_call) and to_call >= 20 * bb      # facing an all-in
        can_raise = "raise" in la and not shove
        last = mine[-1] if mine else None
        u = _rank_of(mem.get("rng") or _FULL, p)

        if raises == 0:
            if to_call <= 0:                                        # big blind option
                if limpers > 0 and self._split(u, 1.0, P["bb_iso"], 0.0, can_raise) == "raise":
                    return self._raise_to(st, round(self._iso_bb(pos, limpers) * bb))
                return {"action": "check"}
            if last is not None:
                return {"action": "call"}
            if limpers == 0:
                r, l = P["fi"].get(pos) or P["fi"]["MP"]
            else:
                l, r = P["vs_limp"]
            a = self._split(u, l, r, 0.0, can_raise)
            if a == "raise":
                size = self._open_size(pos, p / r if r > 0 else 0.0) if limpers == 0 else self._iso_bb(pos, limpers)
                return self._raise_to(st, round(size * bb))
            return {"action": a}

        if raises == 1:
            if last is not None:                                    # limped (or completed), then raised
                a = self._split(u, 1.0 - P["limp_fold"] - P["limp_rr"], P["limp_rr"], 0.0, can_raise)
                if shove and a != "fold":
                    a = "call" if p < P["shove_call"] else "fold"
                return self._raise_to(st, round(3.0 * cur)) if a == "raise" else {"action": a}
            obb = (open_amt or cur) / float(bb)
            opos = pos_name((opener - button) % n, n) if opener >= 0 else "MP"
            blind = pos in ("SB", "BB")
            steal = blind and callers == 0 and limpers == 0 and opos in ("CO", "BTN", "SB")
            grp = pos if blind else "IP"
            if callers >= 1:
                c_, r_ = P["sq"].get(grp) or P["sq"]["IP"]
            elif steal:
                c_, r_ = P["bd"][pos]["s" if obb <= 2.25 else "m" if obb <= 3.0 else "l"]
            else:
                c_, r_ = P["vs1"].get(pos) or P["vs1"]["IP"]
            if obb > 4.0:                                           # big opens are defended tighter
                kc, kr = P["big_open"][0 if obb <= 7.0 else 1]
                c_ *= kc
                r_ *= kr
            a = self._split(u, c_, min(r_, 0.98), P["tb_rand"], can_raise)
            if shove and a != "fold":
                a = "call" if p < P["shove_call"] else "fold"
            if a == "raise":
                mult, add = _pick(self._cumof("tb_oop" if blind else "tb_ip", P["tb_mult"]["oop" if blind else "ip"]),
                                  random.random())
                return self._raise_to(st, round(mult * cur + add * bb))
            return {"action": a}

        if raises == 2:
            if last is not None and last[0] == "raise":             # opened, got 3-bet
                f_, c_, r_ = P["f3b"]
                a = self._split(u, c_, r_, P["fb_rand"], can_raise)
            elif last is None:                                      # cold against a 3-bet
                c_, r_ = P["cold3"]
                a = self._split(u, c_, r_, P["cold_rand"], can_raise)
            else:                                                   # called or limped, then a re-raise
                a = self._split(u, P["call_then_3b"], 0.0, 0.0, False)
            if shove and a != "fold":
                a = "call" if p < P["shove_call"] else "fold"
            if a == "raise":
                size = self._resize("fourbet")
                return self._raise_to(st, size if size == "allin" else round(size * cur))
            return {"action": a}

        if raises == 3:
            if last == ("raise", 1):                                # 3-bet, got 4-bet
                if shove:
                    return {"action": "call" if u < 1.0 - P["f4b_shove"] else "fold"}
                f_, c_, r_ = P["f4b"]
                a = self._split(u, c_, r_, 0.0, can_raise)
            elif last is None:
                a = self._split(u, 0.016, 0.012, 0.0, can_raise)
            else:
                a = self._split(u, P["call_then_3b"] * 0.5, 0.0, 0.0, False)
            if shove and a != "fold":
                a = "call" if p < P["shove_call"] else "fold"
            if a == "raise":
                size = self._resize("fivebet")
                return self._raise_to(st, size if size == "allin" else round(size * cur))
            return {"action": a}

        if last is not None and last[0] == "raise" and last[1] == raises - 2:    # my raise was raised again
            f_, c_, r_ = P["f5b"]
            a = self._split(u, c_, r_, 0.0, can_raise)
            if a == "raise":
                return self._raise_to(st, "allin")
            return {"action": a}
        a = self._split(u, 0.012 if last is None else 0.10, 0.0, 0.0, False)
        if shove and a != "fold":
            a = "call" if p < P["shove_call"] else "fold"
        return {"action": a}

    # ------------------------------------------------------------------ postflop
    def _postflop(self, st, hist, me, hole, board, street):
        C = self.C
        P = C.P
        mem = self.mem
        la = st.get("legal_actions") or ()
        cls = mem.get(street)
        if cls is None:
            cls = mem[street] = classify(hole, board)
        pot = st.get("pot") or 0
        to_call = st.get("to_call") or 0
        mn, mx = st.get("min_raise_to"), st.get("max_raise_to")
        can_raise = "raise" in la and isinstance(mn, int) and isinstance(mx, int)
        ctx = post_ctx(hist, me, street)
        folded = st.get("folded")
        hu = (folded.count(False) if folded else 2) + ctx["folds_now"] <= 2
        u = random.random()

        if to_call <= 0:
            if not can_raise:
                return {"action": "check"}
            role = ctx["role"]
            pb, J = C.pbet(street, role, hu)
            if u >= pb[cls]:
                return {"action": "check"}
            size = _pick(J["psz"][CLS5_OF_FINE[cls]], random.random())
            jam = P["jam"]
            if jam and pot > 0 and mx <= jam["spr"] * pot and random.random() < jam["p"][street]:
                size = ALLIN
            mem["bet_" + street] = (role, hu, size)
            amt = int(round(size * pot)) if P["round_bets"] else int(size * pot + 1e-9)
            return {"action": "raise", "amount": mn if amt < mn else mx if amt > mx else amt}

        if ctx["my_raises"] > 0:
            if ctx["my_first"] and ctx["my_raises"] == 1 and ctx["nraises"] == 2:
                mb = mem.get("bet_" + street)
                if mb is None:                                      # no memory: read the size from the history
                    amt, pot0 = ctx["my_bet"][:2]
                    mb = (ctx["role"], hu, round(amt / float(max(1, pot0)), 2))
                pf, pr = C.praised(street, mb[0], mb[1], mb[2])
            else:
                pf, pr = P["face2"]
        elif ctx["nraises"] <= 1:
            pf, pr = C.pface(street, ctx["node"], bucket(to_call / float(max(1, pot - to_call))), hu)
        else:
            pf, pr = P["face2"]
        if u < pf[cls]:
            return {"action": "fold"}
        if u < pf[cls] + pr[cls] and can_raise:
            R = P["rsize"][street]
            spec = R.get(CLS5_OF_FINE[cls]) or R["*"]
            size = _pick(self._cumof(("rs", street, id(spec)), spec), random.random())
            bets = st.get("bets") or []
            amt = (max(bets) if bets else to_call) + int(size * (pot + to_call) + 1e-9)
            if amt >= P["commit"] * mx:
                amt = mx
            return {"action": "raise", "amount": amt}
        return {"action": "call"}
