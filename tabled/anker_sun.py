"""Replica of Anker Batteries, Sunday only built from Sunday's Table D hands only.

Anker Batteries. Measured on Sunday's 23 rounds, 23000 hands (s1, s1, s1, s1, s1, s1, s1, s1,
s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1, s1); latest third: s1, s1, s1, s1, s1,
s1, s1. VPIP 22, PFR 13, 3-bet 9; opens 2.5bb 100%. Bet sizes (share of pot): flop
0.4/0.62/0.7/1.1/2, turn 0.4/0.62/0.7/1.1/2/all-in, river 0.4/0.62/0.7/1.1/2/all-in.

Parameters written by tabled/build_s.py from the team's real hands (same definitions as
docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base as _base  # noqa: E402
from base import ALLIN, Base  # noqa: E402,F401

try:                                    # this replica's frozen node class mixes
    from _nodes_s import NODES as _NF
    _base._NODES.setdefault('anker_sun', _NF.get('anker_sun', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'anker_sun'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.066, 0.0),
            'UTG+1': (0.08, 0.0),
            'MP': (0.13, 0.0),
            'HJ': (0.192, 0.0),
            'CO': (0.287, 0.0),
            'BTN': (0.479, 0.0),
            'SB': (0.873, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(2.5, 1.0)]},
        # facing limpers: (call, raise)
        vs_limp=(0.0, 0.29),
        bb_iso=0.159,
        iso=(2.5, 1.0),
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.217, 0.066), 'm': (0.109, 0.184), 'l': (0.125, 0.061)},
            'BB': {'s': (0.41, 0.074), 'm': (0.803, 0.122), 'l': (0.273, 0.076)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.102, 0.037), 'SB': (0.164, 0.017), 'BB': (0.916, 0.025)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.076, 0.121),
            'UTG+1': (0.054, 0.075),
            'MP': (0.054, 0.174),
            'HJ': (0.066, 0.157),
            'CO': (0.086, 0.144),
            'BTN': (0.092, 0.066),
            'SB': (0.111, 0.055),
            'BB': (0.708, 0.074),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.689, 0.485), (0.02, 0.44)),
        tb_rand=0.34,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((3.0, 0.0), 0.814), ((3.2, 0.0), 0.16)], 'oop': [((3.0, 0.0), 0.597), ((3.2, 0.0), 0.358)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.424, 0.422, 0.154),
        fb_rand=0.22,
        fourbet=[(2.3, 1.0)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.067, 0.014),
        cold_rand=0.0,
        call_then_3b=0.372,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.836, 0.086, 0.078),
        f4b_shove=0.82,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.194, 0.789, 0.017),
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.753,
                'D_hu': 0.471,
                'S_hu': 0.717,
                'L_hu': 0.615,
                'A_mw': 0.335,
                'D_mw': 0.155,
                'S_mw': 0.28,
                'L_mw': 0.205,
            },
            'turn': {
                'A_hu': 0.657,
                'D_hu': 0.342,
                'S_hu': 0.761,
                'L_hu': 0.262,
                'A_mw': 0.554,
                'D_mw': 0.166,
                'S_mw': 0.175,
                'L_mw': 0.083,
            },
            'river': {
                'A_hu': 0.695,
                'D_hu': 0.582,
                'S_hu': 0.644,
                'L_hu': 0.404,
                'A_mw': 0.092,
                'D_mw': 0.165,
                'S_mw': 0.125,
                'L_mw': 0.077,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.4: {'air': 8.04, 'draw': 5.03, 'weak': 24.08, 'medium': 38.2, 'value': 4.06},
                    0.62: {'air': 0.04, 'draw': 1.03, 'weak': 3.08, 'medium': 24.2, 'value': 8.06},
                    0.7: {'air': 3.04, 'draw': 3.03, 'weak': 3.08, 'medium': 11.2, 'value': 5.06},
                    1.1: {'air': 7.04, 'draw': 2.03, 'weak': 4.08, 'medium': 5.2, 'value': 4.06},
                    2.0: {'air': 1.04, 'draw': 0.03, 'weak': 0.08, 'medium': 8.2, 'value': 3.06},
                },
                'share': {
                    'A_hu': {0.4: 0.279, 0.7: 0.203, 1.1: 0.299, 2.0: 0.218},
                    'A_mw': {0.62: 0.98, 0.7: 0.02},
                    'D_hu': {0.4: 0.433, 0.7: 0.198, 1.1: 0.3, 2.0: 0.068},
                    'D_mw': {0.62: 0.986, 1.1: 0.014},
                    'S_hu': {0.4: 0.211, 0.7: 0.105, 1.1: 0.421, 2.0: 0.263},
                    'S_mw': {0.62: 1.0},
                    'L_hu': {0.4: 0.35, 0.7: 0.15, 1.1: 0.5},
                    'L_mw': {0.62: 1.0},
                },
            },
            'turn': {
                'sizes': {
                    0.4: {'draw': 4.03, 'weak': 18.07, 'medium': 38.17, 'value': 15.13},
                    0.62: {'draw': 0.03, 'weak': 0.07, 'medium': 8.17, 'value': 5.13},
                    0.7: {'air': 1.01, 'draw': 4.03, 'weak': 4.07, 'medium': 11.17, 'value': 8.13},
                    1.1: {'air': 1.01, 'draw': 1.03, 'weak': 3.07, 'medium': 2.17, 'value': 5.13},
                    2.0: {'draw': 0.03, 'weak': 0.07, 'medium': 1.17, 'value': 8.13},
                    ALLIN: {'air': 1.01, 'draw': 1.03, 'weak': 1.07, 'medium': 8.17, 'value': 9.13},
                },
                'share': {
                    'A_hu': {0.4: 0.452, 0.7: 0.214, 1.1: 0.127, 2.0: 0.115, ALLIN: 0.091},
                    'A_mw': {0.62: 0.903, ALLIN: 0.097},
                    'D_hu': {0.4: 0.458, 0.62: 0.012, 0.7: 0.169, 1.1: 0.217, 2.0: 0.084, ALLIN: 0.06},
                    'D_mw': {0.62: 0.903, ALLIN: 0.097},
                    'S_hu': {0.4: 0.288, 0.7: 0.202, 1.1: 0.212, 2.0: 0.087, ALLIN: 0.212},
                    'S_mw': {0.62: 0.917, ALLIN: 0.083},
                    'L_hu': {0.4: 0.5, 0.7: 0.071, 1.1: 0.286, 2.0: 0.143},
                    'L_mw': {0.62: 0.903, ALLIN: 0.097},
                },
            },
            'river': {
                'sizes': {
                    0.4: {'air': 5.07, 'weak': 2.06, 'medium': 16.09, 'value': 24.18},
                    0.62: {'air': 0.07, 'weak': 0.06, 'medium': 1.09, 'value': 3.18},
                    0.7: {'air': 7.07, 'weak': 6.06, 'medium': 3.09, 'value': 7.18},
                    1.1: {'air': 4.07, 'weak': 4.06, 'medium': 2.09, 'value': 5.18},
                    2.0: {'air': 0.07, 'weak': 1.06, 'medium': 0.09, 'value': 0.18},
                    ALLIN: {'air': 4.07, 'weak': 4.06, 'medium': 6.09, 'value': 14.18},
                },
                'share': {
                    'A_hu': {0.4: 0.323, 0.62: 0.016, 0.7: 0.22, 1.1: 0.181, 2.0: 0.071, ALLIN: 0.189},
                    'A_mw': {0.4: 0.265, 0.62: 0.046, 0.7: 0.189, 1.1: 0.232, 2.0: 0.053, ALLIN: 0.215},
                    'D_hu': {0.4: 0.138, 0.62: 0.017, 0.7: 0.121, 1.1: 0.345, 2.0: 0.017, ALLIN: 0.362},
                    'D_mw': {0.4: 0.265, 0.62: 0.046, 0.7: 0.189, 1.1: 0.232, 2.0: 0.053, ALLIN: 0.215},
                    'S_hu': {0.4: 0.317, 0.62: 0.037, 0.7: 0.195, 1.1: 0.159, 2.0: 0.073, ALLIN: 0.22},
                    'S_mw': {0.4: 0.265, 0.62: 0.046, 0.7: 0.189, 1.1: 0.232, 2.0: 0.053, ALLIN: 0.215},
                    'L_hu': {0.4: 0.185, 0.7: 0.222, 1.1: 0.519, ALLIN: 0.074},
                    'L_mw': {0.4: 0.265, 0.62: 0.046, 0.7: 0.189, 1.1: 0.232, 2.0: 0.053, ALLIN: 0.215},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.464, 0.506, 0.03),
            0.4: {
                '*': (0.378, 0.586, 0.035),
                'flop': (0.438, 0.53, 0.032),
                'turn': (0.268, 0.679, 0.053),
                'river': (0.267, 0.72, 0.013),
            },
            0.62: {'*': (0.214, 0.782, 0.004), 'flop': (0.203, 0.797, 0.001)},
            0.7: {'*': (0.591, 0.406, 0.003), 'flop': (0.63, 0.369, 0.001)},
            1.1: {'*': (0.822, 0.176, 0.002), 'flop': (0.874, 0.126, 0.0)},
            2.0: (0.238, 0.669, 0.093),
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.446, 0.489, 0.065),
                    '<40%': (0.168, 0.733, 0.1),
                    '40-75%': (0.372, 0.571, 0.056),
                    '75-110%': (0.538, 0.4, 0.062),
                    'overbet': (0.707, 0.248, 0.044),
                },
                'xr': {
                    'all': (0.76, 0.24, 0.0),
                    '<40%': (0.495, 0.505, 0.0),
                    '40-75%': (0.777, 0.223, 0.0),
                    '75-110%': (0.895, 0.105, 0.0),
                    'overbet': (0.93, 0.07, 0.0),
                },
                'cells': {
                    'flop_n_hu': (0.384, 0.545, 0.071),
                    'flop_n_mw': (0.618, 0.332, 0.05),
                    'flop_x_hu': (0.799, 0.201, 0.0),
                    'flop_x_mw': (0.769, 0.231, 0.0),
                    'flop_ms_hu': (0.636, 0.364, 0.0),
                    'flop_ms_mw': (0.593, 0.407, 0.0),
                },
                'no_xr': True,
            },
            'turn': {
                'nx': {
                    'all': (0.381, 0.566, 0.054),
                    '<40%': (0.131, 0.797, 0.072),
                    '40-75%': (0.376, 0.588, 0.036),
                    '75-110%': (0.598, 0.349, 0.053),
                    'overbet': (0.632, 0.34, 0.027),
                },
                'xr': {
                    'all': (0.688, 0.312, 0.0),
                    '<40%': (0.473, 0.527, 0.0),
                    '40-75%': (0.699, 0.301, 0.0),
                    '75-110%': (0.892, 0.108, 0.0),
                    'overbet': (0.913, 0.087, 0.0),
                },
                'cells': {
                    'turn_b2_n_hu': (0.272, 0.676, 0.053),
                    'turn_b2_n_mw': (0.498, 0.492, 0.009),
                    'turn_b2_x_hu': (0.629, 0.371, 0.0),
                    'turn_b2_x_mw': (0.696, 0.304, 0.0),
                    'turn_n_hu': (0.485, 0.397, 0.118),
                    'turn_n_mw': (0.889, 0.094, 0.017),
                    'turn_x_hu': (0.542, 0.458, 0.0),
                    'turn_x_mw': (0.882, 0.118, 0.0),
                    'turn_ms_hu': (0.747, 0.253, 0.0),
                    'turn_ms_mw': (0.857, 0.143, 0.0),
                },
                'no_xr': True,
            },
            'river': {
                'nx': {
                    'all': (0.391, 0.564, 0.045),
                    '<40%': (0.224, 0.726, 0.05),
                    '40-75%': (0.301, 0.6, 0.1),
                    '75-110%': (0.647, 0.348, 0.005),
                    'overbet': (0.858, 0.139, 0.004),
                },
                'xr': {
                    'all': (0.665, 0.334, 0.001),
                    '<40%': (0.416, 0.584, 0.0),
                    '40-75%': (0.689, 0.311, 0.001),
                    '75-110%': (0.911, 0.089, 0.0),
                    'overbet': (0.978, 0.022, 0.0),
                },
                'cells': {
                    'river_b3_n_hu': (0.313, 0.645, 0.042),
                    'river_b3_n_mw': (0.684, 0.302, 0.014),
                    'river_b3_x_hu': (0.455, 0.545, 0.0),
                    'river_b3_x_mw': (0.89, 0.109, 0.0),
                    'river_ct_n_hu': (0.855, 0.093, 0.053),
                    'river_ct_n_mw': (0.852, 0.145, 0.003),
                    'river_ct_x_hu': (0.874, 0.126, 0.0),
                    'river_ct_x_mw': (0.923, 0.077, 0.0),
                    'river_n_hu': (0.211, 0.699, 0.09),
                    'river_n_mw': (0.653, 0.31, 0.037),
                    'river_x_hu': (0.54, 0.46, 0.0),
                    'river_x_mw': (0.935, 0.065, 0.0),
                    'river_ms_hu': (0.541, 0.459, 0.0),
                    'river_ms_mw': (0.793, 0.207, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.1, 'draw': 0.1, 'weak': 0.1, 'medium': 12.4, 'value': 11.4},
            'turn': {'air': 0.1, 'draw': 0.2, 'weak': 0.2, 'medium': 3.7, 'value': 7.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 0.4, 'value': 4.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {
                '*': [(0.6, 0.372), (1.0, 0.226), (1.8, 0.194), (0.75, 0.145), (ALLIN, 0.063)],
                'value': [(0.6, 0.317), (1.0, 0.193), (1.8, 0.166), (0.75, 0.124), (ALLIN, 0.2)],
                'medium': [(0.6, 0.317), (1.0, 0.193), (1.8, 0.166), (0.75, 0.124), (ALLIN, 0.2)],
            },
            'turn': {'*': [(0.6, 0.476), (1.0, 0.333), (1.8, 0.143)]},
            'river': {'*': [(0.75, 1.0)]},
        },
    )
