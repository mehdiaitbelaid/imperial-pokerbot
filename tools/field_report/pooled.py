"""Pooled results: our chips vs the board's top 10, vs everyone else, vs the whale; plus leaderboard correlations."""
import json,glob,statistics as St,math,collections
ME='Resonance Qt'
LB=json.load(open('out/leaderboard.json'))
TOP=[r['name'] for r in LB if r['name']!=ME][:9]
print('top group:',TOP)
grp=collections.defaultdict(list)
for f in sorted(glob.glob('hands/saturday_r0*.json')):
    d=json.load(open(f));P=d['players'];me=P.index(ME)
    for h in d['hands']:
        res=h['results'];gain=sum(v for v in res if v>0)
        for x,t in enumerate(P):
            if x==me: continue
            fl=0.0
            if gain>0:
                if res[me]<0 and res[x]>0: fl=-(-res[me]*res[x]/gain)
                elif res[x]<0 and res[me]>0: fl=(-res[x]*res[me]/gain)
            g='top' if t in TOP else ('whale' if t=='ediz_slow' else 'rest')
            grp[g].append(fl/20*100)
T=sum(sum(v) for v in grp.values())
for g,v in grp.items(): print('%-5s seat-hands %6d  %+.2f ± %.2f bb per 100 seat-hands  chips %+7.0f (%.0f%%)'%(g,len(v),St.mean(v),St.pstdev(v)/math.sqrt(len(v)),sum(v)*20/100,100*sum(v)/T))
rows=[r for r in LB if r['name']!='ediz_slow']
def corr(x,y):
    mx,my=St.mean(x),St.mean(y);return sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
y=[r['nw_mean'] for r in rows]
print('corr timeouts/round vs non-whale mean %.2f; uploads vs non-whale mean %.2f (n=%d teams, ediz_slow excluded)'%(corr([r['to'] for r in rows],y),corr([r['uploads'] for r in rows],y),len(rows)))
for lo,hi in ((0,1),(2,5),(6,99)):
    g=[r['nw_mean'] for r in rows if lo<=r['uploads']<=hi];print('uploads %d-%d: n=%d median non-whale %+.1f'%(lo,hi,len(g),St.median(g)))
for r in rows:
    if r['early']==r['early'] and r['late']==r['late']:
        se=r['sd']*math.sqrt(1/12+1/12);d=r['late']-r['early']
        if abs(d)/se>=1.8: print('trend %-22s early %+6.1f late %+6.1f change %+6.1f (%.1f se) uploads=%d v%d->v%d'%(r['name'],r['early'],r['late'],d,abs(d)/se,r['uploads'],r['v_first'],r['v_now']))
