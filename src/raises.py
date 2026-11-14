import json,sys,collections
sys.path.insert(0,"/home/claude/imperial-pokerbot")
from engine.cards import evaluate as EV, to_int
def klass(hole,board):
    hc=[to_int(c) for c in hole];bd=[to_int(c) for c in board];cat=EV(hc+bd)[0]
    hr=[c>>2 for c in hc];br=[c>>2 for c in bd];bp=len(br)-len(set(br))
    if cat>=3: return 4
    if cat==2 and bp==0: return 4
    if cat in(1,2):
        if hr[0]==hr[1]: return 3 if hr[0]>max(br) else 2
        mine=[r for r in hr if r in br]
        if not mine: return 0
        k=[r for r in hr if r not in br]
        return 3 if (max(mine)==max(br) and k and k[0]>=11) else 2
    return 0
T=collections.defaultdict(lambda: collections.Counter())
for f in sys.argv[1:]:
    d=json.load(open(f));P=d['players'];me=d['seat']
    for h in d['hands']:
        street='preflop';cur=0;pot=0;bets={};board=[]
        for e in h['events']:
            if e[0]=='post': pot+=e[2];continue
            if e[0]=='board': street=e[1];board=e[2];cur=0;bets={};continue
            if e[0]!='act':continue
            _,s,a,amt=e
            if street!='preflop' and a=='raise' and s!=me and str(s) in h['hole']:
                k=klass(h['hole'][str(s)],board)
                frac=(amt-cur)/max(1,pot+ (cur-bets.get(s,0)))
                kind=('RERAISE' if cur>0 else 'BET')+('_big' if amt>=400 else '_small')
                T[P[s]][(kind,k)]+=1; T['ALL'][(kind,k)]+=1
                if P[s] not in('bigRoddy','FisherMen'): T['ALL-ex-fish'][(kind,k)]+=1
            if a=='raise': pot+=amt-bets.get(s,0);bets[s]=amt;cur=amt
            elif a=='call': pot+=amt;bets[s]=bets.get(s,0)+amt
for p,c in T.items():
    row=[]
    for kind in('RERAISE_big','RERAISE_small','BET_big','BET_small'):
        v=[c[(kind,k)] for k in(4,3,2,0)];t=sum(v)
        row.append("%s n=%d mon%.0f%% tp%.0f%% weak%.0f%% air%.0f%%"%(kind,t,*(100*x/max(1,t) for x in v)))
    print("%-22s"%p[:22],' | '.join(row))
