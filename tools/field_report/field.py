"""Field analysis from our 26 counted-round hand files (every seat's actions; opponents' cards only at showdown).
Outputs out/field.json. Run: python3 -I scripts/field.py hands"""
import json,glob,sys,collections,os
HD=sys.argv[1] if len(sys.argv)>1 else 'hands';os.makedirs('out',exist_ok=True)
ME='Resonance Qt';BB=20
RANKS="23456789TJQKA"
def air(hole,board):
    br=[c[0] for c in board]
    if hole[0][0]==hole[1][0] or hole[0][0] in br or hole[1][0] in br: return False
    cards=hole+board
    for s in "cdhs":
        if sum(1 for c in cards if c[1]==s)>=5: return False
    m=0
    for c in cards: m|=1<<RANKS.index(c[0])
    m=(m<<1)|((m>>12)&1)
    for lo in range(10):
        if (m>>lo)&31==31: return False
    return True
GR={r['G']:r for r in json.load(open('global_rounds.json'))}
def version(team,G):
    for g in range(G,G+3):
        if g in GR and team in GR[g]['teams']: return GR[g]['teams'][team]['version']
    return None
S=collections.defaultdict(lambda:collections.Counter())   # S[team][stat]
SZ=collections.defaultdict(list)       # postflop first-bet sizes (fraction of pot)
OPEN=collections.defaultdict(list)     # open sizes in bb
FLOW=collections.defaultdict(float);CO=collections.Counter()   # chip flow (winner,loser); co-seated hands
NET=collections.Counter();HANDS=collections.Counter()
VS=collections.defaultdict(lambda:collections.Counter())   # VS[(team,'us'|'oth')][stat]: how a team responds to us vs others
RIV=collections.defaultdict(lambda:collections.Counter())  # big river bets shown down: air vs made
ROUNDS=[];WHALE=set()
TV=collections.defaultdict(lambda:collections.Counter())   # per (team,version) style
files=sorted(glob.glob(os.path.join(HD,'saturday_r0[0-9][0-9].json')))
for f in files:
    d=json.load(open(f));G=int(f[-8:-5]);P=d['players'];n=len(P);me=P.index(ME)
    ROUNDS.append(dict(G=G,players=P,bb100=d['round']['bb100'],timeouts=d['round']['timeouts'],think=d['round'].get('think_s'),version=d['round']['version']))
    if 'ediz_slow' in P: WHALE.add(G)
    for h in d['hands']:
        res=h['results']
        for i,x in enumerate(res):
            NET[P[i]]+=x;HANDS[P[i]]+=1
            for j in range(n):
                if j!=i: CO[(P[i],P[j])]+=1
        gain=sum(x for x in res if x>0)
        for i,x in enumerate(res):
            if x<0 and gain>0:
                for j,w in enumerate(res):
                    if w>0: FLOW[(P[j],P[i])]+=-x*w/gain
        stacks=list(h['start_stacks']);contrib=[0]*n;bets=[0]*n;cur=0;street='preflop'
        raises=0;opener=None;threebettor=None;pf_aggr=None;folded=[False]*n;acted=collections.Counter()
        street_aggr=None;first_bet_done=False;flop_first=set();riv_bet=None;is_cbet=False
        vp=set();pr=set();sawflop=set()
        for e in h['events']:
            if e[0]=='post':
                s,a=e[1],e[2];bets[s]+=a;contrib[s]+=a;stacks[s]-=a;cur=max(cur,bets[s]);continue
            if e[0]=='board':
                street=e[1];bets=[0]*n;cur=0;street_aggr=None;first_bet_done=False
                if street=='flop': sawflop={i for i in range(n) if not folded[i]}
                continue
            if e[0]!='act': continue
            _,s,a,amt=e;t=P[s];pot=sum(contrib);tc=cur-bets[s];St=S[t]
            v=version(t,G);TVt=TV[(t,v)]
            if street=='preflop':
                if a in('call','raise'): vp.add(s)
                if a=='raise': pr.add(s)
                if raises==0 and a!='check':
                    St['rfi_opp']+=1;TVt['rfi_opp']+=1
                    if a=='raise': St['open']+=1;TVt['open']+=1;OPEN[t].append(amt/BB)
                    if a=='call': St['limp']+=1
                elif raises==1 and s!=opener and acted[(s,'pf1')]==0:
                    acted[(s,'pf1')]=1;who='us' if opener==me else 'oth'
                    St['3b_opp']+=1;VS[(t,who)]['3b_opp']+=1;TVt['3b_opp']+=1
                    if a=='raise': St['3b']+=1;VS[(t,who)]['3b']+=1;TVt['3b']+=1
                    if a=='fold': VS[(t,who)]['fold_open']+=1
                elif raises==2 and s==opener and acted[(s,'pf2')]==0:
                    acted[(s,'pf2')]=1;St['f3b_opp']+=1;TVt['f3b_opp']+=1
                    if a=='fold': St['f3b']+=1;TVt['f3b']+=1
                    if a=='raise': St['4b']+=1
                if a=='raise':
                    raises+=1;pf_aggr=s
                    if raises==1: opener=s
                    if amt>=bets[s]+stacks[s]: St['pf_jam']+=1
            else:
                if tc>0:
                    who='us' if street_aggr==me else 'oth'
                    St['faceB']+=1;VS[(t,who)]['faceB']+=1;TVt['faceB']+=1
                    if a=='fold': St['foldB']+=1;VS[(t,who)]['foldB']+=1;TVt['foldB']+=1
                    if a=='call': St['callB']+=1;St['calls']+=1
                    if a=='raise': St['raiseB']+=1;St['aggr']+=1
                    if street=='flop' and street_aggr==pf_aggr and street_aggr is not None and is_cbet:
                        VS[(t,'us' if pf_aggr==me else 'oth')]['face_cb']+=1
                        if a=='fold': VS[(t,'us' if pf_aggr==me else 'oth')]['fold_cb']+=1
                else:
                    if a in ('check','raise'):
                        St['checked_to']+=1
                        if a=='raise': St['bet_ct']+=1;St['aggr']+=1
                        if street=='flop' and s==pf_aggr and s not in flop_first:
                            St['cb_opp']+=1;TVt['cb_opp']+=1
                            if a=='raise': St['cb']+=1;TVt['cb']+=1
                        if a=='raise':
                            frac=amt/max(1,pot);allin=amt>=stacks[s]
                            SZ[t].append(frac if not allin else 99.0)
                            if street=='river' and frac>=0.66: riv_bet=s
                if street=='flop': flop_first.add(s)
            # apply
            if a=='raise':
                add=amt-bets[s];contrib[s]+=add;stacks[s]-=add;bets[s]=amt
                if street!='preflop' and cur==0: is_cbet=(street=='flop' and s==pf_aggr)
                cur=amt;street_aggr=s
            elif a=='call':
                contrib[s]+=amt;stacks[s]-=amt;bets[s]+=amt
            elif a=='fold': folded[s]=True
        for s in vp: S[P[s]]['vpip']+=1
        for s in pr: S[P[s]]['pfr']+=1
        for s in range(n): S[P[s]]['hands']+=1;TV[(P[s],version(P[s],G))]['hands']+=1
        for s in sawflop: S[P[s]]['flops']+=1
        sd=h.get('showdown') or {}
        for k in sd: S[P[int(k)]]['sd']+=1
        for k in sd:
            if res[int(k)]>0: S[P[int(k)]]['wsd']+=1
        if riv_bet is not None and str(riv_bet) in sd:
            hole=h['hole'].get(str(riv_bet))
            if hole and len(h['board'])==5:
                RIV[P[riv_bet]]['air' if air(hole,h['board']) else 'made']+=1
json.dump(dict(S={k:dict(v) for k,v in S.items()},SZ=SZ,OPEN=OPEN,FLOW={'%s|%s'%k:v for k,v in FLOW.items()},CO={'%s|%s'%k:v for k,v in CO.items()},
  NET=NET,HANDS=HANDS,VS={'%s|%s'%k:dict(v) for k,v in VS.items()},RIV={k:dict(v) for k,v in RIV.items()},ROUNDS=ROUNDS,WHALE=sorted(WHALE),
  TV={'%s|%s'%k:dict(v) for k,v in TV.items()}),open('out/field.json','w'))
print('files',len(files),'teams',len(S),'whale rounds (ediz_slow at our table):',sorted(WHALE))
