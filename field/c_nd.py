"""Counted-round profile of ND (R1-R11, 2000 hands, +9.6 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.2, 'pfr': 0.1, 'limp': 0.03, 'three_bet': 0.06, 'fold_to_3bet': 0.22, 'open_size_bb': 3.2, 'cbet': 0.73, 'bet': 0.39, 'bet_size': 0.75, 'fold_to_bet': 0.47, 'raise_vs_bet': 0.1, 'air': 0.11}
