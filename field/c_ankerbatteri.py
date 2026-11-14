"""Counted-round profile of Anker Batteries (R1-R11, 2000 hands, +2.1 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.23, 'pfr': 0.17, 'limp': 0.0, 'three_bet': 0.1, 'fold_to_3bet': 0.33, 'open_size_bb': 2.5, 'cbet': 0.8, 'bet': 0.51, 'bet_size': 0.7, 'fold_to_bet': 0.54, 'raise_vs_bet': 0.06, 'air': 0.0}
