"""Counted-round profile of Poké Bot (R1-R11, 3000 hands, -4.0 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.23, 'pfr': 0.16, 'limp': 0.0, 'three_bet': 0.02, 'fold_to_3bet': 0.35, 'open_size_bb': 3.1, 'cbet': 0.72, 'bet': 0.38, 'bet_size': 0.6, 'fold_to_bet': 0.42, 'raise_vs_bet': 0.07, 'air': 0.32}
