import json,collections,statistics as St,math
F=json.load(open('out/field.json'));ME='Resonance Qt'
VS={tuple(k.split('|')):v for k,v in F['VS'].items()};S=F['S']
def agg(who,teams=None):
    c=collections.Counter()
    for (t,w),v in VS.items():
        if w==who and t!=ME and (teams is None or t in teams) and t!='ediz_slow': c.update(v)
    return c
print('HOW THE FIELD RESPONDS TO US vs TO EVERYONE ELSE (all opponents except ediz_slow, pooled)')
for who in ('us','oth'):
    c=agg(who)
    print(who,'fold to postflop bet %.1f%% (n=%d) | fold to c-bet %.1f%% (n=%d) | 3-bet vs open %.1f%% (n=%d) | fold vs open %.1f%%'%(100*c['foldB']/c['faceB'],c['faceB'],100*c['fold_cb']/c['face_cb'],c['face_cb'],100*c['3b']/c['3b_opp'],c['3b_opp'],100*c['fold_open']/c['3b_opp']))
print('\nper team (n>=40 bets faced from us)')
rows=[]
for t in S:
    if t==ME: continue
    u=VS.get((t,'us'),{});o=VS.get((t,'oth'),{})
    if u.get('faceB',0)>=40:
        rows.append((t,u['foldB']/u['faceB'],u['faceB'],o.get('foldB',0)/max(1,o.get('faceB',0)),o.get('faceB',0),
                     u.get('3b',0)/max(1,u.get('3b_opp',1)),u.get('3b_opp',0),o.get('3b',0)/max(1,o.get('3b_opp',1)),o.get('3b_opp',0)))
for r in sorted(rows,key=lambda r:r[1]-r[3]):
    print('%-24s foldB vs us %4.0f%% (%3d)  vs others %4.0f%% (%4d)  diff %+4.0f | 3bet vs our opens %4.1f%% (%3d) vs others %4.1f%% (%4d)'%(r[0],100*r[1],r[2],100*r[3],r[4],100*(r[1]-r[3]),100*r[5],r[6],100*r[7],r[8]))
# sizing fingerprints
print('\nPOSTFLOP FIRST-BET SIZE MIX (fraction of pot) and OPEN SIZES (bb)')
B=[(0,.3,'<30%'),(.3,.45,'30-45'),(.45,.6,'45-60'),(.6,.8,'60-80'),(.8,1.05,'80-105'),(1.05,50,'>105'),(50,1e9,'allin')]
fp={}
for t,L in sorted(F['SZ'].items(),key=lambda kv:-len(kv[1])):
    if len(L)<150: continue
    h=[sum(1 for x in L if lo<=x<hi)/len(L) for lo,hi,_ in B]
    ops=collections.Counter(round(x*2)/2 for x in F['OPEN'].get(t,[]))
    top=ops.most_common(3);no=sum(ops.values())
    ent=-sum(p*math.log2(p) for p in h if p>0)
    fp[t]=dict(mix=h,open=[(k,v/no) for k,v in top],n=len(L),entropy=ent,distinct_open=len([k for k,v in ops.items() if v/no>=0.05]))
    print('%-24s n=%4d '%(t,len(L))+' '.join('%s:%3.0f'%(lab,100*p) for (_,_,lab),p in zip(B,h))+' | H=%.2f | opens '%ent+', '.join('%.1fbb %.0f%%'%(k,100*v/no) for k,v in top))
json.dump(fp,open('out/fingerprints.json','w'))
print('\nBIG RIVER BETS (>=66% pot) SHOWN DOWN: share that were air')
for t,c in sorted(F['RIV'].items(),key=lambda kv:-sum(kv[1].values())):
    n=sum(c.values())
    if n>=12: print('%-24s n=%3d air %.0f%%'%(t,n,100*c.get('air',0)/n))
