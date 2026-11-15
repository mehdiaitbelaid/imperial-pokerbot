"""Replica of Durahim 1453 (likely finalist) for the final-table sparring games.

Durahim 1453. Measured on 9 rounds, 9000 hands (r002, r008, r009, r011, r023, r032, r040, r043,
r048); latest third: r040, r043, r048. VPIP 21, PFR 16, 3-bet 8; opens 2.5bb 89%, 3bb 5%. Bet
sizes (share of pot): flop 0.33/0.66/1/1.7, turn 0.33/0.66/1/1.7/all-in, river
0.33/0.66/1/1.7/all-in.

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
    _base._NODES.setdefault('f_durahim', _NF.get('f_durahim', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'f_durahim'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.203, 0.0),
            'UTG+1': (0.171, 0.0),
            'MP': (0.248, 0.0),
            'HJ': (0.31, 0.0),
            'CO': (0.366, 0.0),
            'BTN': (0.558, 0.0),
            'SB': (0.439, 0.053),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(2.5, 1.0)], 'SB': [(3.0, 1.0)]},
        # facing limpers: (call, raise)
        vs_limp=(0.095, 0.345),
        bb_iso=0.054,
        iso=(2.0, 1.5),
        limp_fold=0.357,
        limp_rr=0.478,
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.082, 0.104), 'm': (0.068, 0.124), 'l': (0.019, 0.117)},
            'BB': {'s': (0.548, 0.052), 'm': (0.296, 0.115), 'l': (0.261, 0.021)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.02, 0.04), 'SB': (0.033, 0.026), 'BB': (0.088, 0.024)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.014, 0.035),
            'UTG+1': (0.006, 0.02),
            'MP': (0.006, 0.016),
            'HJ': (0.011, 0.029),
            'CO': (0.013, 0.04),
            'BTN': (0.021, 0.046),
            'SB': (0.063, 0.08),
            'BB': (0.255, 0.068),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.851, 1.059), (1.16, 0.104)),
        tb_rand=0.28,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={
            'ip': [((3.6, 0.0), 0.418), ((3.0, 0.0), 0.197), ((4.6, 0.0), 0.096), ((40.0, 0.0), 0.091)],
            'oop': [((3.6, 0.0), 0.744), ((4.6, 0.0), 0.154)],
        },
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.744, 0.128, 0.128),
        fb_rand=0.28,
        fourbet=[(2.3, 0.791), ('allin', 0.209)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.02, 0.038),
        cold_rand=0.0,
        call_then_3b=0.281,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.333, 0.315, 0.352),
        f4b_shove=0.812,
        fivebet=[(2.68, 0.294), ('allin', 0.706)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.467, 0.374, 0.159),
        shove_max=0.065,
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.677,
                'D_hu': 0.464,
                'S_hu': 0.774,
                'L_hu': 0.721,
                'A_mw': 0.431,
                'D_mw': 0.334,
                'S_mw': 0.44,
                'L_mw': 0.258,
            },
            'turn': {
                'A_hu': 0.463,
                'D_hu': 0.2,
                'S_hu': 0.601,
                'L_hu': 0.621,
                'A_mw': 0.311,
                'D_mw': 0.233,
                'S_mw': 0.277,
                'L_mw': 0.386,
            },
            'river': {
                'A_hu': 0.342,
                'D_hu': 0.206,
                'S_hu': 0.406,
                'L_hu': 0.222,
                'A_mw': 0.167,
                'D_mw': 0.167,
                'S_mw': 0.174,
                'L_mw': 0.154,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.33: {'air': 11.14, 'draw': 2.04, 'weak': 4.08, 'medium': 2.1, 'value': 0.05},
                    0.66: {'air': 8.14, 'draw': 2.04, 'weak': 5.08, 'medium': 4.1, 'value': 0.05},
                    1.0: {'air': 1.14, 'draw': 2.04, 'weak': 3.08, 'medium': 3.1, 'value': 2.05},
                    1.7: {'air': 1.14, 'draw': 0.04, 'weak': 1.08, 'medium': 6.1, 'value': 5.05},
                },
                'share': {
                    'A_hu': {0.33: 0.261, 0.66: 0.275, 1.0: 0.275, 1.7: 0.19},
                    'A_mw': {0.33: 0.156, 0.66: 0.344, 1.0: 0.281, 1.7: 0.219},
                    'D_hu': {0.33: 0.385, 0.66: 0.361, 1.0: 0.139, 1.7: 0.115},
                    'D_mw': {0.33: 0.111, 0.66: 0.222, 1.0: 0.278, 1.7: 0.389},
                    'S_hu': {0.33: 0.125, 0.66: 0.25, 1.0: 0.375, 1.7: 0.25},
                    'S_mw': {0.33: 0.118, 0.66: 0.118, 1.0: 0.294, 1.7: 0.471},
                    'L_hu': {0.33: 0.211, 0.66: 0.526, 1.0: 0.053, 1.7: 0.211},
                    'L_mw': {0.33: 0.111, 0.66: 0.167, 1.0: 0.306, 1.7: 0.417},
                },
            },
            'turn': {
                'sizes': {
                    0.33: {'air': 3.08, 'draw': 1.02, 'weak': 5.14, 'medium': 1.08, 'value': 0.08},
                    0.66: {'air': 4.08, 'draw': 1.02, 'weak': 3.14, 'medium': 2.08, 'value': 1.08},
                    1.0: {'air': 0.08, 'draw': 0.02, 'weak': 2.14, 'medium': 2.08, 'value': 2.08},
                    1.7: {'air': 0.08, 'draw': 0.02, 'weak': 1.14, 'medium': 1.08, 'value': 2.08},
                    ALLIN: {'air': 0.08, 'draw': 0.02, 'weak': 1.14, 'medium': 1.08, 'value': 2.08},
                },
                'share': {
                    'A_hu': {0.33: 0.141, 0.66: 0.281, 1.0: 0.328, 1.7: 0.109, ALLIN: 0.141},
                    'A_mw': {0.33: 0.211, 0.66: 0.341, 1.0: 0.276, 1.7: 0.098, ALLIN: 0.073},
                    'D_hu': {0.33: 0.289, 0.66: 0.489, 1.0: 0.178, 1.7: 0.044},
                    'D_mw': {0.33: 0.211, 0.66: 0.341, 1.0: 0.276, 1.7: 0.098, ALLIN: 0.073},
                    'S_hu': {0.33: 0.316, 0.66: 0.368, 1.0: 0.211, 1.7: 0.105},
                    'S_mw': {0.33: 0.211, 0.66: 0.341, 1.0: 0.276, 1.7: 0.098, ALLIN: 0.073},
                    'L_hu': {0.33: 0.312, 0.66: 0.5, 1.0: 0.188},
                    'L_mw': {0.33: 0.211, 0.66: 0.341, 1.0: 0.276, 1.7: 0.098, ALLIN: 0.073},
                },
            },
            'river': {
                'sizes': {
                    0.33: {'air': 0.03, 'weak': 2.08, 'medium': 2.08, 'value': 2.23},
                    0.66: {'air': 0.03, 'weak': 1.07, 'medium': 0.08, 'value': 2.23},
                    1.0: {'air': 0.03, 'weak': 0.08, 'medium': 1.07, 'value': 2.23},
                    1.7: {'air': 0.03, 'weak': 0.08, 'medium': 0.08, 'value': 1.23},
                    ALLIN: {'air': 1.02, 'weak': 0.08, 'medium': 0.08, 'value': 2.23},
                },
                'share': {
                    'A_hu': {0.33: 0.375, 0.66: 0.188, 1.0: 0.188, ALLIN: 0.25},
                    'A_mw': {0.33: 0.31, 0.66: 0.238, 1.0: 0.143, 1.7: 0.167, ALLIN: 0.143},
                    'D_hu': {0.33: 0.316, 0.66: 0.237, 1.0: 0.132, 1.7: 0.158, ALLIN: 0.158},
                    'D_mw': {0.33: 0.31, 0.66: 0.238, 1.0: 0.143, 1.7: 0.167, ALLIN: 0.143},
                    'S_hu': {0.33: 0.316, 0.66: 0.237, 1.0: 0.132, 1.7: 0.158, ALLIN: 0.158},
                    'S_mw': {0.33: 0.31, 0.66: 0.238, 1.0: 0.143, 1.7: 0.167, ALLIN: 0.143},
                    'L_hu': {0.33: 0.316, 0.66: 0.237, 1.0: 0.132, 1.7: 0.158, ALLIN: 0.158},
                    'L_mw': {0.33: 0.31, 0.66: 0.238, 1.0: 0.143, 1.7: 0.167, ALLIN: 0.143},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.611, 0.333, 0.056),
            0.33: {'*': (0.858, 0.13, 0.012), 'flop': (0.907, 0.089, 0.004)},
            0.66: {'*': (0.644, 0.347, 0.009), 'flop': (0.66, 0.337, 0.003)},
            1.0: (0.342, 0.487, 0.171),
            1.7: {'*': (0.496, 0.422, 0.081), 'flop': (0.469, 0.443, 0.088)},
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.361, 0.453, 0.186),
                    '<40%': (0.231, 0.483, 0.285),
                    '40-75%': (0.309, 0.549, 0.142),
                    '75-110%': (0.422, 0.33, 0.247),
                    'overbet': (0.829, 0.152, 0.02),
                },
                'xr': {
                    'all': (0.646, 0.299, 0.056),
                    '<40%': (0.412, 0.522, 0.066),
                    '40-75%': (0.618, 0.345, 0.037),
                    '75-110%': (0.766, 0.175, 0.059),
                    'overbet': (0.915, 0.03, 0.056),
                },
                'cells': {
                    'flop_n_hu': (0.318, 0.484, 0.197),
                    'flop_n_mw': (0.507, 0.346, 0.147),
                    'flop_x_hu': (0.634, 0.288, 0.078),
                    'flop_x_mw': (0.664, 0.274, 0.062),
                    'flop_ms_hu': (0.692, 0.304, 0.004),
                    'flop_ms_mw': (0.645, 0.307, 0.049),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.515, 0.375, 0.109),
                    '<40%': (0.067, 0.827, 0.106),
                    '40-75%': (0.51, 0.344, 0.147),
                    '75-110%': (0.744, 0.184, 0.073),
                    'overbet': (0.956, 0.034, 0.01),
                },
                'xr': {
                    'all': (0.717, 0.259, 0.024),
                    '<40%': (0.313, 0.641, 0.046),
                    '40-75%': (0.827, 0.169, 0.005),
                    '75-110%': (0.87, 0.097, 0.033),
                    'overbet': (0.977, 0.021, 0.002),
                },
                'cells': {
                    'turn_b2_n_hu': (0.533, 0.4, 0.067),
                    'turn_b2_n_mw': (0.538, 0.408, 0.055),
                    'turn_b2_x_hu': (0.679, 0.32, 0.001),
                    'turn_b2_x_mw': (0.739, 0.257, 0.005),
                    'turn_n_hu': (0.445, 0.307, 0.249),
                    'turn_n_mw': (0.554, 0.315, 0.131),
                    'turn_x_hu': (0.602, 0.394, 0.005),
                    'turn_x_mw': (0.859, 0.137, 0.004),
                    'turn_ms_hu': (0.766, 0.189, 0.046),
                    'turn_ms_mw': (0.802, 0.163, 0.034),
                },
                'no_xr': False,
            },
            'river': {
                'nx': {
                    'all': (0.555, 0.427, 0.018),
                    '<40%': (0.339, 0.652, 0.009),
                    '40-75%': (0.651, 0.313, 0.036),
                    '75-110%': (0.595, 0.398, 0.007),
                    'overbet': (0.761, 0.232, 0.006),
                },
                'xr': {
                    'all': (0.824, 0.175, 0.001),
                    '<40%': (0.695, 0.304, 0.001),
                    '40-75%': (0.863, 0.137, 0.001),
                    '75-110%': (0.914, 0.085, 0.001),
                    'overbet': (0.949, 0.051, 0.0),
                },
                'cells': {
                    'river_b3_n_hu': (0.531, 0.468, 0.001),
                    'river_b3_n_mw': (0.535, 0.461, 0.004),
                    'river_b3_x_hu': (0.788, 0.213, 0.0),
                    'river_b3_x_mw': (0.803, 0.197, 0.0),
                    'river_ct_n_hu': (0.599, 0.392, 0.009),
                    'river_ct_n_mw': (0.558, 0.432, 0.01),
                    'river_ct_x_hu': (0.958, 0.042, 0.0),
                    'river_ct_x_mw': (0.924, 0.077, 0.0),
                    'river_n_hu': (0.584, 0.358, 0.058),
                    'river_n_mw': (0.509, 0.45, 0.041),
                    'river_x_hu': (0.752, 0.248, 0.0),
                    'river_x_mw': (0.779, 0.222, 0.0),
                    'river_ms_hu': (0.819, 0.18, 0.0),
                    'river_ms_mw': (0.821, 0.18, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.3, 'draw': 1.4, 'weak': 2.2, 'medium': 6.1, 'value': 7.1},
            'turn': {'air': 0.1, 'draw': 1.2, 'weak': 0.2, 'medium': 4.7, 'value': 6.8},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 0.4, 'value': 2.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {'*': [(1.0, 0.279), (1.7, 0.246), (0.33, 0.197), (0.66, 0.164)]},
            'turn': {'*': [(1.7, 0.273), (0.66, 0.182), (0.33, 0.182), (0.5, 0.182)]},
            'river': {'*': [(0.75, 1.0)]},
        },
    )
