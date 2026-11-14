"""Sparring profile `gherk`: hyper-aggressive winner. Targets measured from tournament hands."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = dict(vpip=0.27, pfr=0.18, limp=0, three_bet=0.08, fold_to_3bet=0.58, open_size_bb=2.5,
             cbet=0.83, bet=0.68, bet_size=1.1, fold_to_bet=0.51, raise_vs_bet=0.26, air=0.22)
