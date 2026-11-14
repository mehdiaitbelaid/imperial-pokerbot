"""Sparring: a model of the live practice field, not the field itself.

Pressure responses follow the per responder fold rates printed by
tools/fold_analysis.py over 6,000 live hands (18 teams): preflop VPIP about
0.24 and PFR about 0.15, fold to a heads up flop c-bet 0.55, to a turn barrel
0.32, to stabs after checking 0.67 to 0.74, rarely to raises after betting,
4-bets and shoves strong. Every fold decision is a strength cutoff, so the
hands it continues with are real hands and showdowns stay honest. The cutoffs
come from tools/calibrate_field.py, which samples the strengths this bot holds
in each spot and stores their quantiles in QUANT.
"""
import random

RANKS = "23456789TJQKA"

# Per responder fold rates measured on the live field (heads up unless _mw).
# cbet and xt sit a little under the measured 0.55 and 0.50 because our bench
# bets are mostly 70 to 110% pot, where the size multiplier lifts them back to
# the field rates at that size (0.65 and 0.56).
FOLD = {"cbet": 0.49, "cbet_mw": 0.68, "lead": 0.29, "lead_mw": 0.49, "stab": 0.72,
        "stab_mw": 0.77, "limp": 0.25, "limp_mw": 0.83, "barrel": 0.32, "barrel_mw": 0.50,
        "xt": 0.45, "xt_mw": 0.78, "xt_r": 0.62, "xt_r_mw": 0.83, "river": 0.36,
        "river_mw": 0.78, "other": 0.45, "other_mw": 0.65}
# Fold rate multiplier by bet size as a share of the pot (flop c-bet buckets).
SIZE_MULT = ((0.40, 0.78), (0.70, 1.0), (1.10, 1.12), (99.0, 1.05))
# Spots where the field's fold rate barely moves with size.
FLAT = ("stab", "xt_r")
RAISE_CALL = 0.30   # strength needed to continue after our bet is raised
SHOVE_CALL = 0.45   # strength needed to call a postflop all in

# Strength quantiles per spot, 0%, 5%, ..., 100%. Filled by tools/calibrate_field.py.
QUANT = {
    "barrel": [0.000, 0.332, 0.356, 0.444, 0.487, 0.494, 0.507, 0.513, 0.524, 0.534, 0.546, 0.556, 0.572, 0.602, 0.724, 0.750, 0.787, 0.851, 0.902, 0.929, 0.990],
    "barrel_mw": [0.000, 0.469, 0.495, 0.503, 0.509, 0.519, 0.524, 0.531, 0.546, 0.553, 0.589, 0.717, 0.743, 0.760, 0.770, 0.791, 0.844, 0.858, 0.918, 0.938, 0.990],
    "cbet": [0.000, 0.231, 0.292, 0.304, 0.315, 0.319, 0.324, 0.329, 0.375, 0.513, 0.521, 0.532, 0.544, 0.761, 0.781, 0.840, 0.849, 0.854, 0.863, 0.926, 0.990],
    "cbet_mw": [0.000, 0.213, 0.228, 0.238, 0.250, 0.294, 0.305, 0.310, 0.319, 0.328, 0.340, 0.357, 0.460, 0.496, 0.506, 0.518, 0.547, 0.738, 0.768, 0.836, 0.990],
    "lead": [0.000, 0.223, 0.249, 0.294, 0.306, 0.316, 0.324, 0.332, 0.350, 0.466, 0.507, 0.520, 0.539, 0.720, 0.761, 0.775, 0.818, 0.847, 0.859, 0.926, 0.990],
    "lead_mw": [0.000, 0.213, 0.231, 0.248, 0.289, 0.303, 0.314, 0.326, 0.336, 0.351, 0.450, 0.496, 0.513, 0.534, 0.712, 0.747, 0.769, 0.790, 0.849, 0.916, 0.990],
    "limp": [0.000, 0.096, 0.132, 0.148, 0.158, 0.179, 0.189, 0.199, 0.209, 0.222, 0.246, 0.313, 0.346, 0.355, 0.369, 0.438, 0.467, 0.481, 0.494, 0.519, 0.990],
    "limp_mw": [0.000, 0.110, 0.138, 0.156, 0.176, 0.188, 0.203, 0.215, 0.228, 0.242, 0.281, 0.335, 0.347, 0.356, 0.422, 0.448, 0.470, 0.495, 0.520, 0.697, 0.990],
    "other": [0.000, 0.232, 0.248, 0.289, 0.308, 0.331, 0.363, 0.444, 0.480, 0.491, 0.503, 0.667, 0.714, 0.743, 0.769, 0.782, 0.833, 0.849, 0.914, 0.934, 0.990],
    "other_mw": [0.000, 0.205, 0.224, 0.234, 0.268, 0.298, 0.308, 0.316, 0.330, 0.347, 0.359, 0.455, 0.491, 0.503, 0.519, 0.540, 0.696, 0.749, 0.780, 0.861, 0.990],
    "river": [0.000, 0.425, 0.449, 0.461, 0.473, 0.494, 0.502, 0.512, 0.518, 0.522, 0.532, 0.546, 0.668, 0.683, 0.718, 0.763, 0.823, 0.860, 0.918, 0.929, 0.990],
    "river_mw": [0.000, 0.468, 0.477, 0.494, 0.500, 0.513, 0.522, 0.526, 0.535, 0.537, 0.550, 0.729, 0.752, 0.775, 0.906, 0.924, 0.933, 0.935, 0.947, 0.970, 0.990],
    "stab": [0.000, 0.224, 0.233, 0.247, 0.270, 0.286, 0.292, 0.302, 0.309, 0.316, 0.324, 0.346, 0.357, 0.447, 0.477, 0.486, 0.508, 0.518, 0.528, 0.541, 0.990],
    "stab_mw": [0.000, 0.217, 0.226, 0.233, 0.242, 0.248, 0.286, 0.298, 0.307, 0.310, 0.316, 0.322, 0.328, 0.345, 0.361, 0.484, 0.505, 0.522, 0.533, 0.554, 0.990],
    "xt": [0.000, 0.190, 0.208, 0.216, 0.225, 0.233, 0.238, 0.242, 0.248, 0.333, 0.349, 0.382, 0.406, 0.439, 0.468, 0.496, 0.512, 0.526, 0.544, 0.750, 0.990],
    "xt_mw": [0.000, 0.160, 0.198, 0.210, 0.221, 0.227, 0.233, 0.240, 0.249, 0.336, 0.344, 0.351, 0.358, 0.378, 0.448, 0.490, 0.508, 0.524, 0.545, 0.671, 0.990],
    "xt_r": [0.000, 0.204, 0.210, 0.222, 0.224, 0.227, 0.230, 0.242, 0.438, 0.464, 0.481, 0.493, 0.495, 0.500, 0.506, 0.516, 0.522, 0.529, 0.537, 0.545, 0.990],
    "xt_r_mw": [0.000, 0.164, 0.205, 0.218, 0.222, 0.228, 0.235, 0.244, 0.249, 0.465, 0.479, 0.492, 0.500, 0.503, 0.516, 0.519, 0.526, 0.536, 0.548, 0.937, 0.990],
}
QUANT_DEFAULT = "cbet"

