# Live counted rounds: what we do wrong

Source: `review/live_diagnosis.py` run on `hands-data/hands/saturday_r001.json` to `saturday_r004.json` (refreshed with `pull.py` at the start and before writing). Every figure below is printed by that script. bb/100 is over all hands of the version in question. n is the number of opportunities; anything marked * has n under 30 and is unreliable. A "commit call" is the call that takes our total investment in the hand past 30 bb (600 chips); "gain from folding" compares the actual result with folding at that action, holding everything else fixed.

| Version | Bot | Counted rounds | Hands | Result |
|---|---|---|---|---|
| 5 | vastra-fable-r2.py | r001 (-7.9), r002 (-18.9) | 2000 | -13.4 bb/100 |
| 6 | riad_avengers_v14.py (likely) | r003 (+36.9), r004 (+65.2) | 2000 | +51.0 bb/100 |

Most of the analysis is on v5 because that is the bot that lost. v6 numbers sit next to it where they matter.

## (a) What we are doing wrong

Loss decomposition, v5, exclusive buckets (sum = -13.4 bb/100, equal to the site total):

| Bucket | n | v5 bb/100 | v6 bb/100 (n) |
|---|---|---|---|
| Showdown lost, money in before the river or river checked | 31 | -69.6 | -74.0 (19) |
| Showdown lost after a river call | 8 | -26.5 | -19.6 (6) |
| Blinds folded without contest | 1631 | -14.9 | -14.5 (1508) |
| Called preflop, folded flop or turn | 41 | -10.3 | -13.6 (61) |
| Raised preflop, no c-bet, folded flop or turn | 23 | -9.7 | -7.2 (26) |
| River fold | 10 | -7.5 | -16.2 (16) |
| Opened then folded to a 3-bet | 15 | -4.3 | -5.0 (24) |
| Called preflop then folded preflop | 12 | -1.3 | -2.7 (10) |
| C-bet then folded | 3 | -0.9 | -6.5 (10) |
| BB checked, folded flop or turn | 4 | -0.2 | -0.3 (2) |
| Walks | 11 | +0.3 | 0 |
| Won preflop uncontested | 114 | +12.5 | +28.8 (188) |
| Won postflop without showdown | 62 | +28.3 | +43.6 (86) |
| Showdown won | 35 | +90.6 | +138.3 (44) |

The three buckets carrying the v5 loss are showdowns lost with the money already in (-69.6), showdowns lost after a river call (-26.5) and the blind tax (-14.9, structural). The difference between v5 and v6 is not in losing showdowns (both lose about the same there) but in what they win: v6 wins +138.3 at showdown and +43.6 without showdown against +90.6 and +28.3 for v5.

Ranked mistakes:

