"""Replica of Phil AIvey (likely finalist) for the final-table sparring games.

Phil AIvey. Measured on 5 rounds, 5000 hands (r001, r046, r047, r049, r053); latest third: r053.
VPIP 20, PFR 15, 3-bet 6; opens 3bb 66%, 2.5bb 32%. Bet sizes (share of pot): flop
0.5/0.55/0.75, turn 0.5/0.55/0.75, river 0.5/0.55/0.75/all-in.

Parameters written by tabled/build_f.py from the team's real hands (same definitions as
docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base as _base  # noqa: E402
from base import ALLIN, Base  # noqa: E402,F401

try:                                    # this replica's frozen node class mixes
    from _nodes_f import NODES as _NF
    _base._NODES.setdefault('f_phil', _NF.get('f_phil', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'f_phil'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.104, 0.0),
            'UTG+1': (0.125, 0.0),
            'MP': (0.161, 0.0),
            'HJ': (0.222, 0.0),
            'CO': (0.295, 0.0),
            'BTN': (0.665, 0.0),
            'SB': (0.836, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={
            '*': [(3.0, 1.0)],
            'UTG': [(3.0, 0.899), (4.0, 0.101)],
            'MP': [(3.0, 0.893), (4.0, 0.107)],
            'BTN': [(2.5, 1.0)],
            'SB': [(2.5, 1.0)],
        },
        # facing limpers: (call, raise)
        vs_limp=(0.031, 0.198),
        bb_iso=0.198,
        iso=(3.5, 0.5),
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.032, 0.119), 'm': (0.099, 0.106), 'l': (0.045, 0.08)},
            'BB': {'s': (0.459, 0.03), 'm': (0.469, 0.078), 'l': (0.371, 0.023)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.071, 0.039), 'SB': (0.079, 0.026), 'BB': (0.15, 0.071)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.069, 0.054),
            'MP': (0.049, 0.053),
            'HJ': (0.065, 0.06),
            'CO': (0.081, 0.049),
            'BTN': (0.07, 0.053),
            'SB': (0.07, 0.07),
            'BB': (0.178, 0.037),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.386, 0.861), (0.269, 0.207)),
        tb_rand=0.1,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((3.0, 0.0), 0.951)], 'oop': [((3.5, 0.0), 0.82), ((4.5, 0.0), 0.131)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.685, 0.226, 0.089),
        fb_rand=0.0,
        fourbet=[('allin', 1.0)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.004, 0.004),
        cold_rand=0.0,
        call_then_3b=0.267,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.852, 0.038, 0.11),
        f4b_shove=0.956,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.25, 0.7, 0.05),
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.759,
                'D_hu': 0.571,
                'S_hu': 0.533,
                'L_hu': 0.654,
                'A_mw': 0.126,
                'D_mw': 0.105,
                'S_mw': 0.087,
                'L_mw': 0.094,
            },
            'turn': {
                'A_hu': 0.75,
                'D_hu': 0.368,
                'S_hu': 0.565,
                'L_hu': 0.27,
                'A_mw': 0.08,
                'D_mw': 0.08,
                'S_mw': 0.137,
                'L_mw': 0.035,
            },
            'river': {
                'A_hu': 0.672,
                'D_hu': 0.444,
                'S_hu': 0.292,
                'L_hu': 0.323,
                'A_mw': 0.086,
                'D_mw': 0.086,
                'S_mw': 0.13,
                'L_mw': 0.06,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.5: {'air': 3.05, 'draw': 1.03, 'weak': 2.05, 'medium': 2.21, 'value': 0.05},
                    0.55: {'air': 0.05, 'draw': 1.03, 'weak': 1.05, 'medium': 8.21, 'value': 0.05},
                    0.75: {'air': 0.05, 'draw': 0.03, 'weak': 0.05, 'medium': 2.21, 'value': 3.05},
                },
                'share': {
                    'A_hu': {0.5: 0.671, 0.55: 0.233, 0.75: 0.096},
                    'A_mw': {0.5: 0.593, 0.55: 0.279, 0.75: 0.129},
                    'D_hu': {0.5: 0.589, 0.55: 0.286, 0.75: 0.125},
                    'D_mw': {0.5: 0.593, 0.55: 0.279, 0.75: 0.129},
                    'S_hu': {0.5: 0.569, 0.55: 0.293, 0.75: 0.138},
                    'S_mw': {0.5: 0.593, 0.55: 0.279, 0.75: 0.129},
                    'L_hu': {0.5: 0.569, 0.55: 0.293, 0.75: 0.138},
                    'L_mw': {0.5: 0.593, 0.55: 0.279, 0.75: 0.129},
                },
            },
            'turn': {
                'sizes': {
                    0.5: {'air': 2.05, 'draw': 1.05, 'medium': 0.18, 'value': 1.12},
                    0.55: {'air': 0.05, 'draw': 1.05, 'medium': 6.17, 'value': 3.12},
                    0.75: {'air': 0.05, 'draw': 0.05, 'medium': 1.18, 'value': 1.12},
                },
                'share': {
                    'A_hu': {0.5: 0.392, 0.55: 0.412, 0.75: 0.196},
                    'A_mw': {0.5: 0.447, 0.55: 0.382, 0.75: 0.171},
                    'D_hu': {0.5: 0.466, 0.55: 0.356, 0.75: 0.178},
                    'D_mw': {0.5: 0.447, 0.55: 0.382, 0.75: 0.171},
                    'S_hu': {0.5: 0.643, 0.55: 0.214, 0.75: 0.143},
                    'S_mw': {0.5: 0.447, 0.55: 0.382, 0.75: 0.171},
                    'L_hu': {0.5: 0.466, 0.55: 0.356, 0.75: 0.178},
                    'L_mw': {0.5: 0.447, 0.55: 0.382, 0.75: 0.171},
                },
            },
            'river': {
                'sizes': {
                    0.5: {'air': 3.06, 'weak': 1.06, 'medium': 2.16, 'value': 1.12},
                    0.55: {'air': 0.06, 'weak': 1.06, 'medium': 4.16, 'value': 2.12},
                    0.75: {'air': 0.06, 'weak': 0.06, 'medium': 1.16, 'value': 2.12},
                    ALLIN: {'air': 0.06, 'weak': 1.06, 'medium': 1.16, 'value': 1.12},
                },
                'share': {
                    'A_hu': {0.5: 0.25, 0.55: 0.375, 0.75: 0.292, ALLIN: 0.083},
                    'A_mw': {0.5: 0.342, 0.55: 0.316, 0.75: 0.237, ALLIN: 0.105},
                    'D_hu': {0.5: 0.361, 0.55: 0.333, 0.75: 0.194, ALLIN: 0.111},
                    'D_mw': {0.5: 0.342, 0.55: 0.316, 0.75: 0.237, ALLIN: 0.105},
                    'S_hu': {0.5: 0.361, 0.55: 0.333, 0.75: 0.194, ALLIN: 0.111},
                    'S_mw': {0.5: 0.342, 0.55: 0.316, 0.75: 0.237, ALLIN: 0.105},
                    'L_hu': {0.5: 0.361, 0.55: 0.333, 0.75: 0.194, ALLIN: 0.111},
                    'L_mw': {0.5: 0.342, 0.55: 0.316, 0.75: 0.237, ALLIN: 0.105},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.615, 0.269, 0.115),
            0.5: {'*': (0.866, 0.109, 0.024), 'flop': (0.894, 0.097, 0.009)},
            0.55: (0.406, 0.552, 0.042),
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.559, 0.346, 0.096),
                    '<40%': (0.344, 0.527, 0.129),
                    '40-75%': (0.551, 0.355, 0.094),
                    '75-110%': (0.652, 0.259, 0.089),
                    'overbet': (0.746, 0.199, 0.055),
                },
                'xr': {
                    'all': (0.697, 0.3, 0.004),
                    '<40%': (0.52, 0.477, 0.003),
                    '40-75%': (0.685, 0.314, 0.001),
                    '75-110%': (0.777, 0.222, 0.001),
                    'overbet': (0.705, 0.293, 0.002),
                },
                'cells': {
                    'flop_n_hu': (0.533, 0.381, 0.086),
                    'flop_n_mw': (0.65, 0.222, 0.128),
                    'flop_x_hu': (0.695, 0.305, 0.0),
                    'flop_x_mw': (0.853, 0.147, 0.0),
                    'flop_ms_hu': (0.631, 0.37, 0.0),
                    'flop_ms_mw': (0.619, 0.381, 0.0),
                },
                'no_xr': True,
            },
            'turn': {
                'nx': {
                    'all': (0.453, 0.421, 0.126),
                    '<40%': (0.186, 0.59, 0.224),
                    '40-75%': (0.479, 0.41, 0.111),
                    '75-110%': (0.45, 0.423, 0.127),
                    'overbet': (0.723, 0.213, 0.064),
                },
                'xr': {
                    'all': (0.629, 0.34, 0.031),
                    '<40%': (0.33, 0.632, 0.038),
                    '40-75%': (0.688, 0.265, 0.048),
                    '75-110%': (0.664, 0.325, 0.011),
                    'overbet': (0.753, 0.237, 0.01),
                },
                'cells': {
                    'turn_b2_n_hu': (0.372, 0.467, 0.161),
                    'turn_b2_n_mw': (0.565, 0.347, 0.088),
                    'turn_b2_x_hu': (0.54, 0.455, 0.005),
                    'turn_b2_x_mw': (0.62, 0.373, 0.008),
                    'turn_n_hu': (0.526, 0.345, 0.129),
                    'turn_n_mw': (0.641, 0.331, 0.028),
                    'turn_x_hu': (0.667, 0.292, 0.041),
                    'turn_x_mw': (0.813, 0.101, 0.087),
                    'turn_ms_hu': (0.7, 0.295, 0.005),
                    'turn_ms_mw': (0.788, 0.204, 0.009),
                },
                'no_xr': False,
            },
            'river': {
                'nx': {
                    'all': (0.514, 0.486, 0.0),
                    '<40%': (0.297, 0.703, 0.0),
                    '40-75%': (0.629, 0.371, 0.0),
                    '75-110%': (0.425, 0.575, 0.0),
                    'overbet': (0.691, 0.309, 0.0),
                },
                'xr': {
                    'all': (0.691, 0.309, 0.0),
                    '<40%': (0.403, 0.597, 0.0),
                    '40-75%': (0.816, 0.184, 0.0),
                    '75-110%': (0.763, 0.237, 0.0),
                    'overbet': (0.804, 0.196, 0.0),
                },
                'cells': {
                    'river_b3_n_hu': (0.342, 0.658, 0.0),
                    'river_b3_n_mw': (0.39, 0.61, 0.0),
                    'river_b3_x_hu': (0.418, 0.582, 0.0),
                    'river_b3_x_mw': (0.527, 0.473, 0.0),
                    'river_ct_n_hu': (0.599, 0.401, 0.0),
                    'river_ct_n_mw': (0.674, 0.326, 0.0),
                    'river_ct_x_hu': (0.751, 0.249, 0.0),
                    'river_ct_x_mw': (0.713, 0.287, 0.0),
                    'river_n_hu': (0.644, 0.356, 0.0),
                    'river_n_mw': (0.58, 0.42, 0.0),
                    'river_x_hu': (0.743, 0.257, 0.0),
                    'river_x_mw': (0.766, 0.234, 0.0),
                    'river_ms_hu': (0.834, 0.166, 0.0),
                    'river_ms_mw': (0.785, 0.215, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.3, 'draw': 0.4, 'weak': 0.2, 'medium': 2.1, 'value': 5.1},
            'turn': {'air': 0.1, 'draw': 0.2, 'weak': 0.2, 'medium': 0.7, 'value': 5.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 0.4, 'value': 2.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {
                '*': [(0.75, 0.96), (ALLIN, 0.04)],
                'value': [(0.75, 0.873), (ALLIN, 0.127)],
                'medium': [(0.75, 0.873), (ALLIN, 0.127)],
            },
            'turn': {
                '*': [(0.75, 0.803), (ALLIN, 0.197)],
                'value': [(0.75, 0.37), (ALLIN, 0.63)],
                'medium': [(0.75, 0.37), (ALLIN, 0.63)],
            },
            'river': {'*': [(0.75, 1.0)]},
        },
    )
