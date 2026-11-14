"""Calling station that raises its strong made hands."""
R="23456789TJQKA"
class Agent:
    def act(self,s):
        L=s["legal_actions"];h=s["hole_cards"];hr=[R.index(c[0]) for c in h];br=[R.index(c[0]) for c in s["board"]]
        two=sum(x in br for x in hr)>=2 or (hr[0]==hr[1] and hr[0] in br)
        if "raise" in L and (two or (not br and hr[0]==hr[1] and hr[0]>=10)):
            return {"action":"raise","amount":min(s["max_raise_to"],max(s["min_raise_to"],max(s["bets"])+s["pot"]))}
        return {"action":"check" if "check" in L else "call"}
