"""Sparring profile `roddy`: maniac whale. Targets measured from tournament hands."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = dict(vpip=0.83, pfr=0.34, limp=0.63, three_bet=0.35, fold_to_3bet=0, open_size_bb=3.0,
             cbet=1, bet=0.45, bet_size=0.56, fold_to_bet=0.54, raise_vs_bet=0.22, air=0.35)
