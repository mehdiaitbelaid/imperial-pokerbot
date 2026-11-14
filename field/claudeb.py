"""Sparring profile `claudeb`: typical LLM tight-aggressive. Targets measured from tournament hands."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = dict(vpip=0.25, pfr=0.2, limp=0, three_bet=0.03, fold_to_3bet=0.81, open_size_bb=5.4,
             cbet=0.52, bet=0.33, bet_size=0.62, fold_to_bet=0.48, raise_vs_bet=0.07, air=0.25)
