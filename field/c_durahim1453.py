"""Counted-round profile of Durahim 1453 (R1-R11, 4000 hands, +7.3 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.24, 'pfr': 0.16, 'limp': 0.09, 'three_bet': 0.1, 'fold_to_3bet': 0.21, 'open_size_bb': 2.9, 'cbet': 0.6, 'bet': 0.52, 'bet_size': 0.66, 'fold_to_bet': 0.57, 'raise_vs_bet': 0.13, 'air': 0.21}
