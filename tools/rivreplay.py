"""Replay our real river calls of pot-sized bets through builds; count folds and chips saved.
    HANDS=hands python3 tools/rivreplay.py upload/bot.py upload/bot_v18r.py"""
import importlib.util,json,glob,sys,os
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
mods=[load(p,'m%d'%i) for i,p in enumerate(sys.argv[1:])]
START,BB=2000,20
tot={i:[0,0,0.0] for i in range(len(mods))}  # folds, n, bb saved
for f in sorted(glob.glob(os.path.join(os.environ.get('HANDS','hands'),'saturday_r0[0-9][0-9].json'))):
    d=json.load(open(f));n=len(d['players']);me=d['seat'];rd=int(f[-8:-5])
    if rd<3: continue
    agents=[m.Agent() for m in mods]
    for A in agents: A.on_table_start({"seat":me,"num_players":n,"hands":1000})
    for h in d['hands']:
        hist=[];street='preflop';board=[];posted=0
        stacks=[START]*n;bets=[0]*n;folded=[False]*n;pot=0;cur=0;min_inc=BB;rs=0
        for ev in h['events']:
            if ev[0]=='post':
                s,amt=ev[1],ev[2];hist.append({"seat":s,"street":"preflop","action":"small_blind" if posted==0 else "big_blind","amount":amt});posted+=1
                stacks[s]-=amt;bets[s]+=amt;pot+=amt;cur=max(cur,bets[s])
            elif ev[0]=='board':
                street=ev[1];board=ev[2];bets=[0]*n;cur=0;min_inc=BB;rs=0
            elif ev[0]=='refund':
                stacks[ev[1]]+=ev[2];pot-=ev[2]
            elif ev[0]=='act':
                s,a,amt=ev[1],ev[2],ev[3]
                if s==me and street=='river' and a=='call' and cur>bets[s]:
                    to_call=min(cur-bets[s],stacks[s])
                    if to_call>=0.9*(pot-to_call):
                        max_to=bets[s]+stacks[s];can=max_to>cur
                        st={"type":"act","hand_number":h["n"],"street":street,"seat":s,"button":h["button"],"hole_cards":h["hole"][str(me)],"board":list(board),
                            "small_blind":10,"big_blind":BB,"blind_level":0,"pot":pot,"stacks":list(stacks),"bets":list(bets),"folded":list(folded),"to_call":to_call,
                            "min_raise_to":min(cur+min_inc,max_to) if can else None,"max_raise_to":max_to if can else None,
                            "legal_actions":["fold","call"]+(["raise"] if can else []),"betting":"no_limit","raise_cap":None,"raises_this_street":rs,"history":list(hist)}
                        res=h['results'][me]
                        for i,A in enumerate(agents):
                            votes=[A.act(dict(st))["action"] for _ in range(5)]
                            fold=votes.count('fold')>=3
                            tot[i][1]+=1
                            if fold:
                                tot[i][0]+=1
                                # chips if we had folded: we lose what we had in before the call, i.e. result + to_call if we lost, or forgo the win
                                tot[i][2]+=((-res if res<0 else 0) - (to_call if res<0 else 0) + (0 if res<0 else -(res+to_call)))/BB if False else ((to_call if res<0 else -(res+to_call)))/BB
                        print("r%03d#%d %s board %s bet %d into %d result %+d -> %s"%(rd,h['n'],''.join(h['hole'][str(me)]),' '.join(board),to_call,pot-to_call,res,[ 'fold' if [A.act(dict(st))['action'] for _ in range(1)][0]=='fold' else 'call' for A in agents]))
                hist.append({"seat":s,"street":street,"action":a,"amount":amt})
                if a=='raise':
                    inc=amt-cur
                    if inc>=min_inc:min_inc=inc
                    stacks[s]-=amt-bets[s];pot+=amt-bets[s];bets[s]=amt;cur=amt;rs+=1
                elif a=='call':
                    stacks[s]-=amt;pot+=amt;bets[s]+=amt
                elif a=='fold': folded[s]=True
        shown={k:v for k,v in h['hole'].items() if k in (h.get('showdown') or {})}
        summ={"history":hist,"board":h["board"],"shown":shown,"stacks":[0]*n,"results":h["results"]}
        for A in agents:
            try: A.on_hand_end(summ)
            except Exception: pass
for i,p in enumerate(sys.argv[1:]): print(p.split('/')[-1],"folds %d of %d big river calls, chips saved %+.0f bb"%(tot[i][0],tot[i][1],tot[i][2]))
