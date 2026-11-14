"""Replay real hand histories through a bot: at each of OUR decision points rebuild the
state the engine would have sent and ask the candidate bot what it would do now.
Also: what did opponents hold when they raised over a bet postflop (showdown hands)?"""
import json,sys,importlib.util,collections,random
bot_path=sys.argv[1];files=sys.argv[2:]
sys.path.insert(0,"/home/claude/imperial-pokerbot")
from engine.cards import evaluate as EV
spec=importlib.util.spec_from_file_location("cand",bot_path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R="23456789TJQKA"
def klass(hole,board):
    """4 monster(2pair both cards/set/straight+), 3 overpair or top pair K+ kicker, 2 other pair, 1 draw, 0 air"""
    hc=[m.card_int(c) for c in hole];bd=[m.card_int(c) for c in board]
    cat=EV(hc+bd)[0] if len(bd)>=3 else 0
    hr=[c>>2 for c in hc];br=[c>>2 for c in bd]
    bpairs=len(br)-len(set(br))
    if cat>=4: return 4
    if cat==3: return 4 if (hr[0]==hr[1] or bpairs==0 or True) else 3
    if cat==2:
        if bpairs==0: return 4
        # board paired: we have one real pair
        mine=[r for r in hr if r in br] or ([hr[0]] if hr[0]==hr[1] else [])
        if not mine: return 0
        top=max(br)
        return 3 if (max(mine)>=top) else 2
    if cat==1:
        if hr[0]==hr[1]: return 3 if hr[0]>max(br) else 2
        mine=[r for r in hr if r in br]
        if not mine: return 0
        k=[r for r in hr if r not in br]
        return 3 if (mine[0]==max(br) and k and k[0]>=11) else 2
    return 0
DET=[];FOLD=collections.defaultdict(list);UNF=collections.Counter();raise_show=collections.Counter();bet_show=collections.Counter()
for f in files:
    d=json.load(open(f));P=d['players'];me=d['seat'];n=len(P)
    ag=m.Agent();ag.on_table_start({"seat":me,"num_players":n,"hands":1000,"starting_stack":2000,"big_blind":20,"small_blind":10})
    diffs=[];saved=0
    for h in d['hands']:
        stacks=[2000]*n;bets=[0]*n;folded=[False]*n;contrib=[0]*n;hist=[];board=[];street='preflop';cur=0;min_inc=20
        my_hole=h['hole'].get(str(me));hand_div=[];first=True
        for e in h['events']:
            if e[0]=='post':
                s,a=e[1],e[2];stacks[s]-=a;bets[s]+=a;contrib[s]+=a;cur=max(cur,bets[s])
                hist.append({"seat":s,"street":"preflop","action":"small_blind" if a==h['sb'] and not hist else "big_blind","amount":a});continue
            if e[0]=='board':
                street=e[1];board=e[2];bets=[0]*n;cur=0;min_inc=20;continue
            if e[0]!='act': continue
            _,s,a,amt=e
            if s==me and my_hole:
                to_call=min(cur-bets[s],stacks[s]);max_to=bets[s]+stacks[s]
                can_raise=max_to>cur and any(not folded[j] and stacks[j]>0 for j in range(n) if j!=s)
                st={"hand_number":h['n'],"street":street,"seat":s,"button":h['button'],"hole_cards":my_hole,"board":list(board),"small_blind":10,"big_blind":20,
                    "pot":sum(contrib),"stacks":list(stacks),"bets":list(bets),"folded":list(folded),"to_call":to_call,
                    "min_raise_to":min(cur+min_inc,max_to) if can_raise else None,"max_raise_to":max_to if can_raise else None,
                    "legal_actions":(["fold","call"] if to_call>0 else ["check"])+(["raise"] if can_raise else []),"betting":"no_limit","raise_cap":None,"history":list(hist)}
                new=ag.act(st);na=new["action"];namt=new.get("amount")
                if na=="all_in": na,namt="raise",max_to
                if na!=a or (a=="raise" and abs((namt or 0)-amt)>max(40,0.35*amt)):
                    if first:
                        first=False
                        if na=="fold" and a!="fold":
                            FOLD[d['ref']].append((-contrib[me])-h['results'][me]);DET.append((d['ref'][-4:],(-contrib[me])-h['results'][me],h['n'],''.join(my_hole),''.join(board),street,klass(my_hole,board) if board else '-',a,amt,to_call,st['pot'],[P[x['seat']][:6] for x in hist if x['street']==street and x['action']=='raise'][-1:],h['showdown']))
                        elif a=="fold" and na!="fold": UNF[d['ref']]+=1
                    hand_div.append("%s[%s] was %s%s -> now %s%s"%(street,klass(my_hole,board) if board else '-',a,amt or '',na,namt or ''))
            # opponents: raise over a bet postflop, shown down
            if s!=me and street!='preflop' and a=='raise' and str(s) in h['hole'] and len(board)>=3:
                (raise_show if cur>0 else bet_show)[klass(h['hole'][str(s)],board)]+=1
            if a=='raise':
                inc=amt-cur
                if inc>=min_inc: min_inc=inc
                put=amt-bets[s];stacks[s]-=put;bets[s]=amt;contrib[s]+=put;cur=amt
            elif a=='call':
                stacks[s]-=amt;bets[s]+=amt;contrib[s]+=amt
            elif a=='fold': folded[s]=True
            hist.append({"seat":s,"street":street,"action":a,"amount":amt})
        shown={k:v for k,v in h['hole'].items() if h.get('showdown') and k in h['showdown']}
        ag.on_hand_end({"hand_number":h['n'],"board":h['board'],"shown":shown,"winners":[],"stacks":[],"history":hist})
        if hand_div and h['results'][me]<=-400: diffs.append((h['results'][me],h['n'],''.join(my_hole),''.join(h['board']),hand_div))
    print("\n==",d['ref'],"big losses (<=-400) where candidate plays differently: %d"%len(diffs))
    tot=sum(1 for h in d['hands'] if h['results'][me]<=-400)
    print("   (of %d big-loss hands)"%tot)
    for x in sorted(diffs)[:14]: print("  ",x[0],x[1],x[2],x[3],' || '.join(x[4]))
print("\nOpponents' shown hands when they RAISED over a bet postflop (class 4 monster,3 overpair/TPGK,2 weak pair,0 air):",dict(sorted(raise_show.items())))
print("Opponents' shown hands when they BET first postflop:",dict(sorted(bet_show.items())))

for r,v in FOLD.items():
    print(r,"new folds (first divergence): n=%d, chips saved net %+d (=%+.0f bb/100); saved in %d hands, gave up wins in %d; new non-folds where we used to fold: %d"%(len(v),sum(v),sum(v)/20/10,sum(1 for x in v if x>0),sum(1 for x in v if x<0),UNF[r]))

for x in sorted(DET,key=lambda x:x[1])[:14]: print(x)
