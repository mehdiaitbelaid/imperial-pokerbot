"""Stress-test variant of the ysl replica: what if this team changed its bot overnight.
It now defends against 3-bets (folds 40%). Same open sizes and bet sizes, so our fingerprint still recognises the seat."""
import copy
import importlib.util
import os

_d = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("td_ysl_orig", os.path.join(_d, "ysl.py"))
_m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m)


class Agent(_m.Agent):
    P = copy.deepcopy(_m.Agent.P)


P = Agent.P
P["f3b"] = (0.40, 0.40, 0.20)

