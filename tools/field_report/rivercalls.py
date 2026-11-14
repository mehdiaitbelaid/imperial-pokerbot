"""Our calls of big turn/river bets (>= 66% pot): outcome by opponent tier, our hand class and bot version."""
import json,glob,collections,itertools,statistics as St
ME='Resonance Qt';R="23456789TJQKA"
TOP={'Gherkers','Attention Is All In','Equity Engine','Kojack','AAST','The Market Makers','Phil AIvey','Anker Batteries','Chinese people can fly','WBot','munchlax','Poke'}
def cat(cards):
    rs=sorted((R.index(c[0]) for c in cards),reverse=True);cnt=collections.Counter(rs);su=collections.Counter(c[1] for c in cards)
    fl=any(v>=5 for v in su.values());m=0
    for x in rs:m|=1<<x
    m=(m<<1)|((m>>12)&1);st=any((m>>lo)&31==31 for lo in range(10))
    c=sorted(cnt.values(),reverse=True)
    if st and fl: return 8
    if c[0]==4: return 7
    if c[0]==3 and c[1]>=2: return 6
    if fl: return 5
    if st: return 4
    if c[0]==3: return 3
    if c[0]==2 and c[1]==2: return 2
    if c[0]==2: return 1
    return 0
NAME={0:'no pair',1:'one pair',2:'two pair',3:'trips',4:'straight+',5:'straight+',6:'straight+',7:'straight+',8:'straight+'}
VER=lambda g:'v14' if (3<=g<=11 or g>=22) else ('V18' if 12<=g<=21 else 'v5')
out=collections.defaultdict(list);NR=collections.Counter()
for f in sorted(glob.glob('hands/saturday_r0*.json')):
    d=json.load(open(f));G=int(f[-8:-5]);P=d['players'];n=len(P);me=P.index(ME);NR[VER(G)]+=1;NR['all']+=1
    for h in d['hands']:
        contrib=[0]*n;bets=[0]*n;cur=0;street='preflop';board=[];aggr=None
        for e in h['events']:
            if e[0]=='post': s,a=e[1],e[2];bets[s]+=a;contrib[s]+=a;cur=max(cur,bets[s]);continue
            if e[0]=='board': street=e[1];board=e[2];bets=[0]*n;cur=0;continue
            if e[0]!='act':continue
            _,s,a,amt=e;pot=sum(contrib);tc=cur-bets[s]
            if s==me and street in('turn','river') and tc>0 and a in('call','fold') and aggr is not None and aggr!=me:
                frac=tc/max(1,pot-tc)
                if frac>=0.66:
                    hc=NAME[cat(h['hole'][str(me)]+board)]
                    tier='top' if P[aggr] in TOP else ('whale' if P[aggr]=='ediz_slow' else 'rest')
                    out[(street,a,tier,hc,VER(G))].append(h['results'][me]+contrib[me])  # call result minus fold-now result
            if a=='raise': add=amt-bets[s];contrib[s]+=add;bets[s]=amt;cur=amt;aggr=s
            elif a=='call': contrib[s]+=amt;bets[s]+=amt
print('Value of calling vs folding at that moment (hand result + chips already in = gain over folding)')
tot=collections.Counter()
for k in sorted(out):
    L=out[k]
    if k[1]!='call': continue
    print('%-6s %-5s %-5s %-10s %-4s %4d %5.0f%% %+9.0f %+6.2f'%(k[0],k[1],k[2],k[3],k[4],len(L),100*sum(1 for x in L if x>0)/len(L),sum(L),sum(L)/20/(NR['all']*1000)*100))
# summary: one-pair calls vs non-whale
agg=collections.defaultdict(list)
for k,L in out.items():
    if k[1]=='call' and k[2]!='whale': agg[(k[3])]+=L
print()
for hc,L in agg.items(): print('ALL non-whale calls of >=66%% pot turn/river bets with %-10s n=%4d win %3.0f%% gain over folding %+8.0f chips (%+.1f bb/100 over all %d rounds)'%(hc,len(L),100*sum(1 for x in L if x>0)/len(L),sum(L),sum(L)/20/(NR['all']*1000)*100,NR['all']))
print()
for ver in ('v14','V18'):
    for tier in ('top','rest'):
        L=[x for k,v in out.items() if k[1]=='call' and k[4]==ver and k[2]==tier and k[3] in('one pair','two pair') for x in v]
        rounds=NR[ver]
        if L: print('%s vs %-4s one/two pair calls n=%3d  gain over folding %+7.0f chips = %+.1f bb/100 over its %d rounds'%(ver,tier,len(L),sum(L),sum(L)/20/(rounds*1000)*100,rounds))
