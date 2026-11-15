#!/bin/sh
# show.sh NNN : wait (max ~150 s) for reports/cycle_rNNN.txt to be complete, then print it compactly
cd "$(dirname "$0")/.."
i=0; until grep -q "^END" reports/cycle_r$1.txt 2>/dev/null || [ $i -ge 30 ]; do sleep 5; i=$((i+1)); done
TZ=Europe/London date +%H:%M:%S
grep -q "^END" reports/cycle_r$1.txt 2>/dev/null || { echo NOTYET; exit 0; }
grep -v "^  [A-Z]* *n= *[0-9]* | we folded\|^[0-9]* round(s)$\|OUR RIVER BETS OF\|^OPPONENTS\|^  platform v1[34]\|who 4-bet\|^THEIR 3-BETS\|^  [A-Z]* *n= *[0-9] of.*opps, light=  [0-9] |\|^  [A-Z]*  *[0-9<.+-]*  *n=  [12] |\|^       bets\|(no showdown)\|would have lost\|^  [A-Z]* *n= *[0-9]* folded *[0-9]* net\|^  vs \|^   [A-Z]\|blinds / folded" reports/cycle_r$1.txt | cut -c1-900
