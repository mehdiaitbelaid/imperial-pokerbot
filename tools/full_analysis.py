"""Full round analysis: results, all-in luck, positions, preflop spots, calls vs bet size, opponents.
    HANDS=hands python3 tools/full_analysis.py   (hand files from the team API; never commit them or the token)"""
import json,glob,collections,random,importlib.util,sys,statistics as S
spec=importlib.util.spec_from_file_location("ev",__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__))),'upload','bot_v14.py'));M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
CARD,CP,RANK,FLUSH=M.CARD,M.CP,M.RANK,M.FLUSH
def score(cards):
    p=1;sc=[0]*4;sm=[0]*4
    for c in cards:
        p*=CP[c];s=c&3;sc[s]+=1;sm[s]|=1<<(c>>2)
    v=RANK[p]
    for s in range(4):
        if sc[s]>=5:
            f=FLUSH[sm[s]]
            if f>v:v=f
    return v
def equity(hands,board,n=3000):
    dead=set(board);[dead.update(h) for h in hands]
    deck=[c for c in range(52) if c not in dead];need=5-len(board);w=[0.0]*len(hands);rng=random.Random(1)
    import itertools
    combos=list(itertools.combinations(deck,need)) if need<=2 else None
    it=combos if combos is not None else (rng.sample(deck,need) for _ in range(n))
    cnt=0
    for extra in it:
        b=board+list(extra);sc=[score(h+b) for h in hands];m=max(sc);k=sc.count(m)
        for i,x in enumerate(sc):
            if x==m:w[i]+=1.0/k
        cnt+=1
    return [x/cnt for x in w]
VER={1:'v5',2:'v5'};[VER.__setitem__(r,'v6') for r in range(3,12)];[VER.__setitem__(r,'v7') for r in range(12,22)];[VER.__setitem__(r,'v8') for r in range(22,30)];[VER.__setitem__(r,'v11') for r in range(30,60)]
def pos(rel,n):
    if rel==0:return 'BTN'
    if rel==1:return 'SB'
    if rel==2:return 'BB'
    if rel==n-1:return 'CO'
    if rel==n-2:return 'HJ'
    return 'EP'
