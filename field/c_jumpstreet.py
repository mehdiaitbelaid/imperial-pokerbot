"""Counted-round profile of Jump Street (R1-R11, 1000 hands, +7.5 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.16, 'pfr': 0.11, 'limp': 0.0, 'three_bet': 0.03, 'fold_to_3bet': 0.56, 'open_size_bb': 2.9, 'cbet': 0.55, 'bet': 0.41, 'bet_size': 0.66, 'fold_to_bet': 0.62, 'raise_vs_bet': 0.02, 'air': 0.12}
