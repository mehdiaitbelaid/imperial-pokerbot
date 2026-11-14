# V18 live bot, opponents, and what to change

Source: `review/opponent_profiles.py` (imports card classes, positions and loss buckets from `review/live_diagnosis.py`) run on the counted rounds `hands-data/hands/saturday_r001.json` to `saturday_r013.json`, refreshed with `pull.py` at the start and again before writing (no r014 yet). Every number below is printed by that script unless it is marked as arithmetic or as an assumption. Rates read k/n; n under 30 is marked * and is unreliable. bb/100 is over all hands of the version or seat in question.

| Version | Bot | Counted rounds | Hands | bb/100 per round | Mean |
|---|---|---|---|---|---|
| 5 | vastra-fable-r2.py | r001, r002 | 2,000 | -7.9, -18.9 | -13.4 |
| 6 | riad_avengers_v14.py | r003 to r011 | 9,000 | 36.9, 65.2, 36.2, 75.7, 3.5, 45.3, 12.9, 77.5, 3.9 | +39.7 (sd 29.0 per round) |
| 7 | riad_live_v7.py (V18) | r012, r013 | 2,000 | 21.0, 20.4 | +20.7 |

V18 has two rounds. Everything measured on it alone is a 2,000 hand sample and, at a per round sd of 29 bb/100, its mean is not distinguishable from v6's.

**Late round r014.** Counted round r014 (V18, +28.0, table: Chinese people can fly, GamesGone, munchlax, aydine, matcha mille crêpes cake) arrived at the final pull, after the body of this report was written on r001 to r013. Rerunning the script on all 14 rounds gives, for V18 over 3,000 hands: +23.1 bb/100 (rounds 21.0, 20.4, 28.0); 3-bet .18 (243/1342), fold to 3-bet .62 (58/93); 3-bet then folded to a 4-bet 46 times (−7,685 chips, −12.8 bb/100), so change 1 stands; raise a bet flop / turn / river .04 (7/195) / .02 (2/118) / .04 (3/80), 11 raises in all (0.37 per 100 hands against 0.79 in v6), so change 2 stands at about half the estimate (0.42 × 7 ≈ +3 bb/100); fold to bet flop / turn / river .38 (195) / .42 (118) / .53 (80), so the river overfold in change 5 is smaller than the two round figure. Money flows on 14 rounds sum to 79,916 chips, equal to our total. The tables below keep the 13 round figures.

## Part 1. How V18 decides

`riad_live_v7.py` holds two zlib/base64 blobs and a 40 line wrapper. `_PRE_SRC` is the v17 preflop agent (the v14 Avengers bot plus a stricter starter kit detector); `_POST_SRC` is byte identical to `review/hassan_var_approach.py`. The wrapper sends preflop decisions to the first and flop, turn and river to the second; both learn from every `on_hand_end`. Line numbers below are in the decoded sources.

