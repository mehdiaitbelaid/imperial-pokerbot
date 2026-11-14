# Sunday Table D dossier: our seven opponents

Written Sat 14 Nov 2026, 21:00 UK time. Source: every hand these teams played at our tables in the 54 counted Saturday rounds (7 to 11 rounds, 7,000 to 11,000 hands each), run through Mehdi's `docs/analysis/top_teams.py` (branch `v1`) with the team list changed to this table. Full output: `docs/table-d-raw-profiles.txt`. Rates read k/n; samples under 30 are marked * and are unreliable.

## The format

- Public API (`/pokerbots/api/public`, 20:50): 31 teams in 4 tables; **the top 2 of each table by chips reach the final**; 36 rounds of 1,000 hands, scores from zero; first round Sun 09:00.
- Table D (seed, Saturday average): Resonance Qt (4, +24.0), Anker Batteries (5, +23.1), Chinese people can fly (12, +13.6), WBot (13, +13.4), GamesGone (20, +5.0), Poke (21, +4.5), Anton (28, −20.4), YSL_TWIZZY (29, −20.6).
- The API's `limits` now show `decision_ms: 25` (it was 10 on Saturday) and `bank_s: 10`.
- The bot never sees team names: every rule below needs a seat fingerprint (open size and bet sizes) learned during the round.

## Summary table

| Team | Rounds with us | Their bb/100 there | Chips they gave us (bb/100) | Bot versions | Style |
|---|---|---|---|---|---|
| Anker Batteries | 9 | +7.9 | +8.0 | 6 | tight, c-bets 90% heads up with overbets, never check-raises |
| Chinese people can fly | 10 | −13.2 | **+13.4** | 23 | loose opener, folds 84% to 3-bets, bets 0.33 pot with air and 1.0 pot with value |
| WBot | 9 | **+58.5** | **−8.8** | 9 | bets every street (0.15 pot), raises 25% of bets, defends blinds |
| GamesGone | 10 | +11.0 | +3.9 | 14 | bets 0.5 pot with air and 1.0 pot with value, calls three barrels |
| Poke | 7 | +20.1 | +4.3 | 2 | limps 28% and folds 75% of them to a raise, folds to our bets |
| Anton | 7 | +0.1 | +1.4 | 8 | 3-bets 26 to 32%, folds 88% when his flop bet is raised |
| YSL_TWIZZY | 11 | −32.6 | +5.6 | 6 | nit preflop, calling station postflop, bets only real hands |

## Fingerprints (what a seat shows within about 100 hands)

| Team | Opens | Postflop bet sizes (share of pot) |
|---|---|---|
| Anker Batteries | 2.5bb, 100% of 967 | heads up 1.1, 2.0, 0.7, 0.4; multiway 0.62 |
| Chinese people can fly | 2.5bb 93%, 3bb 6% | 0.33 (65%) or 1.0 (25%); never overbets |
| WBot | 3.5bb (r048) or 2.8bb (r027 to r042) | 0.15 on 71% of turn and 82% of river bets; river 3.0 |
| GamesGone | 2.2bb 95 to 99% | exactly 0.5 or 1.0 |
| Poke | 2.5bb; limps 28% | 0.33, 0.8, 1.6, 0.55, 1.1 |
| Anton | 3bb, 4.5bb, 2.5bb, 6.6bb; 3-bets 3.6x from the blinds | 0.55, 0.8, 0.33, 0.6, 1.1 |
| YSL_TWIZZY | 2.8bb 77%, 2.5bb 20% | 0.48 (57%), 0.77, 0.42, 0.38 |

## Team by team

### Anker Batteries (the other top seed)
- Preflop: VPIP 23, PFR 18. 3-bet 13% (9% in its last three rounds) at 3.0x or 3.2x. Folds to a 3-bet after opening 44% (57% lately, 54/94). **Folds to a 4-bet after 3-betting 78% (138)**. Blinds fold 64% to steals; 80% of our opens got no call.
- As bettor: c-bets 90% heads up (253); 47% of its bets are overbets. Turn barrel 70%, river 49%. **Check-raise 0 of 203.**
- Its overbets are not the nuts: flop 2.0 pot showed weak 4, medium 3, draw 1, value 1 (9*).
- Raised after its bet: folds 71% after a 1.10 bet (17/24*), 50% after 0.40 (12/25*), 7% after 0.62 (1/14*).
- As caller: folds 25% to bets under 40%, 50% at 40 to 75%, 61% at 75 to 110%, 78% to overbets. Calls second and third barrels 65%. Calls the river more lately (folds 28%, 9/32).
- Plan: 4-bet its 3-bets with blockers; raise its 1.10 pot c-bets; bet when it checks (it never check-raises); no river bluffs; thin river value.

