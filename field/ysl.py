"""Sparring profile `ysl`: postflop calling station. Targets measured from tournament hands."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = dict(vpip=0.2, pfr=0.15, limp=0, three_bet=0.03, fold_to_3bet=0.92, open_size_bb=3.1,
             cbet=0.32, bet=0.18, bet_size=0.66, fold_to_bet=0.21, raise_vs_bet=0.04, air=0.11)
