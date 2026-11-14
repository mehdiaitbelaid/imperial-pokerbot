"""Counted-round profile of SARS (R1-R11, 1000 hands, -18.4 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.13, 'pfr': 0.09, 'limp': 0.01, 'three_bet': 0.02, 'fold_to_3bet': 0.7, 'open_size_bb': 3.0, 'cbet': 0.9, 'bet': 0.68, 'bet_size': 0.6, 'fold_to_bet': 0.45, 'raise_vs_bet': 0.17, 'air': 0.1}
