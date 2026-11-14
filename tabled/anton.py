"""Replica of Anton for the Table D sparring table.

Anton: 3-bets 26-32% with nearly any two cards (3.6x from the blinds, 3x in position), 4-bets
2.3x, opens 3bb / 4.5bb / 6.6bb (premiums) / 15bb, 0.83 of those on the button; limps to
re-raise; bets 0.55 and 0.8 pot mostly with air or weak pairs, 0.6 pot with top pair or better,
shoves the flop with real hands; folds 83-88% when its bet is raised.

Parameters written by tabled/build.py from the team's real hands (same definitions as
docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import ALLIN, Base  # noqa: E402,F401


class Agent(Base):
    NAME = 'anton'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.084, 0.037),
            'UTG+1': (0.086, 0.055),
            'MP': (0.147, 0.036),
            'HJ': (0.225, 0.033),
            'CO': (0.196, 0.062),
            'BTN': (0.947, 0.0),
            'SB': (0.994, 0.006),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={
            '*': {
                'top': 0.1,
                'top_sizes': [(6.6, 0.6), (15.0, 0.15), (4.5, 0.15), (3.0, 0.1)],
                'rest': [(3.0, 0.68), (4.5, 0.2), (6.6, 0.06), (15.0, 0.06)],
            },
            'SB': {
                'top': 0.08,
                'top_sizes': [(6.6, 0.6), (15.0, 0.15), (4.5, 0.25)],
                'rest': [(3.0, 0.46), (4.5, 0.42), (15.0, 0.08), (6.6, 0.04)],
            },
        },
        open_scale={'BTN': 0.8334},
        # facing limpers: (call, raise)
        vs_limp=(0.03, 0.6),
        bb_iso=0.789,
        iso=(4.0, 1.0),
        limp_fold=0.149,
        limp_rr=0.791,
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.202, 0.345), 'm': (0.058, 0.355), 'l': (0.106, 0.402)},
            'BB': {'s': (0.282, 0.581), 'm': (0.191, 0.524), 'l': (0.065, 0.649)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.065, 0.151), 'SB': (0.116, 0.164), 'BB': (0.231, 0.175)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.061, 0.152),
            'UTG+1': (0.063, 0.124),
            'MP': (0.052, 0.055),
            'HJ': (0.049, 0.092),
            'CO': (0.045, 0.119),
            'BTN': (0.089, 0.274),
            'SB': (0.097, 0.332),
            'BB': (0.029, 0.696),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.263, 0.548), (0.158, 0.143)),
        tb_rand=0.85,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={
            'ip': [((3.0, 0.0), 0.52), ((3.6, 0.0), 0.42), ((4.6, 0.0), 0.06)],
            'oop': [((3.6, 0.0), 0.8), ((4.6, 0.0), 0.1), ((3.0, 0.0), 0.1)],
        },
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.42, 0.328, 0.253),
        fb_rand=0.6,
        fourbet=[(2.3, 0.93), ('allin', 0.07)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.058, 0.039),
        cold_rand=0.8,
        call_then_3b=0.5,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.43, 0.236, 0.334),
        f4b_shove=0.758,
        fivebet=[(2.3, 0.84), ('allin', 0.16)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.386, 0.564, 0.05),
        shove_max=1.0,
        pre_noise=0.03,
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.801,
                'D_hu': 0.726,
                'S_hu': 0.542,
                'L_hu': 0.848,
                'A_mw': 0.372,
                'D_mw': 0.241,
                'S_mw': 0.411,
                'L_mw': 0.266,
            },
            'turn': {
                'A_hu': 0.57,
                'D_hu': 0.304,
                'S_hu': 0.41,
                'L_hu': 0.394,
                'A_mw': 0.098,
                'D_mw': 0.122,
                'S_mw': 0.206,
                'L_mw': 0.149,
            },
            'river': {
                'A_hu': 0.573,
                'D_hu': 0.285,
                'S_hu': 0.385,
                'L_hu': 0.251,
                'A_mw': 0.51,
                'D_mw': 0.429,
                'S_mw': 0.411,
                'L_mw': 0.411,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.33: {'air': 4.13, 'draw': 1.04, 'weak': 5.08, 'medium': 1.11, 'value': 0.04},
                    0.55: {'air': 15.13, 'draw': 6.04, 'weak': 10.08, 'medium': 6.11, 'value': 1.04},
                    0.6: {'air': 1.13, 'draw': 0.04, 'weak': 2.08, 'medium': 6.11, 'value': 2.04},
                    0.8: {'air': 11.13, 'draw': 0.04, 'weak': 2.08, 'medium': 5.11, 'value': 1.04},
                    1.1: {'air': 2.13, 'draw': 1.04, 'weak': 0.08, 'medium': 2.11, 'value': 0.04},
                    1.7: {'air': 1.13, 'draw': 0.04, 'weak': 1.08, 'medium': 1.11, 'value': 0.04},
                    ALLIN: {'air': 0.13, 'draw': 1.04, 'weak': 1.08, 'medium': 6.11, 'value': 7.04},
                },
                'share': {
                    'A_hu': {0.33: 0.126, 0.55: 0.368, 0.8: 0.046, 1.1: 0.322, ALLIN: 0.138},
                    'A_mw': {0.33: 0.121, 0.55: 0.333, 0.6: 0.152, 0.8: 0.091, 1.1: 0.03, 1.7: 0.03, ALLIN: 0.242},
                    'D_hu': {0.33: 0.186, 0.55: 0.392, 0.6: 0.021, 0.8: 0.227, 1.1: 0.093, 1.7: 0.041, ALLIN: 0.041},
                    'D_mw': {0.33: 0.125, 0.55: 0.438, 0.6: 0.062, 0.8: 0.125, 1.1: 0.062, 1.7: 0.062, ALLIN: 0.125},
                    'S_hu': {0.33: 0.209, 0.55: 0.355, 0.6: 0.055, 0.8: 0.209, 1.1: 0.082, 1.7: 0.036, ALLIN: 0.055},
                    'S_mw': {0.33: 0.121, 0.55: 0.333, 0.6: 0.152, 0.8: 0.091, 1.1: 0.03, 1.7: 0.03, ALLIN: 0.242},
                    'L_hu': {0.33: 0.209, 0.55: 0.355, 0.6: 0.055, 0.8: 0.209, 1.1: 0.082, 1.7: 0.036, ALLIN: 0.055},
                    'L_mw': {0.33: 0.121, 0.55: 0.333, 0.6: 0.152, 0.8: 0.091, 1.1: 0.03, 1.7: 0.03, ALLIN: 0.242},
                },
            },
            'turn': {
                'sizes': {
                    0.33: {'air': 3.07, 'draw': 4.08, 'weak': 3.08, 'medium': 6.1, 'value': 1.06},
                    0.55: {'air': 3.07, 'draw': 3.08, 'weak': 3.08, 'medium': 0.1, 'value': 2.06},
                    0.6: {'air': 0.07, 'draw': 0.08, 'weak': 0.08, 'medium': 3.1, 'value': 3.06},
                    0.75: {'air': 0.07, 'draw': 0.08, 'weak': 2.08, 'medium': 2.1, 'value': 0.06},
                    0.8: {'air': 4.07, 'draw': 3.08, 'weak': 2.08, 'medium': 3.1, 'value': 0.06},
                    ALLIN: {'air': 0.07, 'draw': 1.08, 'weak': 1.08, 'medium': 0.1, 'value': 2.06},
                },
                'share': {
                    'A_hu': {0.33: 0.28, 0.55: 0.246, 0.6: 0.093, 0.75: 0.051, 0.8: 0.22, ALLIN: 0.11},
                    'A_mw': {0.33: 0.278, 0.55: 0.225, 0.6: 0.113, 0.75: 0.053, 0.8: 0.205, ALLIN: 0.126},
                    'D_hu': {0.33: 0.214, 0.55: 0.143, 0.6: 0.179, 0.75: 0.071, 0.8: 0.179, ALLIN: 0.214},
                    'D_mw': {0.33: 0.278, 0.55: 0.225, 0.6: 0.113, 0.75: 0.053, 0.8: 0.205, ALLIN: 0.126},
                    'S_hu': {0.33: 0.286, 0.55: 0.071, 0.6: 0.071, 0.75: 0.143, 0.8: 0.143, ALLIN: 0.286},
                    'S_mw': {0.33: 0.278, 0.55: 0.225, 0.6: 0.113, 0.75: 0.053, 0.8: 0.205, ALLIN: 0.126},
                    'L_hu': {0.33: 0.214, 0.55: 0.143, 0.6: 0.179, 0.75: 0.071, 0.8: 0.179, ALLIN: 0.214},
                    'L_mw': {0.33: 0.278, 0.55: 0.225, 0.6: 0.113, 0.75: 0.053, 0.8: 0.205, ALLIN: 0.126},
                },
            },
            'river': {
                'sizes': {
                    0.33: {'air': 1.09, 'weak': 3.09, 'medium': 2.07, 'value': 2.14},
                    0.55: {'air': 6.09, 'weak': 6.09, 'medium': 1.07, 'value': 0.14},
                    0.6: {'air': 0.09, 'weak': 0.09, 'medium': 0.07, 'value': 4.14},
                    0.8: {'air': 1.09, 'weak': 0.09, 'medium': 2.07, 'value': 0.14},
                    ALLIN: {'air': 1.09, 'weak': 0.09, 'medium': 2.07, 'value': 8.14},
                },
                'share': {
                    'A_hu': {0.33: 0.122, 0.55: 0.39, 0.6: 0.049, 0.8: 0.049, ALLIN: 0.39},
                    'A_mw': {0.33: 0.135, 0.55: 0.338, 0.6: 0.122, 0.8: 0.054, ALLIN: 0.351},
                    'D_hu': {0.33: 0.123, 0.55: 0.338, 0.6: 0.123, 0.8: 0.062, ALLIN: 0.354},
                    'D_mw': {0.33: 0.135, 0.55: 0.338, 0.6: 0.122, 0.8: 0.054, ALLIN: 0.351},
                    'S_hu': {0.33: 0.154, 0.55: 0.154, 0.6: 0.308, ALLIN: 0.385},
                    'S_mw': {0.33: 0.135, 0.55: 0.338, 0.6: 0.122, 0.8: 0.054, ALLIN: 0.351},
                    'L_hu': {0.33: 0.123, 0.55: 0.338, 0.6: 0.123, 0.8: 0.062, ALLIN: 0.354},
                    'L_mw': {0.33: 0.135, 0.55: 0.338, 0.6: 0.122, 0.8: 0.054, ALLIN: 0.351},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.839, 0.081, 0.081),
            0.33: {'*': (0.897, 0.083, 0.02), 'flop': (0.892, 0.1, 0.008)},
            0.55: {'*': (0.928, 0.058, 0.014), 'flop': (0.979, 0.017, 0.004)},
            0.75: (0.622, 0.332, 0.046),
            0.8: {'*': (0.918, 0.016, 0.066), 'flop': (0.917, 0.005, 0.078)},
            1.1: (0.76, 0.029, 0.211),
            1.7: (0.765, 0.189, 0.046),
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.495, 0.287, 0.218),
                    '<40%': (0.223, 0.422, 0.356),
                    '40-75%': (0.491, 0.281, 0.227),
                    '75-110%': (0.644, 0.208, 0.148),
                    'overbet': (0.575, 0.293, 0.132),
                },
                'xr': {
                    'all': (0.715, 0.236, 0.049),
                    '<40%': (0.38, 0.536, 0.084),
                    '40-75%': (0.655, 0.319, 0.026),
                    '75-110%': (0.845, 0.089, 0.066),
                    'overbet': (0.926, 0.061, 0.013),
                },
                'cells': {
                    'flop_n_hu': (0.424, 0.328, 0.248),
                    'flop_n_mw': (0.813, 0.103, 0.084),
                    'flop_x_hu': (0.717, 0.249, 0.033),
                    'flop_x_mw': (0.877, 0.122, 0.001),
                    'flop_ms_hu': (0.619, 0.312, 0.069),
                    'flop_ms_mw': (0.808, 0.118, 0.074),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.463, 0.442, 0.095),
                    '<40%': (0.314, 0.635, 0.052),
                    '40-75%': (0.484, 0.37, 0.146),
                    '75-110%': (0.527, 0.409, 0.064),
                    'overbet': (0.639, 0.283, 0.079),
                },
                'xr': {
                    'all': (0.699, 0.288, 0.013),
                    '<40%': (0.451, 0.517, 0.032),
                    '40-75%': (0.75, 0.248, 0.003),
                    '75-110%': (0.855, 0.142, 0.003),
                    'overbet': (0.917, 0.08, 0.004),
                },
                'cells': {
                    'turn_b2_n_hu': (0.446, 0.485, 0.07),
                    'turn_b2_n_mw': (0.549, 0.392, 0.059),
                    'turn_b2_x_hu': (0.742, 0.256, 0.002),
                    'turn_b2_x_mw': (0.768, 0.227, 0.004),
                    'turn_n_hu': (0.462, 0.405, 0.133),
                    'turn_n_mw': (0.509, 0.385, 0.106),
                    'turn_x_hu': (0.719, 0.278, 0.003),
                    'turn_x_mw': (0.7, 0.298, 0.002),
                    'turn_ms_hu': (0.696, 0.286, 0.018),
                    'turn_ms_mw': (0.738, 0.247, 0.015),
                },
                'no_xr': False,
            },
            'river': {
                'nx': {
                    'all': (0.537, 0.402, 0.061),
                    '<40%': (0.344, 0.549, 0.108),
                    '40-75%': (0.609, 0.341, 0.05),
                    '75-110%': (0.664, 0.316, 0.02),
                    'overbet': (0.711, 0.251, 0.038),
                },
                'xr': {
                    'all': (0.718, 0.255, 0.027),
                    '<40%': (0.594, 0.382, 0.024),
                    '40-75%': (0.814, 0.18, 0.006),
                    '75-110%': (0.664, 0.272, 0.065),
                    'overbet': (0.825, 0.158, 0.017),
                },
                'cells': {
                    'river_b3_n_hu': (0.516, 0.394, 0.089),
                    'river_b3_n_mw': (0.52, 0.396, 0.084),
                    'river_b3_x_hu': (0.697, 0.287, 0.016),
                    'river_b3_x_mw': (0.706, 0.273, 0.021),
                    'river_ct_n_hu': (0.816, 0.164, 0.02),
                    'river_ct_n_mw': (0.625, 0.344, 0.031),
                    'river_ct_x_hu': (0.652, 0.312, 0.036),
                    'river_ct_x_mw': (0.507, 0.377, 0.117),
                    'river_n_hu': (0.473, 0.479, 0.048),
                    'river_n_mw': (0.388, 0.571, 0.041),
                    'river_x_hu': (0.76, 0.235, 0.005),
                    'river_x_mw': (0.747, 0.241, 0.012),
                    'river_ms_hu': (0.843, 0.153, 0.004),
                    'river_ms_mw': (0.807, 0.182, 0.011),
                },
                'no_xr': False,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 2.1, 'draw': 1.1, 'weak': 1.1, 'medium': 14.4, 'value': 7.4},
            'turn': {'air': 0.1, 'draw': 1.2, 'weak': 0.2, 'medium': 1.7, 'value': 7.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 1.4, 'value': 3.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {
                '*': [(0.75, 0.548), (1.1, 0.169), (0.9, 0.127), (ALLIN, 0.157)],
                'value': [(0.75, 0.324), (1.1, 0.1), (0.9, 0.075), (ALLIN, 0.501)],
                'medium': [(0.75, 0.324), (1.1, 0.1), (0.9, 0.075), (ALLIN, 0.501)],
            },
            'turn': {
                '*': [(0.75, 0.436), (1.1, 0.291), (ALLIN, 0.273)],
                'value': [(0.75, 0.076), (1.1, 0.051), (ALLIN, 0.873)],
                'medium': [(0.75, 0.076), (1.1, 0.051), (ALLIN, 0.873)],
            },
            'river': {'*': [(1.0, 1.0)]},
        },
    )
