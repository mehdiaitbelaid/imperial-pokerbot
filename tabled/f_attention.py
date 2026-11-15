"""Replica of Attention Is All In (likely finalist) for the final-table sparring games.

Attention Is All In. Measured on 10 rounds, 10000 hands (r005, r007, r009, r011, r021, r022,
r038, r049, r050, r051); latest third: r049, r050, r051. VPIP 29, PFR 21, 3-bet 14; opens 2.5bb
70%, 2bb 15%. Bet sizes (share of pot): flop 0.33/0.66/0.88/1, turn 0.19/0.33/0.66/1/all-in,
river 0.16/0.33/0.66/all-in.

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
    _base._NODES.setdefault('f_attention', _NF.get('f_attention', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'f_attention'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.141, 0.0),
            'UTG+1': (0.123, 0.0),
            'MP': (0.131, 0.0),
            'HJ': (0.227, 0.0),
            'CO': (0.238, 0.0),
            'BTN': (0.545, 0.0),
            'SB': (0.841, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={
            '*': [(2.5, 1.0)],
            'UTG': [(2.5, 0.679), (4.0, 0.321)],
            'UTG+1': [(2.5, 0.69), (4.0, 0.31)],
            'MP': [(2.5, 0.838), (4.0, 0.162)],
            'HJ': [(2.5, 0.788), (4.0, 0.212)],
        },
        # facing limpers: (call, raise)
        vs_limp=(0.105, 0.333),
        bb_iso=0.76,
        iso=(1.5, 1.5),
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.088, 0.212), 'm': (0.045, 0.386), 'l': (0.117, 0.14)},
            'BB': {'s': (0.325, 0.407), 'm': (0.279, 0.262), 'l': (0.195, 0.33)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.174, 0.035), 'SB': (0.176, 0.124), 'BB': (0.704, 0.074)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.099, 0.062),
            'UTG+1': (0.078, 0.025),
            'MP': (0.083, 0.021),
            'HJ': (0.097, 0.047),
            'CO': (0.112, 0.043),
            'BTN': (0.101, 0.11),
            'SB': (0.176, 0.228),
            'BB': (0.229, 0.299),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.609, 1.167), (0.283, 0.113)),
        tb_rand=0.56,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((3.0, 0.0), 0.949)], 'oop': [((3.0, 0.0), 0.949)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.714, 0.235, 0.051),
        fb_rand=0.0,
        fourbet=[('allin', 1.0)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.016, 0.007),
        cold_rand=0.0,
        call_then_3b=0.114,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.879, 0.058, 0.063),
        f4b_shove=0.81,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.25, 0.7, 0.05),
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.818,
                'D_hu': 0.784,
                'S_hu': 0.593,
                'L_hu': 0.778,
                'A_mw': 0.463,
                'D_mw': 0.336,
                'S_mw': 0.333,
                'L_mw': 0.541,
            },
            'turn': {
                'A_hu': 0.847,
                'D_hu': 0.423,
                'S_hu': 0.592,
                'L_hu': 0.337,
                'A_mw': 0.367,
                'D_mw': 0.288,
                'S_mw': 0.101,
                'L_mw': 0.108,
            },
            'river': {
                'A_hu': 0.873,
                'D_hu': 0.719,
                'S_hu': 0.516,
                'L_hu': 0.32,
                'A_mw': 0.142,
                'D_mw': 0.08,
                'S_mw': 0.076,
                'L_mw': 0.111,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.33: {'air': 22.09, 'draw': 2.03, 'weak': 30.11, 'medium': 21.14, 'value': 3.04},
                    0.66: {'air': 3.09, 'draw': 1.03, 'weak': 1.11, 'medium': 12.14, 'value': 5.04},
                    0.88: {'air': 0.09, 'draw': 0.03, 'weak': 0.11, 'medium': 4.14, 'value': 0.04},
                    1.0: {'air': 1.09, 'draw': 6.03, 'weak': 1.11, 'medium': 6.14, 'value': 3.04},
                },
                'share': {
                    'A_hu': {0.33: 0.519, 0.66: 0.346, 0.88: 0.019, 1.0: 0.115},
                    'A_mw': {0.33: 0.551, 0.66: 0.203, 0.88: 0.072, 1.0: 0.174},
                    'D_hu': {0.33: 0.538, 0.66: 0.277, 1.0: 0.185},
                    'D_mw': {0.33: 0.542, 0.66: 0.136, 0.88: 0.119, 1.0: 0.203},
                    'S_hu': {0.33: 0.542, 0.66: 0.276, 1.0: 0.182},
                    'S_mw': {0.33: 0.556, 0.66: 0.125, 0.88: 0.139, 1.0: 0.181},
                    'L_hu': {0.33: 0.542, 0.66: 0.276, 1.0: 0.182},
                    'L_mw': {0.33: 0.556, 0.66: 0.125, 0.88: 0.139, 1.0: 0.181},
                },
            },
            'turn': {
                'sizes': {
                    0.19: {'air': 0.05, 'draw': 2.05, 'weak': 0.1, 'medium': 1.13, 'value': 2.07},
                    0.33: {'air': 10.05, 'draw': 4.05, 'weak': 19.1, 'medium': 24.13, 'value': 11.07},
                    0.66: {'air': 4.05, 'draw': 0.05, 'weak': 6.1, 'medium': 7.13, 'value': 4.07},
                    1.0: {'air': 0.05, 'draw': 7.05, 'weak': 3.1, 'medium': 4.13, 'value': 1.07},
                    ALLIN: {'air': 0.05, 'draw': 1.05, 'weak': 0.1, 'medium': 1.13, 'value': 2.07},
                },
                'share': {
                    'A_hu': {0.33: 0.542, 0.66: 0.322, 1.0: 0.119, ALLIN: 0.017},
                    'A_mw': {0.33: 0.571, 0.66: 0.274, 1.0: 0.119, ALLIN: 0.036},
                    'D_hu': {0.33: 0.483, 0.66: 0.241, 1.0: 0.172, ALLIN: 0.103},
                    'D_mw': {0.33: 0.571, 0.66: 0.274, 1.0: 0.119, ALLIN: 0.036},
                    'S_hu': {0.33: 0.579, 0.66: 0.105, 1.0: 0.158, ALLIN: 0.158},
                    'S_mw': {0.33: 0.571, 0.66: 0.274, 1.0: 0.119, ALLIN: 0.036},
                    'L_hu': {0.33: 0.529, 0.66: 0.176, 1.0: 0.176, ALLIN: 0.118},
                    'L_mw': {0.33: 0.571, 0.66: 0.274, 1.0: 0.119, ALLIN: 0.036},
                },
            },
            'river': {
                'sizes': {
                    0.16: {'air': 0.1, 'weak': 0.1, 'medium': 1.09, 'value': 5.12},
                    0.33: {'air': 15.1, 'weak': 16.1, 'medium': 17.09, 'value': 12.12},
                    0.66: {'air': 8.1, 'weak': 6.1, 'medium': 3.09, 'value': 3.12},
                    ALLIN: {'air': 6.1, 'weak': 9.1, 'medium': 5.09, 'value': 16.12},
                },
                'share': {
                    'A_hu': {0.16: 0.241, 0.33: 0.471, 0.66: 0.166, ALLIN: 0.123},
                    'A_mw': {0.16: 0.019, 0.33: 0.556, 0.66: 0.315, ALLIN: 0.111},
                    'D_hu': {0.33: 0.256, 0.66: 0.205, ALLIN: 0.538},
                    'D_mw': {0.16: 0.019, 0.33: 0.556, 0.66: 0.315, ALLIN: 0.111},
                    'S_hu': {0.33: 0.75, 0.66: 0.167, ALLIN: 0.083},
                    'S_mw': {0.16: 0.019, 0.33: 0.556, 0.66: 0.315, ALLIN: 0.111},
                    'L_hu': {0.33: 0.411, 0.66: 0.196, ALLIN: 0.393},
                    'L_mw': {0.16: 0.019, 0.33: 0.556, 0.66: 0.315, ALLIN: 0.111},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.772, 0.195, 0.034),
            0.33: {
                '*': (0.817, 0.158, 0.025),
                'flop': (0.86, 0.103, 0.037),
                'turn': (0.774, 0.22, 0.005),
                'river': (0.744, 0.247, 0.009),
            },
            0.66: {'*': (0.813, 0.183, 0.004), 'flop': (0.817, 0.182, 0.001), 'turn': (0.859, 0.14, 0.001)},
            1.0: {'*': (0.64, 0.308, 0.052), 'flop': (0.592, 0.342, 0.065)},
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.506, 0.344, 0.15),
                    '<40%': (0.369, 0.419, 0.212),
                    '40-75%': (0.418, 0.443, 0.14),
                    '75-110%': (0.661, 0.185, 0.154),
                    'overbet': (0.78, 0.148, 0.072),
                },
                'xr': {
                    'all': (0.754, 0.244, 0.002),
                    '<40%': (0.703, 0.297, 0.0),
                    '40-75%': (0.649, 0.351, 0.0),
                    '75-110%': (0.912, 0.088, 0.0),
                    'overbet': (0.963, 0.036, 0.0),
                },
                'cells': {
                    'flop_n_hu': (0.42, 0.387, 0.194),
                    'flop_n_mw': (0.674, 0.261, 0.065),
                    'flop_x_hu': (0.571, 0.429, 0.0),
                    'flop_x_mw': (0.861, 0.139, 0.0),
                    'flop_ms_hu': (0.824, 0.176, 0.0),
                    'flop_ms_mw': (0.946, 0.054, 0.0),
                },
                'no_xr': True,
            },
            'turn': {
                'nx': {
                    'all': (0.44, 0.453, 0.108),
                    '<40%': (0.117, 0.683, 0.2),
                    '40-75%': (0.351, 0.536, 0.112),
                    '75-110%': (0.759, 0.179, 0.062),
                    'overbet': (0.67, 0.309, 0.022),
                },
                'xr': {
                    'all': (0.52, 0.477, 0.003),
                    '<40%': (0.226, 0.772, 0.002),
                    '40-75%': (0.394, 0.605, 0.001),
                    '75-110%': (0.833, 0.166, 0.0),
                    'overbet': (0.873, 0.126, 0.001),
                },
                'cells': {
                    'turn_b2_n_hu': (0.2, 0.717, 0.082),
                    'turn_b2_n_mw': (0.341, 0.579, 0.079),
                    'turn_b2_x_hu': (0.13, 0.87, 0.0),
                    'turn_b2_x_mw': (0.43, 0.571, 0.0),
                    'turn_n_hu': (0.258, 0.433, 0.309),
                    'turn_n_mw': (0.747, 0.192, 0.061),
                    'turn_x_hu': (0.501, 0.499, 0.0),
                    'turn_x_mw': (0.776, 0.224, 0.0),
                    'turn_ms_hu': (0.369, 0.631, 0.0),
                    'turn_ms_mw': (0.617, 0.383, 0.0),
                },
                'no_xr': True,
            },
            'river': {
                'nx': {
                    'all': (0.401, 0.502, 0.096),
                    '<40%': (0.096, 0.867, 0.037),
                    '40-75%': (0.414, 0.434, 0.153),
                    '75-110%': (0.69, 0.259, 0.051),
                    'overbet': (0.809, 0.171, 0.02),
                },
                'xr': {
                    'all': (0.675, 0.316, 0.009),
                    '<40%': (0.415, 0.575, 0.011),
                    '40-75%': (0.598, 0.399, 0.004),
                    '75-110%': (0.89, 0.109, 0.002),
                    'overbet': (0.954, 0.045, 0.001),
                },
                'cells': {
                    'river_b3_n_hu': (0.207, 0.628, 0.165),
                    'river_b3_n_mw': (0.842, 0.126, 0.032),
                    'river_b3_x_hu': (0.365, 0.634, 0.0),
                    'river_b3_x_mw': (0.923, 0.077, 0.0),
                    'river_ct_n_hu': (0.716, 0.229, 0.054),
                    'river_ct_n_mw': (0.944, 0.009, 0.047),
                    'river_ct_x_hu': (0.729, 0.271, 0.0),
                    'river_ct_x_mw': (0.987, 0.013, 0.0),
                    'river_n_hu': (0.422, 0.573, 0.006),
                    'river_n_mw': (0.914, 0.082, 0.003),
                    'river_x_hu': (0.606, 0.394, 0.0),
                    'river_x_mw': (0.972, 0.028, 0.0),
                    'river_ms_hu': (0.8, 0.201, 0.0),
                    'river_ms_mw': (0.885, 0.115, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 1.1, 'draw': 0.1, 'weak': 1.1, 'medium': 7.4, 'value': 9.4},
            'turn': {'air': 0.1, 'draw': 0.2, 'weak': 0.2, 'medium': 3.7, 'value': 8.8},
            'river': {'air': 0.1, 'weak': 2.1, 'medium': 3.4, 'value': 8.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {'*': [(0.85, 1.0)]},
            'turn': {'*': [(0.85, 1.0)]},
            'river': {
                '*': [(0.75, 0.593), (ALLIN, 0.407)],
                'value': [(0.75, 0.1), (ALLIN, 0.9)],
                'medium': [(0.75, 0.1), (ALLIN, 0.9)],
            },
        },
    )
