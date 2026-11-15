"""Replica of Gherkers (likely finalist) for the final-table sparring games.

Gherkers. Measured on 10 rounds, 10000 hands (r001, r004, r009, r020, r036, r038, r044, r045,
r047, r049); latest third: r045, r047, r049. VPIP 23, PFR 18, 3-bet 13; opens 3.5bb 97%, 3.75bb
1%. Bet sizes (share of pot): flop 0.33/0.41/0.7/1.1, turn 0.33/0.7/1.1/all-in, river
0.33/0.7/1.1/all-in.

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
    _base._NODES.setdefault('f_gherkers', _NF.get('f_gherkers', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'f_gherkers'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.121, 0.0),
            'UTG+1': (0.137, 0.0),
            'MP': (0.182, 0.0),
            'HJ': (0.213, 0.0),
            'CO': (0.311, 0.0),
            'BTN': (0.707, 0.0),
            'SB': (1.0, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(3.5, 1.0)]},
        # facing limpers: (call, raise)
        vs_limp=(0.117, 0.247),
        bb_iso=0.247,
        iso=(3.5, 1.0),
        limp_fold=0.933,
        limp_rr=0.0,
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.019, 0.072), 'm': (0.039, 0.096), 'l': (0.023, 0.04)},
            'BB': {'s': (0.268, 0.229), 'm': (0.314, 0.155), 'l': (0.324, 0.103)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.018, 0.046), 'SB': (0.028, 0.095), 'BB': (0.147, 0.067)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.08, 0.083),
            'UTG+1': (0.088, 0.052),
            'MP': (0.093, 0.07),
            'HJ': (0.095, 0.076),
            'CO': (0.078, 0.086),
            'BTN': (0.068, 0.097),
            'SB': (0.072, 0.031),
            'BB': (0.245, 0.145),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.445, 0.993), (0.269, 0.207)),
        tb_rand=0.53,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((3.8, 0.0), 0.678), ((3.2, 0.0), 0.322)], 'oop': [((3.8, 0.0), 0.833), ((3.2, 0.0), 0.167)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.444, 0.374, 0.181),
        fb_rand=0.34,
        fourbet=[(2.3, 1.0)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.033, 0.031),
        cold_rand=0.0,
        call_then_3b=0.25,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.601, 0.325, 0.075),
        f4b_shove=0.97,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.553, 0.432, 0.016),
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.795,
                'D_hu': 0.585,
                'S_hu': 0.839,
                'L_hu': 0.601,
                'A_mw': 0.425,
                'D_mw': 0.357,
                'S_mw': 0.522,
                'L_mw': 0.425,
            },
            'turn': {
                'A_hu': 0.569,
                'D_hu': 0.344,
                'S_hu': 0.615,
                'L_hu': 0.619,
                'A_mw': 0.255,
                'D_mw': 0.223,
                'S_mw': 0.31,
                'L_mw': 0.322,
            },
            'river': {
                'A_hu': 0.494,
                'D_hu': 0.188,
                'S_hu': 0.35,
                'L_hu': 0.466,
                'A_mw': 0.25,
                'D_mw': 0.286,
                'S_mw': 0.15,
                'L_mw': 0.077,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.33: {'air': 9.09, 'draw': 5.04, 'weak': 11.07, 'medium': 7.14, 'value': 2.06},
                    0.41: {'air': 1.09, 'draw': 0.04, 'weak': 0.07, 'medium': 0.14, 'value': 1.06},
                    0.7: {'air': 3.09, 'draw': 0.04, 'weak': 1.07, 'medium': 4.14, 'value': 1.06},
                    1.1: {'air': 8.09, 'draw': 4.04, 'weak': 5.07, 'medium': 20.14, 'value': 9.06},
                },
                'share': {
                    'A_hu': {0.33: 0.368, 0.7: 0.215, 1.1: 0.417},
                    'A_mw': {0.33: 0.29, 0.7: 0.161, 1.1: 0.548},
                    'D_hu': {0.33: 0.329, 0.41: 0.161, 0.7: 0.14, 1.1: 0.371},
                    'D_mw': {0.33: 0.381, 0.7: 0.19, 1.1: 0.429},
                    'S_hu': {0.33: 0.208, 0.7: 0.333, 1.1: 0.458},
                    'S_mw': {0.33: 0.045, 0.7: 0.318, 1.1: 0.636},
                    'L_hu': {0.33: 0.311, 0.41: 0.138, 0.7: 0.168, 1.1: 0.383},
                    'L_mw': {0.33: 0.209, 0.7: 0.256, 1.1: 0.535},
                },
            },
            'turn': {
                'sizes': {
                    0.33: {'air': 2.04, 'draw': 2.06, 'weak': 10.07, 'medium': 10.12, 'value': 3.12},
                    0.7: {'air': 2.04, 'draw': 5.06, 'weak': 1.07, 'medium': 1.12, 'value': 1.12},
                    1.1: {'air': 2.04, 'draw': 2.06, 'weak': 0.07, 'medium': 8.12, 'value': 7.12},
                    ALLIN: {'air': 0.04, 'draw': 0.06, 'weak': 1.07, 'medium': 0.12, 'value': 8.12},
                },
                'share': {
                    'A_hu': {0.33: 0.358, 0.7: 0.171, 1.1: 0.423, ALLIN: 0.049},
                    'A_mw': {0.33: 0.33, 0.7: 0.178, 1.1: 0.437, ALLIN: 0.056},
                    'D_hu': {0.33: 0.438, 0.7: 0.188, 1.1: 0.25, ALLIN: 0.125},
                    'D_mw': {0.33: 0.33, 0.7: 0.178, 1.1: 0.437, ALLIN: 0.056},
                    'S_hu': {0.33: 0.36, 0.7: 0.08, 1.1: 0.48, ALLIN: 0.08},
                    'S_mw': {0.33: 0.33, 0.7: 0.178, 1.1: 0.437, ALLIN: 0.056},
                    'L_hu': {0.33: 0.053, 0.7: 0.368, 1.1: 0.526, ALLIN: 0.053},
                    'L_mw': {0.33: 0.33, 0.7: 0.178, 1.1: 0.437, ALLIN: 0.056},
                },
            },
            'river': {
                'sizes': {
                    0.33: {'air': 1.03, 'weak': 6.08, 'medium': 3.07, 'value': 6.22},
                    0.7: {'air': 0.03, 'weak': 0.08, 'medium': 1.07, 'value': 0.22},
                    1.1: {'air': 1.03, 'weak': 0.08, 'medium': 1.07, 'value': 4.22},
                    ALLIN: {'air': 0.03, 'weak': 0.08, 'medium': 0.07, 'value': 6.22},
                },
                'share': {
                    'A_hu': {0.33: 0.415, 0.7: 0.049, 1.1: 0.341, ALLIN: 0.195},
                    'A_mw': {0.33: 0.405, 0.7: 0.076, 1.1: 0.342, ALLIN: 0.177},
                    'D_hu': {0.33: 0.353, 0.7: 0.118, 1.1: 0.382, ALLIN: 0.147},
                    'D_mw': {0.33: 0.405, 0.7: 0.076, 1.1: 0.342, ALLIN: 0.177},
                    'S_hu': {0.33: 0.267, 0.7: 0.133, 1.1: 0.4, ALLIN: 0.2},
                    'S_mw': {0.33: 0.405, 0.7: 0.076, 1.1: 0.342, ALLIN: 0.177},
                    'L_hu': {0.33: 0.471, 0.7: 0.118, 1.1: 0.412},
                    'L_mw': {0.33: 0.405, 0.7: 0.076, 1.1: 0.342, ALLIN: 0.177},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.513, 0.447, 0.039),
            0.33: {'*': (0.576, 0.395, 0.029), 'flop': (0.572, 0.393, 0.035)},
            0.41: (0.579, 0.256, 0.165),
            0.7: {'*': (0.566, 0.424, 0.01), 'flop': (0.626, 0.37, 0.004)},
            1.1: {'*': (0.335, 0.622, 0.043), 'flop': (0.308, 0.643, 0.048)},
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.39, 0.254, 0.357),
                    '<40%': (0.082, 0.346, 0.573),
                    '40-75%': (0.335, 0.278, 0.387),
                    '75-110%': (0.661, 0.152, 0.187),
                    'overbet': (0.664, 0.184, 0.152),
                },
                'xr': {
                    'all': (0.541, 0.2, 0.259),
                    '<40%': (0.1, 0.327, 0.573),
                    '40-75%': (0.553, 0.162, 0.285),
                    '75-110%': (0.642, 0.214, 0.144),
                    'overbet': (0.841, 0.114, 0.045),
                },
                'cells': {
                    'flop_n_hu': (0.344, 0.273, 0.384),
                    'flop_n_mw': (0.552, 0.187, 0.261),
                    'flop_x_hu': (0.568, 0.133, 0.299),
                    'flop_x_mw': (0.687, 0.158, 0.154),
                    'flop_ms_hu': (0.356, 0.406, 0.237),
                    'flop_ms_mw': (0.503, 0.282, 0.216),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.417, 0.455, 0.128),
                    '<40%': (0.106, 0.636, 0.258),
                    '40-75%': (0.427, 0.48, 0.093),
                    '75-110%': (0.644, 0.293, 0.064),
                    'overbet': (0.858, 0.123, 0.019),
                },
                'xr': {
                    'all': (0.6, 0.292, 0.108),
                    '<40%': (0.269, 0.535, 0.196),
                    '40-75%': (0.576, 0.316, 0.108),
                    '75-110%': (0.773, 0.155, 0.072),
                    'overbet': (0.957, 0.031, 0.012),
                },
                'cells': {
                    'turn_b2_n_hu': (0.332, 0.559, 0.109),
                    'turn_b2_n_mw': (0.465, 0.445, 0.091),
                    'turn_b2_x_hu': (0.737, 0.18, 0.083),
                    'turn_b2_x_mw': (0.696, 0.214, 0.09),
                    'turn_n_hu': (0.422, 0.418, 0.16),
                    'turn_n_mw': (0.621, 0.267, 0.112),
                    'turn_x_hu': (0.368, 0.618, 0.014),
                    'turn_x_mw': (0.589, 0.387, 0.023),
                    'turn_ms_hu': (0.639, 0.203, 0.159),
                    'turn_ms_mw': (0.633, 0.215, 0.151),
                },
                'no_xr': False,
            },
            'river': {
                'nx': {
                    'all': (0.486, 0.423, 0.091),
                    '<40%': (0.308, 0.617, 0.075),
                    '40-75%': (0.549, 0.402, 0.049),
                    '75-110%': (0.586, 0.256, 0.158),
                    'overbet': (0.764, 0.131, 0.105),
                },
                'xr': {
                    'all': (0.535, 0.459, 0.007),
                    '<40%': (0.274, 0.722, 0.003),
                    '40-75%': (0.609, 0.388, 0.003),
                    '75-110%': (0.794, 0.203, 0.003),
                    'overbet': (0.874, 0.124, 0.002),
                },
                'cells': {
                    'river_b3_n_hu': (0.444, 0.512, 0.044),
                    'river_b3_n_mw': (0.453, 0.492, 0.055),
                    'river_b3_x_hu': (0.524, 0.476, 0.0),
                    'river_b3_x_mw': (0.535, 0.466, 0.0),
                    'river_ct_n_hu': (0.593, 0.259, 0.148),
                    'river_ct_n_mw': (0.611, 0.162, 0.227),
                    'river_ct_x_hu': (0.486, 0.514, 0.0),
                    'river_ct_x_mw': (0.455, 0.545, 0.0),
                    'river_n_hu': (0.444, 0.475, 0.081),
                    'river_n_mw': (0.453, 0.464, 0.083),
                    'river_x_hu': (0.388, 0.612, 0.0),
                    'river_x_mw': (0.431, 0.569, 0.0),
                    'river_ms_hu': (0.687, 0.313, 0.0),
                    'river_ms_mw': (0.687, 0.313, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 5.1, 'draw': 6.1, 'weak': 2.1, 'medium': 10.4, 'value': 9.4},
            'turn': {'air': 1.1, 'draw': 0.2, 'weak': 1.2, 'medium': 0.7, 'value': 6.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 0.4, 'value': 6.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {'*': [(0.6, 0.539), (1.0, 0.461)]},
            'turn': {'*': [(1.0, 0.632), (0.6, 0.368)]},
            'river': {'*': [(0.75, 1.0)]},
        },
    )
