"""Counted-round profile of Attention Is All In (R1-R11, 4000 hands, +43.1 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.32, 'pfr': 0.26, 'limp': 0.0, 'three_bet': 0.12, 'fold_to_3bet': 0.7, 'open_size_bb': 2.5, 'cbet': 0.66, 'bet': 0.58, 'bet_size': 0.33, 'fold_to_bet': 0.61, 'raise_vs_bet': 0.09, 'air': 0.14}
