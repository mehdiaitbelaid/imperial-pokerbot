"""Nit: top ~10% preflop, continues with top pair+, folds to aggression otherwise."""
R="23456789TJQKA"
class Agent:
    def act(self,s):
        L=s["legal_actions"];h=s["hole_cards"];a,b=sorted((R.index(c[0]) for c in h),reverse=True)
        if s["street"]=="preflop":
            prem=(a==b and a>=6) or (a>=11 and b>=9) or (a==12 and b>=10)
            if prem and "raise" in L: return {"action":"raise","amount":min(s["max_raise_to"],max(s["min_raise_to"],3*max(s["bets"])))}
            if prem: return {"action":"call"}
            return {"action":"check" if "check" in L else "fold"}
        br=[R.index(c[0]) for c in s["board"]];hr=[R.index(c[0]) for c in h]
        strong=(a==b and a>max(br)) or max(br) in hr or len(set(br))<len(br)+0 and any(x in br for x in hr) and hr[0]!=hr[1] and sum(x in br for x in hr)==2
        if strong:
            if "raise" in L: return {"action":"raise","amount":min(s["max_raise_to"],max(s["min_raise_to"],s["pot"]*2//3+max(s["bets"])))}
            return {"action":"call" if "call" in L else "check"}
        return {"action":"check" if "check" in L else "fold"}
