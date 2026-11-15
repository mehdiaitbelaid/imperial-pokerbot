"""Replica of The Market Makers (likely finalist) for the final-table sparring games.

The Market Makers. Measured on 10 rounds, 10000 hands (r001, r005, r008, r024, r026, r027, r035,
r046, r052, r054); latest third: r046, r052, r054. VPIP 19, PFR 12, 3-bet 5; opens 2.5bb 100%.
Bet sizes (share of pot): flop 0.5/0.7/1/1.3, turn 0.5/0.7/1/all-in, river 0.6/0.7/1/all-in.

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
    _base._NODES.setdefault('f_tmm', _NF.get('f_tmm', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'f_tmm'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.126, 0.0),
            'UTG+1': (0.157, 0.0),
            'MP': (0.195, 0.0),
            'HJ': (0.234, 0.0),
            'CO': (0.261, 0.0),
            'BTN': (0.393, 0.0),
            'SB': (0.31, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(2.5, 1.0)]},
        # facing limpers: (call, raise)
        vs_limp=(0.108, 0.178),
        bb_iso=0.075,
        iso=(3.0, 1.0),
        limp_fold=1.0,
        limp_rr=0.0,
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.128, 0.041), 'm': (0.095, 0.03), 'l': (0.053, 0.098)},
            'BB': {'s': (0.434, 0.036), 'm': (0.476, 0.06), 'l': (0.378, 0.044)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.144, 0.036), 'SB': (0.108, 0.079), 'BB': (0.365, 0.047)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.081, 0.047),
            'UTG+1': (0.117, 0.032),
            'MP': (0.049, 0.022),
            'HJ': (0.089, 0.047),
            'CO': (0.076, 0.056),
            'BTN': (0.09, 0.053),
            'SB': (0.083, 0.048),
            'BB': (0.374, 0.037),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.496, 1.5), (0.161, 0.045)),
        tb_rand=0.1,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((3.0, 0.0), 0.969)], 'oop': [((3.6, 0.0), 0.787), ((4.6, 0.0), 0.191)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.39, 0.43, 0.18),
        fb_rand=0.33,
        fourbet=[(2.3, 0.154), ('allin', 0.846)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.003, 0.012),
        cold_rand=0.0,
        call_then_3b=0.0,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.101, 0.082, 0.817),
        f4b_shove=0.199,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.312, 0.65, 0.038),
        shove_max=0.059,
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.93,
                'D_hu': 0.809,
                'S_hu': 0.846,
                'L_hu': 0.824,
                'A_mw': 0.474,
                'D_mw': 0.284,
                'S_mw': 0.291,
                'L_mw': 0.361,
            },
            'turn': {
                'A_hu': 0.848,
                'D_hu': 0.671,
                'S_hu': 0.705,
                'L_hu': 0.302,
                'A_mw': 0.293,
                'D_mw': 0.085,
                'S_mw': 0.129,
                'L_mw': 0.176,
            },
            'river': {
                'A_hu': 0.912,
                'D_hu': 0.463,
                'S_hu': 0.601,
                'L_hu': 0.269,
                'A_mw': 0.143,
                'D_mw': 0.167,
                'S_mw': 0.139,
                'L_mw': 0.235,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.5: {'air': 36.13, 'draw': 9.03, 'weak': 11.12, 'medium': 0.1, 'value': 0.01},
                    0.7: {'air': 7.13, 'draw': 2.03, 'weak': 27.12, 'medium': 18.1, 'value': 1.01},
                    1.0: {'air': 1.13, 'draw': 0.03, 'weak': 3.12, 'medium': 12.1, 'value': 2.01},
                    1.3: {'air': 0.13, 'draw': 0.03, 'weak': 0.12, 'medium': 3.1, 'value': 2.01},
                },
                'share': {
                    'A_hu': {0.5: 0.528, 0.7: 0.361, 1.3: 0.111},
                    'A_mw': {0.7: 0.649, 1.0: 0.297, 1.3: 0.054},
                    'D_hu': {0.5: 0.534, 0.7: 0.322, 1.0: 0.111, 1.3: 0.034},
                    'D_mw': {0.5: 0.037, 0.7: 0.481, 1.0: 0.407, 1.3: 0.074},
                    'S_hu': {0.5: 0.519, 0.7: 0.148, 1.0: 0.333},
                    'S_mw': {0.7: 0.417, 1.0: 0.417, 1.3: 0.167},
                    'L_hu': {0.5: 0.692, 0.7: 0.231, 1.0: 0.077},
                    'L_mw': {0.5: 0.023, 0.7: 0.512, 1.0: 0.372, 1.3: 0.093},
                },
            },
            'turn': {
                'sizes': {
                    0.5: {'air': 26.09, 'draw': 14.05, 'weak': 17.12, 'medium': 0.1, 'value': 1.04},
                    0.7: {'air': 0.09, 'draw': 1.05, 'weak': 18.12, 'medium': 19.1, 'value': 2.04},
                    1.0: {'air': 0.09, 'draw': 0.05, 'weak': 1.12, 'medium': 10.1, 'value': 5.04},
                    ALLIN: {'air': 0.09, 'draw': 0.05, 'weak': 0.12, 'medium': 2.1, 'value': 4.04},
                },
                'share': {
                    'A_hu': {0.5: 0.657, 0.7: 0.271, ALLIN: 0.071},
                    'A_mw': {0.5: 0.593, 0.7: 0.314, ALLIN: 0.093},
                    'D_hu': {0.5: 0.413, 0.7: 0.413, 1.0: 0.109, ALLIN: 0.065},
                    'D_mw': {0.5: 0.593, 0.7: 0.314, ALLIN: 0.093},
                    'S_hu': {0.5: 0.433, 0.7: 0.367, 1.0: 0.2},
                    'S_mw': {0.5: 0.593, 0.7: 0.314, ALLIN: 0.093},
                    'L_hu': {0.5: 0.421, 0.7: 0.395, 1.0: 0.145, ALLIN: 0.039},
                    'L_mw': {0.5: 0.593, 0.7: 0.314, ALLIN: 0.093},
                },
            },
            'river': {
                'sizes': {
                    0.6: {'air': 34.13, 'weak': 17.1, 'medium': 2.08, 'value': 1.08},
                    0.7: {'air': 1.13, 'weak': 9.1, 'medium': 13.08, 'value': 6.08},
                    1.0: {'air': 0.13, 'weak': 0.1, 'medium': 3.08, 'value': 7.08},
                    ALLIN: {'air': 2.13, 'weak': 3.1, 'medium': 5.08, 'value': 8.08},
                },
                'share': {
                    'A_hu': {0.6: 0.534, 0.7: 0.203, 1.0: 0.135, ALLIN: 0.128},
                    'A_mw': {0.6: 0.613, 0.7: 0.21, 1.0: 0.016, ALLIN: 0.161},
                    'D_hu': {0.6: 0.413, 0.7: 0.326, 1.0: 0.087, ALLIN: 0.174},
                    'D_mw': {0.6: 0.613, 0.7: 0.21, 1.0: 0.016, ALLIN: 0.161},
                    'S_hu': {0.6: 0.483, 0.7: 0.345, 1.0: 0.103, ALLIN: 0.069},
                    'S_mw': {0.6: 0.613, 0.7: 0.21, 1.0: 0.016, ALLIN: 0.161},
                    'L_hu': {0.6: 0.413, 0.7: 0.326, 1.0: 0.087, ALLIN: 0.174},
                    'L_mw': {0.6: 0.613, 0.7: 0.21, 1.0: 0.016, ALLIN: 0.161},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.536, 0.435, 0.029),
            0.5: {'*': (0.777, 0.208, 0.016), 'flop': (0.793, 0.205, 0.002), 'turn': (0.781, 0.181, 0.038)},
            0.6: (0.714, 0.274, 0.012),
            0.7: {'*': (0.297, 0.681, 0.022), 'flop': (0.327, 0.641, 0.031), 'turn': (0.199, 0.794, 0.007)},
            1.0: (0.21, 0.716, 0.074),
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.347, 0.575, 0.078),
                    '<40%': (0.114, 0.806, 0.08),
                    '40-75%': (0.307, 0.61, 0.083),
                    '75-110%': (0.501, 0.443, 0.056),
                    'overbet': (0.717, 0.186, 0.097),
                },
                'xr': {
                    'all': (0.63, 0.354, 0.016),
                    '<40%': (0.466, 0.525, 0.009),
                    '40-75%': (0.562, 0.422, 0.016),
                    '75-110%': (0.772, 0.207, 0.02),
                    'overbet': (0.928, 0.069, 0.003),
                },
                'cells': {
                    'flop_n_hu': (0.26, 0.647, 0.093),
                    'flop_n_mw': (0.57, 0.39, 0.04),
                    'flop_x_hu': (0.576, 0.393, 0.031),
                    'flop_x_mw': (0.741, 0.257, 0.002),
                    'flop_ms_hu': (0.562, 0.434, 0.005),
                    'flop_ms_mw': (0.613, 0.386, 0.001),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.381, 0.543, 0.076),
                    '<40%': (0.173, 0.691, 0.137),
                    '40-75%': (0.329, 0.634, 0.037),
                    '75-110%': (0.497, 0.402, 0.101),
                    'overbet': (0.786, 0.15, 0.064),
                },
                'xr': {
                    'all': (0.52, 0.456, 0.024),
                    '<40%': (0.111, 0.87, 0.02),
                    '40-75%': (0.555, 0.408, 0.037),
                    '75-110%': (0.746, 0.247, 0.007),
                    'overbet': (0.857, 0.136, 0.007),
                },
                'cells': {
                    'turn_b2_n_hu': (0.312, 0.617, 0.07),
                    'turn_b2_n_mw': (0.358, 0.601, 0.041),
                    'turn_b2_x_hu': (0.358, 0.637, 0.005),
                    'turn_b2_x_mw': (0.436, 0.559, 0.005),
                    'turn_n_hu': (0.512, 0.402, 0.086),
                    'turn_n_mw': (0.629, 0.276, 0.095),
                    'turn_x_hu': (0.576, 0.417, 0.007),
                    'turn_x_mw': (0.845, 0.152, 0.003),
                    'turn_ms_hu': (0.548, 0.395, 0.056),
                    'turn_ms_mw': (0.619, 0.353, 0.028),
                },
                'no_xr': False,
            },
            'river': {
                'nx': {
                    'all': (0.503, 0.419, 0.079),
                    '<40%': (0.262, 0.651, 0.087),
                    '40-75%': (0.413, 0.504, 0.083),
                    '75-110%': (0.767, 0.151, 0.082),
                    'overbet': (0.882, 0.1, 0.019),
                },
                'xr': {
                    'all': (0.69, 0.301, 0.009),
                    '<40%': (0.415, 0.577, 0.008),
                    '40-75%': (0.805, 0.189, 0.006),
                    '75-110%': (0.798, 0.199, 0.003),
                    'overbet': (0.925, 0.073, 0.002),
                },
                'cells': {
                    'river_b3_n_hu': (0.406, 0.514, 0.08),
                    'river_b3_n_mw': (0.53, 0.406, 0.064),
                    'river_b3_x_hu': (0.559, 0.442, 0.0),
                    'river_b3_x_mw': (0.605, 0.395, 0.0),
                    'river_ct_n_hu': (0.774, 0.119, 0.106),
                    'river_ct_n_mw': (0.806, 0.136, 0.058),
                    'river_ct_x_hu': (0.803, 0.196, 0.0),
                    'river_ct_x_mw': (0.842, 0.158, 0.0),
                    'river_n_hu': (0.46, 0.452, 0.088),
                    'river_n_mw': (0.476, 0.456, 0.068),
                    'river_x_hu': (0.64, 0.36, 0.0),
                    'river_x_mw': (0.66, 0.34, 0.0),
                    'river_ms_hu': (0.708, 0.292, 0.0),
                    'river_ms_mw': (0.751, 0.249, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.3, 'draw': 0.4, 'weak': 0.2, 'medium': 4.1, 'value': 5.1},
            'turn': {'air': 0.1, 'draw': 0.2, 'weak': 0.2, 'medium': 3.7, 'value': 6.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 1.4, 'value': 6.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={'flop': {'*': [(1.0, 1.0)]}, 'turn': {'*': [(1.0, 1.0)]}, 'river': {'*': [(0.75, 1.0)]}},
    )
