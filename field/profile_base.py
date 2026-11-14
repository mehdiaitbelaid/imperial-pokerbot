"""Parametric sparring bot whose MEASURED statistics (tools/analyze.py) match a profile.

    from profile_base import ProfileAgent
    class Agent(ProfileAgent):
        P = dict(vpip=.27, pfr=.18, limp=0, three_bet=.08, fold_to_3bet=.58, open_size_bb=2.5,
                 cbet=.83, bet=.68, bet_size=1.10, fold_to_bet=.51, raise_vs_bet=.26, air=.22)

All frequencies are fractions and use the analyzer's definitions:
  vpip, pfr      per hand dealt
  limp           calls / first-in spots with no raise yet
  three_bet      re-raises / first actions facing exactly one raise
  fold_to_3bet   folds / spots where it opened and was re-raised
  open_size_bb   raise-to size of a first-in raise, in big blinds
  cbet           flop bets / flop spots as last preflop raiser with no bet to face
  bet            bets / ALL postflop spots with no bet to face (c-bet spots included, as the
                 analyzer counts them; the frequency in the non-c-bet spots is solved for)
  bet_size       median bet as a fraction of the pot
  fold_to_bet, raise_vs_bet   folds / raises per postflop decision facing a bet
  air            share of its bets and raises made with nothing (no pair, no draw)

How: every decision ranks the hand (preflop: percentile among the 169 classes; postflop: a 0..1
made-hand/draw score plus a little noise) and compares it with a threshold. Each threshold is
trimmed by an integral controller on the bot's own running counts, so the strongest hands
raise, the weakest fold, and the round totals land on the targets whatever the field does.
No simulation: roughly 20-40 microseconds per decision.
"""
import math
import random

_R = {r: i for i, r in enumerate("23456789TJQKA")}


def _chen(hi, lo, suited):
    pts = {12: 10.0, 11: 8.0, 10: 7.0, 9: 6.0}.get(hi, (hi + 2) / 2.0)
    if hi == lo:
        return max(5.0, pts * 2)
    s = pts + (2 if suited else 0)
    gap = hi - lo - 1
    s -= (0, 1, 2, 4, 5)[min(gap, 4)]
    if gap <= 1 and hi < 10:
        s += 1
    return s


def _build_pct():
    rows = []
    for hi in range(13):
        for lo in range(hi + 1):
            tb = hi * 0.011 + lo * 0.001
            if hi == lo:
                rows.append((_chen(hi, lo, False) + tb, (hi, lo, False), 6))
            else:
                rows.append((_chen(hi, lo, True) + tb, (hi, lo, True), 4))
                rows.append((_chen(hi, lo, False) + tb, (hi, lo, False), 12))
    rows.sort(key=lambda r: -r[0])
    out, cum = {}, 0
    for _, k, n in rows:
        out[k] = (cum + n / 2.0) / 1326.0
        cum += n
    return out


_PCT = _build_pct()          # (hi, lo, suited) -> share of hands that are better (0 = aces)


def _straight_top(mask):
    m = (mask << 1) | ((mask >> 12) & 1)
    for lo in range(9, -1, -1):
        if (m >> lo) & 31 == 31:
            return lo + 3
    return -1


def _straight_outs(mask):
    n = 0
    for r in range(13):
        if not (mask >> r) & 1 and _straight_top(mask | (1 << r)) >= 0:
            n += 1
    return n