RECORD = False   # the calibration tool switches this on to collect (spot, strength)
LOG = []


def _pf_score(a, b, suited):
    """Rough preflop score, used only to rank the 169 classes."""
    if a == b:
        return 0.55 + a / 26.0 + (0.08 if a >= 9 else 0.0)
    v = (a + b) / 26.0 - 0.02 * max(0, a - b - 1)
    v += 0.06 if suited else 0.0
    if a == 12:
        v += 0.05
    return v


def _build_pct():
    cls = []
    for a in range(13):
        for b in range(a + 1):
            if a == b:
                cls.append((_pf_score(a, b, False), a, b, False, 6))
            else:
                cls.append((_pf_score(a, b, True), a, b, True, 4))
                cls.append((_pf_score(a, b, False), a, b, False, 12))
    cls.sort(key=lambda c: -c[0])
    out, cum = {}, 0
    for _, a, b, s, k in cls:
        cum += k
        out[(a, b, s)] = cum / 1326.0
    return out


PCT = _build_pct()


def pct(hole):
    a, b = RANKS.index(hole[0][0]), RANKS.index(hole[1][0])
    if a < b:
        a, b = b, a
    return PCT[(a, b, hole[0][1] == hole[1][1] and a != b)]


def _straight(mask):
    m = (mask << 1) | (1 if mask & 4096 else 0)
    for t in range(13, 3, -1):
        if (m >> (t - 4)) & 31 == 31:
            return t
    return -1


def _sdraw(mask):
    m = (mask << 1) | (1 if mask & 4096 else 0)
    for t in range(13, 3, -1):
        if bin((m >> (t - 4)) & 31).count("1") >= 4:
            return True
    return False


