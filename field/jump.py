"""Sparring profile `jump`: tight, honest. Targets measured from tournament hands."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = dict(vpip=0.17, pfr=0.09, limp=0.03, three_bet=0.05, fold_to_3bet=0.05, open_size_bb=3.6,
             cbet=0.92, bet=0.31, bet_size=0.74, fold_to_bet=0.46, raise_vs_bet=0.07, air=0)
