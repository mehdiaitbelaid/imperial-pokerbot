"""Counted-round profile of AIl IN (R1-R11, 3000 hands, -21.4 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.22, 'pfr': 0.13, 'limp': 0.02, 'three_bet': 0.08, 'fold_to_3bet': 0.53, 'open_size_bb': 2.9, 'cbet': 0.66, 'bet': 0.41, 'bet_size': 0.59, 'fold_to_bet': 0.26, 'raise_vs_bet': 0.07, 'air': 0.22}
