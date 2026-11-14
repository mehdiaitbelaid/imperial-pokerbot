"""Reconstruct each round's table line-ups from leaderboard chip deltas.
Every table is zero-sum, so a round's teams must split into groups of 6-8 whose chip changes sum to exactly 0.
Exact-cover search with meet-in-the-middle subset sums; counts solutions up to 2 to test uniqueness.
Blind validation: our own table (known from our hand file) is NOT given to the solver and must appear in the answer."""
import json,glob,sys,itertools,collections,time
R=json.load(open('global_rounds.json'))
ours={}
for f in glob.glob('hands/saturday_r0*.json'):
    d=json.load(open(f));ours[int(f[-8:-5])]=tuple(sorted(d['players']))
SIZES=(6,7,8)
def groups_with(p,rest,delta):
    """all subsets g of rest with len(g)+1 in SIZES and sum(delta)==-delta[p]"""
    target=-delta[p];rest=list(rest);h=len(rest)//2;A,B=rest[:h],rest[h:]
    idx=collections.defaultdict(list)
    for k in range(0,max(SIZES)):
        for c in itertools.combinations(B,k):
            idx[(sum(delta[t] for t in c),k)].append(c)
    out=[]
    for k in range(0,max(SIZES)):
        for a in itertools.combinations(A,k):
            sa=sum(delta[t] for t in a)
            for need in SIZES:
                kb=need-1-k
                if kb<0:continue
                for b in idx.get((target-sa,kb),()):
                    out.append((p,)+a+b)
    return out
def cover(rem,delta,limit=2,found=None,path=()):
    if found is None: found=[]
    if not rem: found.append(path);return found
    n=len(rem)
    if n<6: return found
    p=max(rem,key=lambda t:abs(delta[t]))
    for g in groups_with(p,[t for t in rem if t!=p],delta):
        r2=rem-set(g)
        if r2 and len(r2)<6: continue
        cover(r2,delta,limit,found,path+(tuple(sorted(g)),))
        if len(found)>=limit: break
    return found
res={}
for r in R:
    if r['span']!=1: continue
    G=r['G'];T=r['teams'];t0=time.time()
    if sum(v['chips'] for v in T.values())!=0: print(G,'not zero-sum, skipped');continue
    names=sorted(T);delta={n:T[n]['chips'] for n in names}
    sols=cover(frozenset(names),delta)
    ok=None
    if sols and G in ours: ok=ours[G] in sols[0]
    res[G]=dict(groups=[list(g) for g in sols[0]] if sols else None,n_solutions=len(sols),ours_recovered=ok)
    print(G,len(names),'solutions:',len(sols) if len(sols)<2 else '>=2', 'sizes',[len(g) for g in sols[0]] if sols else None,'our table recovered' if ok else ok,'%.1fs'%(time.time()-t0),flush=True)
json.dump(res,open('tables.json','w'),indent=1)
