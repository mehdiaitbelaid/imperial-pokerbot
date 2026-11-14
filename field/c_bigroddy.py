"""Counted-round profile of bigRoddy (R1-R11, 2000 hands, +35.8 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.31, 'pfr': 0.22, 'limp': 0.26, 'three_bet': 0.17, 'fold_to_3bet': 0.57, 'open_size_bb': 6.0, 'cbet': 0.56, 'bet': 0.41, 'bet_size': 1.1, 'fold_to_bet': 0.56, 'raise_vs_bet': 0.14, 'air': 0.24}
