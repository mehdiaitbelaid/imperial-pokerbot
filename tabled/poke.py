"""Replica of Poke for the Table D sparring table.

Poke: limps 28% first in and folds most limps to a raise, opens 2.5bb (3bb from the small
blind), bets 1.6 pot with two pair or better, 0.8 pot on the flop with air and draws, 0.33 pot
with a mixed range; folds 71% when a 0.8 bet is raised; folds a lot to bets and never
check-raises.

Parameters written by tabled/build.py from the team's real hands (same definitions as
docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import ALLIN, Base  # noqa: E402,F401


class Agent(Base):
    NAME = 'poke'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.183, 0.397),
            'UTG+1': (0.218, 0.4),
            'MP': (0.27, 0.315),
            'HJ': (0.334, 0.229),
            'CO': (0.421, 0.206),
            'BTN': (0.643, 0.0),
            'SB': (0.496, 0.11),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(2.5, 1.0)], 'SB': [(3.0, 1.0)]},
        # facing limpers: (call, raise)
        vs_limp=(0.233, 0.3),
        bb_iso=0.3,
        iso=(3.0, 1.0),
        limp_fold=0.688,
        limp_rr=0.0,
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.523, 0.13), 'm': (0.232, 0.043), 'l': (0.155, 0.038)},
            'BB': {'s': (0.855, 0.034), 'm': (0.522, 0.025), 'l': (0.272, 0.049)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.255, 0.051), 'SB': (0.381, 0.022), 'BB': (0.582, 0.016)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.115, 0.03),
            'MP': (0.103, 0.038),
            'HJ': (0.116, 0.02),
            'CO': (0.133, 0.029),
            'BTN': (0.107, 0.032),
            'SB': (0.23, 0.054),
            'BB': (0.503, 0.027),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.386, 1.404), (0.222, 0.621)),
        tb_rand=0.05,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((3.5, 0.0), 1.0)], 'oop': [((3.5, 0.0), 0.6), ((3.0, 0.0), 0.4)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.5, 0.42, 0.08),
        fourbet=[('allin', 1.0)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.006, 0.02),
        call_then_3b=0.074,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.054, 0.601, 0.345),
        f4b_shove=0.292,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.25, 0.7, 0.05),
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.994,
                'D_hu': 0.954,
                'S_hu': 0.997,
                'L_hu': 0.989,
                'A_mw': 0.701,
                'D_mw': 0.632,
                'S_mw': 0.631,
                'L_mw': 0.486,
            },
            'turn': {
                'A_hu': 0.622,
                'D_hu': 0.485,
                'S_hu': 0.634,
                'L_hu': 0.421,
                'A_mw': 0.468,
                'D_mw': 0.23,
                'S_mw': 0.145,
                'L_mw': 0.106,
            },
            'river': {
                'A_hu': 0.582,
                'D_hu': 0.183,
                'S_hu': 0.244,
                'L_hu': 0.223,
                'A_mw': 0.489,
                'D_mw': 0.127,
                'S_mw': 0.102,
                'L_mw': 0.082,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.33: {'air': 20.11, 'draw': 9.06, 'weak': 34.08, 'medium': 47.12, 'value': 2.03},
                    0.55: {'air': 4.11, 'draw': 1.06, 'weak': 5.08, 'medium': 7.12, 'value': 2.03},
                    0.8: {'air': 31.11, 'draw': 10.06, 'weak': 5.08, 'medium': 7.12, 'value': 0.03},
                    1.1: {'air': 4.11, 'draw': 9.06, 'weak': 2.08, 'medium': 2.12, 'value': 0.03},
                    1.6: {'air': 3.11, 'draw': 5.06, 'weak': 1.08, 'medium': 3.12, 'value': 15.03},
                },
                'share': {
                    'A_hu': {0.33: 0.446, 0.55: 0.046, 0.8: 0.123, 1.1: 0.138, 1.6: 0.246},
                    'A_mw': {0.33: 0.468, 0.55: 0.129, 0.8: 0.081, 1.1: 0.113, 1.6: 0.21},
                    'D_hu': {0.33: 0.495, 0.55: 0.1, 0.8: 0.245, 1.1: 0.091, 1.6: 0.071},
                    'D_mw': {0.33: 0.433, 0.55: 0.118, 0.8: 0.244, 1.1: 0.126, 1.6: 0.079},
                    'S_hu': {0.33: 0.283, 0.55: 0.075, 0.8: 0.358, 1.1: 0.094, 1.6: 0.189},
                    'S_mw': {0.33: 0.397, 0.55: 0.069, 0.8: 0.345, 1.1: 0.103, 1.6: 0.086},
                    'L_hu': {0.33: 0.385, 0.8: 0.231, 1.1: 0.154, 1.6: 0.231},
                    'L_mw': {0.33: 0.425, 0.55: 0.102, 0.8: 0.274, 1.1: 0.118, 1.6: 0.081},
                },
            },
            'turn': {
                'sizes': {
                    0.33: {'air': 14.04, 'draw': 25.08, 'weak': 30.09, 'medium': 35.11, 'value': 5.07},
                    0.55: {'air': 0.04, 'draw': 1.08, 'weak': 1.09, 'medium': 1.11, 'value': 0.07},
                    0.8: {'air': 0.04, 'draw': 0.08, 'weak': 0.09, 'medium': 0.11, 'value': 4.07},
                    1.1: {'air': 0.04, 'draw': 0.08, 'weak': 0.09, 'medium': 1.11, 'value': 0.07},
                    1.6: {'air': 0.04, 'draw': 3.08, 'weak': 0.09, 'medium': 2.11, 'value': 15.07},
                },
                'share': {
                    'A_hu': {0.33: 0.746, 0.55: 0.05, 0.8: 0.032, 1.1: 0.029, 1.6: 0.143},
                    'A_mw': {0.33: 0.286, 0.8: 0.071, 1.1: 0.071, 1.6: 0.571},
                    'D_hu': {0.33: 0.826, 0.8: 0.043, 1.6: 0.13},
                    'D_mw': {0.33: 0.409, 0.55: 0.045, 0.8: 0.091, 1.1: 0.045, 1.6: 0.409},
                    'S_hu': {0.33: 0.739, 0.55: 0.043, 0.8: 0.043, 1.1: 0.087, 1.6: 0.087},
                    'S_mw': {0.33: 0.409, 0.55: 0.045, 0.8: 0.091, 1.1: 0.045, 1.6: 0.409},
                    'L_hu': {0.33: 0.787, 0.55: 0.021, 0.8: 0.043, 1.1: 0.043, 1.6: 0.106},
                    'L_mw': {0.33: 0.409, 0.55: 0.045, 0.8: 0.091, 1.1: 0.045, 1.6: 0.409},
                },
            },
            'river': {
                'sizes': {
                    0.33: {'air': 17.12, 'weak': 10.06, 'medium': 19.11, 'value': 11.11},
                    0.55: {'air': 1.12, 'weak': 0.06, 'medium': 1.11, 'value': 1.11},
                    0.8: {'air': 2.12, 'weak': 0.06, 'medium': 0.11, 'value': 2.11},
                    1.1: {'air': 0.12, 'weak': 0.06, 'medium': 0.11, 'value': 0.11},
                    1.6: {'air': 2.12, 'weak': 0.06, 'medium': 0.11, 'value': 5.11},
                },
                'share': {
                    'A_hu': {0.33: 0.67, 0.55: 0.075, 0.8: 0.047, 1.6: 0.208},
                    'A_mw': {0.33: 0.638, 0.55: 0.069, 0.8: 0.054, 1.1: 0.015, 1.6: 0.223},
                    'D_hu': {0.33: 0.659, 0.55: 0.073, 0.8: 0.049, 1.6: 0.22},
                    'D_mw': {0.33: 0.638, 0.55: 0.069, 0.8: 0.054, 1.1: 0.015, 1.6: 0.223},
                    'S_hu': {0.33: 0.659, 0.55: 0.073, 0.8: 0.049, 1.6: 0.22},
                    'S_mw': {0.33: 0.638, 0.55: 0.069, 0.8: 0.054, 1.1: 0.015, 1.6: 0.223},
                    'L_hu': {0.33: 0.659, 0.55: 0.073, 0.8: 0.049, 1.6: 0.22},
                    'L_mw': {0.33: 0.638, 0.55: 0.069, 0.8: 0.054, 1.1: 0.015, 1.6: 0.223},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.585, 0.275, 0.139),
            0.33: {
                '*': (0.594, 0.302, 0.104),
                'flop': (0.612, 0.295, 0.094),
                'turn': (0.562, 0.328, 0.11),
                'river': (0.504, 0.321, 0.175),
            },
            0.55: {'*': (0.542, 0.222, 0.236), 'flop': (0.537, 0.216, 0.248)},
            0.8: {'*': (0.699, 0.194, 0.107), 'flop': (0.729, 0.199, 0.071)},
            1.1: {'*': (0.717, 0.105, 0.178), 'flop': (0.715, 0.082, 0.203)},
            1.6: {'*': (0.334, 0.415, 0.252), 'flop': (0.393, 0.303, 0.304)},
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.482, 0.342, 0.176),
                    '<40%': (0.31, 0.502, 0.188),
                    '40-75%': (0.429, 0.392, 0.179),
                    '75-110%': (0.624, 0.195, 0.181),
                    'overbet': (0.627, 0.242, 0.131),
                },
                'xr': {
                    'all': (0.928, 0.063, 0.009),
                    '<40%': (0.952, 0.042, 0.006),
                    '40-75%': (0.946, 0.051, 0.003),
                    '75-110%': (0.916, 0.082, 0.001),
                    'overbet': (0.983, 0.015, 0.002),
                },
                'cells': {
                    'flop_n_hu': (0.45, 0.369, 0.18),
                    'flop_n_mw': (0.6, 0.24, 0.16),
                    'flop_x_hu': (0.99, 0.01, 0.0),
                    'flop_x_mw': (0.981, 0.019, 0.0),
                    'flop_ms_hu': (0.818, 0.181, 0.0),
                    'flop_ms_mw': (0.79, 0.21, 0.0),
                },
                'no_xr': True,
            },
            'turn': {
                'nx': {
                    'all': (0.414, 0.469, 0.117),
                    '<40%': (0.227, 0.635, 0.138),
                    '40-75%': (0.402, 0.469, 0.13),
                    '75-110%': (0.457, 0.429, 0.114),
                    'overbet': (0.506, 0.454, 0.04),
                },
                'xr': {
                    'all': (0.808, 0.19, 0.002),
                    '<40%': (0.648, 0.351, 0.001),
                    '40-75%': (0.773, 0.227, 0.0),
                    '75-110%': (0.875, 0.125, 0.0),
                    'overbet': (0.919, 0.08, 0.001),
                },
                'cells': {
                    'turn_b2_n_hu': (0.543, 0.393, 0.064),
                    'turn_b2_n_mw': (0.783, 0.186, 0.031),
                    'turn_b2_x_hu': (0.918, 0.082, 0.0),
                    'turn_b2_x_mw': (0.959, 0.04, 0.0),
                    'turn_n_hu': (0.495, 0.339, 0.166),
                    'turn_n_mw': (0.779, 0.19, 0.031),
                    'turn_x_hu': (0.891, 0.109, 0.0),
                    'turn_x_mw': (0.957, 0.043, 0.0),
                    'turn_ms_hu': (0.878, 0.122, 0.0),
                    'turn_ms_mw': (0.887, 0.113, 0.0),
                },
                'no_xr': True,
            },
            'river': {
                'nx': {
                    'all': (0.598, 0.313, 0.089),
                    '<40%': (0.549, 0.364, 0.087),
                    '40-75%': (0.525, 0.358, 0.117),
                    '75-110%': (0.697, 0.247, 0.056),
                    'overbet': (0.808, 0.162, 0.03),
                },
                'xr': {
                    'all': (0.782, 0.204, 0.014),
                    '<40%': (0.521, 0.467, 0.012),
                    '40-75%': (0.821, 0.154, 0.024),
                    '75-110%': (0.832, 0.166, 0.003),
                    'overbet': (0.878, 0.117, 0.004),
                },
                'cells': {
                    'river_b3_n_hu': (0.542, 0.376, 0.082),
                    'river_b3_n_mw': (0.549, 0.368, 0.083),
                    'river_b3_x_hu': (0.782, 0.204, 0.014),
                    'river_b3_x_mw': (0.782, 0.204, 0.014),
                    'river_ct_n_hu': (0.679, 0.209, 0.111),
                    'river_ct_n_mw': (0.76, 0.116, 0.124),
                    'river_ct_x_hu': (0.79, 0.206, 0.004),
                    'river_ct_x_mw': (0.728, 0.268, 0.004),
                    'river_n_hu': (0.622, 0.309, 0.069),
                    'river_n_mw': (0.594, 0.249, 0.157),
                    'river_x_hu': (0.78, 0.219, 0.002),
                    'river_x_mw': (0.692, 0.304, 0.004),
                    'river_ms_hu': (0.811, 0.171, 0.019),
                    'river_ms_mw': (0.807, 0.175, 0.018),
                },
                'no_xr': False,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 4.1, 'draw': 5.1, 'weak': 5.1, 'medium': 34.4, 'value': 17.4},
            'turn': {'air': 1.0, 'draw': 0.1, 'weak': 0.1, 'medium': 9.2, 'value': 12.6},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 3.4, 'value': 9.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {
                'value': [(1.1, 0.429), (0.75, 0.286), (ALLIN, 0.284)],
                '*': [(0.75, 0.501), (1.1, 0.41), (ALLIN, 0.089)],
                'medium': [(0.75, 0.394), (1.1, 0.322), (ALLIN, 0.284)],
            },
            'turn': {
                '*': [(1.1, 0.455), (0.75, 0.303), (ALLIN, 0.242)],
                'value': [(1.1, 0.135), (0.75, 0.09), (ALLIN, 0.774)],
                'medium': [(1.1, 0.135), (0.75, 0.09), (ALLIN, 0.774)],
            },
            'river': {
                '*': [(1.1, 0.436), (0.75, 0.29), (ALLIN, 0.274)],
                'value': [(1.1, 0.074), (0.75, 0.05), (ALLIN, 0.876)],
                'medium': [(1.1, 0.074), (0.75, 0.05), (ALLIN, 0.876)],
            },
        },
    )