A=collections.defaultdict(lambda:collections.defaultdict(list))  # A[ver][key] -> list of results (chips)
C=collections.defaultdict(lambda:collections.Counter())
opp=collections.defaultdict(lambda:collections.defaultdict(float))
luck=collections.defaultdict(list)
rounds=[]
calls=collections.defaultdict(list);gain=collections.defaultdict(list);rluck=collections.defaultdict(float)
for f in sorted(glob.glob(__import__('os').path.join(__import__('os').environ.get('HANDS','hands'),'saturday_r0[0-9][0-9].json'))):
    d=json.load(open(f));rd=int(f[-8:-5]);v=VER[rd];me=d['seat'];P=d['players'];n=len(P);R=d['round']
    opps=[p for i,p in enumerate(P) if i!=me]
    rounds.append((rd,v,R['bb100'],R['timeouts'],R.get('think_s'),R['table'],opps))
    for h in d['hands']:
        res=h['results'];r=res[me];rel=(me-h['button'])%n;ps=pos(rel,n)
        A[v]['all'].append(r);A[v]['pos_'+ps].append(r)
        # attribution
        if r<0:
            win=[(i,x) for i,x in enumerate(res) if x>0 and i!=me];tw=sum(x for _,x in win)
            for i,x in win: opp[v][P[i]]+=r*x/tw
        elif r>0:
            los=[(i,-x) for i,x in enumerate(res) if x<0 and i!=me];tl=sum(x for _,x in los)
            for i,x in los: opp[v][P[i]]+=r*x/tl
        # preflop parse
        street='preflop';bets={};cur=0;raises=0;first_in=True;my_pf=[];limpers=0;pfr_seat=None;contrib=[0]*n;stacks=list(h['start_stacks']);folded=[False]*n
        board=[];last_act_idx=-1;ev=h['events'];acts=[i for i,e in enumerate(ev) if e[0]=='act']
        lastact=acts[-1] if acts else -1;allin_board=None;allin_in=None
        pot=0;facing_log=[]
        for idx,e in enumerate(ev):
            if e[0]=='post':
                bets[e[1]]=e[2];cur=max(cur,e[2]);contrib[e[1]]+=e[2];stacks[e[1]]-=e[2];pot+=e[2];continue
            if e[0]=='board':
                if idx>lastact and allin_board is None:
                    allin_board=list(board);allin_in=[i for i in range(n) if not folded[i]]
                street=e[1];board=e[2];bets={};cur=0;continue
            if e[0]!='act':continue
            _,s,a,amt=e;mine=bets.get(s,0);tc=cur-mine
            if street=='preflop':
                if s==me: my_pf.append((a,raises,limpers,tc))
                if a=='raise':
                    raises+=1;pfr_seat=s
                elif a=='call' and raises==0: limpers+=1
            if s==me and a in('call','fold') and tc>0 and street!='preflop':
                facing_log.append((street,a,tc,pot-0,contrib[me]))
            if a=='raise':
                add=amt-mine;contrib[s]+=add;stacks[s]-=add;pot+=add;bets[s]=amt;cur=amt
            elif a=='call':
                contrib[s]+=amt;stacks[s]-=amt;pot+=amt;bets[s]=mine+amt
            elif a=='fold':folded[s]=True
        if lastact>=0 and allin_board is None and len(board)<5 and len(h['board'])==5 and not folded[me]:
            allin_board=list(board);allin_in=[i for i in range(n) if not folded[i]]
        # preflop categories
        if my_pf:
            a0,r0,l0,tc0=my_pf[0]
            if r0==0 and l0==0 and a0=='raise' and ps in('CO','BTN','SB'):
                C[v]['steal_att']+=1;A[v]['steal'].append(r)
                if sum(1 for e in ev if e[0]=='act' and e[2]!='fold')==1 or all(x<=0 for i,x in enumerate(res) if i!=me) and h['board']==[]: C[v]['steal_won']+=1
            if r0==0 and a0=='raise':C[v]['rfi']+=1;A[v]['rfi'].append(r)
            if r0==1 and ps=='BB':
                C[v]['bb_vs1']+=1;C[v]['bb_'+a0]+=1;A[v]['bbdef_'+a0].append(r)
            if r0==1 and a0=='raise':C[v]['3bet']+=1;A[v]['3bet'].append(r)
            if r0==1:C[v]['face1']+=1
            if any(x[0]=='raise' and x[1]==0 for x in my_pf):
                after=[x for x in my_pf if x[1]>=2]
                if after:
                    C[v]['faced3']+=1;C[v]['vs3_'+after[0][0]]+=1;A[v]['vs3_'+after[0][0]].append(r)
            if any(x[0]=='raise' and x[1]==1 for x in my_pf):
                after=[x for x in my_pf if x[1]>=3]
                if after:C[v]['faced4']+=1;C[v]['vs4_'+after[0][0]]+=1;A[v]['vs4_'+after[0][0]].append(r)
        for st,a,tc,pt,cb in facing_log:
            frac=tc/float(max(1,pt-tc));b='<.5' if frac<0.5 else ('.5-1' if frac<1.0 else '>=1')
            calls[(v,st,b,a)].append(r);gain[(v,st,b,a)].append(r+cb)
        # all-in luck
        if allin_board is not None and me in allin_in and len(allin_in)>=2:
            shown=h['showdown'] or {};hole=h['hole']
            if all(str(i) in hole for i in allin_in):
                hs=[[CARD[c] for c in hole[str(i)]] for i in allin_in];b=[CARD[c] for c in allin_board]
                eq=equity(hs,b,1500);mi=allin_in.index(me);tot=sum(contrib)
                evr=eq[mi]*tot-contrib[me]
                rluck[rd]+=r-evr;luck[v].append((r,evr,rd,h['n'],''.join(hole[str(me)]),' '.join(allin_board),[P[i] for i in allin_in if i!=me],eq[mi]))
