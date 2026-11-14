"""Replica of Anker Batteries for the Table D sparring table.

Anker Batteries: tight, opens 2.5bb everywhere, c-bets 90% heads up with 1.1 / 2.0 / 0.7 / 0.4
pot (mixed range), 0.62 pot multiway, never check-raises, folds 78% of its 3-bets to a 4-bet.

Parameters written by tabled/build.py from the team's real hands (same definitions as
docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import ALLIN, Base  # noqa: E402,F401


class Agent(Base):
    NAME = 'anker'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.098, 0.0),
            'UTG+1': (0.127, 0.0),
            'MP': (0.156, 0.0),
            'HJ': (0.234, 0.0),
            'CO': (0.351, 0.0),
            'BTN': (0.757, 0.0),
            'SB': (0.982, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(2.5, 1.0)]},
        # facing limpers: (call, raise)
        vs_limp=(0.0, 0.351),
        bb_iso=0.069,
        iso=(2.5, 1.0),
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.173, 0.081), 'm': (0.146, 0.127), 'l': (0.132, 0.093)},
            'BB': {'s': (0.537, 0.033), 'm': (0.206, 0.088), 'l': (0.395, 0.026)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.114, 0.015), 'SB': (0.199, 0.029), 'BB': (0.301, 0.033)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.084, 0.089),
            'UTG+1': (0.049, 0.144),
            'MP': (0.088, 0.114),
            'HJ': (0.071, 0.076),
            'CO': (0.093, 0.075),
            'BTN': (0.093, 0.085),
            'SB': (0.104, 0.09),
            'BB': (0.141, 0.12),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((1.006, 0.406), (0.609, 0.235)),
        tb_rand=0.25,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={
            'ip': [((3.0, 0.0), 0.7), ((3.2, 0.0), 0.3)],
            'oop': [((3.0, 0.0), 0.62), ((3.2, 0.0), 0.32), ((4.2, 0.0), 0.06)],
        },
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.574, 0.362, 0.064),
        fb_rand=0.2,
        fourbet=[(2.3, 1.0)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.04, 0.024),
        call_then_3b=0.417,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.708, 0.202, 0.089),
        f4b_shove=0.925,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.052, 0.796, 0.152),
        shove_max=0.045,
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.821,
                'D_hu': 0.822,
                'S_hu': 0.883,
                'L_hu': 0.682,
                'A_mw': 0.411,
                'D_mw': 0.228,
                'S_mw': 0.237,
                'L_mw': 0.243,
            },
            'turn': {
                'A_hu': 0.702,
                'D_hu': 0.663,
                'S_hu': 0.701,
                'L_hu': 0.679,
                'A_mw': 0.351,
                'D_mw': 0.416,
                'S_mw': 0.178,
                'L_mw': 0.116,
            },
            'river': {
                'A_hu': 0.484,
                'D_hu': 0.313,
                'S_hu': 0.404,
                'L_hu': 0.457,
                'A_mw': 0.115,
                'D_mw': 0.115,
                'S_mw': 0.154,
                'L_mw': 0.063,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.4: {'air': 1.03, 'draw': 1.05, 'weak': 1.07, 'medium': 6.16, 'value': 0.07},
                    0.62: {'air': 0.03, 'draw': 2.05, 'weak': 2.07, 'medium': 11.16, 'value': 4.07},
                    0.7: {'air': 1.03, 'draw': 3.05, 'weak': 3.07, 'medium': 2.16, 'value': 1.07},
                    0.85: {'air': 0.03, 'draw': 0.05, 'weak': 0.07, 'medium': 0.16, 'value': 3.07},
                    1.1: {'air': 3.03, 'draw': 1.05, 'weak': 1.07, 'medium': 2.16, 'value': 2.07},
                    2.0: {'air': 0.03, 'draw': 1.05, 'weak': 4.07, 'medium': 3.16, 'value': 1.07},
                },
                'share': {
                    'A_hu': {0.4: 0.177, 0.7: 0.209, 1.1: 0.373, 2.0: 0.241},
                    'A_mw': {0.62: 0.88, 0.85: 0.12},
                    'D_hu': {0.4: 0.286, 0.7: 0.343, 1.1: 0.214, 2.0: 0.157},
                    'D_mw': {0.4: 0.036, 0.62: 0.857, 0.85: 0.107},
                    'S_hu': {0.4: 0.282, 0.7: 0.338, 1.1: 0.211, 2.0: 0.169},
                    'S_mw': {0.62: 0.923, 0.85: 0.077},
                    'L_hu': {0.4: 0.282, 0.7: 0.338, 1.1: 0.211, 2.0: 0.169},
                    'L_mw': {0.4: 0.024, 0.62: 0.881, 0.85: 0.095},
                },
            },
            'turn': {
                'sizes': {
                    0.4: {'air': 0.03, 'draw': 0.02, 'weak': 6.11, 'medium': 5.16, 'value': 4.09},
                    0.62: {'air': 0.03, 'draw': 0.02, 'weak': 0.11, 'medium': 4.16, 'value': 1.09},
                    0.7: {'air': 2.03, 'draw': 1.02, 'weak': 3.11, 'medium': 5.16, 'value': 2.09},
                    0.85: {'air': 0.03, 'draw': 1.02, 'weak': 0.11, 'medium': 1.16, 'value': 0.09},
                    1.1: {'air': 0.03, 'draw': 0.02, 'weak': 2.11, 'medium': 2.16, 'value': 1.09},
                    2.0: {'air': 1.03, 'draw': 0.02, 'weak': 1.11, 'medium': 1.16, 'value': 2.09},
                },
                'share': {
                    'A_hu': {0.4: 0.3, 0.7: 0.286, 1.1: 0.214, 2.0: 0.2},
                    'A_mw': {0.62: 0.667, 0.85: 0.267, 1.1: 0.067},
                    'D_hu': {0.4: 0.227, 0.7: 0.182, 0.85: 0.045, 1.1: 0.364, 2.0: 0.182},
                    'D_mw': {0.62: 0.667, 0.85: 0.267, 1.1: 0.067},
                    'S_hu': {0.4: 0.32, 0.62: 0.04, 0.7: 0.32, 1.1: 0.2, 2.0: 0.12},
                    'S_mw': {0.62: 0.667, 0.85: 0.267, 1.1: 0.067},
                    'L_hu': {0.4: 0.255, 0.62: 0.02, 0.7: 0.255, 0.85: 0.02, 1.1: 0.314, 2.0: 0.137},
                    'L_mw': {0.62: 0.667, 0.85: 0.267, 1.1: 0.067},
                },
            },
            'river': {
                'sizes': {
                    0.4: {'air': 0.05, 'weak': 1.05, 'medium': 5.19, 'value': 4.11},
                    0.62: {'air': 0.05, 'weak': 0.05, 'medium': 1.19, 'value': 0.11},
                    0.7: {'air': 2.05, 'weak': 0.05, 'medium': 0.19, 'value': 0.11},
                    0.85: {'air': 0.05, 'weak': 0.05, 'medium': 0.19, 'value': 0.11},
                    1.1: {'air': 0.05, 'weak': 1.05, 'medium': 1.19, 'value': 0.11},
                },
                'share': {
                    'A_hu': {0.4: 0.722, 0.62: 0.056, 0.7: 0.111, 1.1: 0.111},
                    'A_mw': {0.4: 0.513, 0.62: 0.128, 0.7: 0.103, 0.85: 0.051, 1.1: 0.205},
                    'D_hu': {0.4: 0.606, 0.62: 0.03, 0.7: 0.121, 1.1: 0.242},
                    'D_mw': {0.4: 0.513, 0.62: 0.128, 0.7: 0.103, 0.85: 0.051, 1.1: 0.205},
                    'S_hu': {0.4: 0.606, 0.62: 0.03, 0.7: 0.121, 1.1: 0.242},
                    'S_mw': {0.4: 0.513, 0.62: 0.128, 0.7: 0.103, 0.85: 0.051, 1.1: 0.205},
                    'L_hu': {0.4: 0.606, 0.62: 0.03, 0.7: 0.121, 1.1: 0.242},
                    'L_mw': {0.4: 0.513, 0.62: 0.128, 0.7: 0.103, 0.85: 0.051, 1.1: 0.205},
                },
            },
        },
        jam={'spr': 2.5, 'p': {'flop': 0.75, 'turn': 0.4, 'river': 0.45}},
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.476, 0.439, 0.085),
            0.4: {'*': (0.479, 0.474, 0.046), 'flop': (0.516, 0.428, 0.056)},
            0.62: {'*': (0.161, 0.653, 0.186), 'flop': (0.116, 0.642, 0.242)},
            0.7: (0.575, 0.396, 0.028),
            1.1: {'*': (0.686, 0.302, 0.012), 'flop': (0.745, 0.252, 0.003)},
            2.0: (0.409, 0.48, 0.112),
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.445, 0.498, 0.057),
                    '<40%': (0.26, 0.703, 0.037),
                    '40-75%': (0.405, 0.531, 0.063),
                    '75-110%': (0.562, 0.388, 0.05),
                    'overbet': (0.778, 0.145, 0.078),
                },
                'xr': {
                    'all': (0.753, 0.246, 0.002),
                    '<40%': (0.503, 0.496, 0.001),
                    '40-75%': (0.796, 0.204, 0.0),
                    '75-110%': (0.828, 0.172, 0.0),
                    'overbet': (0.906, 0.094, 0.0),
                },
                'cells': {
                    'flop_n_hu': (0.393, 0.544, 0.064),
                    'flop_n_mw': (0.593, 0.37, 0.037),
                    'flop_x_hu': (0.783, 0.217, 0.0),
                    'flop_x_mw': (0.785, 0.215, 0.0),
                    'flop_ms_hu': (0.613, 0.387, 0.0),
                    'flop_ms_mw': (0.766, 0.234, 0.0),
                },
                'no_xr': True,
            },
            'turn': {
                'nx': {
                    'all': (0.408, 0.539, 0.053),
                    '<40%': (0.149, 0.799, 0.052),
                    '40-75%': (0.424, 0.505, 0.07),
                    '75-110%': (0.595, 0.37, 0.034),
                    'overbet': (0.814, 0.175, 0.011),
                },
                'xr': {
                    'all': (0.684, 0.312, 0.004),
                    '<40%': (0.454, 0.542, 0.003),
                    '40-75%': (0.74, 0.259, 0.001),
                    '75-110%': (0.792, 0.207, 0.001),
                    'overbet': (0.933, 0.066, 0.001),
                },
                'cells': {
                    'turn_b2_n_hu': (0.305, 0.63, 0.065),
                    'turn_b2_n_mw': (0.725, 0.26, 0.015),
                    'turn_b2_x_hu': (0.653, 0.347, 0.0),
                    'turn_b2_x_mw': (0.919, 0.082, 0.0),
                    'turn_n_hu': (0.491, 0.465, 0.044),
                    'turn_n_mw': (0.875, 0.123, 0.002),
                    'turn_x_hu': (0.631, 0.369, 0.0),
                    'turn_x_mw': (0.789, 0.211, 0.0),
                    'turn_ms_hu': (0.734, 0.266, 0.0),
                    'turn_ms_mw': (0.927, 0.073, 0.0),
                },
                'no_xr': True,
            },
            'river': {
                'nx': {
                    'all': (0.382, 0.545, 0.073),
                    '<40%': (0.175, 0.759, 0.066),
                    '40-75%': (0.499, 0.425, 0.077),
                    '75-110%': (0.478, 0.437, 0.084),
                    'overbet': (0.474, 0.484, 0.043),
                },
                'xr': {
                    'all': (0.59, 0.399, 0.01),
                    '<40%': (0.393, 0.596, 0.012),
                    '40-75%': (0.733, 0.263, 0.004),
                    '75-110%': (0.624, 0.372, 0.004),
                    'overbet': (0.712, 0.283, 0.005),
                },
                'cells': {
                    'river_b3_n_hu': (0.339, 0.609, 0.052),
                    'river_b3_n_mw': (0.409, 0.542, 0.049),
                    'river_b3_x_hu': (0.661, 0.339, 0.0),
                    'river_b3_x_mw': (0.628, 0.372, 0.0),
                    'river_ct_n_hu': (0.704, 0.282, 0.014),
                    'river_ct_n_mw': (0.566, 0.413, 0.021),
                    'river_ct_x_hu': (0.579, 0.421, 0.0),
                    'river_ct_x_mw': (0.596, 0.405, 0.0),
                    'river_n_hu': (0.229, 0.535, 0.236),
                    'river_n_mw': (0.273, 0.538, 0.189),
                    'river_x_hu': (0.596, 0.405, 0.0),
                    'river_x_mw': (0.594, 0.406, 0.0),
                    'river_ms_hu': (0.611, 0.389, 0.0),
                    'river_ms_mw': (0.605, 0.396, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.3, 'draw': 1.4, 'weak': 0.2, 'medium': 5.1, 'value': 10.1},
            'turn': {'air': 0.1, 'draw': 0.2, 'weak': 0.2, 'medium': 3.7, 'value': 3.8},
            'river': {'air': 1.1, 'weak': 0.1, 'medium': 1.4, 'value': 5.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {
                'value': [(1.8, 0.355), (1.0, 0.237), (0.6, 0.197), (ALLIN, 0.21)],
                '*': [(0.6, 0.374), (1.0, 0.28), (0.75, 0.187), (1.8, 0.093), (ALLIN, 0.066)],
                'medium': [(0.6, 0.316), (1.0, 0.237), (0.75, 0.158), (1.8, 0.079), (ALLIN, 0.21)],
            },
            'turn': {
                '*': [(0.6, 0.369), (1.0, 0.323), (1.8, 0.231), (ALLIN, 0.077)],
                'value': [(0.6, 0.301), (1.0, 0.263), (1.8, 0.188), (ALLIN, 0.247)],
                'medium': [(0.6, 0.301), (1.0, 0.263), (1.8, 0.188), (ALLIN, 0.247)],
            },
            'river': {'*': [(0.6, 0.7), (1.0, 0.3)]},
        },
    )
