"""Where chips move between us and a given rival: pot type x how the hand ended. Flow attribution as in matrix.py."""
import json,glob,collections,sys
ME='Resonance Qt'
RIV=sys.argv[1:] or ['Attention Is All In','WBot','munchlax','Gherkers','Equity Engine','Kojack','AAST','The Market Makers','FisherMen']
D={r:collections.Counter() for r in RIV};N={r:collections.Counter() for r in RIV};CO=collections.Counter()
for f in sorted(glob.glob('hands/saturday_r0*.json')):
    d=json.load(open(f));P=d['players'];me=P.index(ME)
    for r in RIV:
        if r not in P: continue
        x=P.index(r)
        for h in d['hands']:
            CO[r]+=1;res=h['results'];gain=sum(v for v in res if v>0)
            if gain==0: continue
            fl=0.0
            if res[me]<0 and res[x]>0: fl=-(-res[me]*res[x]/gain)
            elif res[x]<0 and res[me]>0: fl=(-res[x]*res[me]/gain)
            if fl==0: continue
            # classify
            raises=[];street='preflop';last=street;aggr_post={}
            for e in h['events']:
                if e[0]=='board': street=e[1]
                if e[0]=='act':
                    last=street
                    if street=='preflop' and e[2]=='raise': raises.append(e[1])
                    if street!='preflop' and e[2]=='raise': aggr_post.setdefault(street,e[1])
            pf='limped' if not raises else ('single-raised' if len(raises)==1 else '3bet+')
            if len(raises)>=2:
                pf+=' (we 3bet+)' if me in raises[1:] and x not in raises[1:] else (' (they 3bet+)' if x in raises[1:] and me not in raises[1:] else ' (both)')
            sd='showdown' if str(me) in (h['showdown'] or {}) and str(x) in (h['showdown'] or {}) else 'no showdown'
            end='ended '+last
            D[r][(pf,sd)]+=fl;N[r][(pf,sd)]+=1
            # river big bets by rival that we called at showdown
for r in RIV:
    tot=sum(D[r].values())
    print('\n== %s: net %+.0f chips over %d hands (%+.1f bb/100)'%(r,tot,CO[r],tot/20/max(1,CO[r])*100))
    for k,v in sorted(D[r].items(),key=lambda kv:kv[1]):
        print('   %-38s %-12s %+8.0f chips  n=%4d'%(k[0],k[1],v,N[r][k]))
