"""Counted-round profile of test (R1-R11, 1000 hands, -25.4 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.12, 'pfr': 0.06, 'limp': 0.02, 'three_bet': 0.01, 'fold_to_3bet': 0.85, 'open_size_bb': 3.2, 'cbet': 0.0, 'bet': 0.3, 'bet_size': 0.63, 'fold_to_bet': 0.87, 'raise_vs_bet': 0.0, 'air': 0.15}