### Chinese people can fly (our best source, 23 versions so far)
- Preflop: VPIP 35, PFR 24, opens 44% first in lately. **Folds 84% to our 3-bets (337)**; 81% to anyone's (859). 3-bets 6%, always 3.0x.
- **Size tell, the cleanest at the table.** 0.33 pot shown down: flop air 47, weak 12, draw 11, medium 6; turn air 51, weak 37, draw 32, medium 7, value 1; river air 78, weak 44, medium 13, value 8. 1.0 pot: flop value 15, medium 23, weak 6, air 2; turn value 27, medium 22, weak 1; river value 25, medium 13, air 2, weak 2.
- Barrels the turn 96% and river 95% after betting, mostly 0.33.
- **Raised after a 0.33 bet: folds 80% (119/149).** After a 1.0 bet: folds 20% (8/40).
- As caller: folds 70% to bets of 75 to 110% (365).
- Where we lose to it: folding to its river bets (28 hands, −6,784) and turn bets (27, −5,100), most of them 0.33 bluffs.
- Drift: flop c-bet down from 72% to 45%, flop donk from 65% to 12% in its last three rounds.
- Plan: 3-bet its opens wide; raise or call every 0.33 bet; fold one pair to 1.0 pot bets; bluff it with 0.8 to 1.0 pot.

### WBot (the team that beats us)
- Preflop: VPIP 33, PFR 21. 3-bet 5%. Folds 53% to 3-bets, calls 42%. **Blinds fold only 36% to our steals (151).** After 3-betting it folds to a 4-bet 14% (28*).
- As bettor: c-bets 99%, bets 97% of flops when checked to, 90% of turns, 78% of rivers. River 0.15 pot shown: air 124, weak 113, medium 37, value 6.
- **River 3.0 pot: value 8 of 8. All overbets: turn value 13, medium 11, weak 1, air 1; river value 22, medium 1.**
- **Raised after a 0.15 bet: folds 79% (123/155).** After 0.40: folds 37% (14/38). After 0.75: calls or re-raises.
- As caller it raises 22 to 30% of bets. Its flop raises of 75 to 110% are bluff heavy (air 19, draw 12, weak 9, medium 12, value 1); its overbet raises and its turn and river raises are value.
- Where we lose: showdowns after its last bet on the turn (16 hands, −13,289) and river (51 hands, −7,900).
- Plan: raise the 0.15 bets; call them with any pair; **fold one pair to its turn and river overbets**; do not fold top pair to a pot-size flop raise; steal less from its blinds; value bet big.

### GamesGone
- Preflop: VPIP 27, PFR 16, opens 2.2bb. 3-bet 3%, value only. Folds 36% to our 3-bets (53), calls 49%.
- **Size tell.** 0.5 pot: flop air 56, weak 22, draw 20, medium 7, value 1; turn weak 38, air 37, draw 32, medium 8, value 1; river air 46, weak 28, value 2, medium 1. 1.0 pot: flop medium 40, value 15, weak 13, draw 12, air 5; turn value 37, medium 36, weak 20; river value 14, medium 9, weak 5, air 1.
- **Raised after a 0.5 bet: folds 74% (122/164).** After 1.0: folds 31% (24/78).
- C-bets 100% heads up, barrels the turn 100%.
- **Calls down: folds 32% to a second barrel (145) and 18% to a third (57).** Folds 88% to a river bet after a checked turn (33).
- Its turn and river raises are value (18 of 22).
- Where we lose: folding to its turn and river bets (45 hands, −11,928) and our river bluffs called (8 hands, −5,276).
- Plan: raise or call the 0.5 bets; fold one pair to 1.0 bets; never fire three barrels as a bluff; one bet after a checked turn.