bb=lambda xs:sum(xs)/20.0
out=[]
out.append("## rounds");[out.append("R%02d %s %+7.1f to=%d think=%s table=%d vs %s"%(r[0],r[1],r[2],r[3],r[4],r[5],', '.join(r[6]))) for r in rounds]
for v in [x for x in ('v5','v6','v7','v8','v11') if A[x]['all']]:
    al=A[v]['all'];N=len(al);out.append("\n## %s hands=%d bb/100=%+.1f sd_per_hand_bb=%.1f se_bb100=%.1f"%(v,N,bb(al)/N*100,S.pstdev(al)/20,S.pstdev(al)/20/N**.5*100))
    for p in ('EP','HJ','CO','BTN','SB','BB'):
        x=A[v]['pos_'+p]
        if x:out.append("  pos %-3s n=%4d bb/100 %+7.1f"%(p,len(x),bb(x)/len(x)*100))
    c=C[v];out.append("  RFI %d (%.1f%% of hands) net %+.0f bb | steals %d won-uncontested %d net %+.0f bb"%(c['rfi'],100*c['rfi']/N,bb(A[v]['rfi']),c['steal_att'],c['steal_won'],bb(A[v]['steal'])))
    out.append("  BB vs single raise: %d  fold %d call %d 3bet %d | net fold %+.0f call %+.0f 3bet %+.0f bb"%(c['bb_vs1'],c['bb_fold'],c['bb_call'],c['bb_raise'],bb(A[v]['bbdef_fold']),bb(A[v]['bbdef_call']),bb(A[v]['bbdef_raise'])))
    out.append("  facing one raise: %d, we 3-bet %d (%.0f%%) net %+.0f bb"%(c['face1'],c['3bet'],100*c['3bet']/max(1,c['face1']),bb(A[v]['3bet'])))
    out.append("  opened and faced 3-bet: %d fold %d call %d 4bet %d | net fold %+.0f call %+.0f 4bet %+.0f bb"%(c['faced3'],c['vs3_fold'],c['vs3_call'],c['vs3_raise'],bb(A[v]['vs3_fold']),bb(A[v]['vs3_call']),bb(A[v]['vs3_raise'])))
    out.append("  3-bet and faced 4-bet: %d fold %d call %d 5bet %d | net fold %+.0f call %+.0f jam %+.0f bb"%(c['faced4'],c['vs4_fold'],c['vs4_call'],c['vs4_raise'],bb(A[v]['vs4_fold']),bb(A[v]['vs4_call']),bb(A[v]['vs4_raise'])))
    L=luck[v];
    if L:
        act=sum(x[0] for x in L);evs=sum(x[1] for x in L)
        out.append("  all-ins with cards known: %d  actual %+.0f bb  EV %+.0f bb  luck %+.0f bb (%+.1f bb/100)"%(len(L),act/20,evs/20,(act-evs)/20,(act-evs)/20/N*100))
    o=sorted(opp[v].items(),key=lambda kv:kv[1])
    out.append("  lost most to: "+', '.join("%s %+.0f"%(k,x/20) for k,x in o[:6]))
    out.append("  won most from: "+', '.join("%s %+.0f"%(k,x/20) for k,x in o[::-1][:6]))
out.append("\n## postflop calls/folds facing bets (final hand result, bb)")
for v in [x for x in ('v6','v7') if A[x]['all']]:
    for st in ('flop','turn','river'):
        for b in ('<.5','.5-1','>=1'):
            cl=calls[(v,st,b,'call')];fd=calls[(v,st,b,'fold')]
            if cl or fd: out.append("  %s %-5s bet %-4s pot: call n=%3d won %3d gain-vs-folding %+6.0f bb | fold n=%3d"%(v,st,b,len(cl),sum(1 for x in cl if x>0),bb(gain[(v,st,b,'call')]),len(fd)))
out.append("\n## worst all-in EV (v6+v7) and luckiest")
LL=luck['v6']+luck['v7']
for x in sorted(LL,key=lambda x:x[0]-x[1])[:6]:out.append("  unlucky r%02d#%d %s board[%s] vs %s eq %.2f actual %+.0f ev %+.0f bb"%(x[2],x[3],x[4],x[5],x[6],x[7],x[0]/20,x[1]/20))
for x in sorted(LL,key=lambda x:x[1])[:8]:out.append("  bad EV r%02d#%d %s board[%s] vs %s eq %.2f ev %+.0f bb"%(x[2],x[3],x[4],x[5],x[6],x[7],x[1]/20))
out.append("\n## per-round luck (bb/100) and luck-adjusted")
for r in rounds:
    lk=rluck[r[0]]/20/10.0
    out.append("R%02d %s actual %+7.1f luck %+7.1f adjusted %+7.1f%s"%(r[0],r[1],r[2],lk,r[2]-lk,' (ediz table)' if 'ediz_slow' in r[6] else ''))
for v in [x for x in ('v6','v7') if A[x]['all']]:
    rr=[r for r in rounds if r[1]==v];adj=[r[2]-rluck[r[0]]/200.0 for r in rr];adjn=[r[2]-rluck[r[0]]/200.0 for r in rr if 'ediz_slow' not in r[6]]
    out.append("%s mean actual %+.1f  luck-adjusted %+.1f  luck-adjusted without ediz tables %+.1f (n=%d rounds)"%(v,S.mean([r[2] for r in rr]),S.mean(adj),S.mean(adjn),len(adjn)))
print('\n'.join(out))