def classify(hole, board):
    """(score 0..1, is_air). ~0.9+ nuts, 0.66+ strong (two pair+, overpair, top pair good kicker),
    0.37-0.66 other pairs, 0.27-0.6 draws, below 0.25 nothing."""
    h0, h1 = _R[hole[0][0]], _R[hole[1][0]]
    s0, s1 = hole[0][1], hole[1][1]
    if h0 < h1:
        h0, h1, s0, s1 = h1, h0, s1, s0
    nb = len(board)
    bcnt = [0] * 13
    bmask = 0
    bs = {}
    for c in board:
        r = _R[c[0]]
        bcnt[r] += 1
        bmask |= 1 << r
        bs[c[1]] = bs.get(c[1], 0) + 1
    btop = bmask.bit_length() - 1
    bmaxc = max(bcnt)
    bpairs = sum(1 for x in bcnt if x >= 2)
    mx_suit = max(bs.values())

    flush = fdraw = False
    frank = 0
    for s, n in bs.items():
        mine = (s0 == s) + (s1 == s)
        if mine:
            if n + mine >= 5:
                flush = True
                frank = h0 if s0 == s else h1
            elif n + mine == 4 and nb < 5:
                fdraw = True
    amask = bmask | (1 << h0) | (1 << h1)
    st_all = _straight_top(amask)
    straight = st_all >= 0 and st_all > (_straight_top(bmask) if nb >= 5 else -1)

    c0, c1 = bcnt[h0], bcnt[h1]
    paired = True
    if h0 == h1:
        n0 = 2 + c0
        if n0 == 4:
            sc = 1.0
        elif n0 == 3:
            sc = 0.97 if bmaxc >= 2 else 0.91
        elif bmaxc >= 3:
            sc = 0.86
        else:
            if h0 > btop:
                sc = 0.70 + 0.004 * h0
            else:
                higher = sum(1 for r in range(h0 + 1, 13) if bcnt[r])
                sc = max(0.30, 0.53 - 0.07 * higher)
            if bmaxc == 2:
                sc -= 0.04
    else:
        n0, n1 = 1 + c0, 1 + c1
        if n0 == 4 or n1 == 4:
            sc = 1.0
        elif (n0 == 3 and n1 >= 2) or (n1 == 3 and n0 >= 2):
            sc = 0.97
        elif n0 == 3 or n1 == 3:
            sc = 0.95 if bpairs >= 2 else 0.84 + 0.004 * (h1 if n0 == 3 else h0)
        elif n0 == 2 and n1 == 2:
            sc = 0.72 if bmaxc >= 2 else 0.80
        elif n0 == 2 or n1 == 2:
            pr, kick = (h0, h1) if n0 == 2 else (h1, h0)
            if bmaxc >= 3:
                sc = 0.90
            else:
                higher = sum(1 for r in range(pr + 1, 13) if bcnt[r])
                if higher == 0:
                    sc = 0.56 + 0.012 * kick
                elif higher == 1:
                    sc = 0.46 + 0.003 * kick
                else:
                    sc = 0.38 + 0.003 * kick
                if bmaxc == 2:
                    sc -= 0.03
        else:
            paired = False
            sc = 0.04 + 0.012 * h0 + 0.003 * h1
            if h1 > btop:
                sc += 0.03
    if flush:
        sc = max(sc, (0.80 + 0.011 * frank) if mx_suit >= 4 else (0.93 + 0.003 * frank))
    elif straight:
        sc = max(sc, 0.70 if mx_suit >= 4 else (0.84 if mx_suit == 3 else 0.89))
    elif sc < 0.93:
        if mx_suit >= 4:
            sc *= 0.75
        elif mx_suit == 3:
            sc *= 0.95
    draw = 0.0
    if nb < 5 and sc < 0.75:
        k = 1.0 if nb == 3 else 0.7
        if fdraw:
            draw += 0.20 * k
        if not straight:
            outs = _straight_outs(amask) - _straight_outs(bmask)
            if outs >= 2:
                draw += 0.16 * k
            elif outs == 1:
                draw += 0.07 * k
        if draw:
            sc = max(sc + 0.5 * draw, 0.22 + draw)
    made = paired or flush or straight
    return sc, (not made and draw == 0.0)


_QX = (0.0, 0.45, 0.57, 0.87, 1.0)
_QY = (0.03, 0.22, 0.38, 0.66, 1.0)