| # | Mistake | Evidence | Measured cost | Fix as a rule | Expected gain |
|---|---|---|---|---|---|
| 1 | v5 pays off big postflop bets with one pair or less | Commit calls with one pair or worse: n=14*, won 3. Top pair commit calls on flop, turn, river: 3, 4, 2, won 1 of 9. Five of the ten biggest losses are this line (hands 3, 4, 6, 7, 10 below). | Folding at the commit call would have saved 8,129 chips = +20.3 bb/100* | Facing a bet or raise where calling takes our total in past 30 bb: continue only with two pair or better that uses both or one hole card and is not just the board pair; with top pair or an overpair continue only if this seat's learned river plus turn bet frequency this round is above 50% or it has shown a bluff at showdown; otherwise fold. | Up to +20 bb/100 on the v5 sample. Caution: the same counterfactual on v6 is -26.0 bb/100 (n=16*, won 9), so v6's calls were right. The seat condition is what makes the rule safe. |
| 2 | v5 calls big river bets with bluff catchers | River calls of bets over 60% pot: 7*, won 2; folding instead gains 3,408 chips (+8.5 bb/100). River calls of 60% pot or less: 6*, won 3; folding instead would lose 2,948 chips. Calls over 60% pot by our class: top pair 4 (won 1), trips 1 (lost to a full house), weak pair 2 (won 1). | Bucket "showdown lost after river call" -26.5 bb/100 (n=8*) | On the river versus a bet over 60% pot, call with top pair or weaker only when the seat's river bet frequency this round is above 45% or its showdowns after big river bets include a hand with no made hand; keep calling bets of 60% pot or less with any pair. | About +8.5 bb/100 on v5 (n=7*). v6 made 2 such calls (top pair 1, weak pair 1, both lost, +2,352 chips from folding). |
| 3 | v5 does not bet the river | Checked to on the river we bet 17% (n=46) against 33% to 47% for the four winners and 50% for v6 (n=42). Two hands of two pair or better reached showdown without our river bet, both lost (-4,000 chips). Pots that ended on the river: v5 -14.1 bb/100, v6 +28.3. | Not measurable as a counterfactual (we cannot see what a bet would have been paid) | Heads up on the river, checked to: bet 0.6 to 0.8 pot with top pair good kicker or better; with no made hand bet the same size only against a seat whose learned fold to river bet is above 45%. | Not measurable from this data. The v5 to v6 swing in river-ended pots is 42 bb/100, but v6 changed many things at once. |
| 4 | We fold too often to flop bets, in both versions | After our check opponents bet the flop 51% (39/76) in v5 and 67% (43/64) in v6. We folded to that bet 64% (25/39) in v5 and 56% (24/43) in v6. Facing a 40% to 75% pot flop bet we fold 58% (18/31) in v5 and 58% (42/73) in v6; a pure bluff at that size needs 37% folds. | Bucket "called preflop, folded flop or turn": -10.3 bb/100 (n=41) in v5, -13.6 (n=61) in v6. Plus "raised preflop, no c-bet, folded": -9.7 (n=23*) and -7.2 (n=26*). | Versus a single flop bet of 75% pot or less, continue with any pair, any 8 out draw, or two overcards with a backdoor draw; when the seat's learned c-bet or flop bet after our check exceeds 65%, add ace high. Target fold rate below 45% at that size. | Not measurable directly; the two buckets cap the recoverable loss at about 20 bb/100 per version. |
| 5 | Early position opens with non-premium hands | Unraised-pot opens from UTG to HJ outside the top 5%: v5 n=69, -4,068 chips, -2.95 bb per open (-10.2 bb/100); v6 n=92, -0.94 bb per open (-4.3 bb/100). MP opens outside the top 5% lose in both: v5 25 at -3.27 bb, v6 28 at -7.21 bb. Top 5% opens from the same seats: v5 +3.11 bb (n=40), v6 +20.97 bb (n=43). | -10.2 bb/100 (v5), -4.3 (v6) | From UTG to MP open only 77+, AJs+, AQo+, KQs; from HJ add 55+, ATs+, KJs+, QJs. Overlaps with mistake 1: several of those stacks were lost postflop with these hands. | Up to +10 bb/100 (v5) and +4 (v6), not additive with mistake 1. |
| 6 | Suspected timeouts on premium hands | Folds facing a bet with a top 5% hand: v5 7 (TT, 99, AKs, AKo, KQs x3; site counted 8 timeouts), v6 6 (AKo, KQs, JJ x2, TT, 99; site counted 12). No folds of two pair or better postflop. No v5 strong river checks without a bet that we can tie to a timeout. | Realised result of those hands: -1,056 chips (-2.6 bb/100) v5, -855 chips (-2.1) v6. The value lost from folding premium hands is larger but not observable. | Answer every preflop decision from a lookup before any simulation, and make the deadline fallback "call or raise with a top 5% hand" instead of the engine default of check or fold. | Small, about 2 to 3 bb/100 plus the unseen value. |
| 7 | Blind tax | Blinds folded without contest -14.9 bb/100 (n=1631) v5, -14.5 (n=1508) v6. BB per 100 hands in that seat: v5 -7.0, v6 -51.9. SB: v5 +115.3, v6 -28.8. | -14.9 bb/100 | Structural, not a mistake. Folding every hand scores -18.75. | None expected. |

