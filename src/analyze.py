import json,sys,collections
R="23456789TJQKA"
def cls(h):
    a,b=h;ra,rb=R.index(a[0]),R.index(b[0])
    if ra<rb: a,b=b,a;ra,rb=rb,ra
    return a[0]+b[0]+('' if ra==rb else ('s' if a[1]==b[1] else 'o'))
for f in sys.argv[1:]:
    d=json.load(open(f));P=d['players'];me=d['seat'];H=d['hands'];n=len(P)
    print("\n#########",d['ref'],"seat",me,"players",P)
    S={i:collections.Counter() for i in range(n)}
    my=collections.Counter();bypos=collections.defaultdict(list);bystreet=collections.Counter();lines=[]
    folds_strong=[]
    for h in H:
        street='preflop';cur=0;bets={};vp=set();pr=set();last_street_me='preflop';my_actions=[]
        ev=h['events']
        for e in ev:
            if e[0]=='post': bets[e[1]]=e[2];cur=max(cur,e[2]);continue
            if e[0]=='board': street=e[1];bets={};cur=0;continue
            if e[0]!='act':continue
            _,s,a,amt=e;facing=cur>bets.get(s,0);st=S[s]
            if street=='preflop':
                if a in('call','raise'):vp.add(s)
                if a=='raise':pr.add(s)
            else:
                if facing: st['faced']+=1; st['ffold']+=(a=='fold')
                if a=='raise': st['agg']+=1
                elif a in('check','call'): st['pas']+=1
            if s==me:
                my_actions.append((street,a,amt,facing,cur-bets.get(s,0)));last_street_me=street
            if a=='raise': bets[s]=amt;cur=max(cur,amt)
            elif a=='call': bets[s]=bets.get(s,0)+amt
        for i in range(n):
            S[i]['hands']+=1;S[i]['vpip']+=i in vp;S[i]['pfr']+=i in pr;S[i]['chips']+=h['results'][i]
            if h['showdown'] and str(i) in h['showdown']: S[i]['sd']+=1; S[i]['sdwon']+= h['results'][i]>0
        r=h['results'][me];rel=(me-h['button'])%n
        pos={0:'BTN',1:'SB',2:'BB'}.get(rel,'EP%d'%rel if rel<n-2 else 'LP%d'%rel)
        bypos[pos].append(r)
        bystreet[last_street_me]+=r
        hole=h['hole'].get(str(me))
        # folds where we had strong preflop class or folded facing tiny bet (timeout suspicion)
        for st_,a,amt,facing,tc in my_actions:
            if a=='fold' and tc<= h['bb'] and st_!='preflop': folds_strong.append((h['n'],cls(hole),st_,tc))
        lines.append((r,h['n'],cls(hole) if hole else '?',h['board'],h['showdown'],' '.join((P[e[1]][:5]+':'+e[2]+(str(e[3]) if e[3] else '')) if e[0]=='act' else ('|' if e[0]=='board' else '') for e in ev if e[0] in('act','board'))))
    print("name                     bb100  VPIP PFR  FtB(n)    Agg  WSD(sd)")
    for i in range(n):
        s=S[i];print("%-24s %+6.0f %4.0f %4.0f %4.0f(%3d) %4.0f %4.0f(%d)"%(P[i][:24],s['chips']/20/s['hands']*100,100*s['vpip']/s['hands'],100*s['pfr']/s['hands'],100*s['ffold']/max(1,s['faced']),s['faced'],100*s['agg']/max(1,s['agg']+s['pas']),100*s['sdwon']/max(1,s['sd']),s['sd']))
    print("our result by position (bb/100):",{k:round(sum(v)/20/len(v)*100) for k,v in sorted(bypos.items())})
    print("our chips by last street we acted:",dict(bystreet))
    print("postflop folds to <=1bb bet (timeout suspects):",len(folds_strong),folds_strong[:10])
    lines.sort()
    print("--- 8 biggest losses");[print(l) for l in lines[:8]]
    print("--- 5 biggest wins");[print(l[:5]) for l in lines[-5:]]
