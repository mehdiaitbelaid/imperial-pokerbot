#!/bin/sh
# wait.sh NNN [sum] : poll until round NNN is on disk, then write reports/cycle_rNNN.txt
cd "$(dirname "$0")/.."
N=$1; i=0
while [ ! -f hands/sunday_s1_r$N.json ] && [ $i -lt 40 ]; do
  python3 fetch_hands.py --token "$(cat team.token)" >/dev/null 2>&1
  [ -f hands/sunday_s1_r$N.json ] && break
  sleep 20; i=$((i+1))
done
[ -f hands/sunday_s1_r$N.json ] && sh reports/cycle.sh $N $2 > reports/cycle_r$N.txt 2>&1
echo "END" >> reports/cycle_r$N.txt