Not a leak: our c-bet frequency (76%, n=50, v5) matches the winners (76% to 79%, matcha 40%). Our fold to 3-bet is 38% (12/32) in v5, below every winner (43% to 55%).

Late position (question 2), v5: folded to us in CO 130 times, BTN 93, SB 23*. We opened 20% (26/130), 39% (36/93), 78% (18/23*). After our open everyone folded 73% (19/26*) from CO, 50% (18/36) from BTN, 56% (10/18*) from SB; we were 3-bet 4%, 6%, 6%. The late opens earned +0.36 bb each (n=80). The winners: Gherkers CO 30% (116), BTN 66% (62), SB 93% (28*), earning -1.58 bb per late open (n=102); Equity Engine 35%, 45%, 55% (80, 56, 55), +4.07 bb per open (n=83); The Market Makers 26%, 51%, 15% (82, 47, 13*), +0.01 (n=47); matcha 22%, 33%, 67% (27*, 15*, 3*), +9.56 (n=13*). Stealing more is not where the winners make their money. v6 at r003 was almost never folded to on the BTN or SB because ediz_slow entered every pot from UTG.

## (b) What the winners do differently

The four top five teams that sat with us (Attention Is All In never did). Rows are the hands they played at our tables.

| Team | Hands | bb/100 | VPIP | PFR | 3-bet | Fold to 3-bet | Open CO/BTN/SB | C-bet (median size) | Turn bet (size) | River bet (size) | Fold to bet F/T/R | Won at showdown |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| matcha mille crêpes cake | 1000 | +63.7 | .17 | .10 | .05 | .55 (20*) | .22/.33*/.67* | .40 (0.60) n30 | .48 (0.60) n48 | .42 (0.60) n36 | .37/.16/.30* | .68 (47) |
| The Market Makers | 1000 | +12.1 | .23 | .14 | .04 | .47 (17*) | .26/.51/.15* | .77 (0.70) n43 | .62 (0.70) n74 | .47 (0.70) n40 | .42/.56/.60* | .54 (41) |
| Equity Engine | 2000 | +4.1 | .23 | .18 | .02 | .54 (78) | .35/.45/.55 | .77 (0.50) n69 | .43 (0.80) n93 | .41 (0.80) n61 | .51/.44/.32 | .40 (72) |
| Gherkers | 2000 | +73.4 | .32 | .25 | .26 | .43 (35) | .30/.66/.93* | .76 (0.70) n92 | .52 (0.70) n122 | .36 (1.08) n59 | .54/.63/.71* | .60 (60) |
| Us v5 | 2000 | -13.4 | .18 | .12 | .03 | .38 (32) | .20/.39/.78* | .76 (0.60) n50 | .38 (0.75) n85 | .17 (0.70) n46 | .48/.40/.38* | .47 (74) |
| Us v6 | 2000 | +51.0 | .24 | .17 | .11 | .40 (47) | .27/.56/1.00* | .88 (0.80) n59 | .48 (0.80) n84 | .50 (0.80) n42 | .47/.42/.46 | .64 (69) |

3-bet opportunities exceed 400 for every row. Fold to bet sample sizes (flop/turn/river): matcha 65/32/20, Market Makers 76/43/15, Equity Engine 140/57/31, Gherkers 168/68/28, v5 101/57/26, v6 144/73/35. Hands shown after a river bet of two thirds pot or more: matcha 4 (flush, set, top pair, no made hand), Market Makers 7 (top pair 4, straight, set, flush), Equity Engine 4 (set 2, top pair, weak pair), Gherkers 4 (top pair 2, two pair, flush), us v5 4 (no made hand 3, top pair), v6 7 (no made hand 3, overpair, flush, weak pair, top pair).

The winners bet the river when checked to two to almost three times as often as v5 did (33% to 47% against 17%), and when their big river bets get called they mostly show made hands, top pair or better, so they get paid by value instead of paying off. They do not win by stealing: their late position open rates bracket ours and their late opens earn between -1.58 and +9.56 bb each, while matcha, the tightest player at our tables (VPIP .17), was the second best earner. Gherkers is the one outlier with a 26% 3-bet rate against 2% to 5% for everyone else including v5 at 3%; v6 moved toward that profile (3-bet 11%, river bet 50%, showdown win 64%) and is the version that is winning.

