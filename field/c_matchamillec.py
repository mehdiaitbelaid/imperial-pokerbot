"""Counted-round profile of matcha mille crêpes cake (R1-R11, 4000 hands, +9.5 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.19, 'pfr': 0.12, 'limp': 0.01, 'three_bet': 0.07, 'fold_to_3bet': 0.55, 'open_size_bb': 2.8, 'cbet': 0.57, 'bet': 0.43, 'bet_size': 0.6, 'fold_to_bet': 0.35, 'raise_vs_bet': 0.07, 'air': 0.08}
