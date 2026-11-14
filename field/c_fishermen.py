"""Counted-round profile of FisherMen (R1-R11, 1000 hands, -27.7 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.2, 'pfr': 0.12, 'limp': 0.0, 'three_bet': 0.03, 'fold_to_3bet': 0.65, 'open_size_bb': 2.6, 'cbet': 0.83, 'bet': 0.44, 'bet_size': 0.65, 'fold_to_bet': 0.55, 'raise_vs_bet': 0.09, 'air': 0.09}
