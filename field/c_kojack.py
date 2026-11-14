"""Counted-round profile of Kojack (R1-R11, 2000 hands, +83.9 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.2, 'pfr': 0.17, 'limp': 0.01, 'three_bet': 0.08, 'fold_to_3bet': 0.54, 'open_size_bb': 3.6, 'cbet': 0.65, 'bet': 0.43, 'bet_size': 0.55, 'fold_to_bet': 0.56, 'raise_vs_bet': 0.01, 'air': 0.17}
