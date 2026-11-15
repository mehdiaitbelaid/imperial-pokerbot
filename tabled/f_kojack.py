"""Replica of Kojack (likely finalist) for the final-table sparring games.

Kojack. Measured on 10 rounds, 10000 hands (r003, r008, r021, r023, r024, r025, r026, r031,
r048, r050); latest third: r031, r048, r050. VPIP 19, PFR 16, 3-bet 7; opens 2.5bb 92%, 3bb 8%.
Bet sizes (share of pot): flop 0.33/0.38/0.42/0.45/0.55/0.72, turn 0.4/0.55/0.66/0.72/all-in,
river 0.4/0.55/0.66/0.72/all-in.

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
    _base._NODES.setdefault('f_kojack', _NF.get('f_kojack', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'f_kojack'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.142, 0.0),
            'UTG+1': (0.186, 0.0),
            'MP': (0.197, 0.0),
            'HJ': (0.223, 0.0),
            'CO': (0.312, 0.0),
            'BTN': (0.547, 0.0),
            'SB': (0.506, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(2.5, 1.0)], 'SB': [(3.0, 1.0)]},
        # facing limpers: (call, raise)
        vs_limp=(0.038, 0.331),
        bb_iso=0.109,
        iso=(4.0, 1.0),
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.08, 0.198), 'm': (0.09, 0.097), 'l': (0.094, 0.146)},
            'BB': {'s': (0.28, 0.097), 'm': (0.257, 0.123), 'l': (0.156, 0.171)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.063, 0.034), 'SB': (0.028, 0.061), 'BB': (0.139, 0.086)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.038, 0.058),
            'MP': (0.034, 0.04),
            'HJ': (0.013, 0.045),
            'CO': (0.035, 0.067),
            'BTN': (0.056, 0.064),
            'SB': (0.036, 0.057),
            'BB': (0.165, 0.06),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.785, 0.85), (0.578, 0.423)),
        tb_rand=0.13,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={
            'ip': [((3.0, 0.0), 0.8), ((3.3, 0.0), 0.167)],
            'oop': [((3.8, 0.0), 0.66), ((4.0, 0.0), 0.106), ((4.8, 0.0), 0.085)],
        },
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.565, 0.201, 0.233),
        fb_rand=0.49,
        fourbet=[(2.3, 1.0)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.002, 0.063),
        cold_rand=0.7,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.197, 0.369, 0.434),
        f4b_shove=0.64,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.346, 0.295, 0.358),
        shove_max=0.052,
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.808,
                'D_hu': 0.319,
                'S_hu': 0.582,
                'L_hu': 0.534,
                'A_mw': 0.386,
                'D_mw': 0.245,
                'S_mw': 0.278,
                'L_mw': 0.329,
            },
            'turn': {
                'A_hu': 0.561,
                'D_hu': 0.398,
                'S_hu': 0.562,
                'L_hu': 0.283,
                'A_mw': 0.236,
                'D_mw': 0.236,
                'S_mw': 0.174,
                'L_mw': 0.335,
            },
            'river': {
                'A_hu': 0.41,
                'D_hu': 0.238,
                'S_hu': 0.219,
                'L_hu': 0.112,
                'A_mw': 0.179,
                'D_mw': 0.154,
                'S_mw': 0.218,
                'L_mw': 0.083,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.33: {'air': 8.13, 'draw': 0.04, 'weak': 2.05, 'medium': 0.14, 'value': 0.04},
                    0.38: {'air': 1.13, 'draw': 0.04, 'weak': 0.05, 'medium': 0.14, 'value': 0.04},
                    0.42: {'air': 6.13, 'draw': 3.04, 'weak': 0.05, 'medium': 0.14, 'value': 0.04},
                    0.45: {'air': 2.13, 'draw': 0.04, 'weak': 0.05, 'medium': 0.14, 'value': 0.04},
                    0.55: {'air': 1.13, 'draw': 2.04, 'weak': 5.05, 'medium': 14.14, 'value': 0.04},
                    0.72: {'air': 0.13, 'draw': 0.04, 'weak': 0.05, 'medium': 6.14, 'value': 6.04},
                },
                'share': {
                    'A_hu': {0.33: 0.153, 0.38: 0.108, 0.42: 0.128, 0.45: 0.133, 0.55: 0.241, 0.72: 0.236},
                    'A_mw': {0.33: 0.353, 0.42: 0.029, 0.55: 0.324, 0.72: 0.294},
                    'D_hu': {0.38: 0.036, 0.42: 0.164, 0.45: 0.055, 0.55: 0.509, 0.72: 0.236},
                    'D_mw': {0.42: 0.154, 0.55: 0.538, 0.72: 0.308},
                    'S_hu': {0.38: 0.027, 0.42: 0.133, 0.45: 0.04, 0.55: 0.587, 0.72: 0.213},
                    'S_mw': {0.33: 0.218, 0.42: 0.073, 0.55: 0.4, 0.72: 0.309},
                    'L_hu': {0.55: 0.833, 0.72: 0.167},
                    'L_mw': {0.33: 0.218, 0.42: 0.073, 0.55: 0.4, 0.72: 0.309},
                },
            },
            'turn': {
                'sizes': {
                    0.4: {'air': 1.02, 'draw': 6.1, 'weak': 0.03, 'medium': 0.14, 'value': 0.1},
                    0.55: {'air': 0.02, 'draw': 7.1, 'weak': 4.03, 'medium': 12.14, 'value': 2.1},
                    0.66: {'air': 2.02, 'draw': 1.1, 'weak': 0.03, 'medium': 0.14, 'value': 0.1},
                    0.72: {'air': 0.02, 'draw': 0.1, 'weak': 1.03, 'medium': 5.14, 'value': 9.1},
                    ALLIN: {'air': 0.02, 'draw': 0.1, 'weak': 0.03, 'medium': 4.14, 'value': 4.1},
                },
                'share': {
                    'A_hu': {0.4: 0.147, 0.55: 0.44, 0.66: 0.08, 0.72: 0.28, ALLIN: 0.053},
                    'A_mw': {0.4: 0.067, 0.55: 0.533, 0.72: 0.4},
                    'D_hu': {0.4: 0.182, 0.55: 0.485, 0.72: 0.182, ALLIN: 0.152},
                    'D_mw': {0.4: 0.067, 0.55: 0.533, 0.72: 0.4},
                    'S_hu': {0.4: 0.184, 0.55: 0.474, 0.66: 0.026, 0.72: 0.316},
                    'S_mw': {0.4: 0.067, 0.55: 0.533, 0.72: 0.4},
                    'L_hu': {0.4: 0.071, 0.55: 0.643, 0.72: 0.286},
                    'L_mw': {0.4: 0.067, 0.55: 0.533, 0.72: 0.4},
                },
            },
            'river': {
                'sizes': {
                    0.4: {'air': 2.1, 'weak': 0.03, 'medium': 0.08, 'value': 0.19},
                    0.55: {'air': 0.1, 'weak': 2.03, 'medium': 3.08, 'value': 3.19},
                    0.66: {'air': 3.1, 'weak': 0.03, 'medium': 0.08, 'value': 0.19},
                    0.72: {'air': 0.1, 'weak': 0.03, 'medium': 2.08, 'value': 6.19},
                    ALLIN: {'air': 1.1, 'weak': 0.03, 'medium': 0.08, 'value': 3.19},
                },
                'share': {
                    'A_hu': {0.4: 0.077, 0.55: 0.231, 0.66: 0.154, 0.72: 0.5, ALLIN: 0.038},
                    'A_mw': {0.4: 0.119, 0.55: 0.339, 0.66: 0.068, 0.72: 0.373, ALLIN: 0.102},
                    'D_hu': {0.4: 0.154, 0.55: 0.462, 0.72: 0.192, ALLIN: 0.192},
                    'D_mw': {0.4: 0.119, 0.55: 0.339, 0.66: 0.068, 0.72: 0.373, ALLIN: 0.102},
                    'S_hu': {0.4: 0.154, 0.55: 0.462, 0.72: 0.192, ALLIN: 0.192},
                    'S_mw': {0.4: 0.119, 0.55: 0.339, 0.66: 0.068, 0.72: 0.373, ALLIN: 0.102},
                    'L_hu': {0.4: 0.154, 0.55: 0.462, 0.72: 0.192, ALLIN: 0.192},
                    'L_mw': {0.4: 0.119, 0.55: 0.339, 0.66: 0.068, 0.72: 0.373, ALLIN: 0.102},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.478, 0.478, 0.043),
            0.33: (0.657, 0.324, 0.019),
            0.38: (0.768, 0.213, 0.019),
            0.42: (0.447, 0.538, 0.016),
            0.55: {'*': (0.546, 0.446, 0.009), 'turn': (0.448, 0.548, 0.004)},
            0.72: {'*': (0.12, 0.745, 0.136), 'flop': (0.051, 0.748, 0.201)},
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.349, 0.598, 0.053),
                    '<40%': (0.134, 0.816, 0.05),
                    '40-75%': (0.354, 0.587, 0.059),
                    '75-110%': (0.453, 0.484, 0.064),
                    'overbet': (0.471, 0.519, 0.011),
                },
                'xr': {
                    'all': (0.478, 0.514, 0.007),
                    '<40%': (0.343, 0.654, 0.003),
                    '40-75%': (0.395, 0.593, 0.013),
                    '75-110%': (0.628, 0.371, 0.001),
                    'overbet': (0.658, 0.339, 0.003),
                },
                'cells': {
                    'flop_n_hu': (0.28, 0.664, 0.056),
                    'flop_n_mw': (0.588, 0.369, 0.043),
                    'flop_x_hu': (0.435, 0.556, 0.009),
                    'flop_x_mw': (0.576, 0.423, 0.001),
                    'flop_ms_hu': (0.467, 0.531, 0.001),
                    'flop_ms_mw': (0.712, 0.287, 0.001),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.337, 0.635, 0.028),
                    '<40%': (0.199, 0.78, 0.021),
                    '40-75%': (0.298, 0.674, 0.028),
                    '75-110%': (0.577, 0.398, 0.025),
                    'overbet': (0.402, 0.551, 0.047),
                },
                'xr': {
                    'all': (0.582, 0.417, 0.001),
                    '<40%': (0.309, 0.691, 0.001),
                    '40-75%': (0.552, 0.447, 0.0),
                    '75-110%': (0.779, 0.221, 0.0),
                    'overbet': (0.791, 0.208, 0.001),
                },
                'cells': {
                    'turn_b2_n_hu': (0.257, 0.719, 0.024),
                    'turn_b2_n_mw': (0.494, 0.497, 0.01),
                    'turn_b2_x_hu': (0.504, 0.496, 0.0),
                    'turn_b2_x_mw': (0.73, 0.27, 0.0),
                    'turn_n_hu': (0.423, 0.522, 0.055),
                    'turn_n_mw': (0.785, 0.208, 0.007),
                    'turn_x_hu': (0.729, 0.271, 0.0),
                    'turn_x_mw': (0.814, 0.186, 0.0),
                    'turn_ms_hu': (0.565, 0.435, 0.0),
                    'turn_ms_mw': (0.832, 0.167, 0.0),
                },
                'no_xr': True,
            },
            'river': {
                'nx': {
                    'all': (0.642, 0.313, 0.046),
                    '<40%': (0.451, 0.445, 0.104),
                    '40-75%': (0.669, 0.304, 0.027),
                    '75-110%': (0.756, 0.234, 0.01),
                    'overbet': (0.568, 0.36, 0.071),
                },
                'xr': {
                    'all': (0.818, 0.18, 0.002),
                    '<40%': (0.704, 0.294, 0.002),
                    '40-75%': (0.834, 0.165, 0.001),
                    '75-110%': (0.842, 0.157, 0.001),
                    'overbet': (0.811, 0.187, 0.002),
                },
                'cells': {
                    'river_b3_n_hu': (0.575, 0.376, 0.049),
                    'river_b3_n_mw': (0.568, 0.393, 0.039),
                    'river_b3_x_hu': (0.614, 0.386, 0.0),
                    'river_b3_x_mw': (0.718, 0.282, 0.0),
                    'river_ct_n_hu': (0.89, 0.105, 0.006),
                    'river_ct_n_mw': (0.796, 0.193, 0.011),
                    'river_ct_x_hu': (0.917, 0.083, 0.0),
                    'river_ct_x_mw': (0.841, 0.16, 0.0),
                    'river_n_hu': (0.603, 0.319, 0.077),
                    'river_n_mw': (0.612, 0.318, 0.07),
                    'river_x_hu': (0.896, 0.103, 0.0),
                    'river_x_mw': (0.872, 0.128, 0.0),
                    'river_ms_hu': (0.841, 0.159, 0.0),
                    'river_ms_mw': (0.834, 0.166, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.3, 'draw': 1.4, 'weak': 0.2, 'medium': 4.1, 'value': 5.1},
            'turn': {'air': 0.1, 'draw': 0.2, 'weak': 1.2, 'medium': 0.7, 'value': 2.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 0.4, 'value': 3.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={'flop': {'*': [(0.75, 1.0)]}, 'turn': {'*': [(0.75, 1.0)]}, 'river': {'*': [(0.75, 1.0)]}},
    )