def strength(hole, board):
    """0..1 postflop strength; ordering matters, not calibration."""
    hr = [RANKS.index(c[0]) for c in hole]
    br = [RANKS.index(c[0]) for c in board]
    suits = [c[1] for c in hole + board]
    bs = [c[1] for c in board]
    for s in "cdhs":
        if suits.count(s) >= 5 and bs.count(s) < 5:
            return 0.95
    allm = bmask = 0
    for r in br:
        bmask |= 1 << r
    allm = bmask | (1 << hr[0]) | (1 << hr[1])
    st = _straight(allm)
    if st >= 0 and st > _straight(bmask):
        return 0.93
    cnt = {}
    for r in br:
        cnt[r] = cnt.get(r, 0) + 1
    top = max(br)
    hi, lo = max(hr), min(hr)
    if hr[0] == hr[1]:
        if cnt.get(hr[0]):
            return 0.94
        if hr[0] > top:
            return 0.80 + 0.04 * hr[0] / 12.0
        made = 0.42 + 0.12 * hr[0] / 12.0
    else:
        h1, h2 = cnt.get(hr[0], 0), cnt.get(hr[1], 0)
        if h1 and h2:
            return 0.90
        if h1 >= 2 or h2 >= 2:
            return 0.92
        if h1 or h2:
            pr = hr[0] if h1 else hr[1]
            kick = hr[1] if h1 else hr[0]
            if pr == top:
                made = 0.62 + 0.14 * kick / 12.0
            else:
                made = 0.42 + 0.12 * pr / 12.0
        else:
            made = 0.0
    draw = 0.0
    if len(board) < 5:
        fd = any(suits.count(s) == 4 and s in (hole[0][1], hole[1][1]) for s in "cdhs")
        sd = _sdraw(allm) and not _sdraw(bmask)
        if fd and sd:
            draw = 0.40
        elif fd:
            draw = 0.36
        elif sd:
            draw = 0.33
    if made:
        return min(0.79, made + (0.05 if draw else 0.0))
    if draw:
        return draw
    air = 0.02 + 0.20 * hi / 12.0
    if len(board) == 3 and lo > top:
        air += 0.08
    return air


def legal_raise(state, amount):
    if "raise" not in state["legal_actions"] or state.get("min_raise_to") is None:
        return {"action": "call"} if "call" in state["legal_actions"] else {"action": "check"}
    return {"action": "raise", "amount": int(max(state["min_raise_to"], min(state["max_raise_to"], amount)))}


def passive(state):
    return {"action": "check"} if "check" in state["legal_actions"] else {"action": "call"}


def fold(state):
    return {"action": "check"} if "check" in state["legal_actions"] else {"action": "fold"}


def cutoff(spot, target):
    q = QUANT.get(spot) or QUANT.get(spot.replace("_mw", "")) or QUANT[QUANT_DEFAULT]
    x = max(0.0, min(1.0, target)) * 20
    i = min(19, int(x))
    return q[i] + (q[i + 1] - q[i]) * (x - i)


def parse(hist):
    """Preflop aggressor, raise count, limpers and per street first bettor."""
    pfa = None
    nraise = 0
    limpers = 0
    first = {}
    checks = {}
    raises = {}
    street = None
    cur = 0
    for h in hist:
        s, a, stt = h.get("seat"), h.get("action"), h.get("street")
        if stt != street:
            street, cur = stt, 0
        if a in ("small_blind", "big_blind"):
            cur = max(cur, h.get("amount") or 0)
            continue
        if stt == "preflop":
            if a == "raise":
                pfa = s
                nraise += 1
            elif a == "call" and nraise == 0:
                limpers += 1
            continue
        if a == "raise":
            if stt not in first:
                first[stt] = s
            raises[stt] = raises.get(stt, 0) + 1
        elif a == "check" and stt not in first:
            checks.setdefault(stt, []).append(s)
    return pfa, nraise, limpers, first, checks, raises


