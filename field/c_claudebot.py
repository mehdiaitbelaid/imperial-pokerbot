"""Counted-round profile of Claudebot (R1-R11, 2000 hands, -39.8 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.22, 'pfr': 0.18, 'limp': 0.0, 'three_bet': 0.03, 'fold_to_3bet': 0.8, 'open_size_bb': 6.0, 'cbet': 0.42, 'bet': 0.3, 'bet_size': 0.62, 'fold_to_bet': 0.47, 'raise_vs_bet': 0.04, 'air': 0.11}
