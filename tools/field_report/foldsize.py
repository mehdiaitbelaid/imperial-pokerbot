"""Fold rate facing a postflop bet, split by bet size, when the bettor is us vs anyone else (ediz_slow excluded as responder)."""
import json,glob,collections
ME='Resonance Qt';C=collections.Counter()
def b(fr): return '<45%' if fr<0.45 else ('45-80%' if fr<0.8 else '>=80%')
for f in sorted(glob.glob('hands/saturday_r0*.json')):
    d=json.load(open(f));P=d['players'];n=len(P);me=P.index(ME)
    for h in d['hands']:
        contrib=[0]*n;bets=[0]*n;cur=0;street='preflop';aggr=None;nraise=0
        for e in h['events']:
            if e[0]=='post': s,a=e[1],e[2];bets[s]+=a;contrib[s]+=a;cur=max(cur,bets[s]);continue
            if e[0]=='board': street=e[1];bets=[0]*n;cur=0;aggr=None;nraise=0;continue
            if e[0]!='act':continue
            _,s,a,amt=e;pot=sum(contrib);tc=cur-bets[s]
            if street!='preflop' and tc>0 and nraise==1 and s!=me and P[s]!='ediz_slow' and a in('fold','call','raise'):
                k=('us' if aggr==me else 'oth',b(tc/max(1,pot-tc)));C[k+('n',)]+=1
                if a=='fold':C[k+('f',)]+=1
            if a=='raise': add=amt-bets[s];contrib[s]+=add;bets[s]=amt;cur=amt;aggr=s;nraise+=1
            elif a=='call': contrib[s]+=amt;bets[s]+=amt
for sz in ('<45%','45-80%','>=80%'):
    print('%-7s'%sz,'  '.join('%s fold %4.1f%% (n=%5d)'%(w,100*C[(w,sz,'f')]/max(1,C[(w,sz,'n')]),C[(w,sz,'n')]) for w in ('us','oth')))
