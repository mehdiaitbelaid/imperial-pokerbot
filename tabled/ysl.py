"""Replica of YSL_TWIZZY for the Table D sparring table.

YSL_TWIZZY: nit preflop (opens 2.8bb, 2.5 on the button, 3.1 from the small blind; folds 85-88%
to 3-bets and 80% of blinds to steals), calling station after the flop, bets only real hands:
0.48 pot with top pair, 0.77 pot with two pair or better, never folds when raised, never
check-raises.

Parameters written by tabled/build.py from the team's real hands (same definitions as
docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import ALLIN, Base  # noqa: E402,F401


class Agent(Base):
    NAME = 'ysl'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.148, 0.0),
            'UTG+1': (0.157, 0.0),
            'MP': (0.203, 0.0),
            'HJ': (0.257, 0.0),
            'CO': (0.44, 0.0),
            'BTN': (0.635, 0.0),
            'SB': (0.419, 0.232),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(2.8, 1.0)], 'BTN': [(2.5, 1.0)], 'SB': [(3.1, 1.0)]},
        # facing limpers: (call, raise)
        vs_limp=(0.0, 0.234),
        bb_iso=0.111,
        iso=('open', 0.8),
        limp_fold=1.0,
        limp_rr=0.0,
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.092, 0.065), 'm': (0.094, 0.027), 'l': (0.03, 0.057)},
            'BB': {'s': (0.227, 0.055), 'm': (0.225, 0.063), 'l': (0.064, 0.057)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.093, 0.023), 'SB': (0.099, 0.039), 'BB': (0.141, 0.045)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.08, 0.041),
            'UTG+1': (0.07, 0.054),
            'MP': (0.056, 0.029),
            'HJ': (0.071, 0.039),
            'CO': (0.091, 0.039),
            'BTN': (0.089, 0.044),
            'SB': (0.08, 0.027),
            'BB': (0.155, 0.043),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.225, 1.24), (0.091, 0.082)),
        tb_rand=0.05,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((2.95, 0.0), 1.0)], 'oop': [((3.45, 0.0), 0.88), ((4.05, 0.0), 0.12)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.881, 0.044, 0.076),
        fourbet=[(2.15, 0.85), (2.35, 0.15)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.002, 0.023),
        call_then_3b=0.032,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.375, 0.13, 0.495),
        f4b_shove=0.545,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.107, 0.871, 0.021),
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.433,
                'D_hu': 0.253,
                'S_hu': 0.355,
                'L_hu': 0.218,
                'A_mw': 0.283,
                'D_mw': 0.164,
                'S_mw': 0.106,
                'L_mw': 0.141,
            },
            'turn': {
                'A_hu': 0.796,
                'D_hu': 0.205,
                'S_hu': 0.292,
                'L_hu': 0.128,
                'A_mw': 0.246,
                'D_mw': 0.21,
                'S_mw': 0.128,
                'L_mw': 0.027,
            },
            'river': {
                'A_hu': 0.609,
                'D_hu': 0.194,
                'S_hu': 0.311,
                'L_hu': 0.195,
                'A_mw': 0.354,
                'D_mw': 0.119,
                'S_mw': 0.114,
                'L_mw': 0.123,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.33: {'air': 1.04, 'weak': 1.01, 'medium': 0.25, 'value': 0.1},
                    0.38: {'air': 6.04, 'medium': 0.25, 'value': 0.1},
                    0.42: {'air': 0.04, 'medium': 5.25, 'value': 0.1},
                    0.48: {'air': 0.04, 'medium': 33.25, 'value': 2.1},
                    0.66: {'air': 0.04, 'medium': 0.25, 'value': 2.1},
                    0.77: {'air': 0.04, 'medium': 1.25, 'value': 11.1},
                    0.92: {'air': 0.04, 'medium': 0.25, 'value': 1.1},
                },
                'share': {
                    'A_hu': {0.33: 0.03, 0.38: 0.11, 0.42: 0.11, 0.48: 0.62, 0.66: 0.02, 0.77: 0.11},
                    'A_mw': {0.48: 0.632, 0.77: 0.368},
                    'D_hu': {0.42: 0.093, 0.48: 0.537, 0.66: 0.074, 0.77: 0.241, 0.92: 0.056},
                    'D_mw': {0.48: 0.588, 0.77: 0.382, 0.92: 0.029},
                    'S_hu': {0.33: 0.333, 0.38: 0.067, 0.48: 0.6},
                    'S_mw': {0.48: 0.588, 0.77: 0.382, 0.92: 0.029},
                    'L_hu': {0.33: 0.065, 0.38: 0.013, 0.42: 0.065, 0.48: 0.597, 0.66: 0.052, 0.77: 0.169, 0.92: 0.039},
                    'L_mw': {0.48: 0.588, 0.77: 0.382, 0.92: 0.029},
                },
            },
            'turn': {
                'sizes': {
                    0.33: {'air': 0.02, 'weak': 1.04, 'medium': 0.2, 'value': 0.14},
                    0.38: {'air': 2.02, 'weak': 0.04, 'medium': 0.2, 'value': 0.14},
                    0.42: {'air': 0.02, 'weak': 0.04, 'medium': 6.2, 'value': 0.14},
                    0.48: {'air': 1.02, 'weak': 6.04, 'medium': 26.2, 'value': 8.14},
                    0.66: {'air': 0.02, 'weak': 0.04, 'medium': 0.2, 'value': 2.14},
                    0.77: {'air': 0.02, 'weak': 0.04, 'medium': 0.2, 'value': 12.14},
                    0.92: {'air': 0.02, 'weak': 0.04, 'medium': 0.2, 'value': 1.14},
                },
                'share': {
                    'A_hu': {0.38: 0.027, 0.42: 0.107, 0.48: 0.64, 0.66: 0.027, 0.77: 0.147, 0.92: 0.053},
                    'A_mw': {0.33: 0.069, 0.38: 0.025, 0.42: 0.069, 0.48: 0.606, 0.66: 0.019, 0.77: 0.181, 0.92: 0.031},
                    'D_hu': {0.42: 0.037, 0.48: 0.704, 0.77: 0.222, 0.92: 0.037},
                    'D_mw': {0.33: 0.069, 0.38: 0.025, 0.42: 0.069, 0.48: 0.606, 0.66: 0.019, 0.77: 0.181, 0.92: 0.031},
                    'S_hu': {0.33: 0.324, 0.38: 0.029, 0.42: 0.029, 0.48: 0.441, 0.66: 0.029, 0.77: 0.147},
                    'S_mw': {0.33: 0.069, 0.38: 0.025, 0.42: 0.069, 0.48: 0.606, 0.66: 0.019, 0.77: 0.181, 0.92: 0.031},
                    'L_hu': {0.38: 0.077, 0.42: 0.077, 0.48: 0.615, 0.77: 0.231},
                    'L_mw': {0.33: 0.069, 0.38: 0.025, 0.42: 0.069, 0.48: 0.606, 0.66: 0.019, 0.77: 0.181, 0.92: 0.031},
                },
            },
            'river': {
                'sizes': {
                    0.37: {'air': 3.04, 'weak': 1.05, 'medium': 0.15, 'value': 1.16},
                    0.42: {'air': 0.04, 'weak': 0.05, 'medium': 2.15, 'value': 1.16},
                    0.48: {'air': 1.04, 'weak': 4.05, 'medium': 12.15, 'value': 3.16},
                    0.66: {'air': 0.04, 'weak': 1.05, 'medium': 1.15, 'value': 2.16},
                    0.77: {'air': 0.04, 'weak': 0.05, 'medium': 1.15, 'value': 10.16},
                    0.92: {'air': 0.04, 'weak': 0.05, 'medium': 0.15, 'value': 1.16},
                },
                'share': {
                    'A_hu': {0.37: 0.049, 0.42: 0.098, 0.48: 0.439, 0.66: 0.122, 0.77: 0.22, 0.92: 0.073},
                    'A_mw': {0.37: 0.232, 0.42: 0.036, 0.48: 0.357, 0.66: 0.071, 0.77: 0.268, 0.92: 0.036},
                    'D_hu': {0.48: 0.833, 0.77: 0.167},
                    'D_mw': {0.37: 0.232, 0.42: 0.036, 0.48: 0.357, 0.66: 0.071, 0.77: 0.268, 0.92: 0.036},
                    'S_hu': {0.37: 0.727, 0.66: 0.03, 0.77: 0.242},
                    'S_mw': {0.37: 0.232, 0.42: 0.036, 0.48: 0.357, 0.66: 0.071, 0.77: 0.268, 0.92: 0.036},
                    'L_hu': {0.48: 0.556, 0.66: 0.056, 0.77: 0.389},
                    'L_mw': {0.37: 0.232, 0.42: 0.036, 0.48: 0.357, 0.66: 0.071, 0.77: 0.268, 0.92: 0.036},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.0, 0.87, 0.13),
            0.48: {
                '*': (0.0, 0.905, 0.095),
                'flop': (0.0, 0.871, 0.129),
                'turn': (0.0, 0.902, 0.098),
                'river': (0.0, 0.962, 0.038),
            },
            0.77: (0.0, 0.771, 0.229),
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.179, 0.774, 0.047),
                    '<40%': (0.028, 0.893, 0.079),
                    '40-75%': (0.221, 0.744, 0.035),
                    '75-110%': (0.255, 0.714, 0.031),
                    'overbet': (0.27, 0.689, 0.041),
                },
                'xr': {
                    'all': (0.267, 0.733, 0.001),
                    '<40%': (0.048, 0.952, 0.0),
                    '40-75%': (0.244, 0.756, 0.0),
                    '75-110%': (0.355, 0.645, 0.0),
                    'overbet': (0.446, 0.554, 0.0),
                },
                'cells': {
                    'flop_n_hu': (0.103, 0.855, 0.041),
                    'flop_n_mw': (0.423, 0.513, 0.064),
                    'flop_x_hu': (0.239, 0.761, 0.0),
                    'flop_x_mw': (0.523, 0.477, 0.0),
                    'flop_ms_hu': (0.116, 0.884, 0.0),
                    'flop_ms_mw': (0.326, 0.674, 0.0),
                },
                'no_xr': True,
            },
            'turn': {
                'nx': {
                    'all': (0.25, 0.682, 0.068),
                    '<40%': (0.036, 0.878, 0.086),
                    '40-75%': (0.304, 0.651, 0.045),
                    '75-110%': (0.376, 0.555, 0.069),
                    'overbet': (0.34, 0.587, 0.073),
                },
                'xr': {
                    'all': (0.39, 0.609, 0.001),
                    '<40%': (0.09, 0.909, 0.001),
                    '40-75%': (0.431, 0.569, 0.0),
                    '75-110%': (0.483, 0.517, 0.0),
                    'overbet': (0.63, 0.37, 0.0),
                },
                'cells': {
                    'turn_b2_n_hu': (0.211, 0.746, 0.044),
                    'turn_b2_n_mw': (0.544, 0.434, 0.022),
                    'turn_b2_x_hu': (0.342, 0.658, 0.0),
                    'turn_b2_x_mw': (0.666, 0.334, 0.0),
                    'turn_n_hu': (0.179, 0.652, 0.168),
                    'turn_n_mw': (0.61, 0.3, 0.091),
                    'turn_x_hu': (0.461, 0.539, 0.0),
                    'turn_x_mw': (0.705, 0.295, 0.0),
                    'turn_ms_hu': (0.321, 0.679, 0.0),
                    'turn_ms_mw': (0.661, 0.34, 0.0),
                },
                'no_xr': True,
            },
            'river': {
                'nx': {
                    'all': (0.266, 0.634, 0.1),
                    '<40%': (0.067, 0.814, 0.119),
                    '40-75%': (0.284, 0.615, 0.101),
                    '75-110%': (0.384, 0.504, 0.112),
                    'overbet': (0.467, 0.502, 0.031),
                },
                'xr': {
                    'all': (0.504, 0.491, 0.005),
                    '<40%': (0.132, 0.864, 0.004),
                    '40-75%': (0.435, 0.563, 0.002),
                    '75-110%': (0.726, 0.273, 0.001),
                    'overbet': (0.823, 0.175, 0.002),
                },
                'cells': {
                    'river_b3_n_hu': (0.134, 0.792, 0.074),
                    'river_b3_n_mw': (0.134, 0.797, 0.069),
                    'river_b3_x_hu': (0.47, 0.53, 0.0),
                    'river_b3_x_mw': (0.425, 0.575, 0.0),
                    'river_ct_n_hu': (0.542, 0.373, 0.085),
                    'river_ct_n_mw': (0.626, 0.267, 0.107),
                    'river_ct_x_hu': (0.618, 0.382, 0.0),
                    'river_ct_x_mw': (0.713, 0.288, 0.0),
                    'river_n_hu': (0.146, 0.626, 0.228),
                    'river_n_mw': (0.179, 0.628, 0.192),
                    'river_x_hu': (0.501, 0.499, 0.0),
                    'river_x_mw': (0.502, 0.498, 0.0),
                    'river_ms_hu': (0.416, 0.583, 0.0),
                    'river_ms_mw': (0.458, 0.542, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.3, 'draw': 0.4, 'weak': 0.2, 'medium': 1.1, 'value': 9.1},
            'turn': {'air': 0.1, 'draw': 0.2, 'weak': 0.2, 'medium': 0.7, 'value': 10.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 0.4, 'value': 8.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {'*': [(0.68, 1.0)]},
            'turn': {
                '*': [(0.68, 0.938), (ALLIN, 0.062)],
                'value': [(0.68, 0.8), (ALLIN, 0.2)],
                'medium': [(0.68, 0.8), (ALLIN, 0.2)],
            },
            'river': {
                '*': [(0.68, 0.923), (ALLIN, 0.077)],
                'value': [(0.68, 0.754), (ALLIN, 0.246)],
                'medium': [(0.68, 0.754), (ALLIN, 0.246)],
            },
        },
        commit=1.0,
        round_bets=True,
    )