## (c) The ten biggest losing hands, v5

All ten lost the full 100 bb stack (-2000 chips).

| # | Hand | Seat | Cards | Board | Our line | Opponent shown | Mistake |
|---|---|---|---|---|---|---|---|
| 1 | r001#210 | BB | ATo | 3d Tc Ad Kd 4c | call pre; bet flop, call raise; bet turn, call all-in | Equity Engine AA, set | Cooler (two pair against a set) |
| 2 | r001#219 | BTN | A4s | Qd 5d 2h Ah As | open; call flop, turn and a 1,332 river bet | AIl IN A5s, full house | Call, partly cooler (trips with a 4 kicker on a paired board) |
| 3 | r001#835 | BTN | ATs | Qh Kd As 7s 3h | call pre; call 290, 870, 770 | The Market Makers AQo, two pair | Call (top pair weak kicker calls three streets) |
| 4 | r002#71 | HJ | A9o | 7h 8d Qs Jh 8c | call, then re-raise to 672; check-call 565 flop, 763 turn | Durahim 1453 22 | Preflop entry and call (no made hand called off) |
| 5 | r002#184 | MP | KQo | Td 5c Kc 8c 2c | call pre; bet flop, bet turn, raise river all-in | matcha AJo, nut flush | Cooler (second best flush) |
| 6 | r002#205 | BTN | 66 | Ts Ks Qs 7c 3h | call, then re-raise to 662; call 1,338 flop shove | Durahim 1453 97s, flush | Preflop entry and call (66 calls off on a monotone broadway flop) |
| 7 | r002#266 | UTG | 88 | Ac Jd 5h 7c 2d | open; bet flop, call 600 raise; check-call 1,265 turn | WBot AJs, two pair | Call (underpair calls off against a raise on an ace high board) |
| 8 | r002#280 | MP | 66 | 6h 7c 4c 9s 8d | open; raise flop, raise turn, call 996 river | WBot 54s, straight | Mostly cooler; river call with a set on a four card straight board |
| 9 | r002#435 | BB | QQ | 5d 4c 4d 3s 2h | 3-bet, call all-in preflop | AIl IN AKo, straight | Unavoidable |
| 10 | r002#491 | BB | KTo | 9h Ts 9d 3s Qc | call pre; call 1,950 flop shove | bigRoddy T9o, full house | Call (top pair weak kicker calls a 97 bb shove) |

Count: calls 6 (3, 4, 6, 7, 10, and 2 in part), preflop entry 2 (4, 6), bluff 0, cooler or unavoidable 4 (1, 5, 8, 9).

v6 for comparison: its ten biggest losses include four preflop all-ins with 88, 77, QQ and QQ against ediz_slow, which shoved wide; v6's preflop all-ins overall won (12 won for +22,668 chips, 8 lost for -16,000).

## (d) What the data cannot tell us yet

1. Sample size. Every postflop counterfactual above rests on fewer than 30 hands. Mistakes 1 and 2 point the opposite way on v6, so they could be variance in two rounds rather than a v5 rule.
2. Timeouts are not flagged. The detector only sees folds of premium hands facing a bet (7 in v5 against 8 reported, 6 in v6 against 12 reported). A timeout that checks a strong hand, or folds a medium hand, is invisible.
3. Missed value. We cannot see what a river bet would have been paid, so the cost of mistake 3 is not measurable; the same applies to overfolding in mistake 4, since we never see the folded opponent's cards.
4. Opponents' cards are only visible at showdown, so the "shown after big bets" rows are 4 to 7 hands per team and say nothing about bluffs that were never called.
5. The winners profile covers only the hands they played at our tables (1000 to 2000 each); Attention Is All In never sat with us.
6. Hand classes treat a board pair plus our high card as "no made hand", so some "no made hand" showdowns were won on kickers.
