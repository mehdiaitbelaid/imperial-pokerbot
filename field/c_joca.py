"""Counted-round profile of Joca (R1-R11, 3000 hands, -36.2 bb/100)."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = {'vpip': 0.08, 'pfr': 0.01, 'limp': 0.04, 'three_bet': 0.01, 'fold_to_3bet': 0.5, 'open_size_bb': 6.0, 'cbet': 0.4, 'bet': 0.22, 'bet_size': 1.6, 'fold_to_bet': 0.4, 'raise_vs_bet': 0.18, 'air': 0.05}
