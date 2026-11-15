"""Replica of Mohil'sPokerBot (likely finalist) for the final-table sparring games.

Mohil'sPokerBot. Measured on 4 rounds, 4000 hands (r011, r031, r044, r046); latest third: r046.
VPIP 22, PFR 13, 3-bet 6; opens 2.5bb 92%, 3bb 8%. Bet sizes (share of pot): flop 0.5/1, turn
0.5/1, river 0.5/1/all-in.

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
    _base._NODES.setdefault('f_mohil', _NF.get('f_mohil', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'f_mohil'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.11, 0.0),
            'UTG+1': (0.195, 0.0),
            'MP': (0.187, 0.0),
            'HJ': (0.251, 0.0),
            'CO': (0.34, 0.0),
            'BTN': (0.411, 0.0),
            'SB': (0.431, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(2.5, 1.0)], 'SB': [(3.0, 1.0)]},
        # facing limpers: (call, raise)
        vs_limp=(0.105, 0.193),
        bb_iso=0.193,
        iso=(2.5, 1.0),
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.184, 0.139), 'm': (0.184, 0.107), 'l': (0.087, 0.059)},
            'BB': {'s': (0.639, 0.122), 'm': (0.331, 0.117), 'l': (0.136, 0.038)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.251, 0.022), 'SB': (0.296, 0.025), 'BB': (0.339, 0.01)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.038, 0.019),
            'MP': (0.028, 0.029),
            'HJ': (0.03, 0.019),
            'CO': (0.033, 0.018),
            'BTN': (0.058, 0.015),
            'SB': (0.042, 0.035),
            'BB': (0.078, 0.058),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.463, 1.033), (0.269, 0.207)),
        tb_rand=0.1,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((3.0, 0.0), 0.911), ((4.0, 0.0), 0.089)], 'oop': [((3.6, 0.0), 0.792), ((4.6, 0.0), 0.125)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.63, 0.26, 0.11),
        fb_rand=0.0,
        fourbet=[('allin', 1.0)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.018, 0.006),
        cold_rand=0.0,
        call_then_3b=0.0,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.206, 0.12, 0.674),
        f4b_shove=0.581,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.25, 0.7, 0.05),
        shove_max=1.0,
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 1.0,
                'D_hu': 1.0,
                'S_hu': 1.0,
                'L_hu': 1.0,
                'A_mw': 0.42,
                'D_mw': 0.295,
                'S_mw': 0.283,
                'L_mw': 0.312,
            },
            'turn': {
                'A_hu': 0.989,
                'D_hu': 0.999,
                'S_hu': 0.998,
                'L_hu': 0.993,
                'A_mw': 0.217,
                'D_mw': 0.217,
                'S_mw': 0.113,
                'L_mw': 0.096,
            },
            'river': {
                'A_hu': 0.703,
                'D_hu': 0.826,
                'S_hu': 0.8,
                'L_hu': 0.733,
                'A_mw': 0.073,
                'D_mw': 0.073,
                'S_mw': 0.078,
                'L_mw': 0.1,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.5: {'air': 10.09, 'draw': 2.04, 'weak': 3.04, 'medium': 6.19, 'value': 0.04},
                    1.0: {'air': 0.09, 'draw': 2.04, 'weak': 2.04, 'medium': 15.19, 'value': 5.04},
                },
                'share': {
                    'A_hu': {0.5: 0.584, 1.0: 0.416},
                    'A_mw': {0.5: 0.75, 1.0: 0.25},
                    'D_hu': {0.5: 0.636, 1.0: 0.364},
                    'D_mw': {0.5: 0.525, 1.0: 0.475},
                    'S_hu': {0.5: 0.614, 1.0: 0.386},
                    'S_mw': {0.5: 0.5, 1.0: 0.5},
                    'L_hu': {0.5: 0.614, 1.0: 0.386},
                    'L_mw': {0.5: 0.5, 1.0: 0.5},
                },
            },
            'turn': {
                'sizes': {
                    0.5: {'air': 8.07, 'draw': 9.08, 'weak': 4.06, 'medium': 7.14, 'value': 0.04},
                    1.0: {'air': 0.07, 'draw': 0.08, 'weak': 3.06, 'medium': 9.14, 'value': 5.04},
                },
                'share': {
                    'A_hu': {0.5: 0.626, 1.0: 0.374},
                    'A_mw': {0.5: 0.667, 1.0: 0.333},
                    'D_hu': {0.5: 0.815, 1.0: 0.185},
                    'D_mw': {0.5: 0.667, 1.0: 0.333},
                    'S_hu': {0.5: 0.75, 1.0: 0.25},
                    'S_mw': {0.5: 0.667, 1.0: 0.333},
                    'L_hu': {0.5: 0.787, 1.0: 0.213},
                    'L_mw': {0.5: 0.667, 1.0: 0.333},
                },
            },
            'river': {
                'sizes': {
                    0.5: {'air': 9.13, 'weak': 3.05, 'medium': 3.12, 'value': 0.1},
                    1.0: {'air': 0.13, 'weak': 0.05, 'medium': 2.12, 'value': 4.1},
                    ALLIN: {'air': 1.13, 'weak': 1.05, 'medium': 4.12, 'value': 4.1},
                },
                'share': {
                    'A_hu': {0.5: 0.51, 1.0: 0.306, ALLIN: 0.184},
                    'A_mw': {0.5: 0.507, 1.0: 0.299, ALLIN: 0.194},
                    'D_hu': {0.5: 0.524, 1.0: 0.27, ALLIN: 0.206},
                    'D_mw': {0.5: 0.507, 1.0: 0.299, ALLIN: 0.194},
                    'S_hu': {0.5: 0.524, 1.0: 0.27, ALLIN: 0.206},
                    'S_mw': {0.5: 0.507, 1.0: 0.299, ALLIN: 0.194},
                    'L_hu': {0.5: 0.524, 1.0: 0.27, ALLIN: 0.206},
                    'L_mw': {0.5: 0.507, 1.0: 0.299, ALLIN: 0.194},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.388, 0.551, 0.061),
            0.5: {'*': (0.555, 0.438, 0.007), 'flop': (0.623, 0.375, 0.002), 'turn': (0.439, 0.559, 0.002)},
            1.0: {'*': (0.078, 0.76, 0.162), 'flop': (0.027, 0.798, 0.175)},
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.433, 0.438, 0.129),
                    '<40%': (0.192, 0.546, 0.263),
                    '40-75%': (0.438, 0.462, 0.1),
                    '75-110%': (0.535, 0.366, 0.099),
                    'overbet': (0.575, 0.308, 0.116),
                },
                'xr': {
                    'all': (0.522, 0.381, 0.097),
                    '<40%': (0.181, 0.671, 0.148),
                    '40-75%': (0.545, 0.349, 0.106),
                    '75-110%': (0.715, 0.22, 0.065),
                    'overbet': (0.734, 0.226, 0.04),
                },
                'cells': {
                    'flop_n_hu': (0.264, 0.582, 0.154),
                    'flop_n_mw': (0.638, 0.262, 0.1),
                    'flop_x_hu': (0.318, 0.53, 0.152),
                    'flop_x_mw': (0.522, 0.37, 0.108),
                    'flop_ms_hu': (0.337, 0.581, 0.082),
                    'flop_ms_mw': (0.554, 0.412, 0.033),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.422, 0.43, 0.148),
                    '<40%': (0.242, 0.499, 0.259),
                    '40-75%': (0.306, 0.5, 0.194),
                    '75-110%': (0.659, 0.289, 0.052),
                    'overbet': (0.411, 0.481, 0.108),
                },
                'xr': {
                    'all': (0.635, 0.286, 0.079),
                    '<40%': (0.508, 0.325, 0.167),
                    '40-75%': (0.586, 0.351, 0.063),
                    '75-110%': (0.805, 0.167, 0.028),
                    'overbet': (0.666, 0.28, 0.055),
                },
                'cells': {
                    'turn_b2_n_hu': (0.263, 0.583, 0.154),
                    'turn_b2_n_mw': (0.544, 0.358, 0.098),
                    'turn_b2_x_hu': (0.528, 0.369, 0.103),
                    'turn_b2_x_mw': (0.698, 0.236, 0.066),
                    'turn_n_hu': (0.434, 0.355, 0.211),
                    'turn_n_mw': (0.773, 0.164, 0.063),
                    'turn_x_hu': (0.528, 0.362, 0.111),
                    'turn_x_mw': (0.681, 0.241, 0.077),
                    'turn_ms_hu': (0.516, 0.401, 0.083),
                    'turn_ms_mw': (0.747, 0.225, 0.028),
                },
                'no_xr': False,
            },
            'river': {
                'nx': {
                    'all': (0.543, 0.361, 0.096),
                    '<40%': (0.113, 0.749, 0.138),
                    '40-75%': (0.422, 0.455, 0.123),
                    '75-110%': (0.683, 0.218, 0.099),
                    'overbet': (0.785, 0.17, 0.045),
                },
                'xr': {
                    'all': (0.94, 0.047, 0.013),
                    '<40%': (0.723, 0.219, 0.058),
                    '40-75%': (0.961, 0.031, 0.008),
                    '75-110%': (0.972, 0.022, 0.006),
                    'overbet': (0.971, 0.023, 0.006),
                },
                'cells': {
                    'river_b3_n_hu': (0.43, 0.506, 0.064),
                    'river_b3_n_mw': (0.46, 0.467, 0.073),
                    'river_b3_x_hu': (0.916, 0.085, 0.0),
                    'river_b3_x_mw': (0.94, 0.06, 0.0),
                    'river_ct_n_hu': (0.612, 0.306, 0.082),
                    'river_ct_n_mw': (0.797, 0.16, 0.043),
                    'river_ct_x_hu': (0.95, 0.051, 0.0),
                    'river_ct_x_mw': (0.979, 0.02, 0.0),
                    'river_n_hu': (0.506, 0.337, 0.158),
                    'river_n_mw': (0.515, 0.343, 0.141),
                    'river_x_hu': (0.936, 0.065, 0.0),
                    'river_x_mw': (0.955, 0.046, 0.0),
                    'river_ms_hu': (0.988, 0.013, 0.0),
                    'river_ms_mw': (0.973, 0.027, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 1.3, 'draw': 0.4, 'weak': 1.2, 'medium': 3.1, 'value': 2.1},
            'turn': {'air': 0.1, 'draw': 0.2, 'weak': 1.2, 'medium': 1.7, 'value': 6.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 1.4, 'value': 5.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {'*': [(0.57, 0.227), (0.4, 0.227), (1.0, 0.182), (0.5, 0.136)]},
            'turn': {'*': [(0.75, 1.0)]},
            'river': {'*': [(0.75, 1.0)]},
        },
    )