### Poke
- Preflop: VPIP 43, PFR 17. **Limps 28% and folds 75% of limps to a raise (822).** Blinds fold 16% to opens of 2.25bb or less and 76% to opens above 3bb.
- Size tell: 1.6 pot is value (flop value 14, draw 4, air 3, medium 2, weak 1; turn value 15, draw 3, medium 2). Flop 0.8 pot is bluff heavy (air 31, draw 10, medium 7, weak 4). 0.33 pot is mixed with many top pairs (flop medium 41, weak 27, air 17, draw 8).
- Raised after betting: folds 59% after 0.33 (85/143), **71% after 0.80 (34/48)**.
- **Folds to our bets: flop 69% (101), turn 79% (66), river 91% (34).** After checking, folds 80% to a turn stab (141). Check-raise 1 of 353.
- Plan: raise every limp; open 3bb or more when Poke is in the blinds; bet when it checks; raise its 0.8 flop bets; fold to 1.6 pot bets without two pair or better.

### Anton
- Preflop: VPIP 32, PFR 27. **3-bets 26% (32% in its last two rounds)**; 3-bets 52% of our steals (115). 3-bet range shown is any two cards (119 hands, no hand above 4%). Folds to a 4-bet after 3-betting 59% (179), 66% lately (45/68). 4-bets 2.3x.
- Open size tell: 6.6bb showed AA, KK, AK, AQs (18*); 2.5bb showed A7o, 22, 74s, 97o, 53o (12*).
- **Raised after betting: folds 83% (54/65), 88% on the flop (42/48).**
- Size tell: 0.60 pot is value or top pair (flop 8 of 11, turn 6 of 6, river 4 of 4*); 0.55 and 0.80 are air or weak pairs most of the time; overbets are value.
- As caller: folds 68% to bets of 75 to 110% (86% lately, 24/28*).
- Where we lose: showdowns after its last bet (24 hands, −14,939) and folding to its 4-bets (30 hands, −4,684).
- Plan: 4-bet its 3-bets; raise its c-bets; do not call down with ace high in 3-bet pots; fold one pair to its overbets and shoves.

### YSL_TWIZZY
- Preflop: VPIP 20, PFR 16. **Folds 85% to our 3-bets (184) and 84% of blinds to our steals (174).**
- **Calling station: folds 5% to bets under 40% (264), 29% at 40 to 75%, 39% at 75 to 110%, 45% to overbets. Folds 27% to a second barrel and 24% to a third.** Goes to showdown 46% of the time.
- **Its bets are real.** Flop 0.48: medium 32, value 2. 0.77: value 33 of 34 across streets. Turn 0.48: medium 25, value 8, weak 6, air 1. Only its 0.38 flop bet is air (6 of 6*).
- Raised after betting: never folds (0 of 51). Its own raises are value (23 of 23).
- Plan: steal and 3-bet every time; never bluff after the flop; value bet big with top pair or better; fold one pair to 0.77 bets and to any raise.

## What the table has in common

1. **Fixed bet sizes with a meaning.** Five of the seven teams bluff with one size and value bet with another. A per-seat table "size → what was shown, and how often it folds to a raise" is the largest edge available.
2. Small-bet raises (already in V21) fit Chinese people can fly, WBot and Anton. GamesGone's bluff size is 0.5 pot and Poke's is 0.8, which V21's "under 40%" limit misses.
3. Two calling stations (YSL_TWIZZY, GamesGone on later streets): bluffs must stop against a seat that keeps calling.
4. Preflop money: Chinese people can fly and YSL_TWIZZY fold 84 to 88% to 3-bets; Poke folds 75% of limps; Anton's 3-bets fold 59 to 66% to a 4-bet.
5. Teams change bots: Chinese people can fly 23 versions, GamesGone 14, WBot 9, Anton 8. Every rule needs a live stop condition.

## Limits

- Only hands at our tables; each team's data mixes several of its bot versions.
- Showdown samples per exact size are small for Anker Batteries, Anton and Poke overbets.
- All postflop rates are for single pots, most of them heads up.
