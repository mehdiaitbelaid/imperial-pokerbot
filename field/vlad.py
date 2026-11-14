"""Sparring profile `vlad`: solid, big sizes. Targets measured from tournament hands."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = dict(vpip=0.22, pfr=0.18, limp=0.01, three_bet=0.02, fold_to_3bet=0.58, open_size_bb=3.9,
             cbet=0.81, bet=0.52, bet_size=0.8, fold_to_bet=0.33, raise_vs_bet=0.14, air=0.09)
