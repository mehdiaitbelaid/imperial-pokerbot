"""Counted-round profile of Gherkers (R1-R11, 3000 hands, +46.6 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.29, 'pfr': 0.22, 'limp': 0.0, 'three_bet': 0.21, 'fold_to_3bet': 0.4, 'open_size_bb': 3.5, 'cbet': 0.76, 'bet': 0.55, 'bet_size': 0.7, 'fold_to_bet': 0.57, 'raise_vs_bet': 0.17, 'air': 0.22}
