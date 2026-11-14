# Pressure playbook

Data: 6 practice rounds (r012 to r017), 6,000 hands, 18 opponent teams, measured with `python3 tools/fold_analysis.py ../hands-data/hands`. Every data number below is printed by that script; `n` is the number of opportunities. Rows with n under 30 are marked **unreliable**. Tags: [data], [src: URL], [own] for my reasoning.

How to read the EV numbers: "fold through" is the share of attempts where every opponent facing the bet folded. Break even (BE) for a pure bluff is risk / (pot + risk). EV per attempt is fold × pot − (1 − fold) × risk in bb, with zero equity when called, so it is a lower bound for semi bluffs and a fair estimate for air. Pots and risks are field averages for that spot, taken over everyone's bets, not only ours. Bots mostly decide from their own cards, so a fold rate measured against everyone's bets should carry over to our bluffs [own].

## 1. Verdict

The hypothesis is half right. Preflop the field looks alike (13 of 18 teams have VPIP 0.15 to 0.28) [data], but how they react to pressure differs a lot between teams (fold to a heads up c-bet ranges 0.32 to 0.85 over 13 teams; opener fold to a 3-bet ranges 0.00 to 0.88 over 15 teams) [data]. The field does not fold "too much" in general: its fold rate to any postflop first bet is 0.51 (n=3750). It folds too much in one family of spots: **when it has checked or the aggressor has given up**, and to heads up flop c-bets. It does not fold to raises, 3-bets from most seats, 4-bets, shoves, turn barrels or leads into the aggressor.

| Spot | Fold through | n | BE at size used | EV per attempt (bb) | Verdict |
|---|---|---|---|---|---|
| Turn stab after flop bettor checks turn, HU | 0.67 | 90 | 0.44 | +12.77 | over folds |
| Flop stab after preflop aggressor checks, HU | 0.74 | 46 | 0.45 | +3.90 | over folds |
| River bet after turn checked through, HU | 0.62 | 78 | 0.46 | +4.20 | over folds |
| Flop c-bet HU, 40..70% pot | 0.53 | 532 | 0.35 | +3.63 | over folds |
| Flop bet in limped pot, multiway | 0.66 | 89 | 0.41 | +1.51 | over folds |
| SB steal at 2.5bb or less | 0.86 | 44 | 0.57 | +1.02 | over folds |
| 3-bet vs opener Attention Is All In | 0.77 | 48 | 0.66 | +1.43 | over folds (one seat) |
| Turn barrel HU | 0.32 | 512 | 0.41 | −4.92 | does not fold |
| Flop lead into aggressor HU | 0.29 | 465 | 0.46 | −3.33 | does not fold |
| 3-bet, all openers | 0.44 | 731 | 0.66 | −3.57 | does not fold |
| 4-bet | 0.05 | 320 | 0.71 | −34.12 | never folds |
| Flop bet then raise (bluff raise) | 0.24 | 344 | 0.57 | −26.10 | does not fold |
| Steal from CO | 0.41 | 428 | 0.70 | −1.43 | does not fold |

## 2. Scenario table

