#!/bin/sh
# cycle.sh NNN [sum] : compact analysis of round NNN for the tracker. V22 = r002-r007, V24 = r008 on.
cd "$(dirname "$0")/.."
N=$1
F=hands/sunday_s1_r$N.json
T=$(cat team.token)
V22FILES=$(ls hands/sunday_s1_r00[2-7].json)
V24FILES=$(ls hands/sunday_s1_r00[89].json hands/sunday_s1_r01*.json hands/sunday_s1_r020.json)
PV=$(python3 -I -c "import json; print(json.load(open('$F'))['round']['version'])")
B=upload/bot_v24.py; [ "$PV" -ge 16 ] && B=upload/bot_v25.py
V25FILES=$(python3 -I -c "
import json,glob
print(' '.join(f for f in sorted(glob.glob('hands/sunday_s1_r*.json')) if json.load(open(f))['round']['version']>=16))")
echo "## ROUND $N  $(TZ=Europe/London date +%H:%M:%S)"
python3 -I -c "import json,sys; r=json.load(open('$F'))['round']; print({k:r[k] for k in ('ref','version','bb100','chips','timeouts','errors','bank_out','think_s')}, 'violations', len(r['violations']))"
curl -s -m 20 -A "Mozilla/5.0" -H "Authorization: Bearer $T" https://imperialaihack.com/api/poker/results > /tmp/rq_results.json 2>/dev/null
j=0; while [ $j -lt 8 ]; do curl -sL -m 20 -A "Mozilla/5.0" https://poker.imperialaihack.com/pokerbots/api/public > /tmp/rq_public.json 2>/dev/null; python3 -I -c "import json,sys; sys.exit(0 if json.load(open('/tmp/rq_public.json'))['sunday']['stages'][0]['rounds_played']>=int('$N') else 1)" 2>/dev/null && break; sleep 5; j=$((j+1)); done
python3 -I reports/standings.py /tmp/rq_results.json < /tmp/rq_public.json 2>&1 | grep -v "sunday/s1/r\|since V22"
python3 -I -c "
import json
r=[x for x in json.load(open('/tmp/rq_results.json'))['rounds'] if x['ref'].startswith('sunday')]
for v in sorted({x['version'] for x in r}):
    y=[x for x in r if x['version']==v]
    print('  platform v%d: %d rounds, avg %+.1f bb/100, chips %+d, timeouts %d, max think %.2f | %s'%(v,len(y),sum(x['bb100'] for x in y)/len(y),sum(x['chips'] for x in y),sum(x['timeouts'] for x in y),max(x['think_s'] for x in y),' '.join('%+.0f'%x['bb100'] for x in sorted(y,key=lambda x:x['ref']))))"
echo "## LABELS"
python3 reports/labels.py $B $F 2>&1 | cut -c1-900
echo "## TRACK"
python3 -I reports/track.py $F --top 6 2>&1 | grep -v "dossier:\|n=  0 \|^$" | cut -c1-330
echo "## ENDED / LEAKS"
python3 tools/analyze.py $F --me 2>&1 | sed -n '/Our chips by/,/showdown/p' | sed -n '2,4p'
python3 tools/leaks.py $F --worst 0 2>&1 | sed -n '2,5p'
echo "## BIGCALLS this round (one pair or less)"
python3 -I reports/bigcalls.py $F --list 2>&1 | grep "#" | cut -c1-170
echo "## BIGFOLDS this round"
python3 -I reports/bigfolds.py $F 2>&1 | cut -c1-220
echo "## SINCE V25 (r021 on)"
python3 -I reports/barrels.py $V25FILES 2>&1 | cut -c1-200
python3 -I reports/bigfolds.py $V25FILES 2>&1 | head -1
python3 tools/smallraise_live.py $V25FILES 2>&1 | head -3 | cut -c1-160
echo "## ANKER flop+turn called, river (build $B) this round"
python3 reports/anker3.py $B $F 2>&1 | cut -c1-200
if [ -n "$V25FILES" ]; then echo "## ANKER since V25"; python3 reports/anker3.py upload/bot_v25.py $V25FILES 2>&1 | sed -n '/TOTAL/,$p'; python3 -I reports/track.py $V25FILES --top 0 2>&1 | sed -n '1p;/CHIPS FROM/,+1p'; fi
echo "## ANKER CHANGE CHECK"
python3 -I reports/ankcheck.py $F 2>&1 | cut -c1-700
echo "since V25:"; python3 -I reports/ankcheck.py $V25FILES 2>&1 | cut -c1-700
echo "## ANKER vs OUR 3-BETS"
python3 -I reports/ank4.py $F 2>&1
echo "## WHATIF"
python3 tools/whatif.py $B $F 300 2>&1 | tail -1 | cut -c1-200
if [ "$2" = "sum" ]; then
  echo "## SUMMARY V25 (r021..r$N)"
  python3 -I reports/track.py $V25FILES --top 0 2>&1 | grep -v "dossier:\|^$\|BIGGEST" | cut -c1-330
fi
