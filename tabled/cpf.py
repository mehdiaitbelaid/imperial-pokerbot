"""Replica of Chinese people can fly for the Table D sparring table.

Chinese people can fly: loose opener (2.5bb, 3bb from the small blind), folds 81-84% to 3-bets,
bets 0.33 pot with air, draws and weak pairs and 1.0 pot with top pair or better, barrels 95%,
folds 80% when a 0.33 bet is raised.

Parameters written by tabled/build.py from the team's real hands (same definitions as
docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import ALLIN, Base  # noqa: E402,F401


class Agent(Base):
    NAME = 'cpf'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.279, 0.0),
            'UTG+1': (0.281, 0.0),
            'MP': (0.341, 0.0),
            'HJ': (0.517, 0.0),
            'CO': (0.58, 0.0),
            'BTN': (0.828, 0.0),
            'SB': (0.631, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(2.5, 1.0)], 'SB': [(3.0, 1.0)]},
        # facing limpers: (call, raise)
        vs_limp=(0.119, 0.095),
        bb_iso=0.2,
        iso=(3.0, 1.0),
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.251, 0.036), 'm': (0.243, 0.052), 'l': (0.246, 0.042)},
            'BB': {'s': (0.532, 0.096), 'm': (0.48, 0.078), 'l': (0.424, 0.106)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.211, 0.036), 'SB': (0.274, 0.048), 'BB': (0.479, 0.042)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.167, 0.055),
            'UTG+1': (0.183, 0.036),
            'MP': (0.206, 0.047),
            'HJ': (0.145, 0.051),
            'CO': (0.169, 0.051),
            'BTN': (0.164, 0.064),
            'SB': (0.153, 0.061),
            'BB': (0.453, 0.066),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.507, 1.094), (0.168, 0.328)),
        tb_rand=0.1,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((3.0, 0.0), 1.0)], 'oop': [((3.0, 0.0), 1.0)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.81, 0.107, 0.083),
        fourbet=[('allin', 0.81), (2.3, 0.19)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.008, 0.016),
        call_then_3b=0.02,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.244, 0.373, 0.384),
        f4b_shove=0.718,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.167, 0.8, 0.033),
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.607,
                'D_hu': 0.18,
                'S_hu': 0.808,
                'L_hu': 0.605,
                'A_mw': 0.131,
                'D_mw': 0.043,
                'S_mw': 0.087,
                'L_mw': 0.033,
            },
            'turn': {
                'A_hu': 0.952,
                'D_hu': 0.137,
                'S_hu': 0.55,
                'L_hu': 0.332,
                'A_mw': 0.222,
                'D_mw': 0.207,
                'S_mw': 0.073,
                'L_mw': 0.078,
            },
            'river': {
                'A_hu': 0.948,
                'D_hu': 0.672,
                'S_hu': 0.509,
                'L_hu': 0.393,
                'A_mw': 0.09,
                'D_mw': 0.231,
                'S_mw': 0.064,
                'L_mw': 0.103,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.33: {'air': 76.18, 'draw': 20.04, 'weak': 25.07, 'medium': 9.07, 'value': 0.04},
                    0.66: {'air': 0.18, 'draw': 0.04, 'weak': 0.07, 'medium': 1.07, 'value': 1.04},
                    1.0: {'air': 2.18, 'draw': 0.04, 'weak': 6.07, 'medium': 23.07, 'value': 15.04},
                },
                'share': {
                    'A_hu': {0.33: 0.696, 0.66: 0.055, 1.0: 0.249},
                    'A_mw': {0.33: 0.2, 1.0: 0.8},
                    'D_hu': {0.33: 0.815, 0.66: 0.015, 1.0: 0.17},
                    'D_mw': {0.33: 0.286, 1.0: 0.714},
                    'S_hu': {0.33: 0.739, 0.66: 0.045, 1.0: 0.216},
                    'S_mw': {0.33: 0.286, 1.0: 0.714},
                    'L_hu': {0.33: 0.799, 0.66: 0.021, 1.0: 0.181},
                    'L_mw': {0.33: 0.286, 1.0: 0.714},
                },
            },
            'turn': {
                'sizes': {
                    0.33: {'air': 52.11, 'draw': 33.07, 'weak': 38.09, 'medium': 7.06, 'value': 1.06},
                    0.66: {'air': 0.11, 'draw': 1.07, 'weak': 3.09, 'medium': 0.06, 'value': 0.06},
                    1.0: {'air': 0.11, 'draw': 0.07, 'weak': 1.09, 'medium': 22.06, 'value': 27.06},
                },
                'share': {
                    'A_hu': {0.33: 0.64, 0.66: 0.2, 1.0: 0.16},
                    'A_mw': {0.33: 0.158, 1.0: 0.842},
                    'D_hu': {0.33: 0.608, 0.66: 0.02, 1.0: 0.373},
                    'D_mw': {0.33: 0.158, 1.0: 0.842},
                    'S_hu': {0.33: 0.646, 1.0: 0.354},
                    'S_mw': {0.33: 0.158, 1.0: 0.842},
                    'L_hu': {0.33: 0.471, 1.0: 0.529},
                    'L_mw': {0.33: 0.158, 1.0: 0.842},
                },
            },
            'river': {
                'sizes': {
                    0.33: {'air': 80.17, 'weak': 45.1, 'medium': 13.05, 'value': 8.07},
                    0.66: {'air': 2.17, 'weak': 2.1, 'medium': 0.05, 'value': 0.07},
                    1.0: {'air': 2.17, 'weak': 2.1, 'medium': 13.05, 'value': 25.07},
                },
                'share': {
                    'A_hu': {0.33: 0.721, 0.66: 0.018, 1.0: 0.261},
                    'A_mw': {0.33: 0.688, 0.66: 0.022, 1.0: 0.29},
                    'D_hu': {0.33: 0.818, 0.66: 0.061, 1.0: 0.121},
                    'D_mw': {0.33: 0.688, 0.66: 0.022, 1.0: 0.29},
                    'S_hu': {0.33: 0.625, 0.66: 0.031, 1.0: 0.344},
                    'S_mw': {0.33: 0.688, 0.66: 0.022, 1.0: 0.29},
                    'L_hu': {0.33: 0.5, 1.0: 0.5},
                    'L_mw': {0.33: 0.688, 0.66: 0.022, 1.0: 0.29},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.672, 0.292, 0.036),
            0.33: {
                '*': (0.798, 0.201, 0.001),
                'flop': (0.797, 0.203, 0.0),
                'turn': (0.803, 0.197, 0.0),
                'river': (0.806, 0.194, 0.0),
            },
            0.66: (0.586, 0.396, 0.018),
            1.0: {
                '*': (0.243, 0.595, 0.162),
                'flop': (0.182, 0.609, 0.209),
                'turn': (0.307, 0.551, 0.142),
                'river': (0.137, 0.698, 0.165),
            },
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.532, 0.416, 0.052),
                    '<40%': (0.309, 0.612, 0.079),
                    '40-75%': (0.492, 0.447, 0.061),
                    '75-110%': (0.71, 0.269, 0.021),
                    'overbet': (0.743, 0.226, 0.031),
                },
                'xr': {
                    'all': (0.555, 0.405, 0.04),
                    '<40%': (0.378, 0.574, 0.048),
                    '40-75%': (0.465, 0.488, 0.047),
                    '75-110%': (0.736, 0.242, 0.022),
                    'overbet': (0.801, 0.154, 0.045),
                },
                'cells': {
                    'flop_n_hu': (0.456, 0.481, 0.063),
                    'flop_n_mw': (0.726, 0.249, 0.025),
                    'flop_x_hu': (0.522, 0.442, 0.036),
                    'flop_x_mw': (0.686, 0.295, 0.019),
                    'flop_ms_hu': (0.349, 0.522, 0.128),
                    'flop_ms_mw': (0.516, 0.458, 0.026),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.418, 0.481, 0.102),
                    '<40%': (0.199, 0.679, 0.122),
                    '40-75%': (0.389, 0.486, 0.125),
                    '75-110%': (0.593, 0.33, 0.077),
                    'overbet': (0.615, 0.367, 0.018),
                },
                'xr': {
                    'all': (0.471, 0.455, 0.074),
                    '<40%': (0.105, 0.684, 0.211),
                    '40-75%': (0.48, 0.467, 0.054),
                    '75-110%': (0.736, 0.251, 0.013),
                    'overbet': (0.594, 0.376, 0.03),
                },
                'cells': {
                    'turn_b2_n_hu': (0.339, 0.555, 0.106),
                    'turn_b2_n_mw': (0.543, 0.363, 0.094),
                    'turn_b2_x_hu': (0.343, 0.598, 0.059),
                    'turn_b2_x_mw': (0.528, 0.376, 0.096),
                    'turn_n_hu': (0.385, 0.478, 0.137),
                    'turn_n_mw': (0.75, 0.206, 0.043),
                    'turn_x_hu': (0.591, 0.335, 0.074),
                    'turn_x_mw': (0.648, 0.298, 0.054),
                    'turn_ms_hu': (0.543, 0.313, 0.144),
                    'turn_ms_mw': (0.729, 0.207, 0.065),
                },
                'no_xr': False,
            },
            'river': {
                'nx': {
                    'all': (0.473, 0.417, 0.109),
                    '<40%': (0.317, 0.541, 0.142),
                    '40-75%': (0.454, 0.418, 0.128),
                    '75-110%': (0.738, 0.215, 0.047),
                    'overbet': (0.515, 0.436, 0.049),
                },
                'xr': {
                    'all': (0.565, 0.371, 0.065),
                    '<40%': (0.46, 0.5, 0.04),
                    '40-75%': (0.544, 0.341, 0.115),
                    '75-110%': (0.741, 0.245, 0.014),
                    'overbet': (0.563, 0.386, 0.051),
                },
                'cells': {
                    'river_b3_n_hu': (0.333, 0.549, 0.118),
                    'river_b3_n_mw': (0.727, 0.224, 0.049),
                    'river_b3_x_hu': (0.52, 0.46, 0.02),
                    'river_b3_x_mw': (0.808, 0.177, 0.015),
                    'river_ct_n_hu': (0.668, 0.2, 0.132),
                    'river_ct_n_mw': (0.904, 0.053, 0.043),
                    'river_ct_x_hu': (0.674, 0.314, 0.012),
                    'river_ct_x_mw': (0.79, 0.208, 0.002),
                    'river_n_hu': (0.475, 0.401, 0.123),
                    'river_n_mw': (0.723, 0.234, 0.043),
                    'river_x_hu': (0.171, 0.57, 0.259),
                    'river_x_mw': (0.586, 0.26, 0.154),
                    'river_ms_hu': (0.584, 0.387, 0.029),
                    'river_ms_mw': (0.832, 0.151, 0.017),
                },
                'no_xr': False,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.3, 'draw': 1.4, 'weak': 0.2, 'medium': 6.1, 'value': 7.1},
            'turn': {'draw': 1.1, 'weak': 0.1, 'medium': 5.2, 'value': 9.6},
            'river': {'air': 1.1, 'weak': 1.1, 'medium': 2.4, 'value': 12.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {
                '*': [(0.85, 0.795), (0.65, 0.174), (ALLIN, 0.031)],
                'value': [(0.85, 0.739), (0.65, 0.162), (ALLIN, 0.099)],
                'medium': [(0.85, 0.739), (0.65, 0.162), (ALLIN, 0.099)],
            },
            'turn': {
                '*': [(0.85, 0.756), (0.65, 0.166), (ALLIN, 0.078)],
                'value': [(0.85, 0.615), (0.65, 0.135), (ALLIN, 0.25)],
                'medium': [(0.85, 0.615), (0.65, 0.135), (ALLIN, 0.25)],
            },
            'river': {
                '*': [(0.85, 0.742), (0.65, 0.131), (ALLIN, 0.127)],
                'value': [(0.85, 0.503), (0.65, 0.089), (ALLIN, 0.408)],
                'medium': [(0.85, 0.503), (0.65, 0.089), (ALLIN, 0.408)],
            },
        },
    )
