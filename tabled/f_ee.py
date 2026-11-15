"""Replica of Equity Engine (likely finalist) for the final-table sparring games.

Equity Engine. Measured on 10 rounds, 10000 hands (r001, r003, r006, r019, r021, r030, r031,
r045, r049, r052); latest third: r045, r049, r052. VPIP 25, PFR 17, 3-bet 3; opens 3.5bb 100%.
Bet sizes (share of pot): flop 0.45/0.5/0.8, turn 0.5/0.8, river 0.5/0.8/all-in.

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
    _base._NODES.setdefault('f_ee', _NF.get('f_ee', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'f_ee'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.222, 0.0),
            'UTG+1': (0.202, 0.0),
            'MP': (0.264, 0.0),
            'HJ': (0.327, 0.0),
            'CO': (0.354, 0.0),
            'BTN': (0.491, 0.0),
            'SB': (0.587, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(3.5, 1.0)]},
        # facing limpers: (call, raise)
        vs_limp=(0.005, 0.359),
        bb_iso=0.709,
        iso=(3.5, 1.0),
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.225, 0.038), 'm': (0.178, 0.035), 'l': (0.189, 0.024)},
            'BB': {'s': (0.654, 0.006), 'm': (0.411, 0.025), 'l': (0.252, 0.026)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.158, 0.034), 'SB': (0.406, 0.016), 'BB': (0.726, 0.025)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.037, 0.027),
            'UTG+1': (0.034, 0.015),
            'MP': (0.026, 0.036),
            'HJ': (0.031, 0.023),
            'CO': (0.034, 0.025),
            'BTN': (0.048, 0.031),
            'SB': (0.12, 0.03),
            'BB': (0.333, 0.01),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.167, 1.146), (0.123, 0.039)),
        tb_rand=0.1,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={
            'ip': [((3.0, 0.0), 0.836), ((3.33, 0.0), 0.082)],
            'oop': [((3.0, 0.0), 0.756), ((3.4, 0.0), 0.133), ((3.33, 0.0), 0.089)],
        },
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.633, 0.33, 0.036),
        fb_rand=0.0,
        fourbet=[(2.3, 1.0)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.012, 0.01),
        cold_rand=0.0,
        call_then_3b=0.632,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.091, 0.432, 0.477),
        f4b_shove=0.361,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.125, 0.683, 0.192),
        shove_max=0.038,
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.914,
                'D_hu': 0.528,
                'S_hu': 0.425,
                'L_hu': 0.575,
                'A_mw': 0.176,
                'D_mw': 0.173,
                'S_mw': 0.194,
                'L_mw': 0.131,
            },
            'turn': {
                'A_hu': 0.645,
                'D_hu': 0.546,
                'S_hu': 0.544,
                'L_hu': 0.406,
                'A_mw': 0.156,
                'D_mw': 0.347,
                'S_mw': 0.128,
                'L_mw': 0.136,
            },
            'river': {
                'A_hu': 0.65,
                'D_hu': 0.346,
                'S_hu': 0.519,
                'L_hu': 0.261,
                'A_mw': 0.443,
                'D_mw': 0.11,
                'S_mw': 0.209,
                'L_mw': 0.083,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.45: {'air': 11.14, 'draw': 3.06, 'weak': 1.08, 'medium': 0.08, 'value': 0.06},
                    0.5: {'air': 16.14, 'draw': 6.06, 'weak': 9.08, 'medium': 0.08, 'value': 0.06},
                    0.8: {'air': 2.14, 'draw': 3.06, 'weak': 6.08, 'medium': 16.08, 'value': 12.06},
                },
                'share': {
                    'A_hu': {0.45: 0.3, 0.5: 0.283, 0.8: 0.418},
                    'A_mw': {0.8: 1.0},
                    'D_hu': {0.5: 0.549, 0.8: 0.451},
                    'D_mw': {0.8: 1.0},
                    'S_hu': {0.5: 0.541, 0.8: 0.459},
                    'S_mw': {0.8: 1.0},
                    'L_hu': {0.5: 0.541, 0.8: 0.459},
                    'L_mw': {0.8: 1.0},
                },
            },
            'turn': {
                'sizes': {
                    0.5: {'air': 8.06, 'draw': 8.06, 'weak': 12.11, 'medium': 1.06, 'value': 0.1},
                    0.8: {'air': 3.06, 'draw': 2.06, 'weak': 7.11, 'medium': 10.06, 'value': 18.1},
                },
                'share': {
                    'A_hu': {0.5: 0.348, 0.8: 0.652},
                    'A_mw': {0.8: 1.0},
                    'D_hu': {0.5: 0.661, 0.8: 0.339},
                    'D_mw': {0.8: 1.0},
                    'S_hu': {0.5: 0.357, 0.8: 0.643},
                    'S_mw': {0.8: 1.0},
                    'L_hu': {0.5: 0.56, 0.8: 0.44},
                    'L_mw': {0.8: 1.0},
                },
            },
            'river': {
                'sizes': {
                    0.5: {'air': 7.07, 'weak': 7.11, 'medium': 0.06, 'value': 1.17},
                    0.8: {'air': 2.07, 'weak': 3.11, 'medium': 6.06, 'value': 14.17},
                    ALLIN: {'air': 0.07, 'weak': 4.11, 'medium': 2.06, 'value': 7.17},
                },
                'share': {
                    'A_hu': {0.5: 0.222, 0.8: 0.597, ALLIN: 0.181},
                    'A_mw': {0.5: 0.269, 0.8: 0.585, ALLIN: 0.146},
                    'D_hu': {0.5: 0.2, 0.8: 0.467, ALLIN: 0.333},
                    'D_mw': {0.5: 0.269, 0.8: 0.585, ALLIN: 0.146},
                    'S_hu': {0.5: 0.524, 0.8: 0.476},
                    'S_mw': {0.5: 0.269, 0.8: 0.585, ALLIN: 0.146},
                    'L_hu': {0.5: 0.409, 0.8: 0.477, ALLIN: 0.114},
                    'L_mw': {0.5: 0.269, 0.8: 0.585, ALLIN: 0.146},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.74, 0.177, 0.083),
            0.45: (0.814, 0.155, 0.03),
            0.5: {'*': (0.901, 0.09, 0.008), 'flop': (0.911, 0.088, 0.002), 'turn': (0.916, 0.081, 0.003)},
            0.8: {
                '*': (0.653, 0.225, 0.122),
                'flop': (0.664, 0.178, 0.158),
                'turn': (0.627, 0.334, 0.038),
                'river': (0.642, 0.197, 0.161),
            },
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.369, 0.457, 0.174),
                    '<40%': (0.149, 0.688, 0.163),
                    '40-75%': (0.39, 0.39, 0.22),
                    '75-110%': (0.401, 0.463, 0.136),
                    'overbet': (0.726, 0.224, 0.05),
                },
                'xr': {
                    'all': (0.616, 0.355, 0.028),
                    '<40%': (0.502, 0.49, 0.007),
                    '40-75%': (0.585, 0.383, 0.032),
                    '75-110%': (0.661, 0.308, 0.031),
                    'overbet': (0.839, 0.133, 0.028),
                },
                'cells': {
                    'flop_n_hu': (0.302, 0.489, 0.21),
                    'flop_n_mw': (0.566, 0.363, 0.071),
                    'flop_x_hu': (0.583, 0.393, 0.025),
                    'flop_x_mw': (0.681, 0.29, 0.029),
                    'flop_ms_hu': (0.651, 0.333, 0.016),
                    'flop_ms_mw': (0.495, 0.462, 0.044),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.368, 0.462, 0.171),
                    '<40%': (0.211, 0.623, 0.166),
                    '40-75%': (0.293, 0.5, 0.207),
                    '75-110%': (0.598, 0.267, 0.135),
                    'overbet': (0.647, 0.29, 0.064),
                },
                'xr': {
                    'all': (0.628, 0.362, 0.01),
                    '<40%': (0.439, 0.556, 0.006),
                    '40-75%': (0.604, 0.394, 0.002),
                    '75-110%': (0.727, 0.256, 0.017),
                    'overbet': (0.744, 0.254, 0.003),
                },
                'cells': {
                    'turn_b2_n_hu': (0.338, 0.547, 0.116),
                    'turn_b2_n_mw': (0.571, 0.366, 0.063),
                    'turn_b2_x_hu': (0.643, 0.356, 0.001),
                    'turn_b2_x_mw': (0.73, 0.269, 0.001),
                    'turn_n_hu': (0.239, 0.35, 0.41),
                    'turn_n_mw': (0.609, 0.257, 0.134),
                    'turn_x_hu': (0.608, 0.38, 0.013),
                    'turn_x_mw': (0.721, 0.257, 0.022),
                    'turn_ms_hu': (0.56, 0.44, 0.0),
                    'turn_ms_mw': (0.746, 0.253, 0.001),
                },
                'no_xr': False,
            },
            'river': {
                'nx': {
                    'all': (0.431, 0.42, 0.149),
                    '<40%': (0.301, 0.529, 0.17),
                    '40-75%': (0.398, 0.416, 0.186),
                    '75-110%': (0.605, 0.304, 0.09),
                    'overbet': (0.606, 0.326, 0.068),
                },
                'xr': {
                    'all': (0.691, 0.305, 0.004),
                    '<40%': (0.48, 0.517, 0.003),
                    '40-75%': (0.753, 0.246, 0.001),
                    '75-110%': (0.733, 0.266, 0.001),
                    'overbet': (0.814, 0.184, 0.002),
                },
                'cells': {
                    'river_b3_n_hu': (0.436, 0.433, 0.131),
                    'river_b3_n_mw': (0.703, 0.226, 0.07),
                    'river_b3_x_hu': (0.706, 0.294, 0.0),
                    'river_b3_x_mw': (0.858, 0.142, 0.0),
                    'river_ct_n_hu': (0.747, 0.122, 0.131),
                    'river_ct_n_mw': (0.914, 0.054, 0.032),
                    'river_ct_x_hu': (0.792, 0.208, 0.0),
                    'river_ct_x_mw': (0.797, 0.203, 0.0),
                    'river_n_hu': (0.15, 0.611, 0.239),
                    'river_n_mw': (0.369, 0.485, 0.146),
                    'river_x_hu': (0.772, 0.227, 0.0),
                    'river_x_mw': (0.817, 0.184, 0.0),
                    'river_ms_hu': (0.565, 0.434, 0.0),
                    'river_ms_mw': (0.79, 0.211, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.1, 'draw': 1.1, 'weak': 4.1, 'medium': 6.4, 'value': 7.4},
            'turn': {'air': 1.1, 'draw': 0.2, 'weak': 2.2, 'medium': 5.7, 'value': 5.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 3.4, 'value': 6.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {'*': [(0.75, 0.545), (0.81, 0.197), (0.7, 0.136)]},
            'turn': {'*': [(0.75, 0.478), (0.83, 0.304), (0.7, 0.174)]},
            'river': {'*': [(0.77, 0.5), (0.59, 0.2)]},
        },
    )
