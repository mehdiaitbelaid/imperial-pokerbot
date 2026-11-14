"""Counted-round profile of aydine (R1-R11, 2000 hands, +32.1 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.21, 'pfr': 0.13, 'limp': 0.0, 'three_bet': 0.03, 'fold_to_3bet': 0.49, 'open_size_bb': 3.5, 'cbet': 0.77, 'bet': 0.46, 'bet_size': 0.8, 'fold_to_bet': 0.42, 'raise_vs_bet': 0.12, 'air': 0.12}
