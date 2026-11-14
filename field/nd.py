"""Sparring profile `nd`: never folds to 3-bets. Targets measured from tournament hands."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = dict(vpip=0.21, pfr=0.11, limp=0.08, three_bet=0.05, fold_to_3bet=0.07, open_size_bb=3.3,
             cbet=0.58, bet=0.33, bet_size=0.75, fold_to_bet=0.39, raise_vs_bet=0.13, air=0.08)
