# Top teams dossier: Gherkers, Attention Is All In, Equity Engine

Source: `review/top_teams.py --upto r046` run on every counted round `hands-data/hands/saturday_r001.json` to `saturday_r046.json` (46 rounds, 46,000 hands). Every number below is printed by that script; lines marked "arithmetic" combine printed numbers and say how. Rates read k/n; n under 30 is marked * and is unreliable. Without `--upto` the script includes every round on disk.

**Late round r047.** The final `pull.py` brought r047 (our v12, +20.6) after the body was written; Gherkers sat there (also Anker Batteries). With r047 Gherkers has 9 rounds, 9,000 hands, +21.7 bb/100, flow to us −801 (−0.4 per 100). In r047 it played exactly as described: opens 3.5bb on 100% (130), 3-bet .10 (39/398), c-bet .68 (38), FG fired at hand 50; it lost −21.0 bb/100 and took 148 chips from us. Its fold to 3-bet was .65 (20*), higher than its .40 season rate. The Gherkers rules move little: G1 4-bet bluff now .82 (49/60), spots 41 (our v12 folded to its 3-bets 21 times in one round), gain +3.73 bb/100; G2 +2.42; G3 .61 (22/36), +1.40; G4 .67 (146/217), +0.73; G6 +0.04. The tables below keep the r046 cut.

## Summary

1. Each of the three top teams leaves an exact size fingerprint that a seat level rule finds in 20 to 230 hands with zero false positives for Gherkers and Attention Is All In; the Equity Engine rule also fires on Vlad and aydine, which play the same opens and sizes.
2. Equity Engine bets 0.45 or 0.50 pot with air and weak pairs and 0.80 pot with made hands; it folds 30 of 33 times when raised after a 0.45 or 0.50 bet. Raising those bets is worth +9.77 bb/100 at its tables.
3. Attention Is All In folds 47 of 54 times when raised after its 0.31 to 0.34 pot bets. Raising those with weak hands is worth +12.52 bb/100; folding non premiums to its 4bb open is worth +7.30.
4. Attention Is All In is the team we lose most to among the three: −15,026 chips, −10.7 bb/100 over 7,000 hands together. It adapts to its table: in r011 next to a whale it opened 2bb and played VPIP .53.
5. Gherkers opens exactly 3.5bb, 3-bets exactly 3.8x (3.2x some of the time in position), bets 0.33, 0.70 or 1.10 pot, and raises 56% of flop bets under 40% pot.
6. Against Gherkers the money is preflop: we flat its 3-bets with hands below QQ/AK for −14.61bb each, while it folds 0.82 (47/57) to 4-bets. Not flatting plus 4-bet bluffing is worth +4.68 bb/100 combined.
7. Gherkers drift: 3-bet fell from .21 (r001 to r009, inflated by r004 at .36) to .09 in every round since r036; blind defence fold rose from .43 to .71; flop check-raise rose to .42 (15/36) in r044 and r045. Sizes never moved.
8. Equity Engine added a 1.05 pot bet in r045 (21 bets); its 3.5bb opens and 0.45, 0.50, 0.80 sizes are unchanged across all 8 rounds.
9. Never bluff small into Gherkers (fold .16 to bets under 40%), never flat Equity Engine's opens (−2.72bb per call), never 3-bet Attention Is All In light (our 3-bets that it calls or 4-bets lose 5,030 chips).
10. At a final table with all three: take money from Equity Engine and from Attention Is All In's small bets, play tight against Gherkers' 3-bets and Attention Is All In's 4bb opens, and apply every postflop rule heads up only, because every rate here was measured heads up.

## The constraint and the data

The bot never sees team names. It sees seat numbers and public actions. Every rule below therefore starts with a fingerprint that a seat earns from its own actions within the current 1,000 hand round, and every rule has a stop condition on a live stat.

Hand history format (one file per round): `{ref, seat (ours), players: [team names by seat], hands: [...], round: {bb100, timeouts, think_s, version}}`. A hand is `{n, button, sb, bb, start_stacks, hole: {seat: [cards]} (ours always, others only at showdown), showdown, board, events, results}`. Events: `["post", seat, amt]`, `["act", seat, action, amt]` where a raise amount is the raise-to total for the street and a call amount is the chips added, `["board", street, cards]`, `["refund", seat, amt]`, `["win", seat, amt, hand_name]`. `results` is chips won or lost per seat. Every hand starts at 2,000 chips with 10/20 blinds, so 1bb = 20 chips and stacks are 100bb.

## Stat definitions

