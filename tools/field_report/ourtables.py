import json,collections,statistics as St,math
F=json.load(open('out/field.json'));ME='Resonance Qt'
FLOW={tuple(k.split('|')):v for k,v in F['FLOW'].items()};CO={tuple(k.split('|')):v for k,v in F['CO'].items()}
NET=F['NET'];H=F['HANDS'];S=F['S']
print('OUR ROUNDS')
for r in F['ROUNDS']:
    print('R%02d v%-2d %+7.1f to=%d think=%s %s | %s'%(r['G'],r['version'],r['bb100'],r['timeouts'],r['think'],'WHALE' if r['G'] in F['WHALE'] else '     ',', '.join(p for p in r['players'] if p!=ME)))
nw=[r['bb100'] for r in F['ROUNDS'] if r['G'] not in F['WHALE']];w=[r['bb100'] for r in F['ROUNDS'] if r['G'] in F['WHALE']]
print('ours: non-whale mean %+.1f ± %.1f (n=%d); whale-table mean %+.1f (n=%d)'%(St.mean(nw),St.pstdev(nw)/math.sqrt(len(nw)),len(nw),St.mean(w),len(w)))
for lab,rng in (('v6',range(3,12)),('v7',range(12,22)),('v8/10',range(22,30))):
    x=[r['bb100'] for r in F['ROUNDS'] if r['G'] in rng and r['G'] not in F['WHALE']];y=[r['bb100'] for r in F['ROUNDS'] if r['G'] in rng]
    print(lab,'all %+.1f (n=%d) non-whale %+.1f (n=%d)'%(St.mean(y),len(y),St.mean(x) if x else float('nan'),len(x)))
print('\nOUR NET VS EACH OPPONENT (bb per 100 hands sharing a table; + = we took chips from them)')
opp=[]
for t in H:
    if t==ME: continue
    c=CO.get((ME,t),0)
    if not c: continue
    net=(FLOW.get((ME,t),0)-FLOW.get((t,ME),0))/20/c*100
    opp.append((net,t,c//1000,(NET[t]/20/H[t]*100)))
tot=sum((FLOW.get((ME,t),0)-FLOW.get((t,ME),0)) for _,t,_,_ in opp)
for net,t,r,their in sorted(opp,reverse=True):
    chips=FLOW.get((ME,t),0)-FLOW.get((t,ME),0)
    print('%-26s rounds=%d  us vs them %+7.1f bb/100  chips %+8.0f (%4.1f%% of our net)  their bb/100 at our tables %+7.1f'%(t,r,net,chips,100*chips/tot,their))
print('total net chips we won (flow-attributed): %.0f; our NET %d'%(tot,NET[ME]))
json.dump(sorted(opp,reverse=True),open('out/h2h_us.json','w'))
# pairwise among frequently-seen teams (>=3 rounds together)
print('\nPAIRWISE (row beats column, bb/100 of shared hands, pairs with >=3000 shared hands)')
pairs=[]
names=[t for t in H]
for a in names:
    for b in names:
        if a<b and CO.get((a,b),0)>=3000:
            net=(FLOW.get((a,b),0)-FLOW.get((b,a),0))/20/CO[(a,b)]*100
            pairs.append((abs(net),a,b,net,CO[(a,b)]//1000))
for _,a,b,net,c in sorted(pairs,reverse=True)[:40]:
    if net<0: a,b,net=b,a,-net
    print('%-24s > %-24s %+6.1f  (%d rounds)'%(a,b,net,c))
json.dump([(a,b,net,c) for _,a,b,net,c in pairs],open('out/pairs.json','w'))