**Preflop (decoded `_PRE_SRC`, `Agent._preflop`, line 658).**
- Opening: seven nested hand levels (line 186). First in, it opens level ≤ 5 minus seats to the button: UTG opens level 0 (66+, ATs+, A5s to A4s, KTs+, QTs+, JTs, T9s, AJo+, KQo), the button level 5, the SB level 5 if pair or suited else 4. Steals widen by 1 or by 9 levels when the blinds' learned fold to steal (`r_sf`, prior 0.7 with 6 pseudo counts) times the button's non VPIP clears 0.46 / 0.62 (SB 0.60 / 0.74). Sizes: 3.0 bb early, 2.2 bb CO and BTN, 2.5 bb SB, at least 3.25 bb when a blind is a limp folder.
- Limped pots: isolates to 3.5 bb plus 1 bb per extra limper against limp folders; otherwise 4 bb plus limpers, bigger against a whale.
- Facing one raise: value 3-bet with AA, KK or preflop equity against the raiser's range ≥ 0.60 in position, 0.62 out (range width from the raiser's PFR, ×1.4 for late opens). Size 3.0× in position, 3.7× out, +0.8× against a sticky or loose opener. Bluff 3-bets (line 828) when callers = 0 and the open is ≤ 4.5 bb: any level ≤ 6 hand if the opener folded to 3-bets ≥ 78% over ≥ 3, level ≤ 5 at ≥ 70% over ≥ 2, the BLUFF3 list (A5s to A2s, KTs, K9s, QTs, Q9s, J9s, AJo, ATo, KQo, KJo) while the shrunk fold rate is ≥ 0.55. The prior is 0.58 with 3 pseudo counts, so it bluffs every new seat until that seat has defended.
- Flats: pairs up to 6.5 bb, AK up to 8 bb, suited broadways in position or in the BB up to 5 bb; the SB never flats suited broadways (line 846 needs `ip or rel == 2`).
- BB defence: any level ≤ 5 at ≤ 1.5 bb, level ≤ 2 or BB_OFF offsuit or suited level ≤ 4 at ≤ 2.5 bb.
- 3-bet faced after opening: AA, KK or equity ≥ 0.62 4-bet (jam if the 3-bettor's rate ≥ 15% or the 3-bet ≥ 14 bb); call with equity ≥ 0.40 / 0.43 at ≤ 10 bb, pairs at ≤ 6 bb, six suited broadways in position. 4-bets: jam AA, KK; jam equity ≥ 0.56 after our own raise.
- Shoves: call when equity against the seat's shove range (from its shove frequency ×1.3) beats the price by 2%, 6% with callers.
- Starter kit seats (pair, ace or king raisers who never fold): equity table against that exact range.

**Postflop (decoded `_POST_SRC`, `Agent._postflop`, line 1390).**
- Equity: Monte Carlo (≤ 600 trials, ≤ 0.9 ms) against each live seat's range: preflop width from its VPIP, PFR, 3-bet and shove stats blended with what it showed down, then weighted by postflop line (bet, raise, call, check) and by the seat's "bluffiness" (aggression and VPIP). Turn and river bets ≥ 0.60 pot from a seat with bluffiness < 0.30 get the fixed value heavy mix BIG_BET_W (air 0.04, draw 0.15, weak pair 0.20, top pair 0.55, monster 1.0; line 143, applied at line 1385). Falls back to a closed form `quick_equity` when the time budget is spent.
- Betting when checked to: value bet when equity ≥ 0.60 heads up (0.48 three way), 0.64 on the river; size 0.60 / 0.65 / 0.70 pot by street, 0.85 with equity ≥ 0.80 or against stations, +0.10 on wet boards. No leads into the previous aggressor without top pair.
- Bluffs and thin bets: named spots (c-bet, stab after a check, checked through turn or river, turn barrel, limped multiway) bet only when EV(bet) − EV(check) > 2% of the pot, using a beta shrunk per seat fold rate (field prior per spot, seat shift in log odds), a fixed size per spot (0.66 flop, 0.55 later, 0.80 wet c-bet), capped equity when called and hysteresis that switches air off when the seat's fold rate drops near break even. River bluff outside those spots: 30% of the time when the seat folds > 55% of rivers over ≥ 8.
- Facing a bet: call when equity ≥ pot odds + 2% (+2% multiway, −4% for draws with stacks behind). Heads up before the river, fold air to bets ≥ 0.5 pot, weak pairs need +4%. Raise only with equity ≥ 0.80 heads up (0.70 three way), to the current bet plus 0.85 pot; slow play 50% against maniacs.
- Opponent model: preflop agent tracks per seat VPIP, PFR, 3-bet, fold to 3-bet, shove, limp folds, fold to steal, fold by line and size, c-bet, usual bet size, showdown air; postflop agent tracks VPIP, PFR, 3-bet, shove, aggression, fold to bet, river fold, showdown ranges, min raises. Priors are 6 to 25 pseudo counts, so a seat moves halfway to its own rate after 6 to 25 events. Classes: spammer (> 20% shoves after 12 hands), maniac, station, nit, minraiser after 25 hands; starter kit bot in the preflop agent.
- Time: the postflop agent aims for 1.3 s per round (ROUND_TARGET), 0.9 ms per Monte Carlo, keeps 0.6 ms for stack decisions while under 5 s. Site think time 2.21 s (r012), 1 timeout in each of r012 and r013.

### Measured behaviour

| Stat | v5 (2,000) | v6 (9,000) | V18 (2,000) |
|---|---|---|---|
| VPIP | .18 (353/2000) | .23 (2111/9000) | .25 (501/2000) |
| PFR | .12 | .17 | .20 (394/2000) |
| 3-bet | .03 (24/790) | .11 (411/3776) | .17 (147/858) |
| Fold to 3-bet | .38 (12/32) | .57 (127/221) | .60 (41/68) |
| Open first in CO / BTN / SB | .20 / .39 / .78* | .29 / .45 / .66 | .28 (30/109) / .51 (46/90) / .65 (24/37) |
| Blind defence vs steal fold / 3-bet | .79 / .03 (122) | .73 / .10 (443) | .52 / .32 (121) |
| C-bet (median size) | .76 (0.60) n50 | .86 (0.80) n307 | .74 (0.70) n62 |
| Flop bet when checked to | .49 (148) | .60 (693) | .41 (69/169) |
| Turn / river bet when checked to | .38 / .17 | .55 / .49 (358 / 171) | .48 (53/111) / .39 (24/61) |
| Fold to bet flop / turn / river | .48 / .40 / .38* | .53 / .39 / .40 (589 / 268 / 129) | .41 (53/128) / .55 (38/69) / .67 (28/42) |
| Fold to bet < 40% / 40 to 75% / > 75% pot | .14 / .54 / .49 | .23 / .48 / .63 | .24 (11/45) / .53 (48/90) / .58 (60/104) |
| Raise a bet flop / turn / river | .04 / .09 / .12* | .06 / .10 / .10 | .02 (2/128) / .00 (0/69) / .00 (0/42) |
| WTSD / won at showdown | .36 / .47 (74) | .25 / .59 (268) | .24 / .62 (38/61) |

Result by position, V18 (bb/100 in that seat, n ≈ 286 each, all unreliable at this size): UTG +68, MP −46, HJ +33, CO −20, BTN +41, SB +65, BB +5. Pot ended on: preflop +38.5 (1176 hands), flop +4.4 (323), turn −6.5 (194), river −15.7 (307).

Loss decomposition (bb/100 over the version's hands, sums to the site total):

| Bucket | v6 (n) | V18 (n) |
|---|---|---|
| Showdown won | +110.3 (159) | +103.1 (38) |
| Won postflop, no showdown | +42.6 (404) | +28.1 (80) |
| Won preflop uncontested | +22.8 (780) | +27.2 (178) |
| Showdown lost, other line | −60.6 (80) | −24.3 (16*) |
| Showdown lost after river call | −17.8 (29*) | −27.5 (7*) |
| River fold | −9.9 (52) | −23.5 (28*) |
| Opened (or 3-bet) then folded preflop | −8.6 (170) | −19.5 (73) |
| Raised preflop, no c-bet, folded flop or turn | −7.8 (124) | −16.2 (43) |
| Blinds folded, no contest | −13.3 (6816) | −12.9 (1457) |
| Called preflop, folded flop or turn | −11.8 (252) | −10.5 (38) |
| Total | +39.7 | +20.7 |

What V18 does differently from v14, by code, that two rounds cannot show yet: (1) it almost never raises postflop (RAISE_EQ 0.80 heads up against v14's raise logic; 2 raises in 2,000 hands against 71 in 9,000 for v6, which made +40,789 chips on them); (2) river calls against big bets use a fixed value heavy range for every seat with bluffiness < 0.30, so it folds more rivers (.67 vs .40) and the calls it makes are the strongest hands; (3) bet sizes in pressure spots are fixed per spot, never per seat, while v14 read size against each seat's habit; (4) the air fold rule (fold no pair to ≥ 0.5 pot bets before the river) lowers flop folding only because it keeps more weak pairs and draws; (5) the starter kit counter is stricter (only seats that never fold or check their raising hands), which matters only at a kit whale table, none of which V18 has met.

## Part 2. Opponents

37 teams sat with us in counted rounds; all hands they played at our tables are used (1,000 per round). "To us" is the money flow from that team to our seat: in each hand every loser's loss is split across the winners in proportion to what they won. These flows sum to +74,322 chips, exactly our result over the 13 rounds.

### (a) Teams ranked above us

| Team (standing) | Hands with us | bb/100 at our tables | VPIP / PFR / 3-bet / 4-bet | Fold to 3-bet | Open size | C-bet (size) | Turn / river bet when checked to (size) | Fold to bet F / T / R | Fold to bet > 75% pot | Fold to raise after betting | WTSD / won | To us |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Attention Is All In (1) | 4000 (r005, r007, r009, r011) | +43.1 | .32 / .26 / .12 / .02 | .73 (279/382) | 2.5 bb 55%, 2 bb 28% | .66 (0.33) n300 | .60 / .66 (0.33) n301/196 | .63 / .59 / .57 | .84 (178/212) | .80 (51/64) | .23 / .55 | −8,125 (−10.2 bb/100) |
| Gherkers (2) | 3000 (r001, r004, r009) | +46.6 | .29 / .22 / .21 / .04 | .40 (17/43) | always 3.5 bb (350/350) | .76 (0.70) n127 | .53 / .32 (0.70) n146/73 | .54 / .63 / .62 | .79 (103/131) | .75 (21/28*) | .19 / .56 | −815 (−1.4) |
| Equity Engine (3) | 3000 (r001, r003, r006) | +9.9 | .23 / .17 / .02 / .03 | .50 (65/129) | always 3.5 bb (392/392) | .74 (0.50) n99 | .39 / .40 (0.80) | .53 / .46 / .43 | .59 (81/137) | .81 (25/31) | .28 / .44 | +6,398 (+10.7) |
| AAST (4) | 1000 (r013) | −14.5 | .22 / .13 / .04 / .06 | .48 (14/29*) | always 3 bb (84/84) | .61 (1.10) n38 | .57 (1.10) n40 / .35 n23* | .55 / .59* / .75* | .70 (31/44) | .62 (5/8*) | .30 / .43 | +278 (+1.4) |
| ND (5) | 3000 (r003, r005, r012) | +4.1 | .20 / .10 / .06 / .10 | .27 (10/37) | always 3 bb (187/187) | .62 (0.75) n65 | .33 / .33 (0.75) | .46 / .34 / .41 | .60 (84/140) | .06 (1/17*) | .35 / .43 | +3,036 (+5.1) |
| The Market Makers (6) | 3000 (r001, r005, r008) | −7.1 | .20 / .12 / .04 / .03 | .43 (19/44) | always 2.5 bb (308/308) | .81 (0.70) n91 | .74 / .66 (0.70 / 0.60) | .43 / .51 / .66 | .67 (66/99) | .49 (23/47) | .23 / .44 | +4,013 (+6.7) |

Style and weakness, one line each:
- **Attention Is All In**: loose aggressive, opens 40% to 53% from MP to CO, bets one third pot on every street when checked to. Weakness: folds 84% to bets over 75% pot (212) and 80% when its own bet is raised (64), folds 73% to 3-bets (382). It is the team we lose most to among the top six.
- **Gherkers**: 3-bet machine (21% of 1,470 chances, 3.8× size), steals 73% BTN and 94% SB. Weakness: folds 77% to flop bets over 75% pot (87) and bets the river only 32% when checked to.
- **Equity Engine**: tight, never 3-bets (2% of 1,247, 1% of 149 blind defences), fixed 3.5 bb opens. Weakness: folds 81% after its bet is raised (31); a 3-bet from it is close to QQ+.
- **AAST**: one round only; bets 1.1 pot on every street. Weakness: folds 70% to big bets (44), WTSD won 43%; sample too small for more.
- **ND**: passive caller, PFR half of VPIP, folds only 35% to 40 to 75% pot bets (159) and 6% to raises after betting (17*). Weakness: calls too much, so it pays value bets and ignores bluffs.
- **The Market Makers**: barreler at 0.70 pot (flop .75, turn .74, river .66 when checked to). After big bets it showed 12 of 38 weak pair or no made hand. Weakness: overbluffs big bets relative to a 28% bluff catch price.

Exact opening formulas found: Gherkers and Equity Engine 3.5 bb on 100% of opens, ND and AAST 3 bb on 100%, The Market Makers 2.5 bb on 100%, WBot 3.5 bb 94%, FisherMen 3.25 bb 74%. FisherMen isolates limpers to 8 to 10 bb. bigRoddy opens 2.5 bb on 76% of its opens and 100 bb on 13% (open shove in 42 of 1,461 first in chances).

Teams that took the most from us: WBot −16.2 bb/100 (2000 hands), FisherMen −14.0 (3000), Attention Is All In −10.2 (4000), Peanut Cookies −6.8 (2000), Vlad −3.6 (3000). Largest sources: ediz_slow +55.3 (2000), YSL_TWIZZY +36.0 (1000), Anton +27.6 (1000), Claudebot +20.5 (2000). Full per team blocks for all 37 are in the script output.

### (b) Archetypes

Teams with at least 500 hands at our tables (36 of 37). Rule applied in this order on the seat's own stats; VPIP, PFR, limp and 3-bet settle within 50 to 100 hands; turn plus river aggression has only 7 to 12 chances per 100 hands, so it needs the full 100 and remains noisy.

| Archetype | Share (teams) | Detection rule (seat stats) | Pooled evidence | Counter |
|---|---|---|---|---|
| Whale / limper | 6% (ediz_slow, YSL_TWIZZY) | limp ≥ 20% of non BB first actions, or VPIP ≥ 45%, or VPIP ≥ 32% with flop fold < 30% | VPIP .62, limp .42 (1422), WTSD .52, won .43 (464) | Isolate to 4 to 5 bb plus limpers with level ≤ 4, value bet 0.85 pot down to top pair, no bluffs. Already done; +48.9 bb/100 to us. |
| Maniac / shover | 3% (bigRoddy) | preflop shove ≥ 3% of hands or PFR ≥ 40% | open shove 3% (42/1461), BTN open .97, SB 1.00, 3-bet .23 (1564) | Call shoves with the top 12% to 15% (equity vs its shove range plus 2%), never bluff 3-bet it, flat its 2.5 bb opens with pairs. |
| Nit | 22% (Joca, SmartBGerBot, gamblerlove, test, Peanut Cookies, Jump Street, supernut, SARS) | VPIP < 18% | blinds fold to steals .81 (1015), 3-bet .02 (6358), fold to 3-bet .71 (372) | When both blinds are nits steal any two from BTN at 2.2 bb (both fold .81 × .81 = .66 > .595 break even); fold to their 3-bets and river raises. |
| 3-bet aggressor | 6% (Gherkers, Anton) | 3-bet ≥ 15% of chances | 3-bet .21 (1933), 4-bet .19 (236), fold to bets > 75% pot .73 (168), fold to raise after betting .68 (31) | No bluff 3-bets into them, 4-bet QQ+, AK and jam over their 4-bets with QQ+; postflop bluff at ≥ 0.8 pot. |
| Small bet barreler | 11% (Attention Is All In, WBot, Chinese people can fly, Astra La Vista) | turn plus river bet when checked to ≥ 60% with median size ≤ 0.40 pot | c-bet .75, turn .72, river .69 at 0.33 pot; fold to 3-bet .72 (786); fold to bets > 75% pot .71 (489) | Never fold a pair to a 0.33 pot bet (price 20%); raise their bets to 3× with draws and air when the seat folds ≥ 65% to raises; 3-bet them light (break even about 65% folds). |
| Barreler | 8% (The Market Makers, Red, GamesGone) | same, median size > 0.40 | c-bet .80 at 0.50, turn .73, river .67; after big bets showed weak pair or no made hand 19 of 61 | Bluff catch big turn and river bets with top pair or better (a 0.66 pot bet needs 28%). |
| Passive caller | 11% (AIl IN, ND, Mohil'sPokerBot, AAST) | PFR < 0.6 × VPIP | fold to 40 to 75% pot bets .33 (373), fold to raise after betting .27 (60) | Value bet thinner at 0.75 pot, no bluffs, fold to their raises. |
| Standard TAG | 33% (12 teams incl. Equity Engine, Durahim, matcha, FisherMen, Kojack) | none of the above | fold to 3-bet .46 (1040), steal fold .72 (2268), fold F/T/R .52 / .47 / .49 | Current defaults. |

### (c) Where our chips come from

Money flow to our seat per 100 hands seated together (all versions): whale / limper +48.9 (3000 hands), 3-bet aggressor +5.9 (4000; Gherkers −1.4, Anton +27.6), maniac +5.9 (3000), standard TAG +3.2 (34000), passive caller +2.9 (8000), nit +2.7 (15000), barreler +6.0 (8000), small bet barreler **−3.6** (10000). The only archetype we lose to is the small bet barreler, and the two individual teams costing the most outside it are FisherMen (standard TAG, 4-bets 27% of 271 chances, −14.0) and Peanut Cookies (nit, −6.8, 2000 hands).

## Part 3. Changes, ranked

The estimates multiply opportunities per 100 hands by value per opportunity. Where the value per opportunity cannot be measured from the hands it is marked as an assumption.

| # | Change | Evidence | Estimated gain | Rule | Where | Risk | Validate |
|---|---|---|---|---|---|---|---|
| 1 | Stop bluff 3-betting seats that 4-bet | V18 3-bet then folded to a 4-bet 32 times in 2000 hands (−5,218 chips, −13.0 bb/100); v6 43 in 9000 (−4.3). Of the 32, 19 were against Anton (4-bets .38 of 99) and 6 against FisherMen (.27 of 271). None of the 32 held TT+, AK or AQs. | (1.6 − 0.48 folds per 100 hands) × 8.15 bb = 9.1 bb/100 upper bound; half of that, 4.5, after the bluffs that would have won (3-bets that won preflop averaged +4.26 bb, n=87). | New St fields: our 3-bets against this seat and its 4-bets. No bluff branch (BLUFF3 or level gates) when the seat has 4-bet ≥ 2 of our last ≤ 6 3-bets, or its generic 4-bet rate is ≥ 0.20 over ≥ 8 chances. Value 3-bets unchanged. | Decoded `_PRE_SRC`, `Agent._preflop` lines 828 to 841, plus `St` (line 235) and `_learn` (line 418). | Fewer 3-bets against openers who then also fold; capped by the gate. | `tools/replay.py` over r012 and r013 (count 3-bets removed); league bench with a 4-betting sparring bot. |
| 2 | Raise postflop for value again | V18 raised a bet 2 times in 2000 hands (0.10 per 100); v6 71 in 9000 (0.79 per 100) for +40,789 chips, +28.7 bb per raise realised. | 0.69 extra raises per 100 × assumed 7 bb gained over calling (a quarter of the realised 28.7, an assumption) ≈ +5 bb/100. | Heads up facing a bet, raise to 3× the bet when equity ≥ 0.70 on flop or turn (0.80 now), or with two pair or better using a hole card on a board without a four card flush or straight; river raise to 2.5× with equity ≥ 0.85. | Decoded `_POST_SRC` line 71 (RAISE_EQ) and `_postflop` line 1464. | Raising into the value heavy big bets; keep the slow play against maniacs. | Replay V18's real call decisions with two pair or better and count new raises; bench against v14. |
| 3 | Bet bigger into seats that overfold to big bets | Attention Is All In folds .84 to bets > 75% pot (212) against .48 to 40 to 75% (368); Gherkers .79 (131) against .55 (139); 3-bet aggressor pool .73 (168); small bet barreler pool .71 (489). V18 uses fixed spot sizes 0.55 to 0.80. | Air bet EV per pot P: 1.0 pot at .84 folds = 0.84P − 0.16P = +0.68P; 0.66 pot at .48 = 0.48P − 0.52 × 0.66P = +0.14P; gain 0.54P per air bet. At one air bet per 100 hands with such a seat (assumption) and a 15 bb median pot, about +8 bb/100 at those tables. | In `_ev_bet`, track each seat's fold by size bin (< 0.4, 0.4 to 0.75, > 0.75); evaluate d at 0.66 and 1.0 pot with the seat's shrunk rate for each bin and bet the larger d. | Decoded `_POST_SRC` `_ev_bet` line 899 and `_learn_quant` line 764. | Larger losses when called; d includes that. | Replay every V18 c-bet and stab with the new size chosen; bench against an overfolding sparring bot. |
| 4 | Raise small bets from seats that fold to raises | Seats with fold to raise after betting ≥ .65 over ≥ 10: Attention Is All In .80 (64), Equity Engine .81 (31), pokermon .77 (56), Gherkers .75 (28*). v6 faced their ≤ 50% pot bets heads up 72 times in 9000 (0.8 per 100; median pot before the bet 300 chips): called 53 (−3,631), folded 10 (−1,542), raised 9 (+4,386*). V18 met none of these seats. | Bluff raise against a 0.33 pot bet in a 15 bb pot: raise to 15 bb, win 20 bb at .80 folds: 0.80 × 20 − 0.20 × 15 = +13 bb. Applied to the 10 folds: 0.11 per 100 × 13 = +1.4 bb/100 at those tables, more if air calls are included. | Heads up facing a bet ≤ 0.5 pot from a seat with fold to raise after betting ≥ 0.65 over ≥ 10 (new stat), raise to 3× with air plus backdoors or any draw; keep calling with pairs. | Decoded `_POST_SRC` `_postflop` facing a bet block, lines 1452 to 1472; stat in `_learn` line 648. | Seats that fold to raises but 3-bet when strong; stop after two re-raises seen. | Replay v6 hands against those seats; bench. |
| 5 | Call more rivers against small and medium bets | V18 folded 68% of heads up river bets (27 of 40) against 39% in v6 (48 of 124). V18 river folds to bets ≤ 75% pot: 18* (−5,694 chips). Field pooled showdowns after big turn or river bets: weak pair or no made hand 41 of 188 (standard TAG), 19 of 61 (barreler), 16 of 51 (passive). | Not measurable (folded hands are never shown). Cap: the V18 river fold bucket is −23.5 bb/100 against −9.9 in v6. | Apply BIG_BET_W only to bets ≥ 0.75 pot (now 0.60); against bets ≤ 0.5 pot call with any pair; against barreler seats (turn plus river aggression ≥ 0.60) use the generic bet weights. | Decoded `_POST_SRC` constants line 141 (BIG_BET_FRAC) and `_weights` line 1385. | More payoffs against nits (they showed weak pair or none in 7 of 36 big bets). | Replay V18 river decisions; recount after 5 rounds. |
| 6 | 3-bet top hands from the SB | SB with TT+, 99, AK, AQs, AJs, KQs facing one raise: folded 9 of 40 in v6 and 3 of 13* in V18 (AJs, AJs, AQs); SB raises with these hands made +10,916 chips over 32. The SB never flats suited broadways (line 846). | 12 folds in 11,000 hands = 0.11 per 100 × (17.1 bb per SB 3-bet + 0.5 bb blind) ≈ +1.9 bb/100, an upper bound because the raised hands include AA and KK. | In the SB facing one raise, 3-bet TOP5 hands to 3.7× regardless of the equity gate. | Decoded `_PRE_SRC` `_preflop` lines 822 to 846. | Small. | Replay the 12 hands. |
| 7 | Deadline fallback for premium preflop hands | V18 folded JJ in the BB to a 3 bb open with no raise behind (r012#736, to_call 40), which no V18 rule produces; the site counted 1 timeout in each V18 round. | Below 1 bb/100. | In the wrapper, when the preflop agent errors or returns nothing, call or raise TT+, AK instead of check or fold. | `riad_live_v7.py` `Agent.act`, the `except Exception: out = None` path. | None. | Unit test with a forced exception. |
| 8 | Steal wider from CO against nit blinds | V18 CO opens .28 (30/109) earned +5.39 bb each (30); v6 .29 (137) earned +3.36 bb. Nit blinds fold .81 to steals (1015). | 5.45 CO first in chances per 100 hands × 10 points more opens × an assumed 1 bb marginal value ≈ +0.5 bb/100. | When both blinds fold to steals ≥ 0.75 (shrunk `r_sf`), CO uses the BTN level. | Decoded `_PRE_SRC` `_preflop` steal block, lines 718 to 749. | Low. | Replay CO folds at r012, r013. |

### Old leaks in V18

| Leak | Code | Data |
|---|---|---|
| Folding over 55% to flop bets | Air folds to ≥ 0.5 pot bets heads up (line 1459), pairs and draws call on price. | Fixed on the flop: .41 (53/128), .43 to 40 to 75% pot bets (47). Moved later: turn .55 (69), river .67 (42). |
| Paying off past 30 bb with one pair | BIG_BET_W shrinks calls against big turn and river bets. | Not a leak in the data: v6 commit calls with one pair or less n=59, won 26, folding would have cost 12,180 chips; V18 n=18*, won 7, folding would have cost 1,758. |
| Early position opens with non premium hands | Preflop chart unchanged since v14. | Mixed: V18 UTG to HJ non top 5% opens 97, −2.56 bb each (−12.4 bb/100); v6 426 at +0.89 bb. Combined +0.25 bb (523). Watch, do not change yet. |
| Not betting the river for value | Value bet at equity ≥ 0.64 on the river. | Mostly fixed: heads up first to act on the river with top pair or better V18 bet 11 (won 11) and checked 3; river bet when checked to .39 (61) against .17 in v5. |
| Premium hands folded on a timeout | Wrapper falls back to check or fold. | Still present: 1 timeout per V18 round, JJ fold r012#736. |

### Tomorrow's format

Tomorrow only the top 2 by chips at each table go through, then an 8 bot, 5,000 hand final. Our per round spread is 29.0 bb/100 per 1,000 hands (v6, 9 rounds), so a 5,000 hand final has a spread near 29 / √5 ≈ 13 bb/100. At a 6 to 8 bot table third place is worth the same as last, so an edge matters more than smoothness: take any change with positive expected bb/100 even if it adds swings (changes 1 to 4). The one exception is stack off spots with thin edges (calls with equity within 2% of the price): in one 1,000 hand qualifier a single 100 bb flip is 10 bb/100, a third of a standard deviation, so keep JAM_MARGIN as it is rather than lowering it.

## Validation

1. The script runs end to end with no errors on all 13 counted rounds (`python3 review/opponent_profiles.py --check`, exit code 0).
2. Hand checks against raw hands: (a) our V18 chips: the script's sum of `results[our seat]` is 4,195 for r012 and 4,082 for r013, equal to the site's `round.chips` for both rounds; (b) Gherkers' "always 3.5 bb" opens: r001 hand 1, seat 1, `["act", 1, "raise", 70]` after blinds of 10 and 20, so 70 chips = 3.5 bb.
3. Money flow: the flows from every opponent to our seat sum to 74,322.0 chips, equal to our total result 74,322 over r001 to r013 (v5 −5,348, v6 +71,393, V18 +8,277); no gap.
4. `git -C imperial-pokerbots-kit status --short` shows only ` M results/bench.csv`, which belongs to the agent working in that folder; nothing there was created or touched by this work.

Limits: V18 has 2,000 hands, so every V18 only row is a two round sample; Attention Is All In never met V18; folded hands are never shown, so missed value and overfolding are estimated from break even prices, not measured; the archetype rule uses whole round stats, and on 50 to 100 hands the aggression stat rests on about 10 chances.
