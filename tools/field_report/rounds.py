"""Global per-round deltas for every team from leaderboard snapshots, aligned by global round number."""
import csv,json,collections,os
rows=[r for r in csv.DictReader(open('standings-history.csv')) if r['phase']=='saturday' and r['board']=='saturday']
import glob
for pf in sorted(glob.glob('public_r*.json')):   # public API pulls (no token needed)
    pub=json.load(open(pf))
    for t in pub['saturday']['standings']:
        rows.append(dict(fetched_at=pub['now'],name=t['name'],chips=t['chips'],rounds=t['rounds'],hands=t['hands'],version=t['version'],timeouts=t['timeouts']))
snaps=collections.defaultdict(dict)
for r in rows: snaps[r['fetched_at']][r['name']]=dict(chips=int(r['chips']),rounds=int(r['rounds']),hands=int(r['hands']),version=int(r['version']),timeouts=int(r['timeouts']))
byG={}
for t in sorted(snaps):
    G=max(v['rounds'] for v in snaps[t].values())
    byG[G]=snaps[t]   # latest snapshot for that global round count
Gs=sorted(byG);print('global rounds with snapshots:',Gs)
teams=sorted({n for s in byG.values() for n in s})
rounds=[]
prev={n:dict(chips=0,rounds=0,hands=0,version=None,timeouts=0) for n in teams}
for G in Gs:
    s=byG[G];span=G-(rounds[-1]['G'] if rounds else 0)
    rec=dict(G=G,span=span,teams={})
    for n in teams:
        cur=s.get(n,prev[n])
        dr=cur['rounds']-prev[n]['rounds']
        if dr>0: rec['teams'][n]=dict(chips=cur['chips']-prev[n]['chips'],played=dr,version=cur['version'],timeouts=cur['timeouts']-prev[n]['timeouts'])
        prev[n]=cur
    rounds.append(rec)
json.dump(rounds,open('global_rounds.json','w'),indent=0)
for r in rounds: print(r['G'],r['span'],len(r['teams']),sum(v['chips'] for v in r['teams'].values()))
