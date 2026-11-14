#!/bin/sh
# Full V19-vs-v14 battery: duplicate duels (same cards, seats swapped) on nine table types,
# then the final format (5,000 hands, strict clock, 10 s bank).
cd "$(dirname "$0")/.."
A=upload/bot_v19.py; B=upload/bot_v14.py
F="field/gherk.py field/attn.py field/claudeb.py field/vlad.py field/wbot.py field/jump.py"
echo "start $(TZ=Europe/London date +%H:%M:%S)"
python3 tools/duplicate.py $A $B --label "T1 real-like, no whale" --field $F --rounds 30 --seed 11
python3 tools/duplicate.py $A $B --label "T2 top teams + teammates' bots" --field field/gherk.py field/attn.py rivals/m_v3.py rivals/h_var.py rivals/s_v18r.py rivals/m_vf2.py --rounds 30 --seed 12
python3 tools/duplicate.py $A $B --label "T3 with the whale (ediz_like)" --field sparring/ediz_like.py field/gherk.py field/attn.py field/claudeb.py field/wbot.py field/ysl.py --rounds 30 --seed 13
python3 tools/duplicate.py $A $B --label "T4 kit bot + limping fish" --field sparring/starter.py field/fisher.py field/nd.py field/jump.py field/vlad.py field/claudeb.py --rounds 30 --seed 14
python3 tools/duplicate.py $A $B --label "T5 small-bet TRAPS (worst case)" --field sparring/smalltrap.py sparring/smalltrap.py field/gherk.py field/attn.py field/vlad.py field/jump.py --rounds 30 --seed 15
python3 tools/duplicate.py $A $B --label "T6 stations + maniac" --field sp2/calling_station_plus.py sparring/station_plus.py sp2/lag_basic.py sp2/pot_odds_bot.py sparring/maniac.py field/nd.py --rounds 30 --seed 16
python3 tools/duplicate.py $A $B --label "T7 pot-limit" --betting pot_limit --field $F --rounds 12 --seed 17
python3 tools/duplicate.py $A $B --label "T8 fixed-limit" --betting fixed_limit --field $F --rounds 12 --seed 18
python3 tools/duplicate.py $A $B --label "T9 raise cap 3" --raise-cap 3 --field $F --rounds 12 --seed 19
echo "--- final format: 5,000 hands, strict 10 ms, 10 s bank, one table at a time"
python3 local_sim.py $A $B $F --rounds 1 --hands 5000 --seed 20 2>&1 | grep -E "bot  |upload"
echo "end $(TZ=Europe/London date +%H:%M:%S)"
