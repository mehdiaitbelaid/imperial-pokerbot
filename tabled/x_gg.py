"""Stress-test variant of the gg replica: what if this team changed its bot overnight.
Its sizes are reversed: half pot is value, pot is a bluff. Same open sizes and bet sizes, so our fingerprint still recognises the seat."""
import copy
import importlib.util
import os

_d = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("td_gg_orig", os.path.join(_d, "gg.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


class Agent(_m.Agent):
    P = copy.deepcopy(_m.Agent.P)


P = Agent.P
for _st in P["J"]:
    _z = P["J"][_st]["sizes"]
    if 0.5 in _z and 1.0 in _z:
        _z[0.5], _z[1.0] = _z[1.0], _z[0.5]
_r = P["raised"]
if 0.5 in _r and 1.0 in _r:
    _r[0.5], _r[1.0] = _r[1.0], _r[0.5]

