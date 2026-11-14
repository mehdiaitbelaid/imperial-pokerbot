"""Counted-round profile of WBot (R1-R11, 2000 hands, +52.6 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.28, 'pfr': 0.22, 'limp': 0.0, 'three_bet': 0.04, 'fold_to_3bet': 0.62, 'open_size_bb': 3.7, 'cbet': 0.99, 'bet': 0.91, 'bet_size': 0.33, 'fold_to_bet': 0.45, 'raise_vs_bet': 0.3, 'air': 0.41}