def _q(u):
    """Rough quantile function of the postflop score, used only to start the thresholds."""
    u = 0.0 if u < 0 else 1.0 if u > 1 else u
    for i in range(1, 5):
        if u <= _QX[i]:
            return _QY[i - 1] + (_QY[i] - _QY[i - 1]) * (u - _QX[i - 1]) / (_QX[i] - _QX[i - 1])
    return 1.0


class ProfileAgent:
    P = {}
    DEFAULTS = dict(vpip=0.25, pfr=0.18, limp=0.0, three_bet=0.05, fold_to_3bet=0.60, open_size_bb=2.5,
                    cbet=0.60, bet=0.40, bet_size=0.66, fold_to_bet=0.45, raise_vs_bet=0.10, air=0.20)
    # controller gains (per event)
    G_HAND, G_LIMP, G_3B, G_F3B = 0.020, 0.02, 0.02, 0.06
    G_CB, G_BET, G_FOLD, G_RAISE, G_AIR = 0.10, 0.03, 0.04, 0.04, 0.03

    def __init__(self):
        P = dict(self.DEFAULTS)
        P.update(type(self).P)
        self.P = P
        ro = max(0.01, (P["pfr"] - 0.40 * P["three_bet"]) / 0.42)
        other = min(1.0, max(0.0, (P["bet"] - 0.25 * P["cbet"]) / 0.75))
        self.c = {
            "ro": ro,                                        # first-in raise width (PFR)
            "cc": min(1.0, max(0.02, (P["vpip"] - 0.55 * (ro + P["limp"]) - 0.40 * P["three_bet"]) / 0.40)),
            "lw": P["limp"],                                 # limp width
            "t3": P["three_bet"],
            "tq": 4.0 if P["fold_to_3bet"] <= 0 else 1.0 - P["fold_to_3bet"],
            "tc": _q(1.0 - P["cbet"] * (1.0 - P["air"])) + 0.06,
            "tb": _q(1.0 - other),
            "tf": _q(P["fold_to_bet"]) + 0.08,
            "tr": _q(1.0 - P["raise_vs_bet"]) + 0.05,
            "ka": P["air"] / 0.45,                           # bluff promotion factor
        }
        self._hn = None
        self._done = True
        self.h = {}

    # ---- bookkeeping ------------------------------------------------------------------------
    def _adj(self, key, err, g, lo, hi):
        v = self.c[key] + g * err
        self.c[key] = lo if v < lo else hi if v > hi else v

    def _new_hand(self, hn):
        if not self._done:
            self._finish()
        self._hn = hn
        self._done = False
        self.h = {"acted": False, "vpip": 0, "pfr": 0, "opened": False, "limped": False, "faced3": False,
                  "open_thr": 1.0, "limp_thr": 1.0, "agg": None, "cls": {}}

    def _finish(self):
        self._done = True
        h, P = self.h, self.P
        self._adj("ro", P["pfr"] - h["pfr"], self.G_HAND, 0.003, 1.0)
        self._adj("cc", P["vpip"] - h["vpip"], self.G_HAND, 0.0, 1.0)

    def on_hand_end(self, summary):
        hn = summary.get("hand_number")
        if hn != self._hn:
            self._new_hand(hn)
        if not self._done:
            self._finish()

    # ---- actions ----------------------------------------------------------------------------
    def act(self, st):
        if st["hand_number"] != self._hn or self._done:
            self._new_hand(st["hand_number"])
        la = st["legal_actions"]
        if st["street"] == "preflop":
            a = self._preflop(st, la)
            if a["action"] == "raise":
                self.h["vpip"] = self.h["pfr"] = 1
            elif a["action"] == "call":
                self.h["vpip"] = 1
            return a
        return self._postflop(st, la)

    @staticmethod
    def _passive(la):
        return {"action": "check"} if "check" in la else {"action": "fold"}

    @staticmethod
    def _call(st, la):
        if st["to_call"] <= 0 and "check" in la:
            return {"action": "check"}
        return {"action": "call"} if "call" in la else {"action": "check"}

    def _raise(self, st, la, amt, commit=0.7):
        mn, mx = st.get("min_raise_to"), st.get("max_raise_to")
        if "raise" not in la or mn is None or mx is None:
            return self._call(st, la)
        amt = int(amt)
        if amt >= commit * mx:
            amt = mx
        return {"action": "raise", "amount": mn if amt < mn else mx if amt > mx else amt}

    # ---- preflop ----------------------------------------------------------------------------
    def _preflop(self, st, la):
        P, c, h = self.P, self.c, self.h
        hole = st["hole_cards"]
        a, b = _R[hole[0][0]], _R[hole[1][0]]
        if a < b:
            a, b = b, a
        p = _PCT[(a, b, a != b and hole[0][1] == hole[1][1])]
        me, bb = st["seat"], st["big_blind"]
        to_call = st["to_call"]
        raises = st["raises_this_street"]
        cur = max(st["bets"])
        L = max(1.0, cur / float(bb))
        n = len(st["stacks"])
        rel = (me - st["button"] - 3) % n if n > 2 else 0      # 0 = first to act ... n-1 = big blind
        first = not h["acted"]
        h["acted"] = True

        if first and raises == 0:                               # unopened or limped pot
            if rel == n - 1:
                posf = 0.8
            elif rel == n - 2:
                posf = 1.1
            else:
                posf = 0.6 + 0.9 * rel / max(1, n - 3)
            thr = c["ro"] * posf
            h["open_thr"] = max(thr, 0.002)
            limp = 0
            if p < thr and "raise" in la:
                h["opened"] = True
                out = self._raise(st, la, round(P["open_size_bb"] * bb), commit=2.0)
            elif to_call > 0 and P["limp"] > 0 and p < thr + c["lw"] and "call" in la:
                limp = 1
                h["limped"] = True
                h["limp_thr"] = thr + c["lw"]
                out = {"action": "call"}
            else:
                out = self._passive(la)
            self._adj("lw", P["limp"] - limp, self.G_LIMP, 0.0, 1.5)
            return out

        if first and raises == 1:                               # facing one raise
            sf = min(1.0, (5.0 / L) ** 0.6)
            posf = 1.5 if rel == n - 1 else 0.8 if rel == n - 2 else 1.1 if rel == n - 3 else 0.85
            t3 = c["t3"] if L <= 8 else min(c["t3"], 0.04) if L >= 25 else c["t3"] * sf
            did3 = 0
            if p < t3:
                out = self._raise(st, la, 3 * cur + (st["pot"] - cur - 1.5 * bb) * 0.5, commit=0.4)
                did3 = 1 if out["action"] == "raise" else 0
            elif p < (t3 + c["cc"] * posf) * sf or to_call <= 0.12 * st["pot"]:
                out = self._call(st, la)
            else:
                out = self._passive(la)
            self._adj("t3", P["three_bet"] - did3, self.G_3B, 0.0, 1.0)
            return out

        if first:                                               # cold, facing a 3-bet or more
            thr = max(0.012, (0.03 + 0.30 * P["three_bet"]) * min(1.0, (12.0 / L) ** 0.5))
            if p < 0.5 * thr:
                return self._raise(st, la, 2.3 * cur, commit=0.4)
            if p < thr:
                return self._call(st, la)
            return self._passive(la)

        if to_call <= 0:
            return self._passive(la)
        cheap = to_call <= 0.2 * st["pot"]
        if h["opened"] and not h["faced3"]:                     # opened, got re-raised
            h["faced3"] = True
            q = p / h["open_thr"]
            sf = min(1.0, (16.0 / L) ** 0.5)
            if q < c["tq"] * sf or cheap:
                if q < 0.12 and p < 0.05:
                    out = self._raise(st, la, 2.3 * cur, commit=0.4)
                else:
                    out = self._call(st, la)
            else:
                out = self._passive(la)
            if raises == 2:
                self._adj("tq", (1 if out["action"] == "fold" else 0) - P["fold_to_3bet"], self.G_F3B, 0.0, 4.0)
            return out
        if h["limped"] and not h["opened"] and raises <= 1:    # limped, got raised
            keep = (1.0 - (0.25 + 0.5 * P["fold_to_3bet"])) * min(1.0, (6.0 / L) ** 0.6)
            lo = h["open_thr"]
            if cheap or p < lo + (h["limp_thr"] - lo) * keep:
                return self._call(st, la)
            return self._passive(la)
        thr = max(0.012, (0.02 + 0.08 * (1.0 - P["fold_to_3bet"])) * min(1.0, (20.0 / L) ** 0.5))
        if p < 0.4 * thr:
            return self._raise(st, la, st.get("max_raise_to") or 0, commit=0.0)
        if p < thr or cheap:
            return self._call(st, la)
        return self._passive(la)

    # ---- postflop ---------------------------------------------------------------------------
    def _postflop(self, st, la):
        P, c, h = self.P, self.c, self.h
        street = st["street"]
        cls = h["cls"].get(street)
        if cls is None:
            cls = h["cls"][street] = classify(st["hole_cards"], st["board"])
        score, is_air = cls
        me = st["seat"]
        pot, to_call = st["pot"], st["to_call"]
        can_raise = "raise" in la
        s = score + random.uniform(-0.06, 0.06)

        if to_call <= 0:                                        # nothing to face: bet or check
            cb = False
            if street == "flop":
                if h["agg"] is None:
                    h["agg"] = -1
                    for e in reversed(st["history"]):
                        if e["street"] == "preflop" and e["action"] == "raise":
                            h["agg"] = e["seat"]
                            break
                cb = h["agg"] == me
            freq = P["cbet"] if cb else P["bet"]
            prio = s - 0.03 * (st["folded"].count(False) - 2)
            if is_air and random.random() < c["ka"] * freq:
                prio = 0.75 + 0.25 * random.random()
            do = can_raise and prio > (c["tc"] if cb else c["tb"])
            if cb:
                self._adj("tc", (1 if do else 0) - P["cbet"], self.G_CB, -0.3, 1.3)
            self._adj("tb", (1 if do else 0) - P["bet"], self.G_BET, -0.3, 1.3)
            if not do:
                return self._passive(la)
            self._adj("ka", P["air"] - (1 if is_air else 0), self.G_AIR, 0.0, 3.0)
            return self._raise(st, la, P["bet_size"] * pot * random.uniform(0.85, 1.15), commit=0.8)

        # facing a bet or raise: fold the weakest, raise the strongest
        frac = to_call / float(max(1, pot - to_call))
        adj = 0.12 * math.log(max(frac, 0.02) / 0.66, 2)
        adj = -0.2 if adj < -0.2 else 0.35 if adj > 0.35 else adj
        nr = st["raises_this_street"]
        s -= adj + 0.06 * max(0, nr - 1)
        prio = s
        if is_air and random.random() < c["ka"] * P["raise_vs_bet"]:
            prio = 0.80 + 0.20 * random.random()
        fold = rais = 0
        if can_raise and nr < 4 and prio > c["tr"]:
            cur = max(st["bets"])
            out = self._raise(st, la, cur + P["bet_size"] * (pot + to_call) * random.uniform(0.85, 1.15), commit=0.6)
            rais = 1 if out["action"] == "raise" else 0
            if rais:
                self._adj("ka", P["air"] - (1 if is_air else 0), self.G_AIR, 0.0, 3.0)
        elif s < c["tf"] and score < 0.80 and "fold" in la:
            out = {"action": "fold"}
            fold = 1
        else:
            out = self._call(st, la)
        self._adj("tf", P["fold_to_bet"] - fold, self.G_FOLD, -0.3, 1.3)
        self._adj("tr", rais - P["raise_vs_bet"], self.G_RAISE, 0.0, 1.5)
        return out
