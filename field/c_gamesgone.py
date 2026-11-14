"""Counted-round profile of GamesGone (R1-R11, 2000 hands, -23.4 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.25, 'pfr': 0.11, 'limp': 0.02, 'three_bet': 0.05, 'fold_to_3bet': 0.29, 'open_size_bb': 2.7, 'cbet': 0.66, 'bet': 0.6, 'bet_size': 0.5, 'fold_to_bet': 0.52, 'raise_vs_bet': 0.07, 'air': 0.38}
