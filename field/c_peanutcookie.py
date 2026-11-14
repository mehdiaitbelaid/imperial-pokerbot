"""Counted-round profile of Peanut Cookies (R1-R11, 1000 hands, -7.6 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.18, 'pfr': 0.13, 'limp': 0.0, 'three_bet': 0.05, 'fold_to_3bet': 0.12, 'open_size_bb': 2.5, 'cbet': 0.31, 'bet': 0.37, 'bet_size': 0.7, 'fold_to_bet': 0.48, 'raise_vs_bet': 0.0, 'air': 0.5}
