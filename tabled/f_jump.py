"""Replica of Jump Street (likely finalist) for the final-table sparring games.

Jump Street. Measured on 7 rounds, 7000 hands (r005, r023, r031, r035, r041, r042, r051); latest
third: r042, r051. VPIP 20, PFR 14, 3-bet 6; opens 2.5bb 61%, 3bb 26%. Bet sizes (share of pot):
flop 0.33/0.5/0.6/0.77/1, turn 0.33/0.5/0.6/0.66/0.81/1/all-in, river
0.33/0.5/0.6/0.72/0.75/0.87/1/all-in.

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
    _base._NODES.setdefault('f_jump', _NF.get('f_jump', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'f_jump'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.126, 0.0),
            'UTG+1': (0.112, 0.0),
            'MP': (0.172, 0.0),
            'HJ': (0.186, 0.0),
            'CO': (0.301, 0.0),
            'BTN': (0.378, 0.0),
            'SB': (0.691, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={
            '*': [(2.5, 1.0)],
            'MP': [(2.5, 0.632), (3.0, 0.368)],
            'HJ': [(2.5, 0.594), (3.0, 0.406)],
            'CO': [(2.5, 0.6), (2.2, 0.4)],
            'BTN': [(2.5, 0.536), (2.2, 0.464)],
            'SB': [(3.0, 0.59), (2.2, 0.41)],
        },
        # facing limpers: (call, raise)
        vs_limp=(0.096, 0.298),
        bb_iso=0.0,
        iso=(2.0, 1.5),
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.247, 0.056), 'm': (0.12, 0.056), 'l': (0.176, 0.031)},
            'BB': {'s': (0.481, 0.026), 'm': (0.304, 0.07), 'l': (0.164, 0.053)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.062, 0.046), 'SB': (0.141, 0.038), 'BB': (0.421, 0.06)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.086, 0.063),
            'UTG+1': (0.055, 0.058),
            'MP': (0.083, 0.076),
            'HJ': (0.064, 0.062),
            'CO': (0.09, 0.047),
            'BTN': (0.107, 0.072),
            'SB': (0.118, 0.062),
            'BB': (0.248, 0.052),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.441, 1.5), (0.22, 0.02)),
        tb_rand=0.1,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={
            'ip': [((3.3, 0.0), 0.371), ((3.0, 0.0), 0.278), ((3.21, 0.0), 0.278)],
            'oop': [((3.8, 0.0), 0.5), ((3.9, 0.0), 0.162), ((4.35, 0.0), 0.088)],
        },
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.514, 0.299, 0.187),
        fb_rand=0.36,
        fourbet=[(2.3, 1.0)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.023, 0.021),
        cold_rand=0.0,
        call_then_3b=0.44,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.221, 0.251, 0.529),
        f4b_shove=0.687,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.227, 0.473, 0.3),
        shove_max=0.038,
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.788,
                'D_hu': 0.596,
                'S_hu': 0.366,
                'L_hu': 0.466,
                'A_mw': 0.221,
                'D_mw': 0.112,
                'S_mw': 0.154,
                'L_mw': 0.209,
            },
            'turn': {
                'A_hu': 0.722,
                'D_hu': 0.365,
                'S_hu': 0.511,
                'L_hu': 0.31,
                'A_mw': 0.241,
                'D_mw': 0.163,
                'S_mw': 0.178,
                'L_mw': 0.115,
            },
            'river': {
                'A_hu': 0.652,
                'D_hu': 0.388,
                'S_hu': 0.455,
                'L_hu': 0.305,
                'A_mw': 0.264,
                'D_mw': 0.356,
                'S_mw': 0.228,
                'L_mw': 0.382,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.33: {'air': 1.1, 'draw': 0.02, 'weak': 0.02, 'medium': 4.14, 'value': 3.12},
                    0.5: {'air': 5.1, 'draw': 1.02, 'weak': 0.02, 'medium': 1.14, 'value': 0.12},
                    0.6: {'air': 0.1, 'draw': 1.02, 'weak': 0.02, 'medium': 4.14, 'value': 0.12},
                    0.77: {'air': 0.1, 'draw': 0.02, 'weak': 0.02, 'medium': 2.14, 'value': 6.12},
                    1.0: {'air': 3.1, 'draw': 0.02, 'weak': 2.02, 'medium': 2.14, 'value': 2.12},
                },
                'share': {
                    'A_hu': {0.33: 0.232, 0.5: 0.089, 0.6: 0.036, 0.77: 0.143, 1.0: 0.5},
                    'A_mw': {0.33: 0.167, 0.6: 0.417, 0.77: 0.167, 1.0: 0.25},
                    'D_hu': {0.33: 0.123, 0.5: 0.108, 0.6: 0.2, 0.77: 0.154, 1.0: 0.415},
                    'D_mw': {0.33: 0.167, 0.5: 0.167, 0.6: 0.083, 0.77: 0.25, 1.0: 0.333},
                    'S_hu': {0.33: 0.143, 0.5: 0.1, 0.6: 0.186, 0.77: 0.143, 1.0: 0.429},
                    'S_mw': {0.33: 0.2, 0.5: 0.067, 0.6: 0.2, 0.77: 0.233, 1.0: 0.3},
                    'L_hu': {0.33: 0.143, 0.5: 0.1, 0.6: 0.186, 0.77: 0.143, 1.0: 0.429},
                    'L_mw': {0.33: 0.2, 0.5: 0.067, 0.6: 0.2, 0.77: 0.233, 1.0: 0.3},
                },
            },
            'turn': {
                'sizes': {
                    0.33: {'air': 0.04, 'draw': 1.07, 'weak': 0.04, 'medium': 2.11, 'value': 2.15},
                    0.5: {'air': 1.04, 'draw': 1.07, 'weak': 1.04, 'medium': 0.11, 'value': 1.15},
                    0.6: {'air': 2.04, 'draw': 3.07, 'weak': 1.04, 'medium': 0.11, 'value': 0.15},
                    0.66: {'air': 0.04, 'draw': 0.07, 'weak': 0.04, 'medium': 4.11, 'value': 0.15},
                    0.81: {'air': 0.04, 'draw': 0.07, 'weak': 0.04, 'medium': 0.11, 'value': 2.15},
                    1.0: {'air': 0.04, 'draw': 0.07, 'weak': 1.04, 'medium': 2.11, 'value': 4.15},
                    ALLIN: {'air': 0.04, 'draw': 0.07, 'weak': 0.04, 'medium': 0.11, 'value': 2.15},
                },
                'share': {
                    'A_hu': {0.33: 0.179, 0.5: 0.089, 0.6: 0.196, 0.66: 0.161, 0.81: 0.071, 1.0: 0.25, ALLIN: 0.054},
                    'A_mw': {0.33: 0.154, 0.5: 0.049, 0.6: 0.293, 0.66: 0.098, 0.81: 0.089, 1.0: 0.268, ALLIN: 0.049},
                    'D_hu': {0.33: 0.08, 0.6: 0.4, 0.66: 0.08, 0.81: 0.04, 1.0: 0.28, ALLIN: 0.12},
                    'D_mw': {0.33: 0.154, 0.5: 0.049, 0.6: 0.293, 0.66: 0.098, 0.81: 0.089, 1.0: 0.268, ALLIN: 0.049},
                    'S_hu': {0.33: 0.16, 0.6: 0.4, 0.66: 0.04, 0.81: 0.2, 1.0: 0.2},
                    'S_mw': {0.33: 0.154, 0.5: 0.049, 0.6: 0.293, 0.66: 0.098, 0.81: 0.089, 1.0: 0.268, ALLIN: 0.049},
                    'L_hu': {0.33: 0.13, 0.5: 0.019, 0.6: 0.389, 0.66: 0.056, 0.81: 0.111, 1.0: 0.241, ALLIN: 0.056},
                    'L_mw': {0.33: 0.154, 0.5: 0.049, 0.6: 0.293, 0.66: 0.098, 0.81: 0.089, 1.0: 0.268, ALLIN: 0.049},
                },
            },
            'river': {
                'sizes': {
                    0.33: {'air': 1.08, 'weak': 2.09, 'medium': 2.07, 'value': 2.16},
                    0.5: {'air': 0.08, 'weak': 2.09, 'medium': 0.07, 'value': 1.16},
                    0.6: {'air': 4.08, 'weak': 1.09, 'medium': 1.07, 'value': 1.16},
                    0.72: {'air': 0.08, 'weak': 1.09, 'medium': 0.07, 'value': 1.16},
                    0.75: {'air': 0.08, 'weak': 0.09, 'medium': 0.07, 'value': 2.16},
                    0.87: {'air': 0.08, 'weak': 0.09, 'medium': 0.07, 'value': 0.16},
                    1.0: {'air': 1.08, 'weak': 1.09, 'medium': 1.07, 'value': 2.16},
                    ALLIN: {'air': 0.08, 'weak': 0.09, 'medium': 1.07, 'value': 3.16},
                },
                'share': {
                    'A_hu': {
                        0.33: 0.242,
                        0.5: 0.091,
                        0.6: 0.182,
                        0.72: 0.03,
                        0.75: 0.061,
                        0.87: 0.03,
                        1.0: 0.091,
                        ALLIN: 0.273,
                    },
                    'A_mw': {0.33: 0.062, 0.6: 0.25, 0.72: 0.062, 1.0: 0.625},
                    'D_hu': {
                        0.33: 0.267,
                        0.5: 0.067,
                        0.6: 0.067,
                        0.72: 0.067,
                        0.75: 0.067,
                        0.87: 0.067,
                        1.0: 0.267,
                        ALLIN: 0.133,
                    },
                    'D_mw': {0.33: 0.062, 0.6: 0.25, 0.72: 0.062, 1.0: 0.625},
                    'S_hu': {0.33: 0.263, 0.5: 0.053, 0.6: 0.211, 0.75: 0.053, 0.87: 0.053, 1.0: 0.368},
                    'S_mw': {0.33: 0.062, 0.6: 0.25, 0.72: 0.062, 1.0: 0.625},
                    'L_hu': {0.33: 0.225, 0.5: 0.05, 0.6: 0.125, 0.72: 0.05, 0.75: 0.05, 0.87: 0.075, 1.0: 0.375, ALLIN: 0.05},
                    'L_mw': {0.33: 0.062, 0.6: 0.25, 0.72: 0.062, 1.0: 0.625},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.391, 0.5, 0.109),
            0.33: (0.504, 0.267, 0.229),
            0.6: (0.326, 0.643, 0.031),
            0.77: (0.196, 0.625, 0.179),
            1.0: {'*': (0.408, 0.524, 0.068), 'flop': (0.469, 0.508, 0.023)},
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.452, 0.425, 0.123),
                    '<40%': (0.199, 0.58, 0.221),
                    '40-75%': (0.441, 0.451, 0.108),
                    '75-110%': (0.552, 0.352, 0.096),
                    'overbet': (0.738, 0.2, 0.063),
                },
                'xr': {
                    'all': (0.547, 0.424, 0.029),
                    '<40%': (0.359, 0.63, 0.01),
                    '40-75%': (0.509, 0.462, 0.028),
                    '75-110%': (0.619, 0.335, 0.046),
                    'overbet': (0.771, 0.225, 0.004),
                },
                'cells': {
                    'flop_n_hu': (0.272, 0.543, 0.185),
                    'flop_n_mw': (0.438, 0.518, 0.044),
                    'flop_x_hu': (0.455, 0.544, 0.001),
                    'flop_x_mw': (0.464, 0.514, 0.022),
                    'flop_ms_hu': (0.155, 0.68, 0.165),
                    'flop_ms_mw': (0.128, 0.736, 0.136),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.406, 0.534, 0.06),
                    '<40%': (0.145, 0.793, 0.062),
                    '40-75%': (0.396, 0.558, 0.046),
                    '75-110%': (0.645, 0.287, 0.068),
                    'overbet': (0.538, 0.389, 0.073),
                },
                'xr': {
                    'all': (0.476, 0.508, 0.016),
                    '<40%': (0.209, 0.784, 0.007),
                    '40-75%': (0.511, 0.458, 0.031),
                    '75-110%': (0.689, 0.307, 0.004),
                    'overbet': (0.742, 0.252, 0.006),
                },
                'cells': {
                    'turn_b2_n_hu': (0.315, 0.627, 0.058),
                    'turn_b2_n_mw': (0.423, 0.542, 0.035),
                    'turn_b2_x_hu': (0.508, 0.488, 0.004),
                    'turn_b2_x_mw': (0.422, 0.517, 0.061),
                    'turn_n_hu': (0.465, 0.428, 0.107),
                    'turn_n_mw': (0.772, 0.21, 0.018),
                    'turn_x_hu': (0.522, 0.472, 0.006),
                    'turn_x_mw': (0.571, 0.427, 0.002),
                    'turn_ms_hu': (0.464, 0.533, 0.003),
                    'turn_ms_mw': (0.6, 0.395, 0.005),
                },
                'no_xr': False,
            },
            'river': {
                'nx': {
                    'all': (0.54, 0.394, 0.067),
                    '<40%': (0.406, 0.504, 0.09),
                    '40-75%': (0.625, 0.326, 0.049),
                    '75-110%': (0.508, 0.415, 0.078),
                    'overbet': (0.796, 0.175, 0.03),
                },
                'xr': {
                    'all': (0.681, 0.315, 0.004),
                    '<40%': (0.452, 0.545, 0.003),
                    '40-75%': (0.773, 0.226, 0.001),
                    '75-110%': (0.764, 0.234, 0.002),
                    'overbet': (0.874, 0.124, 0.002),
                },
                'cells': {
                    'river_b3_n_hu': (0.55, 0.424, 0.027),
                    'river_b3_n_mw': (0.548, 0.419, 0.033),
                    'river_b3_x_hu': (0.67, 0.331, 0.0),
                    'river_b3_x_mw': (0.673, 0.327, 0.0),
                    'river_ct_n_hu': (0.449, 0.415, 0.137),
                    'river_ct_n_mw': (0.631, 0.31, 0.058),
                    'river_ct_x_hu': (0.76, 0.24, 0.0),
                    'river_ct_x_mw': (0.724, 0.276, 0.0),
                    'river_n_hu': (0.497, 0.314, 0.189),
                    'river_n_mw': (0.45, 0.423, 0.128),
                    'river_x_hu': (0.796, 0.203, 0.0),
                    'river_x_mw': (0.753, 0.247, 0.0),
                    'river_ms_hu': (0.521, 0.479, 0.0),
                    'river_ms_mw': (0.628, 0.372, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.3, 'draw': 0.4, 'weak': 0.2, 'medium': 8.1, 'value': 6.1},
            'turn': {'air': 0.1, 'draw': 0.2, 'weak': 0.2, 'medium': 2.7, 'value': 4.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 0.4, 'value': 3.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {
                '*': [(0.7, 0.388), (0.75, 0.345), (ALLIN, 0.267)],
                'value': [(0.7, 0.076), (0.75, 0.068), (ALLIN, 0.856)],
                'medium': [(0.7, 0.076), (0.75, 0.068), (ALLIN, 0.856)],
            },
            'turn': {
                '*': [(0.75, 0.593), (ALLIN, 0.407)],
                'value': [(0.75, 0.1), (ALLIN, 0.9)],
                'medium': [(0.75, 0.1), (ALLIN, 0.9)],
            },
            'river': {'*': [(0.75, 1.0)]},
        },
    )
