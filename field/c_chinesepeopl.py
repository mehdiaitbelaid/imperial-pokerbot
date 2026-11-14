"""Counted-round profile of Chinese people can fly (R1-R11, 1000 hands, -26.4 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.32, 'pfr': 0.24, 'limp': 0.0, 'three_bet': 0.05, 'fold_to_3bet': 0.8, 'open_size_bb': 2.6, 'cbet': 0.7, 'bet': 0.68, 'bet_size': 0.33, 'fold_to_bet': 0.54, 'raise_vs_bet': 0.04, 'air': 0.37}
