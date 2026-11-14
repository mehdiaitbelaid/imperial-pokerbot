#!/bin/sh
# wait_round.sh N : block until at least N counted rounds played by platform version >= 7 exist, then fetch hands.
cd "$(dirname "$0")/.."
N=${1:-1}
T=$(cat team.token)
i=0
while [ $i -lt 110 ]; do
  C=$(curl -s -m 20 -A "Mozilla/5.0" -H "Authorization: Bearer $T" https://imperialaihack.com/api/poker/results | python3 -I -c "import sys,json; d=json.load(sys.stdin); print(sum(1 for r in d['rounds'] if 'practice' not in r['ref'] and r['version']>=7))" 2>/dev/null)
  if [ "${C:-0}" -ge "$N" ]; then break; fi
  sleep 5; i=$((i+1))
done
python3 fetch_hands.py --token "$T" | tail -1
echo "rounds played by V18 so far: ${C:-0}"
