"""Counted-round profile of pokermon (R1-R11, 3000 hands, +0.4 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.28, 'pfr': 0.18, 'limp': 0.01, 'three_bet': 0.05, 'fold_to_3bet': 0.44, 'open_size_bb': 3.0, 'cbet': 0.62, 'bet': 0.56, 'bet_size': 0.5, 'fold_to_bet': 0.71, 'raise_vs_bet': 0.08, 'air': 0.19}
