"""Replica of FisherMen (likely finalist) for the final-table sparring games.

FisherMen. Measured on 11 rounds, 11000 hands (r008, r012, r013, r019, r021, r025, r035, r039,
r040, r041, r043); latest third: r040, r041, r043. VPIP 30, PFR 24, 3-bet 13; opens 3.25bb 84%,
2.95bb 7%. Bet sizes (share of pot): flop 0.33/0.66/1, turn 0.33/0.66/1/all-in, river
0.33/0.66/1/all-in.

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
    _base._NODES.setdefault('f_fishermen', _NF.get('f_fishermen', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'f_fishermen'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.284, 0.0),
            'UTG+1': (0.337, 0.0),
            'MP': (0.297, 0.0),
            'HJ': (0.355, 0.0),
            'CO': (0.389, 0.0),
            'BTN': (0.596, 0.0),
            'SB': (0.667, 0.182),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={
            '*': [(3.25, 1.0)],
            'BTN': [(3.25, 0.525), (2.95, 0.475)],
            'SB': [(3.25, 0.477), (3.75, 0.383), (3.0, 0.141)],
        },
        # facing limpers: (call, raise)
        vs_limp=(0.037, 0.484),
        bb_iso=0.548,
        iso=(6.0, 2.0),
        limp_fold=0.867,
        limp_rr=0.067,
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.268, 0.073), 'm': (0.124, 0.181), 'l': (0.085, 0.182)},
            'BB': {'s': (0.474, 0.249), 'm': (0.359, 0.48), 'l': (0.167, 0.589)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.026, 0.083), 'SB': (0.046, 0.126), 'BB': (0.068, 0.211)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.084, 0.153),
            'UTG+1': (0.12, 0.034),
            'MP': (0.087, 0.043),
            'HJ': (0.082, 0.079),
            'CO': (0.068, 0.147),
            'BTN': (0.092, 0.269),
            'SB': (0.046, 0.185),
            'BB': (0.126, 0.333),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.415, 1.346), (0.118, 0.64)),
        tb_rand=0.54,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((3.2, 0.0), 0.866)], 'oop': [((4.2, 0.0), 0.703), ((5.2, 0.0), 0.128)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.654, 0.165, 0.18),
        fb_rand=0.57,
        fourbet=[(2.6, 0.276), ('allin', 0.724)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.026, 0.076),
        cold_rand=0.7,
        call_then_3b=0.545,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.792, 0.133, 0.075),
        f4b_shove=0.986,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.548, 0.438, 0.014),
        shove_max=1.0,
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.556,
                'D_hu': 0.504,
                'S_hu': 0.659,
                'L_hu': 0.423,
                'A_mw': 0.269,
                'D_mw': 0.209,
                'S_mw': 0.217,
                'L_mw': 0.243,
            },
            'turn': {
                'A_hu': 0.681,
                'D_hu': 0.415,
                'S_hu': 0.472,
                'L_hu': 0.47,
                'A_mw': 0.338,
                'D_mw': 0.107,
                'S_mw': 0.254,
                'L_mw': 0.2,
            },
            'river': {
                'A_hu': 0.627,
                'D_hu': 0.213,
                'S_hu': 0.378,
                'L_hu': 0.333,
                'A_mw': 0.329,
                'D_mw': 0.198,
                'S_mw': 0.375,
                'L_mw': 0.293,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.33: {'air': 6.08, 'draw': 6.06, 'weak': 8.06, 'medium': 5.12, 'value': 0.07},
                    0.66: {'air': 7.08, 'draw': 3.06, 'weak': 2.06, 'medium': 4.12, 'value': 3.07},
                    1.0: {'air': 3.08, 'draw': 3.06, 'weak': 2.06, 'medium': 14.12, 'value': 10.07},
                },
                'share': {
                    'A_hu': {0.33: 0.31, 0.66: 0.29, 1.0: 0.399},
                    'A_mw': {0.33: 0.1, 0.66: 0.225, 1.0: 0.675},
                    'D_hu': {0.33: 0.446, 0.66: 0.308, 1.0: 0.246},
                    'D_mw': {0.33: 0.174, 0.66: 0.391, 1.0: 0.435},
                    'S_hu': {0.33: 0.417, 0.66: 0.083, 1.0: 0.5},
                    'S_mw': {0.33: 0.083, 0.66: 0.167, 1.0: 0.75},
                    'L_hu': {0.33: 0.333, 0.66: 0.25, 1.0: 0.417},
                    'L_mw': {0.33: 0.139, 0.66: 0.306, 1.0: 0.556},
                },
            },
            'turn': {
                'sizes': {
                    0.33: {'air': 6.04, 'draw': 4.03, 'weak': 11.1, 'medium': 12.12, 'value': 2.11},
                    0.66: {'air': 2.04, 'draw': 2.03, 'weak': 4.1, 'medium': 4.12, 'value': 6.11},
                    1.0: {'air': 1.04, 'draw': 0.03, 'weak': 7.1, 'medium': 6.12, 'value': 13.11},
                    ALLIN: {'air': 0.04, 'draw': 0.03, 'weak': 0.1, 'medium': 3.12, 'value': 2.11},
                },
                'share': {
                    'A_hu': {0.33: 0.329, 0.66: 0.267, 1.0: 0.356, ALLIN: 0.048},
                    'A_mw': {0.33: 0.2, 0.66: 0.229, 1.0: 0.571},
                    'D_hu': {0.33: 0.408, 0.66: 0.184, 1.0: 0.367, ALLIN: 0.041},
                    'D_mw': {0.33: 0.219, 0.66: 0.219, 1.0: 0.562},
                    'S_hu': {0.33: 0.311, 0.66: 0.311, 1.0: 0.344, ALLIN: 0.033},
                    'S_mw': {0.33: 0.227, 0.66: 0.273, 1.0: 0.5},
                    'L_hu': {0.33: 0.375, 0.66: 0.281, 1.0: 0.344},
                    'L_mw': {0.33: 0.219, 0.66: 0.219, 1.0: 0.562},
                },
            },
            'river': {
                'sizes': {
                    0.33: {'air': 8.07, 'weak': 8.08, 'medium': 3.07, 'value': 3.18},
                    0.66: {'air': 1.07, 'weak': 3.08, 'medium': 2.07, 'value': 5.18},
                    1.0: {'air': 2.07, 'weak': 2.08, 'medium': 2.07, 'value': 16.18},
                    ALLIN: {'air': 1.07, 'weak': 1.08, 'medium': 5.07, 'value': 7.18},
                },
                'share': {
                    'A_hu': {0.33: 0.159, 0.66: 0.244, 1.0: 0.378, ALLIN: 0.22},
                    'A_mw': {0.33: 0.296, 0.66: 0.222, 1.0: 0.444, ALLIN: 0.037},
                    'D_hu': {0.33: 0.373, 0.66: 0.169, 1.0: 0.339, ALLIN: 0.119},
                    'D_mw': {0.33: 0.296, 0.66: 0.222, 1.0: 0.444, ALLIN: 0.037},
                    'S_hu': {0.33: 0.324, 0.66: 0.147, 1.0: 0.382, ALLIN: 0.147},
                    'S_mw': {0.33: 0.263, 0.66: 0.263, 1.0: 0.474},
                    'L_hu': {0.33: 0.294, 0.66: 0.235, 1.0: 0.353, ALLIN: 0.118},
                    'L_mw': {0.33: 0.296, 0.66: 0.222, 1.0: 0.444, ALLIN: 0.037},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.743, 0.216, 0.041),
            0.33: {'*': (0.948, 0.048, 0.004), 'flop': (0.953, 0.046, 0.001), 'turn': (0.981, 0.018, 0.002)},
            0.66: {'*': (0.887, 0.048, 0.065), 'turn': (0.88, 0.021, 0.099)},
            1.0: {'*': (0.378, 0.547, 0.075), 'flop': (0.251, 0.664, 0.085), 'turn': (0.428, 0.487, 0.085)},
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.453, 0.474, 0.073),
                    '<40%': (0.217, 0.729, 0.054),
                    '40-75%': (0.475, 0.423, 0.102),
                    '75-110%': (0.562, 0.378, 0.06),
                    'overbet': (0.643, 0.33, 0.027),
                },
                'xr': {
                    'all': (0.529, 0.452, 0.019),
                    '<40%': (0.281, 0.696, 0.023),
                    '40-75%': (0.538, 0.441, 0.022),
                    '75-110%': (0.664, 0.322, 0.014),
                    'overbet': (0.596, 0.399, 0.005),
                },
                'cells': {
                    'flop_n_hu': (0.409, 0.524, 0.067),
                    'flop_n_mw': (0.609, 0.299, 0.092),
                    'flop_x_hu': (0.506, 0.471, 0.023),
                    'flop_x_mw': (0.791, 0.207, 0.002),
                    'flop_ms_hu': (0.399, 0.573, 0.028),
                    'flop_ms_mw': (0.541, 0.456, 0.004),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.474, 0.436, 0.09),
                    '<40%': (0.24, 0.639, 0.121),
                    '40-75%': (0.477, 0.399, 0.124),
                    '75-110%': (0.708, 0.271, 0.021),
                    'overbet': (0.505, 0.471, 0.024),
                },
                'xr': {
                    'all': (0.589, 0.362, 0.049),
                    '<40%': (0.349, 0.575, 0.075),
                    '40-75%': (0.634, 0.317, 0.049),
                    '75-110%': (0.715, 0.257, 0.027),
                    'overbet': (0.777, 0.203, 0.02),
                },
                'cells': {
                    'turn_b2_n_hu': (0.528, 0.433, 0.039),
                    'turn_b2_n_mw': (0.436, 0.54, 0.024),
                    'turn_b2_x_hu': (0.553, 0.387, 0.061),
                    'turn_b2_x_mw': (0.607, 0.364, 0.029),
                    'turn_n_hu': (0.6, 0.236, 0.164),
                    'turn_n_mw': (0.805, 0.144, 0.051),
                    'turn_x_hu': (0.72, 0.278, 0.003),
                    'turn_x_mw': (0.71, 0.288, 0.002),
                    'turn_ms_hu': (0.839, 0.128, 0.033),
                    'turn_ms_mw': (0.771, 0.148, 0.081),
                },
                'no_xr': False,
            },
            'river': {
                'nx': {
                    'all': (0.425, 0.515, 0.06),
                    '<40%': (0.281, 0.647, 0.072),
                    '40-75%': (0.445, 0.484, 0.071),
                    '75-110%': (0.489, 0.47, 0.04),
                    'overbet': (0.657, 0.322, 0.021),
                },
                'xr': {
                    'all': (0.719, 0.251, 0.03),
                    '<40%': (0.515, 0.408, 0.077),
                    '40-75%': (0.767, 0.226, 0.007),
                    '75-110%': (0.902, 0.091, 0.007),
                    'overbet': (0.79, 0.196, 0.014),
                },
                'cells': {
                    'river_b3_n_hu': (0.452, 0.53, 0.018),
                    'river_b3_n_mw': (0.498, 0.404, 0.098),
                    'river_b3_x_hu': (0.569, 0.365, 0.066),
                    'river_b3_x_mw': (0.703, 0.268, 0.029),
                    'river_ct_n_hu': (0.597, 0.263, 0.139),
                    'river_ct_n_mw': (0.713, 0.182, 0.105),
                    'river_ct_x_hu': (0.812, 0.18, 0.008),
                    'river_ct_x_mw': (0.844, 0.15, 0.006),
                    'river_n_hu': (0.259, 0.668, 0.073),
                    'river_n_mw': (0.392, 0.57, 0.038),
                    'river_x_hu': (0.843, 0.153, 0.004),
                    'river_x_mw': (0.794, 0.2, 0.006),
                    'river_ms_hu': (0.709, 0.25, 0.041),
                    'river_ms_mw': (0.788, 0.184, 0.028),
                },
                'no_xr': False,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.1, 'draw': 1.1, 'weak': 0.1, 'medium': 5.4, 'value': 14.4},
            'turn': {'draw': 1.1, 'weak': 0.1, 'medium': 4.2, 'value': 11.6},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 1.4, 'value': 6.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {'*': [(0.5, 0.372), (0.62, 0.256)]},
            'turn': {'*': [(0.5, 0.37), (0.4, 0.222), (0.8, 0.148)]},
            'river': {'*': [(0.23, 0.556), (0.55, 0.222)]},
        },
    )
