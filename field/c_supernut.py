"""Counted-round profile of supernut (R1-R11, 1000 hands, +22.8 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.14, 'pfr': 0.1, 'limp': 0.0, 'three_bet': 0.02, 'fold_to_3bet': 0.78, 'open_size_bb': 3.0, 'cbet': 0.58, 'bet': 0.42, 'bet_size': 1.0, 'fold_to_bet': 0.63, 'raise_vs_bet': 0.05, 'air': 0.0}
