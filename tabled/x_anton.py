"""Stress-test variant of the anton replica: what if this team changed its bot overnight.
It no longer folds to 4-bets or to raises of its bets. Same open sizes and bet sizes, so our fingerprint still recognises the seat."""
import copy
import importlib.util
import os

_d = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("td_anton_orig", os.path.join(_d, "anton.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


class Agent(_m.Agent):
    P = copy.deepcopy(_m.Agent.P)


P = Agent.P
P["f4b"] = (0.10, 0.45, 0.45)
P["f4b_shove"] = 0.30
_r = P["raised"]
for _k in list(_r):
    if isinstance(_r[_k], dict):
        for _s in list(_r[_k]):
            _r[_k][_s] = (0.25, 0.60, 0.15)
    else:
        _r[_k] = (0.25, 0.60, 0.15)

