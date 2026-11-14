"""Sparring profile `wbot`: overbets. Targets measured from tournament hands."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = dict(vpip=0.31, pfr=0.2, limp=0.01, three_bet=0.04, fold_to_3bet=0.77, open_size_bb=3.9,
             cbet=0.95, bet=0.59, bet_size=1.2, fold_to_bet=0.43, raise_vs_bet=0.22, air=0.22)