class Agent:
    def __init__(self):
        self.rng = random.Random()

    def act(self, state):
        hist = state.get("history") or []
        if state["street"] == "preflop":
            return self._pre(state, hist)
        return self._post(state, hist)

    def _pre(self, st, hist):
        bb, to_call = st["big_blind"], st["to_call"]
        n = len(st["stacks"])
        rel = (st["seat"] - st["button"]) % n
        q = pct(st["hole_cards"])
        pfa, nraise, limpers, _, _, _ = parse(hist)
        me = st["seat"]
        my_raises = sum(1 for h in hist if h.get("seat") == me and h.get("action") == "raise")
        cur = max(st["bets"])
        if nraise == 0:
            if rel == 2:
                if q <= 0.10 and limpers:
                    return legal_raise(st, (4 + limpers) * bb)
                return passive(st)
            pos = {0: 0.40, 1: 0.34, n - 1: 0.28, n - 2: 0.21, n - 3: 0.17}.get(rel, 0.14)
            if limpers:
                pos *= 0.6
            if q <= pos:
                size = self.rng.choice((2.5, 3.0, 3.0, 3.5)) + limpers
                return legal_raise(st, size * bb)
            if q <= pos + 0.08 and (rel in (0, 1, n - 1) or limpers):
                return passive(st)
            return fold(st)
        r_bb = cur / float(bb)
        allin = any(st["stacks"][i] == 0 and not st["folded"][i] for i in range(n) if i != me)
        if allin or r_bb >= 25:
            # shoves and huge raises: continue only with the top of the range
            return passive(st) if q <= (0.035 if r_bb < 60 else 0.03) else fold(st)
        if nraise == 1:
            if q <= (0.05 if rel == 2 else 0.035):
                return legal_raise(st, 3.2 * cur)
            call = {2: 0.38, 1: 0.14}.get(rel, 0.12)
            if r_bb > 3.5:
                call *= 3.5 / r_bb
            return passive(st) if q <= call else fold(st)
        if nraise == 2:
            if my_raises:
                # opener facing a 3-bet: folds about 0.47, 4-bets about 0.28
                if q <= 0.042:
                    return legal_raise(st, 2.4 * cur)
                return passive(st) if q <= 0.075 else fold(st)
            return passive(st) if q <= 0.03 else fold(st)
        # 4-bets and beyond: the field rarely folds its 3-bets here
        if my_raises:
            if q <= 0.02:
                return legal_raise(st, st["max_raise_to"] or 0)
            return passive(st) if q <= 0.045 else fold(st)
        return passive(st) if q <= 0.02 else fold(st)

    def _post(self, st, hist):
        me, street = st["seat"], st["street"]
        pot, to_call = st["pot"], st["to_call"]
        n = len(st["stacks"])
        live = sum(1 for f in st["folded"] if not f)
        mw = live > 2
        rng = self.rng.random
        # jitter breaks ties between equal strengths so cutoffs hit their rates
        s = strength(st["hole_cards"], st["board"]) + 0.03 * rng()
        pfa, _, _, first, checks, raises = parse(hist)
        if to_call == 0:
            if s >= 0.62:
                frac = 0.75 if s >= 0.85 else 0.6
                return legal_raise(st, max(st["bets"]) + frac * pot)
            if street == "flop" and pfa == me and street not in first:
                if (not mw and rng() < 0.55) or (mw and s >= 0.33 and rng() < 0.5):
                    return legal_raise(st, max(st["bets"]) + 0.55 * pot)
            if not mw and street != "river" and 0.30 <= s < 0.45 and rng() < 0.35:
                return legal_raise(st, max(st["bets"]) + 0.55 * pot)
            if not mw and checks.get(street) and rng() < 0.25:
                # stab when checked to
                return legal_raise(st, max(st["bets"]) + 0.5 * pot)
            return passive(st)
        bettor = first.get(street)
        allin = any(st["stacks"][i] == 0 and not st["folded"][i] for i in range(n) if i != me)
        if allin:
            return passive(st) if s >= SHOVE_CALL else fold(st)
        i_bet = any(h.get("seat") == me and h.get("street") == street and h.get("action") == "raise" for h in hist)
        if i_bet or raises.get(street, 0) >= 2:
            # facing a raise: these are value; the field folds about a quarter
            if s >= 0.92 and "raise" in st["legal_actions"]:
                return legal_raise(st, max(st["bets"]) * 2.5)
            return passive(st) if s >= RAISE_CALL else fold(st)
        spot = self._spot(street, me, bettor, pfa, first, checks)
        base = FOLD[spot + ("_mw" if mw else "")]
        frac = to_call / float(max(1, pot - to_call))
        mult = 1.0
        for lim, m in SIZE_MULT:
            if frac < lim:
                mult = m
                break
        if spot in FLAT:
            mult = min(mult, 1.0)
        target = min(0.95, base * mult)
        key = spot + ("_mw" if mw else "")
        if s >= 0.90 and rng() < 0.5:
            out = legal_raise(st, max(st["bets"]) * 3)
        elif s >= cutoff(key, target):
            out = passive(st)
        else:
            out = fold(st)
        if RECORD:
            LOG.append((key, s, out["action"] == "fold", frac))
        return out

    @staticmethod
    def _spot(street, me, bettor, pfa, first, checks):
        mine = me in checks.get(street, [])
        if street == "flop":
            if pfa is None:
                return "limp"
            if bettor == pfa:
                return "cbet"
            if me == pfa:
                return "stab" if mine else "lead"
            return "other"
        prev = "flop" if street == "turn" else "turn"
        pb = first.get(prev)
        if pb is None:
            return "xt" if street == "turn" else "xt_r"
        if pb == bettor:
            return "barrel" if street == "turn" else "river"
        if pb == me and mine:
            return "stab"
        return "other" if street == "turn" else "river"
