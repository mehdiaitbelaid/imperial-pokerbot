"""Replica of GamesGone for the Table D sparring table.

GamesGone: opens 2.2bb, 3-bets 3% for value only, bets exactly 0.5 pot (air, draws, weak pairs)
or 1.0 pot (top pair or better), c-bets and barrels the turn 100% heads up, folds 74% when a 0.5
bet is raised, calls down (folds 32% to a second barrel and 18% to a third).

Parameters written by tabled/build.py from the team's real hands (same definitions as
docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import ALLIN, Base  # noqa: E402,F401


class Agent(Base):
    NAME = 'gg'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.231, 0.0),
            'UTG+1': (0.246, 0.0),
            'MP': (0.226, 0.0),
            'HJ': (0.326, 0.0),
            'CO': (0.384, 0.0),
            'BTN': (0.564, 0.0),
            'SB': (0.579, 0.034),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(2.2, 1.0)], 'HJ': [(2.2, 0.909), (3.0, 0.091)], 'CO': [(2.2, 0.941), (3.0, 0.059)]},
        # facing limpers: (call, raise)
        vs_limp=(0.11, 0.287),
        bb_iso=0.206,
        iso=(3.0, 1.0),
        limp_fold=0.743,
        limp_rr=0.0,
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.336, 0.043), 'm': (0.202, 0.031), 'l': (0.135, 0.003)},
            'BB': {'s': (0.741, 0.031), 'm': (0.449, 0.022), 'l': (0.25, 0.002)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.153, 0.025), 'SB': (0.482, 0.017), 'BB': (0.773, 0.032)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.08, 0.02),
            'MP': (0.115, 0.019),
            'HJ': (0.085, 0.024),
            'CO': (0.065, 0.016),
            'BTN': (0.077, 0.021),
            'SB': (0.161, 0.031),
            'BB': (0.299, 0.036),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.218, 1.158), (0.099, 0.036)),
        tb_rand=0.05,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((3.0, 0.0), 0.89), ((4.0, 0.0), 0.11)], 'oop': [((3.0, 0.0), 0.67), ((4.0, 0.0), 0.33)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.514, 0.378, 0.108),
        fourbet=[('allin', 1.0)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.07, 0.03),
        call_then_3b=0.595,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.04, 0.355, 0.605),
        f4b_shove=0.284,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.25, 0.7, 0.05),
        shove_max=0.05,
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.997,
                'D_hu': 0.989,
                'S_hu': 0.974,
                'L_hu': 0.998,
                'A_mw': 0.318,
                'D_mw': 0.187,
                'S_mw': 0.225,
                'L_mw': 0.29,
            },
            'turn': {
                'A_hu': 0.995,
                'D_hu': 0.911,
                'S_hu': 0.979,
                'L_hu': 0.981,
                'A_mw': 0.638,
                'D_mw': 0.344,
                'S_mw': 0.11,
                'L_mw': 0.072,
            },
            'river': {
                'A_hu': 0.375,
                'D_hu': 0.53,
                'S_hu': 0.625,
                'L_hu': 0.282,
                'A_mw': 0.012,
                'D_mw': 0.012,
                'S_mw': 0.03,
                'L_mw': 0.002,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.5: {'air': 56.13, 'draw': 20.07, 'weak': 22.07, 'medium': 7.1, 'value': 1.03},
                    1.0: {'air': 5.13, 'draw': 12.07, 'weak': 13.07, 'medium': 40.1, 'value': 15.03},
                },
                'share': {
                    'A_hu': {0.5: 0.5, 1.0: 0.5},
                    'A_mw': {0.5: 0.5, 1.0: 0.5},
                    'D_hu': {0.5: 0.667, 1.0: 0.333},
                    'D_mw': {0.5: 0.55, 1.0: 0.45},
                    'S_hu': {0.5: 0.676, 1.0: 0.324},
                    'S_mw': {0.5: 0.278, 1.0: 0.722},
                    'L_hu': {0.5: 0.667, 1.0: 0.333},
                    'L_mw': {0.5: 0.494, 1.0: 0.506},
                },
            },
            'turn': {
                'sizes': {
                    0.5: {'air': 37.07, 'draw': 32.06, 'weak': 39.11, 'medium': 8.08, 'value': 1.07},
                    1.0: {'air': 1.07, 'draw': 2.06, 'weak': 20.11, 'medium': 36.08, 'value': 37.07},
                },
                'share': {
                    'A_hu': {0.5: 0.598, 1.0: 0.402},
                    'A_mw': {0.5: 0.483, 1.0: 0.517},
                    'D_hu': {0.5: 0.548, 1.0: 0.452},
                    'D_mw': {0.5: 0.483, 1.0: 0.517},
                    'S_hu': {0.5: 0.359, 1.0: 0.641},
                    'S_mw': {0.5: 0.483, 1.0: 0.517},
                    'L_hu': {0.5: 0.435, 1.0: 0.565},
                    'L_mw': {0.5: 0.483, 1.0: 0.517},
                },
            },
            'river': {
                'sizes': {
                    0.5: {'air': 46.18, 'weak': 28.12, 'medium': 1.04, 'value': 2.06},
                    1.0: {'air': 2.18, 'weak': 5.12, 'medium': 9.04, 'value': 14.06},
                },
                'share': {
                    'A_hu': {0.5: 0.562, 1.0: 0.438},
                    'A_mw': {0.5: 0.5, 1.0: 0.5},
                    'D_hu': {0.5: 0.514, 1.0: 0.486},
                    'D_mw': {0.5: 0.5, 1.0: 0.5},
                    'S_hu': {0.5: 0.514, 1.0: 0.486},
                    'S_mw': {0.5: 0.5, 1.0: 0.5},
                    'L_hu': {0.5: 0.514, 1.0: 0.486},
                    'L_mw': {0.5: 0.5, 1.0: 0.5},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.603, 0.335, 0.062),
            0.5: {
                '*': (0.741, 0.24, 0.019),
                'flop': (0.768, 0.207, 0.025),
                'turn': (0.692, 0.305, 0.003),
                'river': (0.696, 0.296, 0.008),
            },
            1.0: {'*': (0.322, 0.529, 0.149), 'flop': (0.457, 0.379, 0.165), 'turn': (0.16, 0.707, 0.132)},
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.409, 0.468, 0.123),
                    '<40%': (0.166, 0.584, 0.25),
                    '40-75%': (0.441, 0.494, 0.066),
                    '75-110%': (0.483, 0.401, 0.116),
                    'overbet': (0.648, 0.319, 0.033),
                },
                'xr': {
                    'all': (0.642, 0.339, 0.018),
                    '<40%': (0.409, 0.556, 0.035),
                    '40-75%': (0.661, 0.327, 0.012),
                    '75-110%': (0.691, 0.292, 0.017),
                    'overbet': (0.834, 0.162, 0.004),
                },
                'cells': {
                    'flop_n_hu': (0.344, 0.508, 0.148),
                    'flop_n_mw': (0.576, 0.366, 0.059),
                    'flop_x_hu': (0.718, 0.276, 0.006),
                    'flop_x_mw': (0.684, 0.31, 0.006),
                    'flop_ms_hu': (0.291, 0.626, 0.083),
                    'flop_ms_mw': (0.323, 0.59, 0.087),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.436, 0.437, 0.128),
                    '<40%': (0.18, 0.578, 0.241),
                    '40-75%': (0.48, 0.423, 0.097),
                    '75-110%': (0.56, 0.359, 0.081),
                    'overbet': (0.583, 0.344, 0.074),
                },
                'xr': {
                    'all': (0.84, 0.152, 0.008),
                    '<40%': (0.62, 0.365, 0.015),
                    '40-75%': (0.876, 0.121, 0.003),
                    '75-110%': (0.929, 0.07, 0.001),
                    'overbet': (0.756, 0.24, 0.003),
                },
                'cells': {
                    'turn_b2_n_hu': (0.317, 0.551, 0.132),
                    'turn_b2_n_mw': (0.373, 0.535, 0.092),
                    'turn_b2_x_hu': (0.665, 0.335, 0.0),
                    'turn_b2_x_mw': (0.758, 0.242, 0.0),
                    'turn_n_hu': (0.447, 0.321, 0.232),
                    'turn_n_mw': (0.839, 0.152, 0.009),
                    'turn_x_hu': (0.793, 0.207, 0.0),
                    'turn_x_mw': (0.888, 0.111, 0.0),
                    'turn_ms_hu': (0.889, 0.11, 0.0),
                    'turn_ms_mw': (0.957, 0.043, 0.0),
                },
                'no_xr': True,
            },
            'river': {
                'nx': {
                    'all': (0.336, 0.571, 0.094),
                    '<40%': (0.098, 0.833, 0.069),
                    '40-75%': (0.367, 0.51, 0.123),
                    '75-110%': (0.582, 0.312, 0.106),
                    'overbet': (0.548, 0.415, 0.037),
                },
                'xr': {
                    'all': (0.63, 0.311, 0.059),
                    '<40%': (0.134, 0.811, 0.055),
                    '40-75%': (0.663, 0.191, 0.147),
                    '75-110%': (0.835, 0.157, 0.008),
                    'overbet': (0.819, 0.167, 0.014),
                },
                'cells': {
                    'river_b3_n_hu': (0.185, 0.743, 0.073),
                    'river_b3_n_mw': (0.481, 0.486, 0.032),
                    'river_b3_x_hu': (0.525, 0.4, 0.075),
                    'river_b3_x_mw': (0.903, 0.081, 0.015),
                    'river_ct_n_hu': (0.565, 0.381, 0.053),
                    'river_ct_n_mw': (0.812, 0.17, 0.018),
                    'river_ct_x_hu': (0.692, 0.281, 0.027),
                    'river_ct_x_mw': (0.826, 0.168, 0.007),
                    'river_n_hu': (0.346, 0.487, 0.167),
                    'river_n_mw': (0.774, 0.173, 0.053),
                    'river_x_hu': (0.285, 0.649, 0.066),
                    'river_x_mw': (0.77, 0.122, 0.107),
                    'river_ms_hu': (0.612, 0.316, 0.072),
                    'river_ms_mw': (0.909, 0.074, 0.017),
                },
                'no_xr': False,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 7.1, 'draw': 4.1, 'weak': 2.1, 'medium': 1.4, 'value': 9.4},
            'turn': {'air': 0.1, 'draw': 3.2, 'weak': 1.2, 'medium': 0.7, 'value': 11.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 0.4, 'value': 10.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {
                'value': [(1.0, 0.431), (0.6, 0.288), (ALLIN, 0.281)],
                '*': [(0.4, 0.502), (0.6, 0.182), (0.7, 0.109), (1.0, 0.119), (ALLIN, 0.088)],
                'medium': [(0.4, 0.396), (0.6, 0.144), (0.7, 0.086), (1.0, 0.093), (ALLIN, 0.281)],
            },
            'turn': {
                '*': [(0.4, 0.47), (1.0, 0.313), (ALLIN, 0.217)],
                'value': [(0.4, 0.184), (1.0, 0.123), (ALLIN, 0.693)],
                'medium': [(0.4, 0.184), (1.0, 0.123), (ALLIN, 0.693)],
            },
            'river': {
                '*': [(1.0, 0.43), (0.4, 0.287), (ALLIN, 0.283)],
                'value': [(1.0, 0.06), (0.4, 0.04), (ALLIN, 0.9)],
                'medium': [(1.0, 0.06), (0.4, 0.04), (ALLIN, 0.9)],
            },
        },
    )
