"""Sparring profile `fisher`: limping aggro fish. Targets measured from tournament hands."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = dict(vpip=0.42, pfr=0.07, limp=0.55, three_bet=0.06, fold_to_3bet=0, open_size_bb=2.7,
             cbet=0.86, bet=0.6, bet_size=0.52, fold_to_bet=0.49, raise_vs_bet=0.3, air=0.27)
