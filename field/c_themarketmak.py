"""Counted-round profile of The Market Makers (R1-R11, 3000 hands, -7.1 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.2, 'pfr': 0.12, 'limp': 0.0, 'three_bet': 0.04, 'fold_to_3bet': 0.4, 'open_size_bb': 2.5, 'cbet': 0.81, 'bet': 0.73, 'bet_size': 0.7, 'fold_to_bet': 0.48, 'raise_vs_bet': 0.05, 'air': 0.21}
