"""Counted-round profile of Red (R1-R11, 3000 hands, -2.3 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.23, 'pfr': 0.18, 'limp': 0.0, 'three_bet': 0.03, 'fold_to_3bet': 0.9, 'open_size_bb': 6.0, 'cbet': 0.85, 'bet': 0.72, 'bet_size': 0.5, 'fold_to_bet': 0.53, 'raise_vs_bet': 0.07, 'air': 0.18}
