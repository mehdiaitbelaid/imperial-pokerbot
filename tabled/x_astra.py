"""Stress-test variant of the f_astra replica (Astra La Vista): what if this team adapted overnight.
Same open sizes and bet sizes (the fingerprint still matches), leaks reversed: it folds about 35%
when its small or medium bet is raised, about 45% to a 3-bet after opening, about 40% to a 4-bet
after 3-betting (calls, or shoves the top of its range), and its sizes are swapped: the smallest
bet size is now value-heavy and the biggest one holds the bluffs."""
import copy
import importlib.util
import os

_d = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("tf_astra_orig", os.path.join(_d, "f_astra.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)
ALLIN = _m.ALLIN


class Agent(_m.Agent):
    P = copy.deepcopy(_m.Agent.P)


P = Agent.P
P["f3b"] = (0.45, 0.35, 0.20)
P["f4b"] = (0.40, 0.35, 0.25)
P["f4b_shove"] = 0.40
_r = P["raised"]
_r["default"] = (0.35, 0.50, 0.15)
for _s in list(_r):
    if _s != "default" and _s <= 0.8:
        _r[_s] = (0.35, 0.50, 0.15)
for _st in P["J"]:
    _z = P["J"][_st]["sizes"]
    _k = sorted(s for s in _z if s != ALLIN)
    if len(_k) >= 2:
        _z[_k[0]], _z[_k[-1]] = _z[_k[-1]], _z[_k[0]]
