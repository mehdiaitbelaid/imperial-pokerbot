"""Counted-round profile of Equity Engine (R1-R11, 3000 hands, +9.9 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.23, 'pfr': 0.17, 'limp': 0.0, 'three_bet': 0.02, 'fold_to_3bet': 0.49, 'open_size_bb': 3.7, 'cbet': 0.74, 'bet': 0.45, 'bet_size': 0.8, 'fold_to_bet': 0.5, 'raise_vs_bet': 0.15, 'air': 0.27}
