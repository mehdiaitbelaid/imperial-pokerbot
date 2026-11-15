"""Replica of matcha mille crêpes cake (likely finalist) for the final-table sparring games.

matcha mille crêpes cake. Measured on 8 rounds, 8000 hands (r002, r008, r010, r011, r014, r031,
r036, r043); latest third: r036, r043. VPIP 20, PFR 13, 3-bet 6; opens 2.5bb 70%, 2.25bb 14%.
Bet sizes (share of pot): flop 0.34/0.5/0.6/0.7/0.75/0.9, turn 0.34/0.5/0.6/0.7/0.75/0.9, river
0.34/0.5/0.6/0.7/0.75/0.9/1/all-in.

Parameters written by tabled/build_g.py from the team's real hands (same definitions as
docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import base as _base  # noqa: E402
from base import ALLIN, Base  # noqa: E402,F401

try:                                    # this replica's frozen node class mixes
    from _nodes_g import NODES as _NF
    _base._NODES.setdefault('f_matcha', _NF.get('f_matcha', {}))
except Exception:
    pass


class Agent(Base):
    NAME = 'f_matcha'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.122, 0.0),
            'UTG+1': (0.103, 0.0),
            'MP': (0.106, 0.031),
            'HJ': (0.158, 0.012),
            'CO': (0.296, 0.0),
            'BTN': (0.47, 0.0),
            'SB': (0.571, 0.054),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={
            '*': [(2.5, 1.0)],
            'MP': [(2.5, 0.859), (2.25, 0.087), (3.5, 0.054)],
            'HJ': [(2.5, 0.779), (2.25, 0.158), (3.5, 0.063)],
            'CO': [(2.5, 0.698), (2.25, 0.202), (3.5, 0.101)],
            'BTN': [(2.5, 0.538), (2.25, 0.311), (3.5, 0.152)],
            'SB': [(3.0, 0.422), (2.0, 0.359), (3.5, 0.219)],
        },
        # facing limpers: (call, raise)
        vs_limp=(0.059, 0.348),
        bb_iso=0.111,
        iso=(2.5, 1.0),
        limp_fold=0.69,
        limp_rr=0.034,
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.078, 0.082), 'm': (0.107, 0.088), 'l': (0.082, 0.2)},
            'BB': {'s': (0.247, 0.158), 'm': (0.227, 0.084), 'l': (0.314, 0.087)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.172, 0.054), 'SB': (0.185, 0.091), 'BB': (0.176, 0.068)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.131, 0.052),
            'UTG+1': (0.12, 0.049),
            'MP': (0.106, 0.05),
            'HJ': (0.114, 0.061),
            'CO': (0.146, 0.044),
            'BTN': (0.142, 0.055),
            'SB': (0.098, 0.061),
            'BB': (0.123, 0.025),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.628, 0.826), (0.214, 0.02)),
        tb_rand=0.1,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={
            'ip': [((3.0, 0.0), 0.346), ((3.6, 0.0), 0.288), ((36.36, 0.0), 0.26)],
            'oop': [((3.6, 0.0), 0.652), ((3.33, 0.0), 0.081), ((3.2, 0.0), 0.081)],
        },
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.527, 0.237, 0.237),
        fb_rand=0.49,
        fourbet=[(2.11, 0.071), ('allin', 0.929)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.038, 0.028),
        cold_rand=0.0,
        call_then_3b=0.148,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.248, 0.235, 0.516),
        f4b_shove=0.293,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.214, 0.743, 0.043),
        shove_max=1.0,
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.916,
                'D_hu': 0.83,
                'S_hu': 0.692,
                'L_hu': 0.627,
                'A_mw': 0.453,
                'D_mw': 0.186,
                'S_mw': 0.211,
                'L_mw': 0.293,
            },
            'turn': {
                'A_hu': 0.771,
                'D_hu': 0.511,
                'S_hu': 0.504,
                'L_hu': 0.412,
                'A_mw': 0.321,
                'D_mw': 0.148,
                'S_mw': 0.143,
                'L_mw': 0.114,
            },
            'river': {
                'A_hu': 0.759,
                'D_hu': 0.478,
                'S_hu': 0.64,
                'L_hu': 0.365,
                'A_mw': 0.354,
                'D_mw': 0.211,
                'S_mw': 0.281,
                'L_mw': 0.124,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.34: {'air': 2.06, 'draw': 3.03, 'weak': 3.04, 'medium': 1.2, 'value': 0.08},
                    0.5: {'air': 5.06, 'draw': 1.03, 'weak': 1.04, 'medium': 7.2, 'value': 3.08},
                    0.6: {'air': 0.06, 'draw': 0.03, 'weak': 1.04, 'medium': 12.2, 'value': 1.08},
                    0.7: {'air': 1.06, 'draw': 0.03, 'weak': 1.04, 'medium': 5.2, 'value': 0.08},
                    0.75: {'air': 0.06, 'draw': 0.03, 'weak': 0.04, 'medium': 3.2, 'value': 3.08},
                    0.9: {'air': 0.06, 'draw': 0.03, 'weak': 0.04, 'medium': 1.2, 'value': 4.08},
                },
                'share': {
                    'A_hu': {0.34: 0.21, 0.5: 0.315, 0.6: 0.145, 0.7: 0.121, 0.75: 0.113, 0.9: 0.097},
                    'A_mw': {0.5: 0.4, 0.6: 0.2, 0.7: 0.367, 0.9: 0.033},
                    'D_hu': {0.34: 0.389, 0.5: 0.3, 0.6: 0.1, 0.7: 0.133, 0.75: 0.044, 0.9: 0.033},
                    'D_mw': {0.5: 0.062, 0.6: 0.688, 0.7: 0.125, 0.9: 0.125},
                    'S_hu': {0.34: 0.217, 0.5: 0.348, 0.6: 0.174, 0.7: 0.043, 0.75: 0.043, 0.9: 0.174},
                    'S_mw': {0.5: 0.5, 0.6: 0.214, 0.7: 0.071, 0.75: 0.071, 0.9: 0.143},
                    'L_hu': {0.34: 0.333, 0.5: 0.333, 0.6: 0.122, 0.7: 0.106, 0.75: 0.049, 0.9: 0.057},
                    'L_mw': {0.5: 0.258, 0.6: 0.484, 0.7: 0.097, 0.75: 0.032, 0.9: 0.129},
                },
            },
            'turn': {
                'sizes': {
                    0.34: {'air': 2.04, 'draw': 1.02, 'weak': 3.08, 'medium': 1.17, 'value': 1.09},
                    0.5: {'air': 3.04, 'draw': 2.02, 'weak': 5.08, 'medium': 3.17, 'value': 5.09},
                    0.6: {'air': 0.04, 'draw': 0.02, 'weak': 1.08, 'medium': 9.17, 'value': 1.09},
                    0.7: {'air': 0.04, 'draw': 0.02, 'weak': 2.08, 'medium': 6.17, 'value': 1.09},
                    0.75: {'air': 0.04, 'draw': 0.02, 'weak': 0.08, 'medium': 3.17, 'value': 2.09},
                    0.9: {'air': 0.04, 'draw': 0.02, 'weak': 0.08, 'medium': 1.17, 'value': 2.09},
                },
                'share': {
                    'A_hu': {0.34: 0.242, 0.5: 0.263, 0.6: 0.101, 0.7: 0.192, 0.75: 0.141, 0.9: 0.061},
                    'A_mw': {0.5: 0.533, 0.6: 0.133, 0.7: 0.333},
                    'D_hu': {0.34: 0.179, 0.5: 0.357, 0.6: 0.143, 0.7: 0.107, 0.75: 0.071, 0.9: 0.143},
                    'D_mw': {0.5: 0.533, 0.6: 0.133, 0.7: 0.333},
                    'S_hu': {0.34: 0.276, 0.5: 0.31, 0.6: 0.103, 0.7: 0.069, 0.75: 0.103, 0.9: 0.138},
                    'S_mw': {0.5: 0.533, 0.6: 0.133, 0.7: 0.333},
                    'L_hu': {0.34: 0.203, 0.5: 0.359, 0.6: 0.141, 0.7: 0.078, 0.75: 0.094, 0.9: 0.125},
                    'L_mw': {0.5: 0.533, 0.6: 0.133, 0.7: 0.333},
                },
            },
            'river': {
                'sizes': {
                    0.34: {'air': 3.05, 'weak': 2.09, 'medium': 0.11, 'value': 0.14},
                    0.5: {'air': 0.05, 'weak': 6.09, 'medium': 1.11, 'value': 5.14},
                    0.6: {'air': 1.05, 'weak': 1.09, 'medium': 3.11, 'value': 3.14},
                    0.7: {'air': 0.05, 'weak': 1.09, 'medium': 4.11, 'value': 2.14},
                    0.75: {'air': 1.05, 'weak': 0.09, 'medium': 1.11, 'value': 2.14},
                    0.9: {'air': 0.05, 'weak': 0.09, 'medium': 0.11, 'value': 1.14},
                    1.0: {'air': 1.05, 'weak': 1.09, 'medium': 0.11, 'value': 0.14},
                    ALLIN: {'air': 0.05, 'weak': 0.09, 'medium': 4.11, 'value': 4.14},
                },
                'share': {
                    'A_hu': {0.34: 0.298, 0.5: 0.14, 0.6: 0.088, 0.7: 0.14, 0.75: 0.07, 0.9: 0.07, 1.0: 0.018, ALLIN: 0.175},
                    'A_mw': {0.5: 0.267, 0.6: 0.2, 0.7: 0.067, 0.9: 0.2, 1.0: 0.267},
                    'D_hu': {0.5: 0.231, 0.6: 0.308, 0.7: 0.154, 0.75: 0.077, ALLIN: 0.231},
                    'D_mw': {0.5: 0.267, 0.6: 0.2, 0.7: 0.067, 0.9: 0.2, 1.0: 0.267},
                    'S_hu': {
                        0.34: 0.118,
                        0.5: 0.412,
                        0.6: 0.088,
                        0.7: 0.088,
                        0.75: 0.059,
                        0.9: 0.059,
                        1.0: 0.147,
                        ALLIN: 0.029,
                    },
                    'S_mw': {0.5: 0.286, 0.6: 0.214, 0.9: 0.214, 1.0: 0.286},
                    'L_hu': {
                        0.34: 0.093,
                        0.5: 0.352,
                        0.6: 0.185,
                        0.7: 0.093,
                        0.75: 0.074,
                        0.9: 0.037,
                        1.0: 0.093,
                        ALLIN: 0.074,
                    },
                    'L_mw': {0.5: 0.267, 0.6: 0.2, 0.7: 0.067, 0.9: 0.2, 1.0: 0.267},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.434, 0.491, 0.075),
            0.34: (0.749, 0.233, 0.018),
            0.5: (0.716, 0.264, 0.02),
            0.6: (0.108, 0.873, 0.019),
            0.7: (0.467, 0.495, 0.038),
            0.75: (0.217, 0.62, 0.163),
            0.9: (0.174, 0.596, 0.23),
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.406, 0.492, 0.102),
                    '<40%': (0.22, 0.687, 0.093),
                    '40-75%': (0.367, 0.499, 0.133),
                    '75-110%': (0.534, 0.393, 0.072),
                    'overbet': (0.641, 0.335, 0.024),
                },
                'xr': {
                    'all': (0.577, 0.361, 0.062),
                    '<40%': (0.495, 0.387, 0.118),
                    '40-75%': (0.511, 0.446, 0.043),
                    '75-110%': (0.649, 0.299, 0.052),
                    'overbet': (0.836, 0.148, 0.016),
                },
                'cells': {
                    'flop_n_hu': (0.343, 0.551, 0.106),
                    'flop_n_mw': (0.564, 0.346, 0.09),
                    'flop_x_hu': (0.565, 0.407, 0.029),
                    'flop_x_mw': (0.726, 0.271, 0.003),
                    'flop_ms_hu': (0.489, 0.324, 0.187),
                    'flop_ms_mw': (0.555, 0.384, 0.061),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.374, 0.516, 0.11),
                    '<40%': (0.185, 0.765, 0.05),
                    '40-75%': (0.318, 0.558, 0.124),
                    '75-110%': (0.506, 0.353, 0.141),
                    'overbet': (0.755, 0.22, 0.024),
                },
                'xr': {
                    'all': (0.567, 0.374, 0.059),
                    '<40%': (0.556, 0.408, 0.036),
                    '40-75%': (0.456, 0.471, 0.073),
                    '75-110%': (0.646, 0.293, 0.061),
                    'overbet': (0.882, 0.102, 0.016),
                },
                'cells': {
                    'turn_b2_n_hu': (0.332, 0.551, 0.118),
                    'turn_b2_n_mw': (0.685, 0.259, 0.055),
                    'turn_b2_x_hu': (0.434, 0.526, 0.04),
                    'turn_b2_x_mw': (0.731, 0.246, 0.022),
                    'turn_n_hu': (0.315, 0.532, 0.153),
                    'turn_n_mw': (0.659, 0.328, 0.014),
                    'turn_x_hu': (0.639, 0.345, 0.016),
                    'turn_x_mw': (0.729, 0.265, 0.006),
                    'turn_ms_hu': (0.589, 0.283, 0.129),
                    'turn_ms_mw': (0.816, 0.135, 0.05),
                },
                'no_xr': False,
            },
            'river': {
                'nx': {
                    'all': (0.349, 0.566, 0.086),
                    '<40%': (0.138, 0.757, 0.105),
                    '40-75%': (0.318, 0.588, 0.094),
                    '75-110%': (0.522, 0.411, 0.067),
                    'overbet': (0.682, 0.286, 0.032),
                },
                'xr': {
                    'all': (0.556, 0.435, 0.009),
                    '<40%': (0.404, 0.589, 0.007),
                    '40-75%': (0.48, 0.515, 0.004),
                    '75-110%': (0.793, 0.203, 0.003),
                    'overbet': (0.852, 0.145, 0.003),
                },
                'cells': {
                    'river_b3_n_hu': (0.351, 0.562, 0.088),
                    'river_b3_n_mw': (0.351, 0.562, 0.087),
                    'river_b3_x_hu': (0.344, 0.656, 0.0),
                    'river_b3_x_mw': (0.42, 0.58, 0.0),
                    'river_ct_n_hu': (0.561, 0.395, 0.044),
                    'river_ct_n_mw': (0.643, 0.262, 0.095),
                    'river_ct_x_hu': (0.829, 0.172, 0.0),
                    'river_ct_x_mw': (0.852, 0.148, 0.0),
                    'river_n_hu': (0.177, 0.725, 0.099),
                    'river_n_mw': (0.188, 0.726, 0.086),
                    'river_x_hu': (0.42, 0.58, 0.0),
                    'river_x_mw': (0.472, 0.528, 0.0),
                    'river_ms_hu': (0.566, 0.434, 0.0),
                    'river_ms_mw': (0.562, 0.437, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 0.1, 'draw': 0.1, 'weak': 1.1, 'medium': 7.4, 'value': 12.4},
            'turn': {'draw': 0.1, 'weak': 2.1, 'medium': 7.2, 'value': 13.6},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 1.4, 'value': 4.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {
                '*': [(0.8, 0.433), (0.5, 0.385), (1.0, 0.144), (ALLIN, 0.039)],
                'value': [(0.8, 0.394), (0.5, 0.351), (1.0, 0.131), (ALLIN, 0.124)],
                'medium': [(0.8, 0.394), (0.5, 0.351), (1.0, 0.131), (ALLIN, 0.124)],
            },
            'turn': {
                '*': [(0.8, 0.451), (0.5, 0.193), (1.15, 0.129), (1.0, 0.129), (ALLIN, 0.098)],
                'value': [(0.8, 0.344), (0.5, 0.147), (1.15, 0.098), (1.0, 0.098), (ALLIN, 0.313)],
                'medium': [(0.8, 0.344), (0.5, 0.147), (1.15, 0.098), (1.0, 0.098), (ALLIN, 0.313)],
            },
            'river': {'*': [(0.75, 1.0)]},
        },
    )
