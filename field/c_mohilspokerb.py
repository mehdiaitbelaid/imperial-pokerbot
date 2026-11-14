"""Counted-round profile of Mohil'sPokerBot (R1-R11, 1000 hands, +118.8 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.27, 'pfr': 0.1, 'limp': 0.07, 'three_bet': 0.08, 'fold_to_3bet': 0.17, 'open_size_bb': 3.2, 'cbet': 0.92, 'bet': 0.43, 'bet_size': 0.5, 'fold_to_bet': 0.44, 'raise_vs_bet': 0.16, 'air': 0.23}
