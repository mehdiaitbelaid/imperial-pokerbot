"""Hardened variant of the f_gherkers replica: the same bot after its team fixed its folding leaks
(folds at most 50% to 3-bets, 45% to 4-bets and 45% when its bet is raised)."""
import copy
import importlib.util
import os

_d = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("td_f_gherkers_orig", os.path.join(_d, "f_gherkers.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


def _cap(t, cap):
    f = t[0]
    if f <= cap:
        return t
    extra = f - cap
    return (cap, t[1] + 0.7 * extra, t[2] + 0.3 * extra)


class Agent(_m.Agent):
    P = copy.deepcopy(_m.Agent.P)


P = Agent.P
P["f3b"] = _cap(P["f3b"], 0.50)
P["f4b"] = _cap(P["f4b"], 0.45)
if P.get("f4b_shove", 0) > 0.5:
    P["f4b_shove"] = 0.5
_r = P["raised"]
for _k in list(_r):
    if isinstance(_r[_k], dict):
        for _s in list(_r[_k]):
            _r[_k][_s] = _cap(_r[_k][_s], 0.45)
    else:
        _r[_k] = _cap(_r[_k], 0.45)
