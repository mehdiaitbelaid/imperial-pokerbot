"""Replica of WBot for the Table D sparring table.

WBot: opens 2.8bb (3.3 from the small blind) or 3.5bb (4.0), one size per round; bets almost
every time it can: 0.15 pot on most turns and rivers, 3.0 pot or all-in with two pair or better;
raises a quarter of the bets it faces (pot size raises are bluff heavy, 2x pot raises are
value); folds 79% when a 0.15 bet is raised; defends its blinds.

Parameters written by tabled/build.py from the team's real hands (same definitions as
docs/table-d-raw-profiles.txt); every key is explained in tabled/base.py (DEFAULTS).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from base import ALLIN, Base  # noqa: E402,F401


class Agent(Base):
    NAME = 'wbot'
    P = dict(
        # first in, by position: (raise, limp)
        fi={
            'UTG': (0.231, 0.0),
            'UTG+1': (0.263, 0.0),
            'MP': (0.296, 0.0),
            'HJ': (0.383, 0.0),
            'CO': (0.532, 0.0),
            'BTN': (0.826, 0.0),
            'SB': (0.543, 0.0),
        },
        # open sizes in big blinds: [(size, weight)]
        open_bb={'*': [(2.8, 1.0)], 'SB': [(3.3, 1.0)]},
        variants=[(0.6, {'open_bb': {'*': [(2.8, 1.0)], 'SB': [(3.3, 1.0)]}}), (0.4, {'open_bb': {'*': [(3.5, 1.0)], 'SB': [(4.0, 1.0)]}})],
        # facing limpers: (call, raise)
        vs_limp=(0.0, 0.523),
        bb_iso=0.082,
        iso=('open', 1.0),
        # blinds against a CO / BTN / SB open of <=2.25bb (s), <=3bb (m), more (l), no caller: (call, 3-bet)
        bd={
            'SB': {'s': (0.327, 0.082), 'm': (0.23, 0.063), 'l': (0.317, 0.08)},
            'BB': {'s': (0.889, 0.095), 'm': (0.683, 0.054), 'l': (0.46, 0.065)},
        },
        # one raise and at least one caller: (call, 3-bet)
        sq={'IP': (0.092, 0.0), 'SB': (0.087, 0.0), 'BB': (0.131, 0.006)},
        # any other single raise, by own position (IP = other seats outside the blinds): (call, 3-bet)
        vs1={
            'IP': (0.201, 0.058),
            'UTG+1': (0.296, 0.054),
            'MP': (0.17, 0.071),
            'HJ': (0.186, 0.05),
            'CO': (0.19, 0.054),
            'BTN': (0.213, 0.064),
            'SB': (0.199, 0.027),
            'BB': (0.563, 0.078),
        },
        # (call, 3-bet) multipliers against opens of 4-7bb and of more than 7bb
        big_open=((0.526, 0.207), (0.181, 0.296)),
        tb_rand=0.1,
        # 3-bet size: (multiple of the raise, plus big blinds)
        tb_mult={'ip': [((3.0, 0.75), 1.0)], 'oop': [((3.5, 0.5), 0.5), ((3.5, 0.75), 0.5)]},
        # opened and was 3-bet: (fold, call, 4-bet)
        f3b=(0.535, 0.42, 0.045),
        fourbet=[('allin', 1.0)],
        # 3-bet in front, not yet in the pot: (call, 4-bet)
        cold3=(0.062, 0.015),
        call_then_3b=0.333,
        # 3-bet and was 4-bet, not all-in: (fold, call, 5-bet); f4b_shove: fold to a 4-bet shove
        f4b=(0.063, 0.597, 0.34),
        f4b_shove=0.389,
        fivebet=[('allin', 1.0)],
        # 4-bet and was raised again: (fold, call, raise)
        f5b=(0.25, 0.7, 0.05),
        # bet frequency: A c-bet or barrel, D donk, S checked to, L lead; heads up / multiway
        betf={
            'flop': {
                'A_hu': 0.993,
                'D_hu': 0.979,
                'S_hu': 0.999,
                'L_hu': 0.998,
                'A_mw': 0.962,
                'D_mw': 0.937,
                'S_mw': 0.909,
                'L_mw': 0.902,
            },
            'turn': {
                'A_hu': 0.952,
                'D_hu': 0.938,
                'S_hu': 0.995,
                'L_hu': 0.634,
                'A_mw': 0.662,
                'D_mw': 0.611,
                'S_mw': 0.417,
                'L_mw': 0.583,
            },
            'river': {
                'A_hu': 0.864,
                'D_hu': 0.905,
                'S_hu': 0.804,
                'L_hu': 0.436,
                'A_mw': 0.509,
                'D_mw': 0.367,
                'S_mw': 0.221,
                'L_mw': 0.314,
            },
        },
        # per street: hands shown down after each bet size, and each line's size shares
        J={
            'flop': {
                'sizes': {
                    0.15: {'air': 112.17, 'draw': 22.05, 'weak': 42.09, 'medium': 10.07, 'value': 1.01},
                    0.33: {'air': 14.17, 'draw': 3.05, 'weak': 9.09, 'medium': 12.07, 'value': 0.01},
                    0.4: {'air': 19.17, 'draw': 8.05, 'weak': 20.09, 'medium': 7.07, 'value': 0.01},
                    0.6: {'air': 21.17, 'draw': 4.05, 'weak': 8.09, 'medium': 8.07, 'value': 0.01},
                    0.75: {'air': 3.17, 'draw': 9.05, 'weak': 12.09, 'medium': 17.07, 'value': 7.01},
                    1.0: {'air': 15.17, 'draw': 10.05, 'weak': 5.09, 'medium': 12.07, 'value': 6.01},
                    ALLIN: {'air': 1.17, 'draw': 1.05, 'weak': 0.09, 'medium': 6.07, 'value': 1.01},
                },
                'share': {
                    'A_hu': {0.15: 0.29, 0.33: 0.056, 0.4: 0.131, 0.6: 0.056, 0.75: 0.355, 1.0: 0.093, ALLIN: 0.019},
                    'A_mw': {0.15: 0.456, 0.33: 0.039, 0.4: 0.097, 0.6: 0.078, 0.75: 0.262, 1.0: 0.068},
                    'D_hu': {0.15: 0.495, 0.33: 0.077, 0.4: 0.107, 0.6: 0.085, 0.75: 0.087, 1.0: 0.134, ALLIN: 0.016},
                    'D_mw': {0.15: 0.446, 0.33: 0.068, 0.4: 0.122, 0.6: 0.081, 0.75: 0.149, 1.0: 0.108, ALLIN: 0.027},
                    'S_hu': {0.15: 0.373, 0.33: 0.072, 0.4: 0.06, 0.6: 0.145, 0.75: 0.096, 1.0: 0.217, ALLIN: 0.036},
                    'S_mw': {0.15: 0.426, 0.33: 0.088, 0.4: 0.088, 0.6: 0.074, 0.75: 0.147, 1.0: 0.162, ALLIN: 0.015},
                    'L_hu': {0.4: 0.536, 0.6: 0.071, 0.75: 0.286, 1.0: 0.107},
                    'L_mw': {0.15: 0.45, 0.33: 0.074, 0.4: 0.101, 0.6: 0.081, 0.75: 0.141, 1.0: 0.134, ALLIN: 0.02},
                },
            },
            'turn': {
                'sizes': {
                    0.15: {'air': 108.11, 'draw': 64.07, 'weak': 107.12, 'medium': 34.07, 'value': 2.03},
                    0.33: {'air': 1.11, 'draw': 3.07, 'weak': 4.12, 'medium': 5.07, 'value': 0.03},
                    0.4: {'air': 0.11, 'draw': 0.07, 'weak': 3.12, 'medium': 5.07, 'value': 1.03},
                    0.6: {'air': 0.11, 'draw': 2.07, 'weak': 4.12, 'medium': 6.07, 'value': 0.03},
                    0.75: {'air': 0.11, 'draw': 0.07, 'weak': 3.12, 'medium': 1.07, 'value': 5.03},
                    1.0: {'air': 1.11, 'draw': 2.07, 'weak': 0.12, 'medium': 3.07, 'value': 4.03},
                    ALLIN: {'air': 2.11, 'draw': 0.07, 'weak': 1.12, 'medium': 11.07, 'value': 17.03},
                },
                'share': {
                    'A_hu': {0.15: 0.753, 0.33: 0.036, 0.4: 0.019, 0.6: 0.026, 0.75: 0.04, 1.0: 0.033, ALLIN: 0.093},
                    'A_mw': {0.15: 0.85, 0.4: 0.025, 1.0: 0.025, ALLIN: 0.1},
                    'D_hu': {0.15: 0.75, 0.33: 0.023, 0.4: 0.068, ALLIN: 0.159},
                    'D_mw': {0.15: 0.864, 0.4: 0.023, 1.0: 0.023, ALLIN: 0.091},
                    'S_hu': {0.15: 0.846, 0.33: 0.019, 0.6: 0.038, 0.75: 0.019, 1.0: 0.058, ALLIN: 0.019},
                    'S_mw': {0.15: 0.864, 0.4: 0.023, 1.0: 0.023, ALLIN: 0.091},
                    'L_hu': {0.15: 0.811, 0.33: 0.021, 0.4: 0.032, 0.6: 0.021, 1.0: 0.032, ALLIN: 0.084},
                    'L_mw': {0.15: 0.864, 0.4: 0.023, 1.0: 0.023, ALLIN: 0.091},
                },
            },
            'river': {
                'sizes': {
                    0.15: {'air': 125.16, 'weak': 113.14, 'medium': 37.06, 'value': 7.04},
                    0.33: {'air': 0.16, 'weak': 0.14, 'medium': 3.06, 'value': 1.04},
                    0.6: {'air': 1.16, 'weak': 0.14, 'medium': 1.06, 'value': 0.04},
                    0.75: {'air': 0.16, 'weak': 0.14, 'medium': 0.06, 'value': 0.04},
                    3.0: {'air': 0.16, 'weak': 0.14, 'medium': 0.06, 'value': 8.04},
                    ALLIN: {'air': 2.16, 'weak': 1.14, 'medium': 3.06, 'value': 16.04},
                },
                'share': {
                    'A_hu': {0.15: 0.852, 0.33: 0.013, 3.0: 0.054, ALLIN: 0.082},
                    'A_mw': {0.15: 0.856, 3.0: 0.051, ALLIN: 0.093},
                    'D_hu': {0.15: 0.769, ALLIN: 0.231},
                    'D_mw': {0.15: 0.856, 3.0: 0.051, ALLIN: 0.093},
                    'S_hu': {0.15: 0.789, 3.0: 0.053, ALLIN: 0.158},
                    'S_mw': {0.15: 0.856, 3.0: 0.051, ALLIN: 0.093},
                    'L_hu': {0.15: 0.788, 3.0: 0.03, ALLIN: 0.182},
                    'L_mw': {0.15: 0.856, 3.0: 0.051, ALLIN: 0.093},
                },
            },
        },
        # raised after betting this size: (fold, call, re-raise)
        raised={
            'default': (0.617, 0.267, 0.116),
            0.15: {
                '*': (0.802, 0.179, 0.018),
                'flop': (0.857, 0.142, 0.001),
                'turn': (0.723, 0.234, 0.043),
                'river': (0.838, 0.159, 0.003),
            },
            0.33: {'*': (0.586, 0.351, 0.064), 'flop': (0.588, 0.352, 0.06)},
            0.4: {'*': (0.406, 0.467, 0.127), 'flop': (0.415, 0.448, 0.137)},
            0.6: {'*': (0.393, 0.319, 0.288), 'flop': (0.368, 0.296, 0.336)},
            0.75: {'*': (0.216, 0.436, 0.349), 'flop': (0.171, 0.439, 0.39)},
            1.0: {'*': (0.364, 0.195, 0.441), 'flop': (0.353, 0.16, 0.486)},
        },
        # facing a bet: (fold, call, raise) overall, by size of the bet, and by node (see base.post_ctx)
        face={
            'flop': {
                'nx': {
                    'all': (0.44, 0.244, 0.316),
                    '<40%': (0.292, 0.363, 0.345),
                    '40-75%': (0.43, 0.243, 0.327),
                    '75-110%': (0.547, 0.188, 0.265),
                    'overbet': (0.412, 0.157, 0.432),
                },
                'xr': {
                    'all': (0.568, 0.066, 0.366),
                    '<40%': (0.367, 0.083, 0.549),
                    '40-75%': (0.557, 0.036, 0.407),
                    '75-110%': (0.749, 0.039, 0.212),
                    'overbet': (0.581, 0.064, 0.355),
                },
                'cells': {
                    'flop_n_hu': (0.416, 0.275, 0.309),
                    'flop_n_mw': (0.527, 0.135, 0.338),
                    'flop_x_hu': (0.616, 0.02, 0.364),
                    'flop_x_mw': (0.763, 0.021, 0.215),
                    'flop_ms_hu': (0.406, 0.045, 0.549),
                    'flop_ms_mw': (0.642, 0.038, 0.32),
                },
                'no_xr': False,
            },
            'turn': {
                'nx': {
                    'all': (0.418, 0.349, 0.232),
                    '<40%': (0.26, 0.526, 0.214),
                    '40-75%': (0.395, 0.324, 0.281),
                    '75-110%': (0.69, 0.186, 0.124),
                    'overbet': (0.527, 0.297, 0.177),
                },
                'xr': {
                    'all': (0.629, 0.096, 0.276),
                    '<40%': (0.465, 0.173, 0.362),
                    '40-75%': (0.616, 0.032, 0.351),
                    '75-110%': (0.827, 0.091, 0.082),
                    'overbet': (0.76, 0.062, 0.178),
                },
                'cells': {
                    'turn_b2_n_hu': (0.423, 0.418, 0.159),
                    'turn_b2_n_mw': (0.884, 0.1, 0.016),
                    'turn_b2_x_hu': (0.557, 0.114, 0.328),
                    'turn_b2_x_mw': (0.95, 0.013, 0.037),
                    'turn_n_hu': (0.3, 0.345, 0.355),
                    'turn_n_mw': (0.871, 0.065, 0.064),
                    'turn_x_hu': (0.295, 0.052, 0.653),
                    'turn_x_mw': (0.922, 0.01, 0.068),
                    'turn_ms_hu': (0.637, 0.103, 0.261),
                    'turn_ms_mw': (0.981, 0.005, 0.014),
                },
                'no_xr': False,
            },
            'river': {
                'nx': {
                    'all': (0.527, 0.339, 0.133),
                    '<40%': (0.345, 0.556, 0.099),
                    '40-75%': (0.498, 0.327, 0.175),
                    '75-110%': (0.629, 0.225, 0.146),
                    'overbet': (0.771, 0.164, 0.064),
                },
                'xr': {
                    'all': (0.943, 0.048, 0.01),
                    '<40%': (0.817, 0.164, 0.019),
                    '40-75%': (0.979, 0.017, 0.004),
                    '75-110%': (0.981, 0.016, 0.003),
                    'overbet': (0.975, 0.02, 0.004),
                },
                'cells': {
                    'river_b3_n_hu': (0.341, 0.55, 0.109),
                    'river_b3_n_mw': (0.389, 0.496, 0.115),
                    'river_b3_x_hu': (0.937, 0.063, 0.0),
                    'river_b3_x_mw': (0.943, 0.058, 0.0),
                    'river_ct_n_hu': (0.655, 0.205, 0.141),
                    'river_ct_n_mw': (0.695, 0.141, 0.164),
                    'river_ct_x_hu': (0.965, 0.035, 0.0),
                    'river_ct_x_mw': (0.971, 0.029, 0.0),
                    'river_n_hu': (0.549, 0.297, 0.154),
                    'river_n_mw': (0.566, 0.339, 0.094),
                    'river_x_hu': (0.953, 0.047, 0.0),
                    'river_x_mw': (0.948, 0.052, 0.0),
                    'river_ms_hu': (0.968, 0.033, 0.0),
                    'river_ms_mw': (0.973, 0.027, 0.0),
                },
                'no_xr': True,
            },
        },
        # hands shown down after its raises
        raise_comp={
            'flop': {'air': 23.1, 'draw': 23.1, 'weak': 16.1, 'medium': 35.4, 'value': 14.4},
            'turn': {'air': 1.0, 'draw': 7.1, 'weak': 5.1, 'medium': 8.2, 'value': 14.6},
            'river': {'air': 0.1, 'weak': 0.1, 'medium': 1.4, 'value': 7.4},
        },
        # raise sizes as a share of the pot after calling
        rsize={
            'flop': {'value': [(2.0, 0.6), (1.0, 0.4)], 'medium': [(2.0, 0.45), (1.0, 0.55)], '*': [(1.0, 0.88), (2.0, 0.12)]},
            'turn': {'value': [(ALLIN, 0.6), (1.0, 0.2), (2.0, 0.2)], '*': [(1.0, 0.45), (2.0, 0.15), (ALLIN, 0.4)]},
            'river': {'*': [(ALLIN, 0.6), (1.0, 0.2), (2.0, 0.2)]},
        },
    )
