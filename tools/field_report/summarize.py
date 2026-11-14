import json,collections,statistics as St,math,os
os.makedirs('out',exist_ok=True)
F=json.load(open('out/field.json'));GR=json.load(open('global_rounds.json'))
pub=json.load(open(sorted(__import__('glob').glob('public_r*.json'))[-1]))['saturday']['standings']
ME='Resonance Qt'
# ---------- leaderboard-level ----------
per=collections.defaultdict(list)   # team -> list of (G, bb100, span, version, timeouts)
for r in GR:
    for t,v in r['teams'].items():
        per[t].append((r['G'],v['chips']/v['played']/1000*100/20,v['played'],v['version'],v['timeouts']/v['played']))
rows=[]
for i,t in enumerate([x for x in pub if x['ranked'] and x['rounds']>=10]):
    name=t['name'];L=per[name]
    single=[x for x in L if x[2]==1]
    nw=[x[1] for x in single if x[1]<=120];wh=[x[1] for x in single if x[1]>120]
    vers=[x[3] for x in L];ups=sum(1 for a,b in zip(vers,vers[1:]) if b!=a)
    early=[x[1] for x in single if x[0]<=12 and x[1]<=120];late=[x[1] for x in single if x[0]>=13 and x[1]<=120]
    sd=St.pstdev(nw) if len(nw)>1 else float('nan')
    rows.append(dict(rank=i+1,name=name,total=t['bb100'],rounds=t['rounds'],nw_mean=St.mean(nw),nw_se=sd/math.sqrt(len(nw)),nw_n=len(nw),whale=len(wh),
        pos=sum(1 for x in nw if x>0),early=St.mean(early) if early else float('nan'),late=St.mean(late) if late else float('nan'),
        uploads=ups,v_first=vers[0],v_now=t['version'],to=t['timeouts']/t['rounds'],sd=sd))
json.dump(rows,open('out/leaderboard.json','w'),indent=1)
print('LEADERBOARD (total through latest pull; non-whale stats over single-round snapshots R1-R24, whale = round > +120)')
print('%-26s %6s %6s %5s %3s %6s %6s %6s %3s %5s %5s'%('team','total','nwMean','se','wh','pos','early','late','up','ver','to/r'))
for r in rows:
    print('%2d %-23s %+6.1f %+6.1f %5.1f %3d %3d/%-2d %+6.1f %+6.1f %3d %2d>%-2d %4.1f'%(r['rank'],r['name'][:23],r['total'],r['nw_mean'],r['nw_se'],r['whale'],r['pos'],r['nw_n'],r['early'],r['late'],r['uploads'],r['v_first'],r['v_now'],r['to']))
# skill rank by non-whale mean
print('\nNON-WHALE RANKING')
for i,r in enumerate(sorted(rows,key=lambda r:-r['nw_mean'])[:15]): print(i+1,r['name'],'%+.1f ± %.1f'%(r['nw_mean'],r['nw_se']),'board rank',r['rank'])
# upload effect
eff=[]
for t,L in per.items():
    L=[x for x in L if x[2]==1]
    for k in range(1,len(L)):
        if L[k][3]!=L[k-1][3]:
            before=[x[1] for x in L[max(0,k-3):k] if x[1]<=120];after=[x[1] for x in L[k:k+3] if x[1]<=120]
            if before and after: eff.append((t,L[k][0],St.mean(after)-St.mean(before)))
print('\nuploads with 3-round before/after windows:',len(eff),'mean change %+.1f'%St.mean(x[2] for x in eff),'sd %.1f'%St.pstdev(x[2] for x in eff),'positive',sum(1 for x in eff if x[2]>0))
up=[r for r in rows];
hi=[r['nw_mean'] for r in rows if r['uploads']>=6];lo=[r['nw_mean'] for r in rows if r['uploads']<=1]
print('nw mean: teams with >=6 uploads %.1f (n=%d), teams with <=1 upload %.1f (n=%d)'%(St.mean(hi),len(hi),St.mean(lo),len(lo)))
print('late uploads (R18+):',sorted(x for x in eff if x[1]>=18))
