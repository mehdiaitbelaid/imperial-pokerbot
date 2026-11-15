#!/bin/sh
cd "$(dirname "$0")/.."
sh reports/show.sh $1 | grep -v "^  [A-Z]* *[+-][0-9. ]*bb/100 VPIP\|^since V25\|ENDED\|^  preflop\|^  postflop\|^  showdown \|raised preflop then\|bet the flop or turn\|^## WHATIF\|BIGFOLDS\|platform v15\|^TOTAL (1 round\|^## SINCE\|^## TRACK\|^## LABELS\|rounds_played\|BIGCALLS this\|ANKER CHANGE CHECK$" | sed 's/ANKER CHECK (\([0-9]*\) round(s)): /AC\1: /; s/; base / | /g; s/fold to our /f-/g'
