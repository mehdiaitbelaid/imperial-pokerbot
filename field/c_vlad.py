"""Counted-round profile of Vlad (R1-R11, 3000 hands, -8.5 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.22, 'pfr': 0.15, 'limp': 0.0, 'three_bet': 0.03, 'fold_to_3bet': 0.37, 'open_size_bb': 3.5, 'cbet': 0.82, 'bet': 0.52, 'bet_size': 0.8, 'fold_to_bet': 0.41, 'raise_vs_bet': 0.15, 'air': 0.15}
