"""Counted-round profile of Astra La Vista (R1-R11, 2000 hands, +15.2 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.22, 'pfr': 0.16, 'limp': 0.0, 'three_bet': 0.06, 'fold_to_3bet': 0.62, 'open_size_bb': 2.8, 'cbet': 0.84, 'bet': 0.72, 'bet_size': 0.33, 'fold_to_bet': 0.4, 'raise_vs_bet': 0.1, 'air': 0.16}
