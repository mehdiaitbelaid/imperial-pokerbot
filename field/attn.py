"""Sparring profile `attn`: bets a lot, folds to pressure. Targets measured from tournament hands."""
from profile_base import ProfileAgent


class Agent(ProfileAgent):
    P = dict(vpip=0.28, pfr=0.2, limp=0, three_bet=0.03, fold_to_3bet=0.88, open_size_bb=2.8,
             cbet=0.52, bet=0.5, bet_size=0.65, fold_to_bet=0.75, raise_vs_bet=0.06, air=0.3)