Size buckets are fractions of the pot before the bet. "Shrunk" means the per seat rate blended with the field prior (section 3). Hand order for every bluff rule: value first, then semi bluffs (flush draw or straight draw, then overcards with a blocker), pure air last; hands with showdown value (any pair) are checked unless the row says otherwise [own, consistent with the draw first rule at https://upswingpoker.com/double-barreling-tips/].

| Spot | Field (measured) | Theory | Exploit rule for our bot | Size | Stop condition |
|---|---|---|---|---|---|
| Blind steal | Blinds fold: SB vs BTN 0.81 (n=631), SB vs CO 0.79 (589), BB vs BTN 0.61 (676), BB vs CO 0.63 (527), BB vs SB 0.69 (288). Fold through: BTN 0.55 (566), CO 0.41 (428), SB 0.69 (288); SB at 2.5bb or less 0.86 (44) | BB should defend about 83% vs a 2.2x BTN open; vs over folding blinds the BTN opens 63.6% instead of 43.6%, worth about 2bb/100 [src: https://upswingpoker.com/poker-blinds-strategy/, https://upswingpoker.com/how-to-respond-big-blind-small-blind-too-tight/] | SB, folded to us: open to 2.5bb (raise to 50) with any hand when the BB's shrunk fold to SB steal ≥ 0.65. BTN and CO: keep the current range; do not widen as pure bluffs (BTN fold through at 2.5bb or less is 0.58, below its BE 0.62, n=327) | SB 2.5bb; BTN 2.5bb | BB shrunk fold to steal < 0.62 (BE at 2.5bb is 0.57 plus margin) |
| Fold to open by size | Per responder fold: ≤2.5bb 0.76 (3521), 2.5..3.5bb 0.79 (6857), 3.5..5bb 0.76 (2296) | Small opens cost less per steal [own] | Use 2.5bb everywhere; folds barely rise with size, so bigger opens only raise BE | 2.5bb | none |
| 3-bet | Opener folds 0.47 (973), 4-bets 0.28. Fold through 0.44 (731), BE 0.66. Per opener: WBot 0.72 (128), Attention 0.77 (48), bigRoddy 0.03 (95), ND 0.03 (32), Joca 0.00 (39) | 3x the open in position, 4 to 4.5x out of position; add bluffs vs players who fold to 3-bets, go linear vs players who do not [src: https://upswingpoker.com/3-bet-strategy-aggressive-preflop/]. Bluffs with an ace or king block the strongest continues [src: https://upswingpoker.com/4-bet-size-strategy/, search result only] | Facing one open, no callers, opener's shrunk fold to 3-bet ≥ 0.75 after ≥ 8 observations: 3-bet bluff with A5s to A2s, K9s to K6s, suited connectors 65s+, then offsuit Ax. Otherwise 3-bet value only | 3x open IP, 4x OOP | Opener shrunk fold to 3-bet < 0.70, or opener 4-bet rate > 0.15 |
| 4-bet | 3-bettor folds 0.06 (322), fold through 0.05 (320) | Bluffs need about 59% folds at 2.5bb / 7.5bb / 19bb sizes [src: https://upswingpoker.com/mdf-vs-no/] | Never 4-bet bluff. 4-bet for value only | n/a | permanent |
| Preflop shove | Responders fold 0.88 to open shoves (pot ≤3bb, n=171), 0.28 (pot 10..30bb, 120), 0.09 (pot >30bb, 265) | Shoves risk 100bb to win 1.5bb: BE 0.98 [data] | No preflop shove as a bluff | n/a | permanent |
| Flop c-bet HU | Fold 0.55 (889), raise 0.07. Fold through by size: <40% 0.40 (45), 40..70% 0.53 (532), 70..110% 0.65 (199), >110% 0.56 (113) | IP c-bet more on high card, paired and disconnected boards, mostly 33%; size up and bet less with draws on board; monotone: bet less and smaller [src: https://blog.gtowizard.com/flop-heuristics-ip-c-betting-in-cash-games/]. Vs over folders bluff more [src: https://blog.gtowizard.com/the-five-imbalances-of-exploitative-poker/] | We raised preflop, 2 players, checked to us or we act first: bet every hand except weak pairs we keep for showdown. Today we bet air only 0.37 of the time (62 air spots) [data] | 55% pot; 75% on boards with a flush draw or 3 connected cards | Responder shrunk fold to c-bet HU < 0.45, or responder raise vs c-bet > 0.15 |
| Flop c-bet multiway | Fold through 0.43 (155), BE 0.46; at 70..110% 0.67 (42) | Multiway: check more (LJ checks 11 points more vs both blinds), pot size bets drop from 18% to 1.3% [src: https://blog.gtowizard.com/playing-in-position-against-two-callers/] | Value and strong draws only. No air | 66% | permanent |
| Flop stab after aggressor checks | HU fold through 0.74 (46); MW 0.44 (25, unreliable) | Checked ranges lose their strong hands, probe light and linear [src: https://blog.gtowizard.com/the-turn-probe-bet/] | Preflop aggressor checked to us HU: bet all air, draws and weak pairs | 66% | Checker shrunk fold < 0.55 or check raise > 0.08 |
| Flop bet in limped pot | HU fold through 0.25 (57); MW 0.66 (89), at 70..110% 0.88 (34) | Limped ranges are capped; solver drops limping except SB [src: https://par.nsf.gov/servlets/purl/10119653] | Multiway limped pot, checked to us: bet air and draws. Heads up limped pot: value only | 75% | MW fold through tracked per table < 0.50 |
| Flop lead into aggressor | HU fold through 0.29 (465), MW 0.21 (84). We lead 0.44 of these spots and lead air 0.18 [data] | Vs players who c-bet a lot, stop donk betting; check and raise [src: https://blog.gtowizard.com/exploiting-excessive-c-betting-by-ip/] | Stop leading air and weak pairs into the aggressor. Lead only monsters and top pair | 50% | n/a |
| Fold to raise after betting | Flop bettor folds to a raise 0.27 (359); bluff raise fold through 0.24 (344), BE 0.57; check raise n=14 (unreliable); field check raise rate 0.00 to 0.12 by team | Raise mostly for value vs over c-bettors; keep a folding range [src: https://blog.gtowizard.com/exploiting-excessive-c-betting-by-ip/] | No bluff raises on any street. Raise for value only | 3x the bet | permanent |
| Turn second barrel | Caller folds 0.32 (512); fold through by size: 40..70% 0.25 (267), 70..110% 0.41 (150), >110% 0.46 (54, BE 0.62) | About 50/50 value to bluff at 75% pot; bluff with draws and blockers [src: https://upswingpoker.com/double-barreling-tips/] | Barrel value and draws with 8+ outs only. Our turn barrels are already value heavy (air bet 0.00 of 8 spots, unreliable) [data] | 70% | Caller shrunk fold to barrel ≥ 0.50: add air |
| Turn stab after flop bettor checks | HU fold through 0.67 (90); at 40..70% 0.76 (33) | Probe after the aggressor gives up [src: https://blog.gtowizard.com/the-turn-probe-bet/] | We called the flop bet, bettor checks turn, HU: bet value, draws, weak pairs and air | 55% | Checker shrunk fold < 0.50 |
| Turn bet after flop checked through | HU fold through 0.50 (84), at 40..70% 0.46 (35), BE 0.35; MW 0.56 (43) | Attack runouts the checked range cannot have [src: https://blog.gtowizard.com/the-five-imbalances-of-exploitative-poker/] | HU, checked to us or first: bet air and draws (today air 0.07, draws 0.09 of the time) | 50% | Responder shrunk fold < 0.45 |
| Turn raise | Bettor folds 0.18 (131); bluff raise fold through 0.17 (124) | as flop raise | No bluff raises | n/a | permanent |
| River bet by size (HU) | Fold through: <40% 0.14 (77), 40..70% 0.46 (203), 70..110% 0.48 (118) | Bigger bets allow more bluffs; 66 to 75% pot usually best [src: https://upswingpoker.com/mdf-vs-no/] | Never bluff below 40% pot | 50 to 60% | n/a |
| River after turn checked through | HU fold through 0.62 (78), 40..70% 0.58 (36), 70..110% 0.64 (36); MW 0.64 (42). We bet air here 0.02 of the time (50 air spots) [data] | Same as turn probe [src: https://blog.gtowizard.com/the-turn-probe-bet/] | HU, checked to us or first: bluff all no pair hands, busted draws first. Check weak pairs | 55% | Responder shrunk fold to river bet < 0.45 |
| River third barrel | HU fold through 0.34 (280), BE 0.33 | The population tends to under bluff rivers [src: https://upswingpoker.com/mdf-vs-no/]; callers still decide from their own hand [own] | Third barrel value only, plus busted draws vs seats with shrunk river fold ≥ 0.55 | 55% | default off |
| River stab after turn bettor checks | HU fold through 0.76 (25, unreliable) | as above | Treat like the turn stab once n ≥ 30 | 55% | Checker shrunk fold < 0.50 |
| River raise or shove | Bettor folds to raise 0.10 (61); bluff raise fold through 0.08 (59); shove fold through 0.29 (94) | Population under bluffs river raises, fold to them [src: https://upswingpoker.com/mdf-vs-no/] | No river bluff raises or bluff shoves | n/a | permanent |
| Overbets | Flop c-bet >110% fold through 0.56 vs BE 0.71 (113); turn barrel >110% 0.46 vs 0.62 (54) | Overbet with nut advantage on bricks vs capped ranges, 125% to 300% pot, polarized [src: https://upswingpoker.com/overbetting-poker-when-should-you-overbet/] | Overbet for value only (two pair or better) vs seats whose call rate vs big bets is high. Never as a bluff | 150% | n/a |

## 3. Per opponent switches

Observations come from watching every hand at the table, not only ours. Per opponent observation rates per 100 hands [data]: blind vs steal rows sum to 7.74 (1.93 + 1.51 + 0.82 + 1.80 + 1.68), flop c-bet HU 2.54, opener vs 3-bet 2.78, turn barrel HU 1.46, river bet HU 1.18. So the c-bet and 3-bet stats reach 8 observations only after about 300 hands [own arithmetic: 8 / 2.78 × 100 = 288].

Shrinkage: `shrunk = (prior × N0 + folds) / (N0 + n)`. Priors and pseudo counts N0 estimated from the spread between teams (beta binomial, method of moments) [data]:

| Stat | Prior p | Between team sd | N0 | Teams | Team range |
|---|---|---|---|---|---|
| Fold to any postflop first bet | 0.51 | 0.10 | 25 | 17 | 0.21..0.74 |
| Fold vs steal (blinds) | 0.71 | 0.10 | 20 | 16 | 0.40..0.85 |
| Fold to c-bet HU | 0.55 | 0.14 | 12 | 13 | 0.32..0.85 |
| Fold to c-bet MW | 0.69 | 0.12 | 13 | 8 | 0.47..1.00 |
| Opener fold to 3-bet | 0.46 | 0.28 | 2 | 15 | 0.00..0.88 |
| Fold to turn barrel | 0.33 | 0.07 | 42 | 14 | 0.08..0.56 |
| Fold to river bet | 0.48 | 0.15 | 10 | 13 | 0.15..0.86 |

When to switch on [own]: population level rules (flop c-bet HU, stabs after checks, river after turn checks through) start at hand 1, because the prior alone beats BE by 10 points or more. Seat specific rules (3-bet bluffs, third barrels) need the shrunk rate to clear BE + 0.10 with at least 8 observations. Turn a rule off when the shrunk rate drops below BE + 0.03 (hysteresis so one call does not flip it).

Detection rules [own thresholds, anchored on the measured teams]:

* **Station**: shrunk fold to any postflop first bet < 0.35 after 20 or more observations (YSL_TWIZZY measured 0.21, n=116), or VPIP > 0.40 with PFR under a third of VPIP (FisherMen VPIP 0.42, PFR 0.07). Action: no bluffs at that seat, value bet top pair or better on all three streets at 66 to 75% pot.
* **Maniac**: VPIP > 0.45 and 3-bet vs open > 0.15 after 50 hands (bigRoddy VPIP 0.55, 3-bet 0.20; Joca VPIP 0.66, 3-bet 0.33). Action: no preflop bluffs, no 3-bet bluffs (fold through vs bigRoddy 0.03, n=95; Joca 0.00, n=39), call 3-bets and shoves wider. Postflop stats decide separately: bigRoddy still folds 0.85 to heads up c-bets (n=105).
* **Fights back**: raise vs postflop bet > 0.15 (WBot 0.21, bigRoddy 0.18, FisherMen 0.26, Gherkers 0.27, Joca 0.32, Equity Engine 0.17) or check raise > 0.08 (Gherkers 0.12). Action: c-bet air at that seat only on dry high card boards at 33%, give up when raised.
* **Our own bets get raised**: if any seat raises more than 0.25 of our first bets over 12 or more of our bets, drop pure air from every bluff rule against that seat [own]. Field baseline vs us: flop first bets raised 0.13 (n=199), turn 0.20 (89), river 0.04 (46).

## 4. Self protection

* **Small bets**: MDF vs a bet b into pot P is P / (P + b): 0.75 vs 33%, 0.67 vs 50% [src: https://upswingpoker.com/mdf-vs-no/]. Our fold to heads up c-bets is 0.27 (n=122), well inside it. Our fold to a turn bet after the flop checks through is 0.88 (n=32): this is exactly the stab spot in section 2, so a bot running this playbook would farm us. Rule: facing a bet ≤ 70% pot after both players checked the previous street, continue with any pair, any draw, and two overcards, so we fold at most about 0.45 [own].
* **Big turn and river bets**: when the field bets over 60% pot on the turn or river and shows down, it holds a monster 0.41, top pair 0.26, weak pair 0.17, draw 0.07, air 0.10 (n=337). That is 0.17 bluffs against the 0.30 a 75% bet allows [src for 0.30: https://upswingpoker.com/mdf-vs-no/]. So fold weak pairs and ace high to big turn and river bets by default; call down only seats with a measured bluff share above 0.25 at showdown (FisherMen air 0.26, n=31; bigRoddy draws and air 0.31, n=36). Under bluffing opponents call for folding bluff catchers and stopping bluff raises [src: https://blog.gtowizard.com/how-to-adjust-when-villain-has-no-bluffs/].
* **Their calls are loose**: opponents who called a bet over 60% pot and showed down held weak pair 0.29 and air 0.15 (n=474). Value bets can be thinner than the bluffs are wide: bet top pair for value on all three streets against any seat that is not a nit.
* **Raises are value**: field bettors who get raised fold only 0.27 on the flop, and the field rarely bluff raises (raise vs bet 0.04 to 0.32 by team). Fold one pair to turn and river raises from seats with raise vs bet under 0.10.
* **3-bets against us**: our opens get raised 0.19 (n=595) and our 3-bets get 4-bet 0.32 (n=146); we fold to 4-bets 0.17 (n=42) and the field 4-bets 0.28 of the time it faces a 3-bet (n=973). Against seats flagged as maniacs, 3-bet only hands we will get all in with [own].
* **When to trap**: the field bets into a heads up check 0.39 of the time (n=2355), and into our checks 0.36 (n=388), so it is not targeting us. Betting beats checking monsters by default; check monsters only out of position against seats that bet into checks often, and only on boards where we would also check air [own]. Pluribus computes how it would act with every hand it could hold and balances across them so its action does not give its hand away [src: https://par.nsf.gov/servlets/purl/10119653].
* **Do not become predictable**: with the stab rules on, our bets after an opponent check become mostly air. Keep top pair and draws in every stab range (the hand order above), and use the same size for value and bluffs in each spot [own].

## 5. Ranked implementation list

Arithmetic: extra attempts per 100 hands = our opportunities per 100 × share of those spots where we hold the hands the rule adds × share of those we do not bet today. Gain = extra attempts × EV per attempt (field, pure bluff, lower bound). Our opportunity counts and hand class shares come from section 7 of the script output (6,000 of our hands). Gains are not additive exactly, because earlier streets change later opportunities [own].

1. **River bluff after turn checked through, HU, 55% pot.** Opportunities 1.47 per 100 (n=88); air 0.57 of spots, bet 0.02 today. Extra attempts 1.47 × 0.57 × 0.98 = 0.82. EV +4.20 per attempt (n=78). Gain ≈ 0.82 × 4.20 = **+3.4 bb/100**. Cost: one line classification (first bettor per street, who checked) plus a no pair check. Microseconds.
2. **Flop c-bet HU with all air and draws, 55% pot.** Opportunities 2.45 per 100 (n=147); air 0.42 of spots bet 0.37, draws 0.06 bet 0.44. Extra attempts 2.45 × (0.42 × 0.63 + 0.06 × 0.56) = 2.45 × 0.298 = 0.73. EV +3.63 (n=532). Gain ≈ 0.73 × 3.63 = **+2.7 bb/100**. Cost: none beyond existing c-bet code; switch off per seat with the c-bet fold counter.
3. **Turn stabs when the opponent checks the turn, HU, 55% pot.** (a) Flop bettor checks turn to us: opportunities 0.28 per 100 (n=17, unreliable hand mix), bet 0.47 today, so extra 0.28 × 0.53 = 0.15 attempts × EV +12.77 (n=90) = +1.9. (b) Flop checked through: opportunities 1.12 per 100 (n=67); air 0.43 bet 0.07, draws 0.33 bet 0.09; extra 1.12 × (0.43 × 0.93 + 0.33 × 0.91) = 1.12 × 0.70 = 0.78 attempts × EV +1.05 (40..70%, n=35) = +0.8. Gain ≈ **+2.7 bb/100**. Cost: same line state as item 1.
4. **Flop stabs: aggressor checks HU, and multiway limped pots.** (a) Opportunities 0.28 per 100 (n=17), bet 0.41 today: 0.28 × 0.59 = 0.17 attempts × EV +3.90 (n=46) = +0.6. (b) Multiway limped pot: opportunities 0.90 per 100 (n=54); air 0.44 bet 0.00, draws 0.15 bet 0.12; 0.90 × (0.44 + 0.15 × 0.88) = 0.90 × 0.57 = 0.51 attempts × EV +1.51 (n=89) = +0.8. Gain ≈ **+1.4 bb/100**. Cost: needs "who was preflop aggressor" and "limped pot" flags.
5. **SB steal at 2.5bb with any two when the BB folds to steals.** Opportunities 1.50 per 100 (n=90), raise 0.51 today, mostly at 3.5..5bb (33 of 46), where our SB opens made EV +0.44 per attempt (n=33). Field EV at ≤2.5bb +1.02 (n=44). Resize: 1.50 × 0.51 × (1.02 − 0.44) = 0.44. Widen: 1.50 × 0.49 × 1.02 = 0.75. Gain ≈ **+1.2 bb/100**. Cost: trivial; per seat BB counter for the stop rule.

Next after these: 3-bet bluffs only vs measured over folders. Vs Attention Is All In we face 17.60 opens per 100 hands when it sits with us; 0.10 more 3-bets × 17.60 × EV +1.43 (n=48) = +2.5 bb/100 at those tables, but over our 6 rounds (352 opens from Attention, 331 from WBot at EV +0.62, n=128) it is (352 × 0.10 × 1.43 + 331 × 0.10 × 0.62) / 6000 × 100 ≈ +1.2 bb/100 before the 300 hand warm up. Cost: a per seat 3-bet response counter.

Also stop the leak in the opposite direction: our flop leads into the aggressor fold through 0.36 (n=56, EV −0.53), field leads −3.33 (n=465). Stopping air leads saves 2.13 per 100 × 0.45 air × 0.18 bet × 3.33 ≈ 0.6 bb/100.

### Spots where pressure loses money

* Preflop opens as bluffs from EP (fold through 0.17, n=591, EV −4.14), HJ (0.32, n=339, −3.14), CO (0.41, n=428, −1.43); BTN pure air steals are slightly negative (0.55 vs BE 0.66, n=566, −0.51).
* 3-bets in general (0.44, n=731, −3.57) and especially vs bigRoddy (0.03, n=95, −8.99), ND (0.03, n=32, −7.64), Joca (0.00, n=39, −8.94), Claudebot (0.47, n=74, −5.24), Jump Street (0.42, n=89, −3.21), Phil AIvey (0.39, n=51, −4.13).
* Any 4-bet bluff (0.05, n=320, −34.12), 5-bet (0.05, n=407), preflop shove into a pot over 30bb (0.00, n=198) or 10..30bb (0.09, n=79).
* Flop leads into the aggressor (HU 0.29, n=465, −3.33; MW 0.21, n=84, −5.32), heads up limped pots (0.25, n=57, −0.69), multiway c-bets at 40..70% (0.33, n=92, −0.77), overbet c-bets (0.56 vs 0.71, n=113, −5.13).
* Every bluff raise: flop (0.24, n=344, −26.10), flop raise all in (0.13, n=105), turn (0.17, n=124, −39.79), river (0.08, n=59, −51.78).
* Turn barrels as bluffs (0.32, n=512, −4.92), turn overbets (0.46 vs 0.62, n=54, −14.61), turn leads into the flop bettor (0.23, n=80, −7.11), turn shoves (0.32 vs 0.43, n=82, −16.30).
* River bets under 40% pot (0.14, n=77, −4.87) and river third barrels (0.34 vs 0.33, n=280, about zero).
* Against stations and maniacs at any street: YSL_TWIZZY folds to any first bet 0.21 (n=116), Astra La Vista folds to river bets 0.30 (n=53).

## 6. Sources

* https://blog.gtowizard.com/flop-heuristics-ip-c-betting-in-cash-games/ : IP c-bet sizes and frequency by texture (33% common, 66% on straight draw boards, less betting on monotone and flush draw boards).
* https://blog.gtowizard.com/how-to-adjust-when-villain-has-no-bluffs/ : vs non bluffers bet 100% instead of 67%, fold about 82% vs raises instead of about 40%, drop bluff raises.
* https://blog.gtowizard.com/the-five-imbalances-of-exploitative-poker/ : bluff more vs over folders, size up vs elastic folders, attack runouts a checked range cannot hold.
* https://blog.gtowizard.com/the-turn-probe-bet/ : probe after a checked back flop, mostly small and linear; check raise instead vs over c-bettors.
* https://blog.gtowizard.com/exploiting-excessive-c-betting-by-ip/ : stop donk betting and raise more vs over c-bettors, keep a folding range.
* https://blog.gtowizard.com/playing-in-position-against-two-callers/ : multiway checking rises 11 points, pot size c-bets fall from 18% to 1.3%.
* https://upswingpoker.com/double-barreling-tips/ : turn value to bluff about 50/50 at 75% pot, bluff with draws and blockers.
* https://upswingpoker.com/how-to-respond-big-blind-small-blind-too-tight/ : BTN opens 63.6% instead of 43.6% vs tight blinds, about 2bb/100.
* https://upswingpoker.com/poker-blinds-strategy/ : BB defends about 83% vs a 2.2x BTN open (search result summary).
* https://upswingpoker.com/3-bet-strategy-aggressive-preflop/ : 3-bet 3x IP, 4 to 4.5x OOP, polarized vs linear, add bluffs vs folders.
* https://upswingpoker.com/4-bet-size-strategy/ : blockers for 4-bet bluffs (search result only, not opened).
* https://upswingpoker.com/mdf-vs-no/ : MDF use and limits; population under bluffs river bets and river raises; 75% bet allows about 30% bluffs.
* https://upswingpoker.com/overbetting-poker-when-should-you-overbet/ : overbet with nut advantage vs capped ranges on bricks, 125% to 300% (search result summary).
* https://par.nsf.gov/servlets/purl/10119653 : Pluribus (Science 2019): 1 to 14 bet sizes per decision, limping discarded except SB, donk bets used more than pros, balances its strategy across all hands it could hold.
* docs/x-findings.md : field fold rates and overshooting when folding too much (Nguyen and Choi write up).
