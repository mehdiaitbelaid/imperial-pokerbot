"""Replica of Astra La Vista (likely finalist) for the final-table sparring games.

Astra La Vista. Measured on 8 rounds, 8000 hands (r004, r010, r027, r028, r030, r038, r042,
r050); latest third: r042, r050. VPIP 20, PFR 15, 3-bet 5; opens 3bb 59%, 2.5bb 41%. Bet sizes
(share of pot): flop 0.33/0.5/0.6/0.75/0.85/all-in, turn 0.33/0.6/0.75/all-in, river
0.33/0.6/0.75/all-in.

Parameters written by tabled/build_g.py from the team's real hands (same definitions as
docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base as _base  # noqa: E402
from base import ALLIN, Base  # noqa: E402,F401

try:                                    # this replica's frozen node class mixes
    from _nodes_g import NODES as _NF
    _base._NODES.setdefault('f_astra', _NF.get('f_astra', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'f_astra'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.119, 0.0),
            'UTG+1': (0.149, 0.0),
            'MP': (0.195, 0.0),
            'HJ': (0.243, 0.0),
            'CO': (0.331, 0.0),
            'BTN': (0.493, 0.0),
            'SB': (0.471, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(3.0, 1.0)], 'CO': [(2.5, 1.0)], 'BTN': [(2.5, 1.0)], 'SB': [(3.0, 0.521), (2.5, 0.479)]},
        # facing limpers: (call, raise)
        vs_limp=(0.085, 0.231),
        bb_iso=0.231,
        iso=(3.5, 1.0),
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.005, 0.056), 'm': (0.026, 0.073), 'l': (0.049, 0.067)},
            'BB': {'s': (0.305, 0.013), 'm': (0.451, 0.045), 'l': (0.428, 0.072)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.099, 0.049), 'SB': (0.109, 0.028), 'BB': (0.311, 0.043)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.09, 0.045),
            'MP': (0.07, 0.024),
            'HJ': (0.115, 0.03),
            'CO': (0.059, 0.032),
            'BTN': (0.109, 0.071),
            'SB': (0.071, 0.057),
            'BB': (0.201, 0.07),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.735, 0.924), (0.173, 0.02)),
        tb_rand=0.1,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((3.0, 0.0), 0.468), ((3.6, 0.0), 0.367)], 'oop': [((3.6, 0.0), 0.804), ((4.6, 0.0), 0.103)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.57, 0.163, 0.267),
        fb_rand=0.55,
        fourbet=[(2.3, 0.414), ('allin', 0.586)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.025, 0.037),
        cold_rand=0.0,
        call_then_3b=0.464,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.137, 0.315, 0.549),
        f4b_shove=0.546,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.179, 0.8, 0.021),
        shove_max=1.0,
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.922,
                'D_hu': 0.865,
                'S_hu': 0.84,
                'L_hu': 0.864,
                'A_mw': 0.269,
                'D_mw': 0.085,
                'S_mw': 0.118,
                'L_mw': 0.085,
            },
            'turn': {
                'A_hu': 0.937,
                'D_hu': 0.751,
                'S_hu': 0.696,
                'L_hu': 0.565,
                'A_mw': 0.194,
                'D_mw': 0.026,
                'S_mw': 0.05,
                'L_mw': 0.059,
            },
            'river': {
                'A_hu': 0.944,
                'D_hu': 0.423,
                'S_hu': 0.472,
                'L_hu': 0.359,
                'A_mw': 0.268,
                'D_mw': 0.146,
                'S_mw': 0.147,
                'L_mw': 0.099,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.33: {'air': 19.11, 'draw': 5.03, 'weak': 12.12, 'medium': 1.11, 'value': 0.02},
                    0.5: {'air': 5.11, 'draw': 2.03, 'weak': 7.12, 'medium': 4.11, 'value': 0.02},
                    0.6: {'air': 2.11, 'draw': 0.03, 'weak': 8.12, 'medium': 10.11, 'value': 2.02},
                    0.75: {'air': 0.11, 'draw': 0.03, 'weak': 1.12, 'medium': 4.11, 'value': 1.02},
                    0.85: {'air': 0.11, 'draw': 1.03, 'weak': 1.12, 'medium': 3.11, 'value': 0.02},
                    ALLIN: {'air': 1.11, 'draw': 0.03, 'weak': 0.12, 'medium': 3.11, 'value': 2.02},
                },
                'share': {
                    'A_hu': {0.33: 0.35, 0.5: 0.227, 0.6: 0.241, 0.75: 0.143, ALLIN: 0.039},
                    'A_mw': {0.33: 0.056, 0.85: 0.889, ALLIN: 0.056},
                    'D_hu': {0.33: 0.744, 0.6: 0.192, 0.75: 0.016, ALLIN: 0.048},
                    'D_mw': {0.33: 0.056, 0.85: 0.889, ALLIN: 0.056},
                    'S_hu': {0.33: 0.667, 0.5: 0.056, 0.6: 0.222, 0.75: 0.056},
                    'S_mw': {0.33: 0.056, 0.85: 0.889, ALLIN: 0.056},
                    'L_hu': {0.33: 0.725, 0.5: 0.013, 0.6: 0.195, 0.75: 0.027, ALLIN: 0.04},
                    'L_mw': {0.33: 0.056, 0.85: 0.889, ALLIN: 0.056},
                },
            },
            'turn': {
                'sizes': {
                    0.33: {'air': 13.08, 'draw': 10.05, 'weak': 18.12, 'medium': 2.09, 'value': 0.07},
                    0.6: {'air': 3.08, 'draw': 0.05, 'weak': 5.12, 'medium': 10.09, 'value': 7.07},
                    0.75: {'air': 0.08, 'draw': 0.05, 'weak': 1.12, 'medium': 4.09, 'value': 7.07},
                    ALLIN: {'air': 0.08, 'draw': 0.05, 'weak': 1.12, 'medium': 4.09, 'value': 0.07},
                },
                'share': {
                    'A_hu': {0.33: 0.623, 0.6: 0.199, 0.75: 0.146, ALLIN: 0.033},
                    'A_mw': {0.33: 0.566, 0.6: 0.236, 0.75: 0.137, ALLIN: 0.061},
                    'D_hu': {0.33: 0.483, 0.6: 0.31, 0.75: 0.138, ALLIN: 0.069},
                    'D_mw': {0.33: 0.566, 0.6: 0.236, 0.75: 0.137, ALLIN: 0.061},
                    'S_hu': {0.33: 0.4, 0.6: 0.3, 0.75: 0.1, ALLIN: 0.2},
                    'S_mw': {0.33: 0.566, 0.6: 0.236, 0.75: 0.137, ALLIN: 0.061},
                    'L_hu': {0.33: 0.426, 0.6: 0.328, 0.75: 0.115, ALLIN: 0.131},
                    'L_mw': {0.33: 0.566, 0.6: 0.236, 0.75: 0.137, ALLIN: 0.061},
                },
            },
            'river': {
                'sizes': {
                    0.33: {'air': 24.15, 'weak': 18.12, 'medium': 4.07, 'value': 1.06},
                    0.6: {'air': 3.15, 'weak': 3.12, 'medium': 3.07, 'value': 4.06},
                    0.75: {'air': 0.15, 'weak': 0.12, 'medium': 3.07, 'value': 1.06},
                    ALLIN: {'air': 0.15, 'weak': 0.12, 'medium': 3.07, 'value': 4.06},
                },
                'share': {
                    'A_hu': {0.33: 0.647, 0.6: 0.206, 0.75: 0.098, ALLIN: 0.049},
                    'A_mw': {0.33: 0.613, 0.6: 0.227, 0.75: 0.101, ALLIN: 0.059},
                    'D_hu': {0.33: 0.613, 0.6: 0.227, 0.75: 0.101, ALLIN: 0.059},
                    'D_mw': {0.33: 0.613, 0.6: 0.227, 0.75: 0.101, ALLIN: 0.059},
                    'S_hu': {0.33: 0.583, 0.6: 0.25, 0.75: 0.083, ALLIN: 0.083},
                    'S_mw': {0.33: 0.613, 0.6: 0.227, 0.75: 0.101, ALLIN: 0.059},
                    'L_hu': {0.33: 0.613, 0.6: 0.227, 0.75: 0.101, ALLIN: 0.059},
                    'L_mw': {0.33: 0.613, 0.6: 0.227, 0.75: 0.101, ALLIN: 0.059},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.561, 0.357, 0.082),
            0.33: {'*': (0.731, 0.249, 0.02), 'flop': (0.675, 0.302, 0.023), 'turn': (0.876, 0.119, 0.006)},
            0.6: {'*': (0.33, 0.515, 0.155), 'flop': (0.234, 0.594, 0.172), 'turn': (0.356, 0.435, 0.209)},
            0.75: (0.464, 0.49, 0.047),
            0.85: (0.321, 0.204, 0.475),
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.385, 0.514, 0.101),
                    '<40%': (0.21, 0.644, 0.145),
                    '40-75%': (0.372, 0.524, 0.105),
                    '75-110%': (0.481, 0.449, 0.07),
                    'overbet': (0.636, 0.309, 0.055),
                },
                'xr': {
                    'all': (0.611, 0.302, 0.086),
                    '<40%': (0.347, 0.576, 0.077),
                    '40-75%': (0.608, 0.238, 0.155),
                    '75-110%': (0.719, 0.245, 0.036),
                    'overbet': (0.894, 0.082, 0.023),
                },
                'cells': {
                    'flop_n_hu': (0.319, 0.566, 0.115),
                    'flop_n_mw': (0.595, 0.35, 0.055),
                    'flop_x_hu': (0.523, 0.384, 0.093),
                    'flop_x_mw': (0.644, 0.248, 0.108),
                    'flop_ms_hu': (0.63, 0.349, 0.02),
                    'flop_ms_mw': (0.669, 0.323, 0.008),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.351, 0.547, 0.102),
                    '<40%': (0.153, 0.747, 0.1),
                    '40-75%': (0.414, 0.461, 0.125),
                    '75-110%': (0.505, 0.392, 0.103),
                    'overbet': (0.582, 0.384, 0.034),
                },
                'xr': {
                    'all': (0.496, 0.489, 0.016),
                    '<40%': (0.308, 0.677, 0.015),
                    '40-75%': (0.702, 0.291, 0.007),
                    '75-110%': (0.51, 0.484, 0.006),
                    'overbet': (0.638, 0.354, 0.008),
                },
                'cells': {
                    'turn_b2_n_hu': (0.262, 0.678, 0.06),
                    'turn_b2_n_mw': (0.44, 0.526, 0.034),
                    'turn_b2_x_hu': (0.425, 0.575, 0.0),
                    'turn_b2_x_mw': (0.681, 0.319, 0.0),
                    'turn_n_hu': (0.309, 0.435, 0.256),
                    'turn_n_mw': (0.734, 0.187, 0.078),
                    'turn_x_hu': (0.561, 0.439, 0.0),
                    'turn_x_mw': (0.731, 0.269, 0.0),
                    'turn_ms_hu': (0.293, 0.707, 0.0),
                    'turn_ms_mw': (0.656, 0.344, 0.0),
                },
                'no_xr': True,
            },
            'river': {
                'nx': {
                    'all': (0.344, 0.543, 0.113),
                    '<40%': (0.164, 0.761, 0.075),
                    '40-75%': (0.423, 0.399, 0.177),
                    '75-110%': (0.504, 0.346, 0.15),
                    'overbet': (0.549, 0.382, 0.07),
                },
                'xr': {
                    'all': (0.495, 0.442, 0.063),
                    '<40%': (0.222, 0.72, 0.058),
                    '40-75%': (0.418, 0.476, 0.106),
                    '75-110%': (0.815, 0.162, 0.023),
                    'overbet': (0.762, 0.209, 0.03),
                },
                'cells': {
                    'river_b3_n_hu': (0.258, 0.635, 0.107),
                    'river_b3_n_mw': (0.271, 0.622, 0.108),
                    'river_b3_x_hu': (0.497, 0.46, 0.044),
                    'river_b3_x_mw': (0.496, 0.451, 0.052),
                    'river_ct_n_hu': (0.601, 0.35, 0.049),
                    'river_ct_n_mw': (0.7, 0.255, 0.045),
                    'river_ct_x_hu': (0.622, 0.291, 0.087),
                    'river_ct_x_mw': (0.59, 0.279, 0.131),
                    'river_n_hu': (0.344, 0.489, 0.167),
                    'river_n_mw': (0.306, 0.557, 0.137),
                    'river_x_hu': (0.452, 0.527, 0.022),
                    'river_x_mw': (0.468, 0.495, 0.037),
                    'river_ms_hu': (0.429, 0.534, 0.037),
                    'river_ms_mw': (0.458, 0.494, 0.048),
                },
                'no_xr': False,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.1, 'draw': 2.1, 'weak': 3.1, 'medium': 6.4, 'value': 8.4},
            'turn': {'air': 0.1, 'draw': 0.2, 'weak': 0.2, 'medium': 3.7, 'value': 7.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 2.4, 'value': 7.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {
                '*': [(0.24, 0.25), (0.5, 0.167), (0.6, 0.167), (ALLIN, 0.248)],
                'value': [(0.24, 0.069), (0.5, 0.046), (0.6, 0.046), (ALLIN, 0.793)],
                'medium': [(0.24, 0.069), (0.5, 0.046), (0.6, 0.046), (ALLIN, 0.793)],
            },
            'turn': {'*': [(0.23, 0.286), (0.5, 0.286), (0.7, 0.286)]},
            'river': {
                '*': [(0.75, 0.833), (ALLIN, 0.167)],
                'value': [(0.75, 0.467), (ALLIN, 0.533)],
                'medium': [(0.75, 0.467), (ALLIN, 0.533)],
            },
        },
    )
