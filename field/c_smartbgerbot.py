"""Counted-round profile of SmartBGerBot (R1-R11, 2000 hands, -12.7 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.13, 'pfr': 0.1, 'limp': 0.0, 'three_bet': 0.02, 'fold_to_3bet': 0.81, 'open_size_bb': 3.2, 'cbet': 0.53, 'bet': 0.38, 'bet_size': 0.65, 'fold_to_bet': 0.44, 'raise_vs_bet': 0.04, 'air': 0.12}