- **VPIP / PFR**: share of hands with a preflop call or raise / a preflop raise.
- **Limp**: first preflop action unopened (no raise yet), not in the BB, is a call.
- **First in (fi) open**: first action with no raise and no limper before it; open size in bb is the raise-to amount divided by 20.
- **3-bet**: first action facing exactly one raise is a raise; multiple = raise-to / the open raise-to. **4-bet / 5-bet**: same facing two / three raises.
- **Fold to 3-bet**: the seat opened, then its next action faces a second raise and is a fold. **Fold to 4-bet**: the seat 3-bet, then faces a further raise and folds.
- **Squeeze**: facing one raise plus at least one caller.
- **Blind defence vs steal**: seat in SB or BB facing one first in raise from CO, BTN or SB with no callers.
- **Shove**: preflop raise that puts the seat all in.
- **Positions**: from the button: BTN, SB, BB, then UTG, UTG+1 (8 handed), MP, HJ, CO.
- **Pot / bet size**: a bet is a raise with nothing to call; size = bet / pot before it (all chips in, including blinds). A raise size = (raise-to minus current bet) / (pot after calling). Size buckets: under 40%, 40 to 75%, 75 to 110%, overbet above 110% (the 110% edge sits at 1.12 so Gherkers' fixed 1.10 pot bet stays in one bucket). "Bets over 100% pot" counts any bet above 1.0 pot.
- **C-bet**: preflop last raiser bets the flop when nobody bet before it. **Barrel**: last raiser of the previous street bets again first. **Bet when checked to**: first action on a street with someone having checked before. **Donk**: betting first into the previous street's aggressor who has not yet acted. **Check-raise**: checked, then faced a bet on the same street, then raised.
- **Fold vs bet**: first action facing a single bet on a street (fold / call / raise shares), split by street and by size bucket. **Vs raise after their bet**: the seat bet or raised, then faced a raise on the same street. **Vs second barrel**: called a flop bet, faces a turn bet from the same seat. **Third barrel**: also called the turn.
- **Hand classes at showdown** (from the seat's own cards and the board at the street of the action): value = two pair or better made with the hole cards; medium = top pair or overpair; weak = any lower pair; draw = flush draw or four to a straight with a hole card; air = the rest.
- **WTSD**: share of hands that saw a flop and reached showdown. **W$SD**: share of showdowns won.
- **Flow to us**: chips a seat paid to our seat. In each hand every loser's loss is split across the winners in proportion to what they won, so the flows of our seat sum exactly to our result.
- **Spots per 100**: our seat's opportunities of that exact kind against the team, per 100 hands seated together.
- **Rule EV**: for a bluff, fold rate × pot won minus (1 − fold rate) × chips risked, zero equity when called (a floor for hands with draws). "Now" is our realised result in the same spots from the decision point on (final result plus chips already in). Gain per 100 = spots per 100 × (rule EV − now).

## Sample

Hands are hands seated at the same table; their bb/100 is their result there; flow is chips from them to our seat.

| Team | Rounds | Hands | Their bb/100 | Flow to us | Per 100 together |
|---|---|---|---|---|---|
| Gherkers | r001, r004, r009, r020, r036, r038, r044, r045 | 8,000 | +27.0 | −653 | −0.4 |
| Attention Is All In | r005, r007, r009, r011, r021, r022, r038 | 7,000 | +42.9 | −15,026 | −10.7 |
| Equity Engine | r001, r003, r006, r019, r021, r030, r031, r045 | 8,000 | +18.0 | +9,865 | +6.2 |

By our version (round.version):

| Team | Our version: rounds | Their bb/100 | Flow to us (bb/100) | Our bb/100 those rounds |
|---|---|---|---|---|
| Gherkers | v5: r001 | +70.9 | −1,333 (−6.7) | −7.9 |
| | v6: r004, r009 | +34.5 | +518 (+1.3) | +39.0 |
| | v7: r020 | −22.9 | +1,812 (+9.1) | +17.5 |
| | v11: r036, r038, r044, r045 | +24.8 | −1,650 (−2.1) | +9.8 |
| Attention Is All In | v6: r005, r007, r009, r011 | +43.1 | −8,126 (−10.2) | +14.1 |
| | v7: r021 | +30.2 | +1,387 (+6.9) | +17.7 |
| | v8: r022 | +67.2 | −4,917 (−24.6) | −12.0 |
| | v11: r038 | +30.7 | −3,370 (−16.9) | +21.5 |
| Equity Engine | v5: r001 | −37.3 | +3,912 (+19.6) | −7.9 |
| | v6: r003, r006 | +33.5 | +2,486 (+6.2) | +56.3 |
| | v7: r019, r021 | +43.8 | +300 (+0.8) | −7.9 |
| | v11: r030, r031, r045 | +8.8 | +3,167 (+5.3) | +16.5 |

Per round, their bb/100: Gherkers r001 +70.9, r004 +75.8, r009 −6.9, r020 −22.9, r036 +20.1, r038 +19.1, r044 +26.0, r045 +34.1. Attention Is All In r005 −8.7, r007 −6.1, r009 +1.9, r011 +185.2, r021 +30.2, r022 +67.2, r038 +30.7. Equity Engine r001 −37.3, r003 +45.4, r006 +21.5, r019 +56.6, r021 +31.1, r030 +29.2, r031 +20.4, r045 −23.1.

Our own version spread (bb/100 per 1,000 hand round): v11 17 rounds, mean +14.4, sd 36.5; v6 9 rounds, mean +39.7, sd 29.0.

## Gherkers

### Preflop

- VPIP .24 (1933/8000), PFR .18 (1461/8000), limp .00 (18/3839).
- Opens first in: UTG .12 (112/911), UTG+1 .13 (62/476), MP .17 (135/780), HJ .22 (141/646), CO .32 (154/478), BTN .69 (195/282), SB .83 (93/112).
- **Open size: 3.5bb on 96% of 892 opens.** UTG to HJ 100%; CO 91%, BTN 91%, SB 94%, the rest 3.55 to 3.8bb, almost all in r020 (3.5bb 75%, 3.75bb 10%). Over one limper it raises to 4.5bb, 100% (38). Size does not change with position otherwise.
- **3-bet .14 (520/3759)**; by own position UTG+1 .07 (7/106), MP .10 (24/244), HJ .11 (44/401), CO .12 (66/557), BTN .15 (108/743), SB .18 (155/856), BB .14 (116/852); against opener UTG .09 (71/809), UTG+1 .08 (35/444), MP .11 (90/804), HJ .14 (91/652), CO .19 (105/559), BTN .26 (104/407), SB .29 (24/84).
- **3-bet size: 3.8x the open** (3.8 or 3.81 after chip rounding on 75% of 520) **or 3.2x** (25%). From the blinds 3.8x on 91% (271); in position 3.8x 57%, 3.2x 44% (249). Most common: 2.5bb open to 9.5bb from the blinds (80), 2.6bb to 9.9bb (114), 3bb to 11.4bb (46).
- Squeeze .07 (36/523). 4-bet: facing a 3-bet it folds .79, calls .14, raises .07 (521); 4-bet size always 2.3x (36).
- **Fold to 3-bet after opening .40 (136)**, calls .41, 4-bets .18. Fold to 4-bet after 3-betting **.82 (57)**. Facing a 5-bet: folds .64 (11*).
- Blind defence vs steal: fold .59, call .19, 3-bet .21 (744); against opens up to 2.25bb fold .58 (62), 2.25 to 3bb fold .57 (499), above 3bb fold .66 (183). Against our steals: fold .64, 3-bet .25 (44).
- Shoves: 2 in 8,000 hands (KK, QQ).
- Shown after a 3.5bb open (59): KJo 12%, AKo 10%, KK 8%, JJ 7%, AQo 7%, ATo 5%, then broadways and small pairs. Shown after 3-bets (46): AKo, AKs, TT, JJ 9% each, QQ 7%, KK 7%, AJs, 99 4%, then single junk hands (98o, K6o, J7o, J7s, 42o). Shown after 4-bets (9*): AKo, QQ, KK 22% each, A9s, AA, TT. Cold call shown (42): AQo 12%, KQo, ATo, A8o 7%, A9o, KJo, 66, JTs, KTs, AJo, A8s 5%. BB call shown (36): K9o 11%, then K8s, KJo, AQo, KQo, Q9o 6%.

### Postflop as aggressor

- C-bet heads up .80 (227), multiway .35 (55). Turn barrel heads up .56 (184); river barrel heads up .48 (64).
- **Bet sizes are a fixed set: 1.10, 0.33 and 0.70 pot.** Flop bets: 1.1 40%, 0.33 28%, 0.7 18% (394). Turn: 1.1 44%, 0.33 31%, 0.7 17% (167). River: 0.33 37%, 1.1 31% (59). Bets over 100% pot .44 (270/620).
- C-bet by texture: paired .74 (46), monotone .54 (13*), high card .70 (121), low connected .72 (29*), other .74 (73). Size by texture: monotone heads up uses 0.33 most (38% of 24*); paired and other multiway 1.1 (67%, 65%).
- Bet when checked to: flop .67 (184), turn .53 (104), river .35 (66). Donk: flop .49 (206), turn .26 (43), river .11 (18*). Check-raise: flop .22 (34/154), turn .09 (77), river .00 (35).
- **Size tells at showdown** (class at the street of the bet): flop 0.33 pot: air 6, weak 9, draw 5, value 2, medium 4 (26); flop 1.10: medium 15, value 9, air 7, weak 5, draw 3 (39); turn 0.33: medium 7, weak 10, value 2, draw 2, air 1 (22); turn 1.10: medium 6, value 6, air 2, draw 1 (15*); river 0.33: weak 5, value 5, medium 1, air 1 (12*). Read: 0.33 is weak pairs, draws and air; 1.10 is top pair and better most of the time.
- When raised after betting: after 0.33 it folds 16, calls 12, raises 1; after 0.70 folds 5, calls 5; after 1.10 calls 13, folds 5, raises 1.

### Postflop as defender

| Facing a bet | Fold | Call | Raise | n |
|---|---|---|---|---|
| Flop, all | .45 | .24 | .30 | 475 |
| Flop under 40% | .09 | .35 | .56 | 99 |
| Flop 40 to 75% | .43 | .23 | .34 | 205 |
| Flop 75 to 110% | .68 | .20 | .12 | 130 |
| Flop overbet | .73 | .17 | .10 | 41 |
| Turn, all | .51 | .40 | .10 | 196 |
| River, all | .49 | .45 | .06 | 94 |
| All streets under 40% / 40 to 75% / 75 to 110% / overbet | .16 / .46 / .69 / .79 | | | 192 / 310 / 200 / 63 |
| Our bets: flop / turn / river | .57 / .81 / .54 | | | 47 / 26* / 13* |

- Vs raise after its bet: fold .51, call .45 (73). Vs second barrel: fold .43 (67); third barrel fold .42 (24*); river bet after checked turn fold .50 (18*). After a missed c-bet facing a stab: flop fold .38 (39), turn .63 (46).
- Called down and showed: called a river bet with weak 15, medium 15, air 8, value 4.

### Showdown

WTSD .20 (188/956), W$SD .56 (105/188). Biggest wins: r038 #164 KK set +2,300; r004 #723 QQ overpair +2,258; r009 #754 KK overpair +2,230. Biggest losses (2,000 each): r001 #396 KJs top pair, #511 KJo trips, #727 QTo two pair, #795 77 weak pair.

### How they beat us and how we beat them (flow to us, all 8 rounds)

Lost most:
- Preflop, we fold to their 3-bet: 186 hands, −4,037. Examples: r045 #594 we flat a 3.5bb open with AJs, G squeezes to 13.3bb, we fold; r036 #349 we open QTs to 3.25bb, G 3-bets to 12.35bb, we fold; r036 #373 same line with QTs.
- River, we fold to their bet: 7 hands, −3,175. r001 #783 ATo, G bets 110% flop, we call, river 33% bet, we fold (−818); r020 #174 JTo, G bets 110% flop and turn, we call twice, fold to river jam (−661); r004 #246 66, G 3-bets, bets 110% flop, jams river, we fold (−610).
- Preflop, we fold to their open: 211 hands, −3,165. r001 #7 K6s, #56 K8o, #91 95o fold to a 3.5bb open (−20 each).

Won most:
- River, they fold to our bet: 7 hands, +3,154. r020 #744 44, G bets 110% flop and turn, checks river, we jam 74%, G folds (+849); r004 #910 88, we jam river 91% after G checks (+743); r044 #473 ATo, we jam 112% river after G checks (+665).
- Turn, they fold to our bet: 20 hands, +2,704. r044 #395 ATo, we 3-bet, c-bet 80%, jam turn, G folds (+563); r004 #962 AA, 80% turn bet after G's 0.33 flop bet (+388); r009 #326 K8s, 50% turn stab (+245).
- Flop, they fold to our bet: 26 hands, +2,291. r009 #761 QQ 160% c-bet in a 3-bet pot (+296); r038 #98 KK 160% (+240); r020 #118 ATo 66% (+226).

## Attention Is All In

### Preflop

- VPIP .30 (2128/7000), PFR .23 (1611/7000), limp .00 (2/3526).
- Opens first in: UTG .23 (212/929), UTG+1 .12 (50/417), MP .28 (202/712), HJ .34 (210/612), CO .42 (201/478), BTN .73 (167/230), SB .88 (98/111).
- **Open size: 2.5bb or 4bb in its normal mode** (every round except r011: 2.5bb on 84% to 91%, 4bb on 9% to 16%). 4bb is used from early seats: UTG 17%, UTG+1 40%, MP 11%, HJ 7%, CO 1%, BTN and SB never. **Shown after a 4bb open: AA, AQs, 99 29% each, QQ 14% (7*).** Shown after a 2.5bb open (64): AJo 8%, A9o 6%, AQo, KTo, ATo 5%, then a wide spread down to Q4o, T4o, 75o.
- **Loose mode, r011 only** (table with ediz_slow, VPIP .75): opens 2bb 54%, 2.5bb 25%, 3bb 21% (410), VPIP .53, +185.2 bb/100. Shown after a 2bb open (42): 86o, 54o, A4o, QTo 5% each, then any two cards. It adapts to its table, so expect this mode against a whale.
- Over one limper: 3bb on 72% (18*).
- **3-bet .14 (437/3116), exactly 3.0x** (90%) or 4.0x (10%); in position 3x 95% (97); from the blinds 3x 88%, 4x 11% (340). By own position: MP .00 (0/212), HJ .04 (13/305), CO .04 (16/433), BTN .11 (66/605), SB .21 (149/725), BB .25 (191/753). Against opener: UTG .07 (53/786), UTG+1 .11, MP .10, HJ .14, CO .27 (107/399), BTN .29 (75/263), SB .20 (19/95).
- **3-bet range is polar**: shown (50) AA 14%, AKo 14%, KK 6%, QQ 4%, then J7o, J8o 4%, K4o, J3o, 92o, 83o, T7o, J2o, QJo, J4o 2% each.
- Squeeze .09 (45/503). Facing a 3-bet: folds .82, calls .15, 4-bets .03 (738). **Fold to 3-bet after opening .71 (428)**; to our 3-bets .60 (107). 4-bet sizes are large (8.93x 42% of 19*); 4-bet shown AA, QQ, KK (3*). Fold to 4-bet after 3-betting .78 (51).
- Blind defence vs steal: fold .51, call .18, 3-bet .31 (431); up to 2.25bb fold .51 (63); 2.25 to 3bb fold .45, 3-bet .38 (255); above 3bb fold .64 (113). Against our steals: 3-bet 8 of 8*.
- Shoves 22 in 7,000; shown AA, KK, QQ (5*).

### Postflop as aggressor

- C-bet heads up .81 (271), multiway .47 (157). **Turn barrel heads up .85 (284), river barrel heads up .87 (174).**
- **Sizes: 0.33 pot is its default.** Flop bets 0.33 40%, 1.0 14%, 0.66 14%, 0.31 7% (495); turn 0.33 35%, 1.0 17%, 0.66 16%, 0.19 11% (289); river 0.33 41%, 0.16 16%, 0.66 13%, 1.51 8% (201). Bets over 100% pot .06 (60/985). Monotone heads up 0.33 on 79% (14*).
- Bet when checked to: flop .53 (288), turn .52 (151), river .55 (109). Donk: flop .41 (297), river .70 (30). **Check-raise: .00 on every street** (0/197 flop, 0/96 turn, 0/30 river).
- C-bet by texture: paired .66 (64), monotone .50 (18*), high card .69 (179), low connected .67 (36), other .73 (131).
- **Size tells at showdown**: flop 0.33: weak 20, medium 13, air 12, value 2, draw 1 (48); turn 0.33: medium 16, weak 10, air 7, value 4, draw 3 (40); river 0.33: medium 12, weak 11, air 10, value 9 (42); river 1.51 pot: value 7, weak 7, air 1, medium 1 (16*); flop 1.00: draw 6, medium 5, value 2, air 1 (14*). The 0.33 bet is mostly one pair or less.
- **When raised after a 0.33 bet: folds 46, calls 5, raises 2.** After 0.66: folds 15, calls 4. After 1.00: folds 8, calls 5, raises 1.

### Postflop as defender

| Facing a bet | Fold | Call | Raise | n |
|---|---|---|---|---|
| Flop, all / heads up / multiway | .60 / .48 / .78 | .30 / .38 / .18 | .10 / .14 / .04 | 547 / 326 / 221 |
| Turn, all / heads up | .51 / .42 | .42 / .50 | .07 / .08 | 265 / 203 |
| River, all / heads up | .46 / .37 | .44 / .52 | .10 / .11 | 111 / 92 |
| All streets under 40% / 40 to 75% / 75 to 110% / overbet | .39 / .47 / .77 / .81 | | | 146 / 470 / 249 / 58 |
| Our bets 75 to 110% | .81 | .09 | .10 | 78 |

- **Vs raise after its bet: fold .81 (101).** Vs second barrel fold .33 (131); third barrel fold .17 (52); river bet after checked turn fold .90 (20*). After a missed c-bet facing a stab: flop fold .87 (39).
- Called a river bet and showed: weak 20, medium 12, air 10, value 7.

### Showdown

WTSD .21 (253/1196), W$SD .53 (135/253). Biggest wins: r007 #35 A2s flush +4,080; r011 #934 AA +4,020; r011 #447 K9o two pair +4,000. Biggest losses (2,000 each): r005 #223 J3o air, r005 #445 AQo top pair, r005 #743 AA, r007 #130 J4o air.

### How they beat us and how we beat them

Lost most:
- Showdown after they bet the river last: 16 hands, −8,595. r011 #776 T2o, we call a 19% river jam with a pair (−2,000; they had KJs); r022 #592 AKo, we call 76% turn and 77% river jam (−2,000; 94o made a straight); r022 #641 A2s, three 43% bets called (−2,000; J8o).
- Showdown after they bet the turn last: 3 hands, −4,137. r011 #447 AKo vs K9o, they raise our flop bet, jam turn; r038 #987 A4s vs J7s; r021 #256 44 vs A8o (−137).
- River, we fold to their bet: 8 hands, −3,505. r022 #519 T8o, after 3-betting and calling two small bets (−904); r022 #572 JTs (−742); r021 #163 A4o, called 33% flop and turn, folded to a 100% river bet (−642).

Won most:
- Flop, they fold to our bet: 45 hands, +4,069. r022 #578 88 160% (+330); r021 #323 ATo 80% in a 3-bet pot (+254); r007 #679 TT 80% (+254).
- Preflop, they fold to our 3-bet: 96 hands, +3,950. r038 #416 QTs, r021 #898 AA, r007 #869 J6s, each over a 4bb open (+80 flow).
- Turn, they fold to our bet: 31 hands, +2,880. r038 #761 55 (+411), r021 #118 33 (+272), r005 #182 A6s (+232), each a turn stab after they checked.

## Equity Engine

### Preflop

- VPIP .26 (2056/8000), PFR .18 (1418/8000), limp .00 (1/4180).
- Opens first in: UTG .23 (246/1090), UTG+1 .19 (61/314), MP .27 (240/896), HJ .33 (217/657), CO .34 (174/514), BTN .50 (160/322), SB .57 (110/192).
- **Open size: 3.5bb on 100% of opens in every position and every round.** Hand check: r045 has 171 first in raises and all are 70 chips. **Isolation: 3.5bb plus 1bb per limper** (4.5bb over one limper 87% of 70, 5.5bb over two 11%, 6.5bb over three).
- **3-bet .03 (95/3363), 3.0x** on 78%; by own position .02 to .04 everywhere. **3-bet shown (15*): QQ 40%, AA 27%, AKo 20%, JJ 7%, KK 7%.** Squeeze .03 (16/523).
- Facing a 3-bet: folds .79, calls .18, 4-bets .02 (661). Fold to 3-bet after opening .63 (318); to our 3-bets .56 (93). 4-bet shown JJ, KK, AKo, AJo (8*). **Fold to 4-bet after 3-betting .14 (14*)**: it does not fold its 3-bets.
- Blind defence vs steal: fold .64, call .33, 3-bet .03 (529); up to 2.25bb fold .55 (106); 2.25 to 3bb fold .66 (401). Against our steals: fold .52, call .45 (86).
- Shoves 8 in 8,000: AA, QQ, JJ.
- Shown after a 3.5bb open (103): KQo 9%, JJ 6%, AQo 5%, 66, A5s, ATo 4%, then T9o, KTo, JTo, QJo, A4o.

### Postflop as aggressor

- **C-bet heads up .93 (212), multiway .14 (63).** Turn barrel heads up .62 (190), river barrel .70 (86).
- **Sizes: 0.80, 0.50 and 0.45 pot**, plus 1.05 pot from r045. Flop c-bets 0.8 45%, 0.45 27%, 0.5 26%, 1.05 2% (206); turn barrels 0.8 62%, 0.5 28%; river 0.8 58%, 0.5 19%. Multiway it bets 0.8 almost always (high card multiway 96% of 24*). In r045 it bet 1.05 pot 21 times; bets over 100% pot went from 1 in 539 bets (r001 to r030) to .12 (23/195) in r031 and r045.
- C-bet by texture: paired .76 (50), monotone .73 (15*), high card .72 (120), low connected .80 (20*), other .79 (70).
- Check-raise: flop .03 (8/276), turn .01 (1/113), river .00 (68). Donk flop .24 (428), turn .37 (70).
- **Size tells at showdown**: flop 0.45: air 9, weak 1 (10*); flop 0.50: air 14, weak 5, draw 3 (22*); flop 0.80: value 12, medium 11, weak 6, air 2, draw 1 (32); turn 0.50: weak 7, air 6, draw 5 (18*); turn 0.80: value 16, medium 6, weak 5, air 2 (29*); river 0.50: weak 6, air 5 (11*); river 0.80: value 12, medium 4, weak 2, air 1 (19*). **Not one medium or value hand was shown after a 0.45 or 0.50 flop bet (0 of 32).**
- **When raised after betting: 0.45 folds 5 of 5; 0.50 folds 25 of 28; 0.80 folds 24, calls 9, raises 5 (38); 1.05 calls 2, raises 2.**

### Postflop as defender

| Facing a bet | Fold | Call | Raise | n |
|---|---|---|---|---|
| Flop, all / heads up | .51 / .44 | .39 / .43 | .10 / .13 | 544 / 353 |
| Turn, all / heads up | .51 / .43 | .38 / .43 | .12 / .14 | 245 / 182 |
| River, all / heads up | .57 / .51 | .34 / .37 | .09 / .11 | 132 / 107 |
| All streets under 40% / 40 to 75% / 75 to 110% / overbet | .32 / .49 / .63 / .76 | | | 163 / 441 / 246 / 71 |
| Our bets 40 to 75% / 75 to 110% | .60 / .64 | | | 58 / 96 |

- Vs raise after its bet: fold .73 (78). Vs second barrel fold .45 (114); third barrel fold .47 (40); **river bet after checked turn fold .82 (38)**. After a missed c-bet facing a stab: turn fold .58 (43).
- Called a river bet and showed: weak 22, air 10, value 7, medium 6.

### Showdown

WTSD .19 (217/1159), W$SD .46 (100/217). Biggest wins: r003 #151 77 set +4,020; r021 #99 J8o two pair +2,848; r003 #135 QQ set +2,637. Biggest losses (2,000 each): r001 #177 KTo, #196 Q9s, #344 TT, #365 JJ, all weak pairs.

### How they beat us and how we beat them

Lost most:
- River, we fold to their bet: 14 hands, −5,505. r031 #195 K2s, we raise the turn, EE jams river 58%, we fold (−919); r006 #171 A4o, EE leads 100% river (−533); r003 #714 AKo, three 0.80 bets, we fold the river (−463).
- Turn, we fold to their bet: 21 hands, −5,390. r045 #777 55, EE bets 1.05 flop and jams turn (−639); r030 #317 QJo and #393 KTs, 0.80 turn bet after our 3-bet pot (−533 each).
- Preflop 5-bet shoves: 2 hands, −4,000. r019 #387 AA loses to QQ; r031 #49 KK loses to QQ.

Won most:
- Turn, they fold to our bet: 40 hands, +5,937. r021 #459 ATo (+636); r045 #305 KJo (+563); r045 #531 66 after EE's 0.50 flop bet (+437).
- River, they fold to our bet: 15 hands, +5,222. r031 #96 KQo river jam (+1,298); r030 #188 A5o after two EE 0.50 bets (+859); r045 #49 AJo (+563).
- Flop, they fold to our bet: 57 hands, +4,593. r031 #550 AKo 160% (+269); r045 #779 AA (+240); r030 #798 QQ (+240).

## Fingerprints

Each rule is evaluated on one seat's own public actions up to hand H of the round. A seat round is one team in one 1,000 hand round; there are 295 seat rounds in the data. All-in bets are excluded from the size checks because the stack caps them. "False positive" counts other teams' seat rounds where the rule fires at hand H.

| Code | Rule | First firing hand per target round | Target hit at H=100 / 200 / 1000 | False positives at H=100 | At H=1000 |
|---|---|---|---|---|---|
| FG | ≥3 opens, ≥90% exactly 3.5bb, and either a non all-in postflop bet of 1.08 to 1.12 pot or a 3-bet of 3.78x to 3.82x | 30, 30, 40, 20, 20, 70, 230, 120 | 6/8, 7/8, 7/8 | 0/287 (0%) | 3/287 (1.0%): WBot 1/8, kaiserbot 2/5 |
| FEE | ≥5 opens, ≥90% exactly 3.5bb; ≥3 non all-in bets, ≥90% at 0.45, 0.50, 0.80 or 1.05 pot, at least one 0.80; every 3-bet 2.9x to 3.45x | 200, 50, 80, 30, 30, 50, 50, 40 | 7/8, 7/8, 8/8 | 8/287 (2.8%): Vlad 3/6, aydine 5/5 | 10/287 (3.5%): Vlad 6/6, aydine 4/5 |
| FA | ≥5 opens, ≥90% at 2, 2.5, 3 or 4bb with a 4bb or 2bb open seen; ≥3 non all-in bets, half or more at 0.31 to 0.35 pot | 40, 70, 60, never (r011), 60, 90, 190 | 4/7, 3/7, 4/7 | 0/288 (0%) | 0/288 (0%) |

Notes for the implementer:
- FG is the cleanest: zero false positives up to hand 300 and every Gherkers round caught by hand 300. Latch it: once FG fires, keep the label for the round, because the 90% open share can dip when Gherkers opens 3.75bb (r020).
- FEE also fires on Vlad and aydine. Their whole profile matches Equity Engine (3.5bb opens on 100%, 3-bet .03 at 3x, bets with median 0.80), so the same counters apply; treat the label as "Equity Engine family". Latch it too.
- FA toggles because Attention Is All In's 0.33 share drops below half in some stretches. Latch on first firing. It misses r011 (loose mode, 2bb and 3bb opens with 0.33 bets but a different mix); in that mode the useful tells are 2bb opens plus 3.0x 3-bets plus zero check-raises.
- Confidence by hand count: FG fires by hand 70 in 6 of 8 rounds, FEE by hand 80 in 7 of 8, FA by hand 90 in 5 of 7.

## Drift

Rounds in time order, split into thirds.

### Gherkers (r001, r004, r009 | r020, r036, r038 | r044, r045)

| Stat | Third 1 | Third 2 | Third 3 |
|---|---|---|---|
| VPIP | .29 (3000) | .22 (3000) | .20 (2000) |
| PFR | .22 | .17 | .15 |
| 3-bet | .21 (305/1470) | .09 (127/1342) | .09 (88/947) |
| 4-bet | .04 (137) | .06 (251) | .11 (133) |
| Fold to 3-bet | .40 (43) | .36 (55) | .47 (38) |
| Fold to 4-bet after 3-bet | .86 (29*) | .78 (18*) | .80 (10*) |
| C-bet flop | .76 (127) | .68 (94) | .66 (61) |
| Check-raise flop | .16 (70) | .17 (48) | .42 (36) |
| Fold vs bets 75 to 110% | .76 (88) | .65 (62) | .60 (50) |
| Fold to raise after its bet | .75 (28*) | .29 (35) | .60 (10*) |
| Blind defence fold | .43 (328) | .73 (280) | .71 (136) |
| Bets over 100% pot | .45 (275) | .42 (210) | .41 (135) |
| Open size | 3.5bb 100% | 3.5bb 90% | 3.5bb 98% |
| C-bet size median | 0.70 | 0.70 | 0.70 |
| bb/100 | +46.6 | +5.4 | +30.1 |

Per round 3-bet: r001 .13, r004 .36, r009 .09, r020 .12, r036 .08, r038 .09, r044 .09, r045 .09. The high early 3-bet rate is r004 alone.

Stable enough to rely on: 3.5bb opens, the 3.8x and 3.2x 3-bet multiples, the 0.33 / 0.70 / 1.10 bet sizes and the share of 1.10 bets, the 4.5bb isolation, folding about four in five 4-bets, folding about seven in ten bets of 75% pot or more.

Moved: 3-bet frequency (stable at .08 to .09 since r036), blind defence fold (up from .43 to .71 to .73), flop check-raise (.42 in the latest two rounds, n=36), fold to big bets (down from .76 to .60), VPIP and PFR (down). Rules that depend on the moved stats carry stop conditions below.

### Attention Is All In (r005, r007, r009 | r011, r021 | r022, r038)

VPIP .25 / .40 / .29, PFR .18 / .33 / .21, 3-bet .12 / .11 / .20, fold to 3-bet .77 / .65 / .76, fold to raise after its bet .80 / .86 / .76*, fold vs bets 75 to 110% .84 / .81 / .63, blind defence fold .63 / .63 / .36, check-raise flop .00 in every third. Its code never changed; the middle third is the r011 loose mode. Latest rounds: 3-bet up to .20 and blind defence fold down to .36.

### Equity Engine (r001, r003, r006 | r019, r021, r030 | r031, r045)

3-bet .02 / .03 / .03, fold to 3-bet .49 / .67 / .75, fold vs bets 75 to 110% .49 / .68 / .72, fold to raise after its bet .81 / .67* / .70*, bets over 100% pot .00 / .00 / .12, open 3.5bb 100% throughout, c-bet size median 0.50 throughout, bb/100 +9.9 / +39.0 / −1.4.

## Counter strategy

All postflop rules below were measured heads up. Apply them only when the fingerprinted seat is our only live opponent. "Weak hands" means our made class is weak pair, draw or air at that street. Gains assume we sit with the team for 100 hands; rules for different teams add up only at a table where both sit.

### Gherkers (fingerprint FG)

1. **G2. IF FG AND G 3-bets our open AND our hand is below QQ/AK THEN fold (never flat).**
   Measured: 14 flats with such hands realised −14.61bb each from the decision on. Break even: folding is worth 0. Gain +2.56 bb/100 (0.17 spots per 100 × 14.61). Stop: if G's live 3-bet rate exceeds .20 over ≥ 100 chances (r004 behaviour), widen the continue range again.
2. **G1. IF FG AND G 3-bets our open AND we would fold THEN 4-bet to 2.3x its 3-bet with blockers (suited aces A5s to A2s, KQs) at most once per 20 hands against that seat.**
   Measured fold to 4-bet after 3-betting .82 (47/57). Break even: risk / (risk + pot) averaged over the 20 spots = 0.59 (median 3-bet 11.4bb, median pot 14.9bb before our 4-bet). EV +8.48bb per 4-bet bluff with zero equity. Spots: our folds to its 3-bets, 20 in 8,000 hands (0.25 per 100). Gain +2.12 bb/100. Stop: live fold to 4-bet below .65 over ≥ 8, or a 5-bet seen.
3. **G3. IF FG AND G bets 0.31 to 0.37 pot heads up AND we hold a weak hand THEN raise to 3x its bet.**
   Measured: after a 0.33 or 0.35 bet G folds 21 of 34 (.62) when raised. Break even: 3B / (3B + P + B) = 0.43 at B = 0.33P. EV +7.08bb per spot against +2.90bb realised now. Spots 32 (0.40 per 100). Gain +1.67 bb/100. Stop: live fold to raise after a 0.33 bet below .50 over ≥ 10.
4. **G4. IF FG AND we bluff into G heads up THEN size 0.80 pot, never 40 to 75% and never under 40%.**
   Measured: G folds .69 (137/200) to bets of 75 to 110% against .46 (310) at 40 to 75% and .16 (192) under 40%. Break even at 0.80 pot: 0.80 / 1.80 = 0.44. EV +7.74bb per bluff against +2.97bb at our current mid sizes. Spots 14 (0.17 per 100). Gain +0.84 bb/100. Stop: live fold vs 75 to 110% bets below .55 over ≥ 20 (third 3 is .60).
5. **G6. IF FG AND G checks to us heads up AND we hold a weak hand THEN bet 0.66 pot.**
   Measured: G folded 24 of 39 (.62) to our bets after checking. Break even 0.66 / 1.66 = 0.40. EV +11.00bb against +10.57bb realised when we checked. Spots 27 (0.34 per 100). Gain +0.15 bb/100. Stop: flop check-raise rate above .35 over ≥ 20 (third 3 is .42 on 36, so start this rule on the turn and river only).

Value note without a gain figure: G raises .56 of flop bets under 40% (99), so with two pair or better a 0.33 pot flop bet gets raised more often than any other size.

### Attention Is All In (fingerprint FA, latched)

1. **A1. IF FA AND AIAI bets 0.30 to 0.37 pot heads up AND we hold a weak hand THEN raise to 3x its bet.**
   Measured: when raised after a 0.31 to 0.34 bet AIAI folds 47 of 54 (.87). Break even 0.43. EV +23.64bb per spot against +2.27bb realised now (we mostly call). Spots 41 (0.59 per 100). Gain +12.52 bb/100. Stop: live fold to raise after a small bet below .60 over ≥ 10, or two 3-bets seen.
2. **A4. IF FA AND AIAI opens 4bb AND our hand is below QQ/AK THEN fold.**
   Measured: 32 spots where we continued with such hands realised −15.97bb each. Shown after 4bb: AA, AQs, 99, QQ (7*). Gain +7.30 bb/100 (0.46 per 100 × 15.97). Stop: 4bb share of its opens above .25 over ≥ 40 opens (normal is .09 to .16), or a 4bb open shown with less than a pair of nines or AQ.
3. **A3. IF FA AND AIAI bets 0.50 pot or more heads up AND we hold weak pair or air THEN fold.**
   Measured: 17 calls realised −10.21bb each. Gain +2.48 bb/100. Stop: none needed while its 0.66 and 1.0 bets keep showing medium or better (flop 1.0: draw 6, medium 5, value 2, air 1, 14*).
4. **A2. IF FA AND AIAI checks to us heads up AND we hold a weak hand THEN bet 0.66 pot.**
   Measured: it folded 27 of 29* to our bets after checking (it never check-raises: 0/197 flop, 0/96 turn, 0/30 river). Break even 0.40. EV +17.62bb against +2.81bb realised when we checked. Spots 8 (0.11 per 100). Gain +1.69 bb/100. Stop: one check-raise seen from this seat.
5. **A5. IF FA AND AIAI bets about 0.33 pot AND we hold weak pair or air THEN never flat; raise per A1 or fold.**
   Measured: 23 such calls realised −0.15bb each, gain +0.05 bb/100. It is listed because the call is the line that cost us most at showdown (16 river showdowns after its bets, −8,595); A1 replaces it.

### Equity Engine (fingerprint FEE, also catches Vlad and aydine)

1. **E5. IF FEE AND EE opens AND we would flat THEN 3-bet to 3x in position or 3.5x from the blinds with pairs, suited broadways and suited aces; fold the rest.**
   Measured: our 100 3-bets over its opens realised +8.56bb each; our 82 flats realised −2.72bb each. EE folds .56 (52/93) to our 3-bets and 4-bets .01 of them. Converting every flat at the realised 3-bet result is +11.56 bb/100, an upper bound because flatted hands are weaker than our 3-bet range. A pure bluff 3-bet to 10.5bb into a 5bb pot needs 0.68 folds, so the rule rests on postflop play after it calls, not on the fold rate. Stop: live fold to 3-bet below .45 over ≥ 20, or its 4-bet rate above .08.
2. **E1. IF FEE AND EE bets 0.42 to 0.53 pot heads up AND we hold a weak hand THEN raise to 3x its bet.**
   Measured: after a 0.45 or 0.50 bet EE folds 30 of 33 (.91) when raised; 0 of 32 shown flop hands at those sizes were medium or better. Break even 3B / (3B + P + B) = 0.48 at B = 0.45P. EV +23.16bb per spot against +9.91bb realised now. Spots 59 (0.74 per 100). Gain +9.77 bb/100. Stop: live fold to raise after a 0.45 or 0.50 bet below .60 over ≥ 8.
3. **E4. IF FEE AND we bluff into EE heads up THEN size 0.80 pot.**
   Measured: EE folds .63 (154/246) to 75 to 110% bets against .49 (441) at 40 to 75%. Break even 0.44. EV +5.32bb per bluff against +2.86bb at mid sizes. Spots 21 (0.26 per 100). Gain +0.65 bb/100. Stop: live fold vs 75 to 110% bets below .52 over ≥ 20.
4. **E2. IF FEE AND EE bets 0.78 to 0.83 pot on the turn or river AND we hold weak pair or air THEN fold.**
   Measured: turn 0.80 showdowns value 16, medium 6, weak 5, air 2 (29*); river 0.80 value 12, medium 4, weak 2, air 1 (19*). Our 7 calls realised −5.26bb each. Gain +0.46 bb/100. Stop: two 0.80 river bets shown with air.
5. **E6. IF FEE AND EE 3-bets or 5-bets THEN continue with QQ+ and AK only and never 4-bet bluff.**
   Measured: 3-bet shown QQ, AA, AKo, JJ, KK only (15*); fold to 4-bet after 3-betting .14 (14*); our two 5-bet pots with AA and KK both ran into QQ. Gain not measurable (8 spots in 8,000 hands); the rule protects against the −4,000 line above.

## What not to do

- **Gherkers:** do not bluff with bets under 40% pot (fold .16, raise .34 of 192). Do not bluff-raise its 1.10 pot bets (when raised it called 13, folded 5). Do not fold weak pairs to every 1.10 turn or river bet: in the 3 such calls we won +49.57bb each (n too small to build a rule, but folding there tested negative at −1.86 bb/100). Do not steal from the blinds against it with a weak range while its blind 3-bet is .21 (744) and .25 against our steals (44).
- **Attention Is All In:** do not 3-bet its opens light: of our 107 3-bets it folded 64 (+2,270) but its calls (31, −2,150) and 4-bets (12, −2,880) left the line at −2,760 chips. Do not call down its 0.33 barrels with one pair below top pair: it barrels .85 turn and .87 river heads up and shows weak and medium pairs at that size. Do not overfold the river to it after it checked the turn without reading size: its river 1.51 pot bet is value 7, weak 7 (16*).
- **Equity Engine:** do not flat its opens (82 flats, −2.72bb each). Do not 4-bet bluff its 3-bets. Do not change our current stabbing when it checks: we already bet 49 of 51 flops after its check, and turning the remaining weak checks into bets tested negative (−1.66 bb/100). Do not read its new 1.05 pot bet as a bluff size: it showed only calls and raises when raised (4*) and jammed the turn after it in r045 #777.

## If all three are at the final table

- **Who to target.** Equity Engine is the main source: +6.2 bb/100 flow to us across 8,000 hands and positive in every one of our versions; E5 and E1 together are worth up to +21 bb/100 at its table (upper bound from +11.56 and +9.77). Attention Is All In is the second source through A1 and A4 (+19.8 bb/100 combined), but it is also the team that took the most from us (−10.7 bb/100), so the gain there comes mainly from not paying it off.
- **Who to avoid.** Gherkers' preflop 3-bets and Attention Is All In's 4bb opens. Against Gherkers, the edge is small (flow −0.4 bb/100) and comes from G1 and G2; do not go looking for marginal spots against it.
- **How the counters interact.** Every postflop rule is a heads up rule. With three fingerprinted seats live, multiway pots behave differently: Equity Engine c-bets only .14 multiway and then bets 0.80; Attention Is All In c-bets .47 multiway; Gherkers raises flop bets .22 multiway. So never raise a small bet (A1, E1, G3) when another of these seats is still to act behind the bettor. A1 and E1 fire on the same action (raise 3x) against different sizes, so the size check is what separates them: 0.30 to 0.37 pot from an FA seat, 0.42 to 0.53 from an FEE seat, 0.31 to 0.37 from an FG seat. Gherkers sits after Attention Is All In or Equity Engine in some seat orders; if G is behind, a raise of AIAI's 0.33 bet can face G's flop raise rate of .30, so skip the raise.
- **Variance when only the most chips wins.** Our v11 rounds have sd 36.5 bb/100 per 1,000 hands, so over a 5,000 hand final our standard error is about 16 bb/100 (arithmetic: 36.5 / √5). The leaderboard gap given in the brief, us about +32 against Gherkers about +62, is about two standard errors at that length, so playing for a slightly higher mean beats playing safe. The rules here mostly reduce variance (folds A3, A4, A5, G2, E2, E6) or risk small amounts at high fold rates (A1 at .87, E1 at .91). Accept the extra variance of A1, E1 and G1; keep stacking off with one pair against all three out of the plan, since most of the 2,000 chip showdowns listed above for these teams were won or lost with a single pair.

## Secondary teams

| Team | Rounds, hands | Their bb/100 | Flow to us (per 100) |
|---|---|---|---|
| The Market Makers | 8 (r001, r005, r008, r024, r026, r027, r035, r046), 8,000 | +9.2 | +6,990 (+4.4); v11 r035, r046 −5,468 (−13.7) |
| AAST | 8 (r013, r015, r017, r032, r034, r035, r036, r040), 8,000 | +19.3 | −5,347 (−3.3); v11 five rounds −6,358 (−6.4) |
| WBot | 8 (r002, r007, r016, r020, r027, r033, r039, r042), 8,000 | +63.6 | −16,706 (−10.4); v11 three rounds −5,586 (−9.3) |
| Kojack | 8 (r003, r008, r021, r023, r024, r025, r026, r031), 8,000 | +33.3 | +2,054 (+1.3) |
| Anker Batteries | 7 (r005, r006, r015, r028, r034, r042, r045), 7,000 | +4.1 | +12,314 (+8.8) |

**The Market Makers.** VPIP .19, PFR .12; opens 2.5bb on 100% (726); 3-bet .04 (153/3405) at 3.0x or 3.6x; fold to 3-bet after opening .39 (137); blind defence fold .65 (497). Defence: folds .22 (86) under 40%, .42 (330) at 40 to 75%, .62 (154) at 75 to 110%, .85 (26*) to overbets; fold to raise after its bet .51 (112). Fingerprint FTMM (90% of opens 2.5bb, 80% of bets at 0.5, 0.6, 0.7 or 1.0 pot): 8/8 rounds by H=100, false positives 7/287 (2.4%) at H=100 and 8/287 (2.8%) at H=1000 (Peanut Cookies 4/4, Mohil'sPokerBot 4/4). Weakness: calls small and medium bets and wins only .42 of its 227 showdowns, so value bet thinner at 0.6 to 0.75 pot and do not bluff it below 75% pot.

**AAST.** VPIP .23, PFR .16; opens 3bb 94%, 3.5bb 6% (857); 3-bet .09 (282/3190) at 3.0x or 3.7x; 4-bets .14 of 856 chances; fold to 3-bet after opening .51 (187); blind defence fold .46, 3-bet .24 (497), 3-bet .49 against opens of 2.25bb or less (120). Postflop it uses Gherkers' size set (1.1, 0.7, 0.33, plus 0.8). Defence: folds .42 (139) under 40%, .60 (357) at 40 to 75%, .72 (210) at 75 to 110%, .87 (55) to overbets; our 40 to 75% bets fold it .82 (34). Fingerprint FAAST (90% of opens 3bb, 70% of bets at 1.1, 0.8, 0.7 or 0.33): 6/8 by H=200, false positives 0/287 at every H. Weakness: folds .87 to overbets, so bluff it big; do not min-steal its blinds.

**WBot.** VPIP .33, PFR .21; opens 3.5bb 50%, 2.8bb 44%; 3-bet .05; fold to 3-bet after opening .52 (408); blind defence fold .38 (574). C-bets 1.00 heads up (265), bets 0.15 pot on 71% of turn bets and 81% of river bets, bets the turn .90 when checked to; overbets 3.0 and 2.39 pot on the river (6% each). Defence: folds .32 (167) under 40%, .45 (475) at 40 to 75%, .61 (218) at 75 to 110%; raises .22 to .31 of bets; fold to raise after its bet .56 (329). Fingerprint FW (90% of opens at 2.8, 3.3, 3.5 or 4bb, 40% of bets at 0.15 pot): 8/8 by H=500, false positives 2/287 (0.7%, kaiserbot 2/5). Weakness, read from our losses: its river overbets are value; we called 8 overbets for −16,000 chips. Fold to WBot overbets without a strong hand.

**Kojack.** VPIP .20, PFR .16; opens 2.5bb 90%, 3bb 10%; 3-bet .07 (237) at 3.0x or 3.8x; 4-bets .10 of 724; fold to 3-bet after opening .60 (229); blind defence fold .69 (485). Defence: folds .27 (144) under 40%, .45 (321) at 40 to 75%, .61 (209) at 75 to 110%; check-raise .00 on turn (69) and river (48); bets the river only .24 when checked to (80). Fingerprint FK (90% of opens 2.5 or 3bb, 60% of bets at 0.40, 0.45, 0.55 or 0.72): 7/8 by H=200, false positives 8/287 (2.8%: supernut 5/8, munchlax 2/8, bigRoddy 1/9). Weakness: never check-raises late streets and folds .61 to big bets; our river bets into it won 18 times for +5,820.

**Anker Batteries.** VPIP .23, PFR .18; opens 2.5bb on 100% (704); 3-bet .14 (452) at 3.0x or 3.2x; fold to 3-bet after opening .37 (153); blind defence fold .64 (442). Flop bets 1.1 pot 33% and 2.0 pot 18%. Defence: folds .25 (153) under 40%, .51 (372) at 40 to 75%, .61 (190) at 75 to 110%, .79 (33) to overbets; fold to raise after its bet .44 (59); check-raise .00 on turn (37). Fingerprint FANK (90% of opens 2.5bb, 70% of bets at 0.4, 0.62, 0.7, 1.1 or 2.0): 7/7 by H=200, false positives 4/288 (1.4%, Peanut Cookies 4/4). Weakness: its turn bets lose at showdown (we won +5,385 in 6 turn showdowns after it bet last), so call its turn bets with top pair or better.

## Validation

- Script: `python3 review/top_teams.py` runs end to end on 46 rounds with no errors (about 4 s).
- Chip flows: 0 hands where the split flows of our seat differ from `results[our seat]`; sum of flows 248,951 equals our total 248,951. No round where the site's `round.chips` differs from the sum of our per hand results. The per spot flows for each target sum to its total flow (Gherkers −653, Attention Is All In −15,026, Equity Engine +9,865).
- Hand checks against raw events, recounted by a separate scan that does not use the script's replay:
  - Gherkers, open size: r001 has 128 first in raises by seat 1, all 70 chips (3.5bb), matching "r001 3.5 100% (n=128)". Gherkers, 3-bet multiple: r036 #349 we raise to 65, seat 1 (BB) raises to 247; 247 / 65 = 3.80.
  - Attention Is All In, loose mode sizes: r011 first in raises are 221 at 40 chips, 103 at 50, 86 at 60 (410), matching 2bb 54%, 2.5bb 25%, 3bb 21%. Bet size: r021 #163 pot after preflop is 478 (80 + 144 + 224 + 30), its flop bet is 157 = 0.33 pot; turn pot 792, bet 261 = 0.33.
  - Equity Engine, open size: r045 has 171 first in raises, all 70 chips. Bet size: r003 #714 pot 140, flop bet 112 = 0.80; turn pot 364, bet 291 = 0.80; river pot 946, bet 756 = 0.80.
- False positive rates are computed over all 295 seat rounds of all 43 opposing teams in the data, at H = 50, 100, 200, 300, 500 and 1000.

## Limits

- Folded hands are never shown, so size tells come from hands that reached showdown only; a size that is rarely called is underrepresented.
- Every bluff EV assumes zero equity when called; draws make the real EV higher.
- The "now" baseline for each rule mixes all our versions; v11 alone has fewer spots.
- Attention Is All In has no round after r038 at our tables; its latest behaviour is from 2,000 hands.
- Fold rates after being raised are measured against raises from every player, not ours alone, because our own raises against these teams are few (Gherkers 6, Attention Is All In 12, Equity Engine 17 heads up).
