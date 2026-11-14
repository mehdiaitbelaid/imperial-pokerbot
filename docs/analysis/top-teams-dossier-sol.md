1. Use seat behaviour profiles, with fresh recognition each round, rather than persistent team identities.
2. Analysed 45 counted rounds and 45,000 hands, frozen at r001 through r045.
3. Gherkers 3-bet 520/3,759 opportunities and used unusually frequent postflop overbets.
4. Attention Is All In folded to 3-bets 303/428 times and river barrelled 151/175 opportunities.
5. Equity Engine 3-bet only 95/3,363 opportunities; its usual betting signature also identifies other teams.
6. The Gherkers fingerprint produced 0/325 false round alerts; its target recall rests on only 8 rounds, which is unreliable.
7. The Attention fingerprint produced 0/326 false round alerts and recognised 6/7 target rounds, which is unreliable.
8. The Equity fingerprint produced 8/325 false round alerts and missed its changed r045 betting behaviour.
9. Counter profits below are explicit model hypotheses; several comparable samples contain fewer than 30 opportunities.
10. The stdlib script completed 45,000 hand cash checks and 45 round checks; no existing report or credential file was read.

## Scope, definitions, and limits

The snapshot contains `saturday_r001.json` through `saturday_r045.json`, with recorded slots from 15:00 through 18:40 on 2026-11-14. Practice files were excluded. There are 44 teams and 333 seat rounds in this snapshot.

**U means unreliable because the denominator is below 30.** Showdown evidence is also selected evidence: folded hands remain unknown.

All betting sizes below are chips or fractions of the pot before the action. Raises use the recorded street total. For postflop raises, the size bucket measures the raise increment above a call, divided by the pot after calling.

An open opportunity requires an unopened, unlimped pot. Limp includes overlimping. The 3-bet denominator is a decision facing one previous raise. The 4-bet denominator includes cold 4-bet opportunities. Fold to 3-bet concerns the original raiser; fold to 4-bet concerns the 3-bettor.

A c-bet opportunity requires the preflop aggressor to receive an unbet flop action. Donk bets remove that opportunity. Heads up and multiway refer to players reaching the flop. A barrel follows an unraised bet and call on the previous street.

Raw hands do not identify the incremental profit of a strategy that was never played. The counter section therefore supplies reproducible, price matched bluff models, not claimed causal improvements to Resonance Qt.

## Exposure and results

“From our seat” uses an explicit pot-layer accounting convention: each losing contribution is allocated among that layer’s winners equally. This handles side pots and dead money, but split pots can create fractional allocations. It is not a uniquely identifiable bilateral cash ledger.

| Target | Counted rounds | Hands | Net chips at our tables | bb/100 there | Allocated result against our seat |
|---|---|---:|---:|---:|---|
| Gherkers | 1, 4, 9, 20, 36, 38, 44, 45 | 8,000 | Won 43,230 | 27.019 | Won 653.667 |
| Attention Is All In | 5, 7, 9, 11, 21, 22, 38 | 7,000 | Won 60,083 | 42.916 | Won 15,026.333 |
| Equity Engine | 1, 3, 6, 19, 21, 30, 31, 45 | 8,000 | Won 28,756 | 17.973 | Lost 9,865 |

Resonance Qt won 261,702 chips over the 45,000 hands, or 29.078 bb/100. These are results at our tables, not reconstructed tournament standings. Opponent lineups and our bot versions changed.

## Preflop dossiers

Each frequency is numerator/denominator followed by its percentage.

| Behaviour | Gherkers | Attention Is All In | Equity Engine |
|---|---|---|---|
| VPIP | 1,933/8,000, 24.16% | 2,128/7,000, 30.40% | 2,056/8,000, 25.70% |
| PFR | 1,461/8,000, 18.26% | 1,611/7,000, 23.01% | 1,418/8,000, 17.73% |
| Limp | 18/8,000, 0.23% | 2/7,000, 0.03% | 1/8,000, 0.01% |
| Open | 892/3,685, 24.21% | 1,140/3,489, 32.67% | 1,208/3,985, 30.31% |
| 3-bet | 520/3,759, 13.83% | 437/3,116, 14.02% | 95/3,363, 2.82% |
| 4-bet | 36/521, 6.91% | 19/738, 2.57% | 15/661, 2.27% |
| Fold to 3-bet | 55/136, 40.44% | 303/428, 70.79% | 199/318, 62.58% |
| Fold to 4-bet | 47/57, 82.46% | 40/51, 78.43% | 2/14, 14.29%, U |
| SB defence against a raise | 221/965, 22.90% | 226/809, 27.94% | 181/865, 20.92% |
| BB defence against a raise | 347/1,027, 33.79% | 469/864, 54.28% | 419/966, 43.37% |
| SB defence against CO, BTN, or SB steal | 129/387, 33.33% | 91/222, 40.99% | 61/261, 23.37% |
| BB defence against those steals | 190/418, 45.45% | 156/253, 61.66% | 173/333, 51.95% |
| SB 3-bet against those steals | 104/387, 26.87% | 74/222, 33.33% | 11/261, 4.21% |
| BB 3-bet against those steals | 64/418, 15.31% | 68/253, 26.88% | 10/333, 3.00% |
| Preflop shove | 2/8,000, 0.03% | 22/7,000, 0.31% | 8/8,000, 0.10% |

### Exact opens by position

In the size columns, `70 × 140` means 140 opens to 70 chips. Every observed unopened size is listed.

| Target and position | Open frequency | Exact sizes |
|---|---|---|
| Gherkers UTG | 140/1,077, 13.00% | 70 × 140 |
| Gherkers UTG1 | 62/476, 13.03% | 70 × 62 |
| Gherkers LJ | 107/614, 17.43% | 70 × 107 |
| Gherkers HJ | 141/646, 21.83% | 70 × 141 |
| Gherkers CO | 154/478, 32.22% | 70 × 140; 71 × 2; 75 × 3; 76 × 7; 77 × 2 |
| Gherkers BTN | 195/282, 69.15% | 70 × 178; 72 × 1; 75 × 11; 76 × 5 |
| Gherkers SB | 93/112, 83.04% | 70 × 87; 71 × 1; 72 × 1; 74 × 2; 84 × 1; 88 × 1 |
| Attention UTG | 212/929, 22.82% | 40 × 107; 50 × 68; 80 × 37 |
| Attention UTG1 | 50/417, 11.99% | 50 × 30; 80 × 20 |
| Attention LJ | 202/712, 28.37% | 40 × 114; 50 × 66; 80 × 22 |
| Attention HJ | 210/612, 34.31% | 50 × 196; 80 × 14 |
| Attention CO | 201/478, 42.05% | 50 × 113; 60 × 86; 80 × 2 |
| Attention BTN | 167/230, 72.61% | 50 × 167 |
| Attention SB | 98/111, 88.29% | 50 × 98 |
| Equity UTG | 246/1,090, 22.57% | 70 × 246 |
| Equity UTG1 | 61/314, 19.43% | 70 × 61 |
| Equity LJ | 240/896, 26.79% | 70 × 240 |
| Equity HJ | 217/657, 33.03% | 70 × 217 |
| Equity CO | 174/514, 33.85% | 70 × 174 |
| Equity BTN | 160/322, 49.69% | 70 × 160 |
| Equity SB | 110/192, 57.29% | 70 × 110 |

### Sizing formulas and shoves

**Gherkers**

All 520 observed 3-bets were within one chip of either `round(3.2 × previous raise total)` or `round(3.8 × previous raise total)`. The split was 132 and 388 respectively.

Every out of position 3-bet matched the 3.8 formula, 247/247. In position, only 132/273 matched 3.2. Position alone therefore does not determine the smaller multiplier.

All 36 4-bets matched 2.3 times the preceding raise total within one chip. Median 3-bet total was 198 chips; median 4-bet total was 483. All 38 isolation raises were to 90, consistent with 70 plus 20 per limper in those observed cases.

Both shoves were shown: KK and QQ. That hand distribution is U.

**Attention Is All In**

The exact 3-bet formula was:

`raise_to = previous_raise_total × (3 + callers_since_that_raise)`

It matched 437/437 3-bets: 392 used a multiplier of 3, 43 used 4, and 2 used 5. Median 3-bet total was 180.

All 19 4-bets were shoves to 2,000, so their sizing sample is U. Of 22 preflop shoves, 5 were shown: AA twice, KK twice, QQ once. The revealed range is U and cannot establish that all shoves are premiums.

**Equity Engine**

74/95 3-bets were exactly three times the preceding raise total. Median 3-bet total was 180. Common totals were 150 × 24, 180 × 22, and 195 × 13.

13/15 4-bets matched 2.3 times the preceding raise within one chip. The whole 4-bet sizing sample is U. Median total was 482.

Of 109 isolation raises, 101 fit 70 plus 20 per limper. The other 8 were to 61 over one limper. All 8 shoves were shown: AA × 3, QQ × 3, JJ × 2. This revealed shove sample is U.

## Postflop as aggressor

Size is the median pot fraction among actions taking that line. A size sample can be U even when its opportunity denominator is adequate.

| Line | Gherkers | Attention Is All In | Equity Engine |
|---|---|---|---|
| Heads up flop c-bet | 182/227, 80.18%; size 0.700, n182 | 220/271, 81.18%; size 0.330, n220 | 197/212, 92.92%; size 0.500, n197 |
| Multiway flop c-bet | 19/55, 34.55%; size 0.700, n19 U | 74/157, 47.13%; size 0.657, n74 | 9/63, 14.29%; size 0.800, n9 U |
| Turn barrel | 92/162, 56.79%; size 0.701, n92 | 241/287, 83.97%; size 0.330, n241 | 112/181, 61.88%; size 0.799, n112 |
| River barrel | 29/62, 46.77%; size 0.699, n29 U | 151/175, 86.29%; size 0.329, n151 | 60/86, 69.77%; size 0.799, n60 |
| Triple barrel | 16/37, 43.24% | 146/163, 89.57% | 37/57, 64.91% |
| Flop bet when checked to | 124/184, 67.39%; size 0.701, n124 | 154/288, 53.47%; size 0.329, n154 | 110/233, 47.21%; size 0.800, n110 |
| Turn bet when checked to | 55/104, 52.88%; size 0.701, n55 | 79/151, 52.32%; size 0.326, n79 | 52/133, 39.10%; size 0.7995, n52 |
| River bet when checked to | 23/66, 34.85%; size 0.621, n23 U | 60/109, 55.05%; size 0.155, n60 | 37/84, 44.05%; size 0.798, n37 |
| Flop check raise | 34/154, 22.08% | 0/197, 0% | 8/276, 2.90% |
| Turn check raise | 7/77, 9.09% | 0/96, 0% | 1/113, 0.88% |
| River check raise | 0/35, 0% | 0/30, 0% | 0/68, 0% |
| Flop first-bet overbet | 167/394, 42.39% | 14/495, 2.83% | 12/419, 2.86% |
| Turn first-bet overbet | 78/167, 46.71% | 26/289, 9.00% | 9/211, 4.27% |
| River first-bet overbet | 25/59, 42.37% | 20/201, 9.95% | 3/104, 2.88% |

Gherkers’ first bets cluster around 0.33, 0.70, and 1.10 pot. Its flop check raises have median size 1.000 pot after calling, n34. Turn check raises have the same median, n7 U.

Attention’s ordinary sizes cluster around 0.33, 0.66, and 1.00 pot. Its unusually small checked-to turn and river medians are materially influenced by r011. No check raises were observed.

Equity’s ordinary first bets cluster around 0.45, 0.50, and 0.80 pot. Its flop check raise median was 0.817 pot after calling, n8 U. Its turn sample was n1 U. Its r045 overbets are a separate drift signal discussed below.

### Revealed hand classes by line and size

These are the made classes **on the street of the action**, reconstructed from subsequently revealed hole cards. They are not estimates of the unseen betting range.

Codes: H high card, P pair, D two pair, T trips, S straight, F flush, B full house, Q quads. Pair classifications include pairs on the board. Brackets contain the revealed sample size. U marks unreliable cells. “None” means no revealed sample. Checked-to rows overlap c-bet or barrel rows.

**Gherkers**

| Line | At most ⅓ pot | Above ⅓ through ½ | Above ½ through ¾ | Above ¾ through pot | Over pot |
|---|---|---|---|---|---|
| Flop c-bet HU | H5 P10 D2 [17 U] | None | P2 [2 U] | None | H3 P4 D5 T2 [14 U] |
| Flop c-bet MW | None | None | P2 [2 U] | None | H2 P1 [3 U] |
| Turn barrel | P10 D1 [11 U] | None | H1 P1 D1 [3 U] | T1 [1 U] | H1 P3 D5 T5 [14 U] |
| River barrel | P3 D2 T1 S1 B1 [8 U] | D1 T1 [2 U] | None | None | P1 D1 T1 F1 [4 U] |
| Flop checked to | H4 P4 [8 U] | P1 [1 U] | P4 [4 U] | None | H6 P6 D2 T1 [15 U] |
| Turn checked to | P9 D3 T1 [13 U] | None | P1 T1 [2 U] | T1 [1 U] | H1 P2 D2 T1 [6 U] |
| River checked to | H1 P2 B1 [4 U] | T1 [1 U] | P1 [1 U] | None | H1 P1 [2 U] |
| Flop other bet | H3 P4 D1 [8 U] | H1 P1 D1 [3 U] | H1 P1 D1 [3 U] | None | H2 P12 D2 T2 [18 U] |
| Turn other bet | P2 D1 T1 [4 U] | None | H3 P2 D1 [6 U] | D1 [1 U] | H1 P2 T1 [4 U] |
| River other bet | P2 D2 B1 [5 U] | H1 [1 U] | None | None | D1 [1 U] |
| Flop check raise | None | None | H1 [1 U] | H1 P1 [2 U] | None |
| Turn check raise | None | None | D1 [1 U] | None | None |
| Flop other raise | None | None | H2 P5 D1 T2 [10 U] | H3 P4 D2 T2 Q1 [12 U] | T1 [1 U] |
| Turn other raise | None | D1 T1 [2 U] | P1 T1 [2 U] | None | F1 [1 U] |
| River raise | B1 [1 U] | None | F2 [2 U] | B1 [1 U] | None |

The overbet sample contains both weak and strong made hands. It does not justify treating every overbet as a bluff.

**Attention Is All In**

| Line | At most ⅓ pot | Above ⅓ through ½ | Above ½ through ¾ | Above ¾ through pot | Over pot |
|---|---|---|---|---|---|
| Flop c-bet HU | H7 P14 D2 T2 [25 U] | H1 P3 [4 U] | H5 P6 [11 U] | H2 P1 D1 [4 U] | P1 [1 U] |
| Flop c-bet MW | H3 P2 [5 U] | None | P3 D1 T1 [5 U] | H2 P4 D1 [7 U] | None |
| Turn barrel | H9 P19 D6 T3 S1 [38] | P1 D1 [2 U] | H5 P8 D6 T2 S1 [22 U] | H4 P7 [11 U] | D2 S1 [3 U] |
| River barrel | H5 P14 D13 T3 S4 F1 B2 [42] | P2 D3 [5 U] | H2 P11 D5 T1 S1 [20 U] | P2 D2 S1 [5 U] | None |
| Flop checked to | H3 P6 D2 T1 [12 U] | None | P3 D1 T1 [5 U] | H2 P5 D1 [8 U] | P2 [2 U] |
| Turn checked to | H1 P4 D2 T1 [8 U] | None | D2 T1 [3 U] | P1 [1 U] | D4 [4 U] |
| River checked to | P2 D5 S1 B1 [9 U] | None | D1 T1 [2 U] | None | None |
| Flop other bet | H4 P14 D3 [21 U] | None | H2 D2 T1 [5 U] | H2 P7 D1 [10 U] | T1 [1 U] |
| Turn other bet | P3 D2 [5 U] | None | H1 [1 U] | H2 P2 S1 [5 U] | None |
| River other bet | P1 D2 B1 [4 U] | B1 [1 U] | S1 F1 [2 U] | None | P7 D3 T4 S2 B1 [17 U] |
| Flop raise | None | None | T1 [1 U] | P6 D3 T2 F1 [12 U] | F1 [1 U] |
| Turn raise | None | F1 [1 U] | P1 B1 [2 U] | P2 D1 F1 [4 U] | D1 F1 [2 U] |
| River raise | D3 T2 [5 U] | D2 F2 [4 U] | None | T1 [1 U] | None |

Its frequent small barrels contain revealed high-card hands. That supports a mixed betting range, not unrestricted bluff catching.

**Equity Engine**

| Line | At most ⅓ pot | Above ⅓ through ½ | Above ½ through ¾ | Above ¾ through pot | Over pot |
|---|---|---|---|---|---|
| Flop c-bet HU | None | H13 P7 [20 U] | None | P9 T3 [12 U] | P1 [1 U] |
| Flop c-bet MW | None | None | None | P2 [2 U] | None |
| Turn barrel | P1 [1 U] | H3 P5 D1 [9 U] | D1 [1 U] | P9 D5 T4 S1 [19 U] | P1 [1 U] |
| River barrel | D1 S1 F1 [3 U] | P4 D3 S1 [8 U] | None | P1 D5 T3 F1 B3 [13 U] | S1 [1 U] |
| Flop checked to | None | H6 P3 [9 U] | None | P6 D1 T1 B1 [9 U] | None |
| Turn checked to | None | H2 P1 D1 [4 U] | None | P4 T2 [6 U] | None |
| River checked to | D1 F1 B1 [3 U] | H1 P1 [2 U] | None | P2 D2 F1 B1 [6 U] | None |
| Flop other bet | None | H6 P3 D2 [11 U] | None | H2 P6 D2 T5 [15 U] | P2 [2 U] |
| Turn other bet | T1 B1 [2 U] | H1 P5 [6 U] | None | D2 T2 S1 F2 B1 [8 U] | S1 [1 U] |
| River other bet | D1 [1 U] | H1 P2 [3 U] | None | T1 S1 F1 [3 U] | None |
| Flop check raise | None | None | None | P1 [1 U] | None |
| Flop other raise | None | H1 T1 [2 U] | P3 D1 T1 [5 U] | P5 T4 [9 U] | None |
| Turn raise | D1 T1 [2 U] | None | P3 S1 B1 [5 U] | P3 D1 T1 [5 U] | None |
| River raise | D1 [1 U] | None | P1 D1 F1 [3 U] | T1 S1 [2 U] | None |

The small heads up c-bet sample looks weaker than the large sample, but both revealed samples are U. Treat that distinction as a hypothesis.

## Postflop as defender

Cells show **fold/call/raise counts; n**. These are exact response frequencies with a common denominator, rather than rounded percentages.

### Against first bets

| Street and bet size | Gherkers | Attention | Equity |
|---|---|---|---|
| Flop at most ⅓ pot | 7/28/53; n88 | 35/25/9; n69 | 16/40/7; n63 |
| Flop above ⅓ through ½ | 22/32/54; n108 | 60/33/16; n109 | 66/71/18; n155 |
| Flop above ½ through ¾ | 68/22/17; n107 | 86/79/11; n176 | 71/40/19; n130 |
| Flop above ¾ through pot | 79/25/14; n118 | 107/20/15; n142 | 72/44/5; n121 |
| Flop over pot | 40/8/6; n54 | 40/8/3; n51 | 54/15/6; n75 |
| Turn at most ⅓ pot | 8/31/10; n49 | 7/27/5; n39 | 10/19/4; n33 |
| Turn above ⅓ through ½ | 16/16/2; n34 | 24/15/4; n43 | 13/26/9; n48 |
| Turn above ½ through ¾ | 21/16/6; n43 | 28/55/5; n88 | 40/24/10; n74 |
| Turn above ¾ through pot | 36/13/1; n50 | 58/11/4; n73 | 48/18/6; n72 |
| Turn over pot | 18/2/0; n20 U | 18/4/0; n22 U | 13/5/0; n18 U |
| River at most ⅓ pot | 10/24/1; n35 | 3/17/0; n20 U | 8/14/3; n25 U |
| River above ⅓ through ½ | 9/10/1; n20 U | 11/12/0; n23 U | 10/7/4; n21 U |
| River above ½ through ¾ | 11/5/0; n16 U | 16/16/10; n42 | 27/12/4; n43 |
| River above ¾ through pot | 7/2/3; n12 U | 17/3/1; n21 U | 25/10/1; n36 |
| River over pot | 9/1/1; n11 U | 4/1/0; n5 U | 5/2/0; n7 U |

Gherkers raises small flop bets frequently. This is a poor opponent for an automatic tiny bluff policy. Attention’s responses are strongly size dependent. Equity’s large aggregate fold counts do not imply that every specific heads up price is profitable to bluff.

### Against raises after they bet, c-bets, and later barrels

| Situation | Gherkers | Attention | Equity |
|---|---|---|---|
| Raised after own flop bet | 30/25/3; n58 | 52/12/3; n67 | 35/8/6; n49 |
| Raised after own turn bet | 6/6/0; n12 U | 22/1/0; n23 U | 16/5/0; n21 U |
| Raised after own river bet | 1/2/0; n3 U | 8/3/0; n11 U | 6/4/1; n11 U |
| Facing flop c-bet | 121/52/64; n237 | 152/102/26; n280 | 159/124/20; n303 |
| Facing turn barrel | 29/34/4; n67 | 43/82/6; n131 | 51/51/12; n114 |
| Facing river barrel | 22/27/1; n50 | 17/38/10; n65 | 32/24/6; n62 |

Attention often abandons its own betting line against a raise, but becomes relatively persistent after calling a previous street. The raised-turn samples are all U.

## Showdowns

| Measure | Gherkers | Attention | Equity |
|---|---|---|---|
| Reached showdown per dealt hand | 195/8,000, 2.44% | 268/7,000, 3.83% | 239/8,000, 2.99% |
| Reached showdown after seeing flop | 195/963, 20.25% | 268/1,211, 22.13% | 239/1,181, 20.24% |
| Received a payout at showdown | 109/195, 55.90% | 143/268, 53.36% | 121/239, 50.63% |

Payout at showdown includes split-pot wins.

## Seat fingerprints

Evaluate the preceding 200 dealt hands, first after hand 200 and every 100 hands thereafter. Use only that seat’s public actions. The feature minimums below are recognition thresholds, not claims that small samples are reliable statistical estimates.

A pot-fraction match allows an absolute tolerance of 0.012.

**F_G, Gherkers-like**

Require all of:

1. At least 8 unopened raises, with at least 90% sized from 70 through 77.
2. At least 5 3-bets, with at least 90% within one chip of either 3.2 or 3.8 times the preceding raise total.
3. At least 5 postflop first bets, with at least 80% near 0.33, 0.70, or 1.10 pot.

**F_A, Attention-like**

Require all of:

1. At least 8 unopened raises; at least 3 are from BTN or SB, all to 50.
2. At least 2 unopened raises to 40 or 80.
3. At least 5 3-bets, with at least 95% exactly 3, 4, or 5 times the preceding raise total.
4. At least 8 postflop first bets, with at least 80% near 0.33, 0.66, 1.00, 0.308, 0.190, or 0.155 pot.

**F_E, Equity-family**

Require all of:

1. At least 8 unopened raises, all to 70.
2. At least 8 postflop first bets, with at least 90% near 0.45, 0.50, or 0.80 pot.
3. At least 2 first bets near 0.50 and at least 2 near 0.80 pot.

F_E identifies a betting family. It does not uniquely identify Equity Engine.

### Measured classification results

A round false positive means at least one alert during that other seat’s round. Block tests use nonoverlapping 200 hand blocks. All 43 other team labels, including Resonance Qt, were included for each target.

| Fingerprint | Target rounds detected | Other seat rounds falsely detected | Target blocks detected | Other blocks falsely detected | False team labels |
|---|---|---|---|---|---|
| F_G | 8/8, 100%, U | 0/325, 0% | 32/40, 80.00% | 0/1,625, 0% | None |
| F_A | 6/7, 85.71%, U | 0/326, 0% | 14/35, 40.00% | 0/1,630, 0% | None |
| F_E | 7/8, 87.50%, U | 8/325, 2.46% | 32/40, 80.00% | 28/1,625, 1.72% | Vlad in 4 rounds; aydine in 4 |

First detection, in each target’s chronological round order:

| Profile | First detection hand |
|---|---|
| F_G | 200, 200, 200, 200, 200, 200, 300, 200 |
| F_A | 200, 800, 200, absent, 200, 200, 600 |
| F_E | 600, 200, 300, 200, 200, 200, 200, absent |

These are exploratory, in-sample results. The thresholds were assessed on this archive, not an unseen future round. Zero observed false positives does not establish zero future false positives. Blocks from one round are correlated.

## Drift across the evening

Thirds are global round thirds: r001 through r015, r016 through r030, and r031 through r045.

| Target and period | Target hands | VPIP | PFR | bb/100 | HU c-bet | First-bet overbet | Fold to 3-bet |
|---|---:|---:|---:|---:|---|---|---|
| Gherkers early | 3,000 | 28.60% | 21.87% | 46.607 | 84/97, 86.60% | 125/275, 45.45% | 17/43, 39.53% |
| Gherkers middle | 1,000 | 25.40% | 18.70% | Negative 22.935 | 25/34, 73.53% | 42/93, 45.16% | 8/22, 36.36%, U |
| Gherkers late | 4,000 | 20.52% | 15.45% | 24.816 | 73/96, 76.04% | 103/252, 40.87% | 30/71, 42.25% |
| Attention early | 4,000 | 32.25% | 25.57% | 43.075 | 134/162, 82.72% | 39/604, 6.46% | 237/340, 69.71% |
| Attention middle | 2,000 | 26.50% | 18.10% | 48.705 | 68/83, 81.93% | 13/305, 4.26% | 41/57, 71.93% |
| Attention late | 1,000 | 30.80% | 22.60% | 30.705 | 18/26, 69.23%, U | 8/76, 10.53% | 25/31, 80.65% |
| Equity early | 3,000 | 23.37% | 16.90% | 9.865 | 70/77, 90.91% | 1/235, 0.43% | 61/125, 48.80% |
| Equity middle | 3,000 | 26.60% | 17.73% | 38.970 | 78/83, 93.98% | 0/304, 0% | 53/79, 67.09% |
| Equity late | 2,000 | 27.85% | 18.95% | Negative 1.363 | 49/52, 94.23% | 23/195, 11.79% | 85/114, 74.56% |

**Gherkers:** the sizing mechanism remained recognisable, but the frequencies moved. Its r004 3-bet rate was 205/575, 35.65%. In r036, r038, r044, and r045 it was respectively 38/498, 37/413, 41/438, and 47/509. Do not carry the early aggregate aggression rate into a later round. Opponent composition, adaptation, and uploads are competing explanations; opponent version identifiers are absent.

**Attention:** r011 was behaviourally unusual despite the supplied information that its bot was unchanged. It VPIPed 532/1,000 hands, 53.20%, and supplied the 221 opens to 40 and 86 opens to 60. F_A missed this round. Its r038 3-bet rate was 134/516, 25.97%. A fixed bot can still have state or opponent dependent behaviour. The raw data cannot resolve the cause.

**Equity:** r045 introduced frequent first bets near 1.05 pot. It overbet 23/86 first bets that round, 26.74%, compared with 0/109 in r031. F_E failed to recognise r045. This is a material reason to expire the old sizing profile rather than assuming a name implies an unchanged strategy.

## Counter rules for implementation

### Maths and interpretation

Let \(P\) be the pot before our aggressive action, \(R\) our additional investment, and \(f\) the opponent’s fold probability. The zero-equity, give-up model is:

\[
EV=fP-(1-f)R,\qquad f_{\mathrm{BE}}=\frac{R}{P+R}.
\]

A call of \(B\) into a pot that was \(P\) before the bet needs showdown equity \(B/(P+2B)\), before future action. For example, a 1.10 pot bet gives a 34.38% immediate call threshold. That does not establish our hand’s equity against its range.

The forecasts below:

1. Use only heads up situations where the aggressor already had one live opponent before acting.
2. Match observed sizes, with the stated tolerance, and start only after the first fingerprint detection.
3. Allocate pooled opponent opportunities equally across the other seats using weight \(1/(N-1)\).
4. Assume the measured response transfers to our bluff and remains stable.
5. Assume zero equity and no further investment when continued against.

Thus “bb/100” means **hypothetical action profit per 100 dealt hands while seated with that target**, under this exposure model. It is not verified uplift over our existing bot. It excludes false-identification costs, hand-selection effects, and changes in opponents’ responses. Do not add overlapping rows together.

For an implementation that uses only a fraction \(q\) of the eligible opportunities, the corresponding forecast scales by \(q\) under the same assumptions.

### Ranked rules

Ranks within each target use the model point estimate. U rows belong in shadow evaluation. The full matched sample is also supplied so an implementer can distinguish recognition delay from evidence about the response itself.

| Target and rank | Implementable rule |
|---|---|
| Gherkers 1 | IF seat matches F_G AND the turn is heads up, it has checked, the pot is unbet, and we can make a legal first bet, THEN consider a bluff of `round(0.8 × pot)`. |
| Gherkers 2 | IF seat matches F_G AND the flop is heads up and we can make the first bet, THEN consider `round(0.8 × pot)` with the bluff portion of the betting range. |
| Attention 1 | IF seat matches F_A AND the flop is heads up and we can make the first bet, THEN use `round(0.8 × pot)` for selected bluffs. |
| Attention 2 | IF seat matches F_A AND the turn is heads up, it has checked, and the pot is unbet, THEN consider `round(0.8 × pot)`. |
| Attention 3 | IF seat matches F_A AND it makes the first flop bet \(B\) heads up, our street contribution is zero, and a raise is legal and affordable, THEN test a raise to `3 × B`. |
| Attention 4 | IF seat matches F_A AND only our seat and its opening raise remain preflop, THEN test a 3-bet to `3 × open_total`. |
| Equity 1 | IF seat matches F_E AND the turn is heads up, it has checked, and the pot is unbet, THEN test `round(0.8 × pot)`. |
| Equity 2 | IF seat matches F_E AND it makes the first flop bet \(B\) heads up, our street contribution is zero, and a raise is legal and affordable, THEN test a raise to `3 × B`. |
| Equity 3 | IF seat matches F_E AND only our seat and its opening raise remain preflop, THEN test a 3-bet to `3 × open_total`. |

Keep value decisions and ordinary equity calculations in the base strategy. The dossier does not establish the correct bluff combinations.

| Rule | Full matched folds | Folds after recognition | Mean \(P\) | Mean \(R\) | Break even fold rate | Model bb/100 after recognition |
|---|---|---|---:|---:|---:|---:|
| Gherkers 1 | 7/8 U | 5/6, 83.33%, U | 549.000 | 438.667 | 44.41% | 0.2231 U |
| Gherkers 2 | 17/34 | 15/30, 50.00% | 297.800 | 237.900 | 44.41% | 0.0894 |
| Attention 1 | 27/40 | 16/23, 69.57%, U | 223.913 | 179.261 | 44.46% | 0.2582 U |
| Attention 2 | 4/6 U | 3/4, 75.00%, U | 393.500 | 314.500 | 44.42% | 0.0957 U |
| Attention 3 | 10/15 U | 2/2, 100%, U | 362.000 | 321.000 | 47.00% | 0.0800 U |
| Attention 4 | 6/7 U | 6/7, 85.71%, U | 72.857 | 130.000 | 64.08% | 0.0351 U |
| Equity 1 | 14/15 U | 9/10, 90.00%, U | 435.200 | 347.700 | 44.41% | 0.3399 U |
| Equity 2 | 8/10 U | 7/9, 77.78%, U | 283.111 | 324.667 | 53.42% | 0.1300 U |
| Equity 3 | 20/31 | 16/24, 66.67%, U | 102.917 | 200.000 | 66.02% | 0.0045 U |

**Practical priority:** Attention’s flop first-bet response is the strongest candidate here: its full matched sample has 40 opportunities, and the script’s Wilson lower-bound fold model remains profitable. Gherkers’ flop model has a positive point estimate but a negative lower-bound forecast. Equity’s turn hypothesis is promising but U and vulnerable to profile drift.

### Stop conditions

Apply these separately to each seat and rule.

| Rule family | Stop condition |
|---|---|
| Any profile | Stop the overlay when adequately observed public sizes contradict its fingerprint. Rebuild the seat profile within the current round. |
| First bets near 0.80 pot | After 30 comparable current-seat responses, stop bluff expansion if the fold rate is at or below the action’s calculated break even rate. |
| Flop raise to 3 times the bet | Stop if the comparable raise sample fails its price-specific break even test; until the sample reaches 30, retain U status. |
| Preflop 3-bet to 3 times the open | Stop if comparable fold frequency fails the price-specific test. Do not substitute aggregate fold to 3-bet for this test. |
| Equity family | Stop the old sizing overlay when the seat develops the r045-style overbet behaviour. F_E alone never establishes team identity. |

### Lines that lose under the tested model, or lack support

**Gherkers**

Do not turn its aggregate 47/57 folds to 4-bets into a small 4-bet bluff rule. In comparable heads up responses to roughly 2.3 times its 3-bet, it folded only 3/8, U. The model required 59.32% folds and returned negative 0.1350 bb/100 under the equal-seat exposure model.

Avoid automatic tiny flop bluffs. Against bets at most one third pot, it folded 7/88 and raised 53/88. Also avoid assuming a 1.10 pot bet always represents air; the revealed classes contain substantial made value.

**Attention**

Avoid calling a flop bet solely to fold to the next ordinary barrel. It turn barrelled 241/287 opportunities and river barrelled 151/175. A float needs a concrete equity or later-action plan.

Avoid assuming a full-pot flop bluff is an improvement over the smaller tested price. In the comparable heads up full-pot sample, it folded 9/22, U, below the 50% break even rate.

**Equity**

Avoid indiscriminate preflop 3-bet bluffs. Against comparable heads up 3-bets to three times its open, it folded 20/31, 64.52%, while the model required 65.91%.

Avoid bluff 4-bets based on its ordinary preflop looseness. It folded only 2/14 responses to 4-bets overall, U. Avoid treating its old low-overbet profile as permanent after r045.

## Brief opponents

All percentages below have the displayed sample denominators.

| Team | Rounds and hands | Result at our tables | VPIP / PFR | 3-bet | Fold to 3-bet | HU c-bet |
|---|---|---|---|---|---|---|
| The Market Makers | 7; 7,000 | Won 16,417; 11.726 bb/100 | 1,343/7,000, 19.19%; 829/7,000, 11.84% | 138/2,990, 4.62% | 48/125, 38.40% | 160/169, 94.67% |
| AAST | 8; 8,000 | Won 30,812; 19.258 bb/100 | 1,824/8,000, 22.80%; 1,287/8,000, 16.09% | 282/3,190, 8.84% | 95/187, 50.80% | 143/242, 59.09% |
| WBot | 8; 8,000 | Won 101,828; 63.642 bb/100 | 2,617/8,000, 32.71%; 1,700/8,000, 21.25% | 162/3,196, 5.07% | 211/408, 51.72% | 264/265, 99.62% |
| Kojack | 8; 8,000 | Won 53,315; 33.322 bb/100 | 1,579/8,000, 19.74%; 1,303/8,000, 16.29% | 237/3,314, 7.15% | 138/229, 60.26% | 158/196, 80.61% |
| Anker Batteries | 7; 7,000 | Won 5,740; 4.100 bb/100 | 1,627/7,000, 23.24%; 1,227/7,000, 17.53% | 452/3,131, 14.44% | 57/153, 37.25% | 174/184, 94.57% |

The Market Makers combines a low 3-bet rate with persistent preflop continuation and frequent heads up c-bets. AAST c-bets less automatically. WBot deserves serious attention despite its absence from the primary target list: its broad participation and near automatic c-bet accompanied the strongest table result among these entries. Kojack’s fold to 3-bet tendency merits price-specific testing. Anker’s frequent 3-bets and low fold to 3-bet rate make a generic preflop bluff escalation unattractive.

## Validation

The script ran end to end. All 45,000 hands reconciled recorded payouts minus net contributions to `results`. All 45 round chip totals and hand counts reconciled to round metadata.

The independent hand evaluator and pot layers reproduced payouts within one chip. There were 31 odd-chip split-pot hands; maximum discrepancy was one chip. Bilateral transfer figures therefore retain the stated equal-share allocation convention.

Two raw hand checks per primary target:

| Target | Raw open check | Raw postflop arithmetic check |
|---|---|---|
| Gherkers | r001, hand 1, seat 1: recorded raise to 70 from CO | r001, hand 62: raiser contributes 56, Gherkers contributes 56, folded BB contributes 20. Pot 132. Gherkers bets 45, or 34.09% pot. |
| Attention | r005, hand 3, seat 0: recorded raise to 50 from LJ | r005, hand 6: opener 50, BB 50, folded SB 10. Pot 110. Attention bets 36, or 32.73% pot. |
| Equity | r001, hand 4, seat 5: recorded BTN raise to 70 | r001, hand 75: opener 70, SB 70, folded BB 20. Pot 160. Equity c-bets 72, exactly 45.00% pot. |

The environment denied `mktemp` under `/tmp`. The full stdlib script below was executed through `python3 -c` in memory. No file was written.

## Playing a final table containing all three

1. **Recognise each seat independently.** Start with the base strategy, collect public action features, and apply overlays after recognition. Reset identity assumptions between rounds. F_E remains a family label.
2. **Keep heads up and multiway policies separate.** Equity’s c-bet rate changes from 197/212 heads up to 9/63 multiway. Gherkers also reduces from 182/227 to 19/55. A rare multiway bet should not receive the same automatic bluff response as a frequent heads up c-bet.
3. **Use prices before aggression labels.** Gherkers’ broad 3-betting does not make every 4-bet bluff profitable. Attention’s frequent barrels do not make every bluff catcher profitable. Preserve hand equity, blockers, position, and legal sizing in the base policy.
4. **Track drift during the 5,000 hand final.** Keep rolling public sizing and response statistics. The r045 Equity change demonstrates why a recognised seat can require a new profile. Do not let an early fingerprint permanently override current evidence.
5. **Separate qualification utility from final-table chip EV.** With every hand resetting to 2,000, this is not conventional elimination-stack ICM. During rounds where the top 2 advance, use qualification probability only if actual cumulative standings are available. In the final, optimise the stated chip objective and avoid speculative variance increases justified only by an opponent’s name.

## Full stdlib analysis script

```python
import json, pathlib, collections, itertools, statistics, math, hashlib

ROOT = pathlib.Path("/Users/mehdiaitbelaid/Desktop/imperial-ai-hack-2026/hands-data/hands")
PRIMARY = ["Gherkers", "Attention Is All In", "Equity Engine"]
BRIEF = ["The Market Makers", "AAST", "WBot", "Kojack", "Anker Batteries"]
STREETS = ["preflop", "flop", "turn", "river"]
BUCKETS = ["le33", "33to50", "50to75", "75to100", "over100"]
T = collections.defaultdict(
    lambda: {"c": collections.Counter(), "d": collections.defaultdict(collections.Counter)}
)
SESSIONS = []
DECISIONS = []
QUALITY = collections.Counter()


def bucket(x):
    return BUCKETS[
        next(
            (i for i, v in enumerate((1/3, .5, .75, 1)) if x <= v + 1e-9),
            4,
        )
    ]


def rate(k, n):
    return {
        "yes": k,
        "n": n,
        "pct": round(100*k/n, 2) if n else None,
        "unreliable": n < 30,
    }


def desc(xs):
    return {
        "n": len(xs),
        "median": round(statistics.median(xs), 4) if xs else None,
        "modes": collections.Counter(xs).most_common(6),
    }


def rank(cards):
    best = (-1,)
    for five in itertools.combinations(cards, 5):
        rs = ["23456789TJQKA".index(c[0])+2 for c in five]
        counts = collections.Counter(rs)
        groups = sorted(((n, r) for r, n in counts.items()), reverse=True)
        flush = len({c[1] for c in five}) == 1
        unique = sorted(set(rs))
        straight = (
            5 if unique == [2, 3, 4, 5, 14]
            else unique[-1]
            if len(unique) == 5 and unique[-1]-unique[0] == 4
            else 0
        )
        if flush and straight:
            v = (8, straight)
        elif groups[0][0] == 4:
            v = (7, groups[0][1], groups[1][1])
        elif [g[0] for g in groups] == [3, 2]:
            v = (6, groups[0][1], groups[1][1])
        elif flush:
            v = (5, *sorted(rs, reverse=True))
        elif straight:
            v = (4, straight)
        elif groups[0][0] == 3:
            v = (
                3, groups[0][1],
                *sorted((r for r in rs if r != groups[0][1]), reverse=True),
            )
        elif [g[0] for g in groups][:2] == [2, 2]:
            v = (
                2,
                *sorted((g[1] for g in groups if g[0] == 2), reverse=True),
                groups[-1][1],
            )
        elif groups[0][0] == 2:
            v = (
                1, groups[0][1],
                *sorted((r for r in rs if r != groups[0][1]), reverse=True),
            )
        else:
            v = (0, *sorted(rs, reverse=True))
        best = max(best, v)
    return best


CLASSES = [
    "high card", "pair", "two pair", "trips", "straight",
    "flush", "full house", "quads", "straight flush",
]


def hole_name(cards):
    rs = sorted(
        cards, key=lambda c: "23456789TJQKA".index(c[0]), reverse=True
    )
    return "".join(c[0] for c in rs) + (
        "" if rs[0][0] == rs[1][0]
        else "s" if rs[0][1] == rs[1][1]
        else "o"
    )


def positions(h, N):
    labels = {
        6: ["UTG", "HJ", "CO", "BTN", "SB", "BB"],
        7: ["UTG", "LJ", "HJ", "CO", "BTN", "SB", "BB"],
        8: ["UTG", "UTG1", "LJ", "HJ", "CO", "BTN", "SB", "BB"],
    }[N]
    return {
        (h["button"]+3+j) % N: label
        for j, label in enumerate(labels)
    }


def add(team, key, den=0, num=0):
    T[team]["c"][key+"_n"] += den
    T[team]["c"][key+"_yes"] += num


def sizes(team, key, x):
    T[team]["d"][key][round(x, 3)] += 1


def unpack(counter):
    return [x for x, n in counter.items() for _ in range(n)]


files = sorted(
    p for p in ROOT.glob("saturday_r0*.json")
    if int(p.stem.rsplit("r", 1)[1]) <= 45
)
manifest = []

for fi, path in enumerate(files):
    raw = path.read_bytes()
    d = json.loads(raw)
    teams = d["players"]
    N = len(teams)
    our = d["seat"]
    rn = int(path.stem.rsplit("r", 1)[1])
    third = min(2, fi*3//len(files))
    manifest.append({
        "round": rn,
        "slot": d["round"].get("slot"),
        "hands": len(d["hands"]),
        "seats": N,
        "our_version": d["round"].get("version"),
        "sha256": hashlib.sha256(raw).hexdigest(),
    })
    sessions = []
    for seat, team in enumerate(teams):
        session = {
            "team": team, "round": rn, "third": third,
            "features": [], "net": 0,
        }
        SESSIONS.append(session)
        sessions.append(session)
        T[team]["c"]["rounds"] += 1
    QUALITY["files"] += 1

    for h in d["hands"]:
        QUALITY["hands"] += 1
        assert sum(h["results"]) == 0
        assert h["bb"] == 20 and h["sb"] == 10
        assert all(v == 2000 for v in h["start_stacks"])
        c = [0]*N
        contrib = [0]*N
        paid = [0]*N
        alive = set(range(N))
        street = 0
        board = []
        mx = 20
        nr = 0
        limpers = 0
        pfagg = None
        pf_callers = set()
        vp = set()
        pfr = set()
        acted = set()
        seen3 = set()
        seen4 = set()
        raised_at = {}
        fold3 = set()
        fold4 = set()
        flopset = set()
        shown = {
            int(s): cards
            for s, cards in h["hole"].items()
            if str(s) in h["showdown"]
        }
        pos = positions(h, N)
        checked = set()
        check_responded = set()
        firstbettor = None
        streetraises = 0
        streetcalled = False
        prevbettor = None
        street_raisers = set()
        bets_by_street = {}
        last_bet = None
        last_ratio = 0
        last_tag = ""
        fbet = {i: [] for i in range(N)}
        handobs = []
        streetseen = set()
        wager = None

        for s, team in enumerate(teams):
            T[team]["c"]["hands"] += 1
            T[team]["c"]["chips"] += h["results"][s]
            T[team]["c"]["third%d_hands" % third] += 1
            T[team]["c"]["third%d_chips" % third] += h["results"][s]
            sessions[s]["net"] += h["results"][s]
            fbet[s].append(("hand", h["n"]))

        for ei, e in enumerate(h["events"]):
            typ = e[0]
            if typ == "post":
                _, s, v = e
                c[s] += v
                contrib[s] += v
            elif typ == "refund":
                _, s, v = e
                contrib[s] -= v
                c[s] -= v
            elif typ == "win":
                paid[e[1]] += e[2]
            elif typ == "board":
                if street > 0:
                    prevbettor = (
                        firstbettor
                        if streetraises == 1 and streetcalled
                        else None
                    )
                street = STREETS.index(e[1])
                board = e[2]
                c = [0]*N
                mx = 0
                nr = 0
                checked = set()
                check_responded = set()
                streetseen = set()
                firstbettor = None
                streetraises = 0
                streetcalled = False
                street_raisers = set()
                last_bet = None
                last_ratio = 0
                last_tag = ""
                wager = None
                if street == 1:
                    flopset = alive.copy()
                    for s in flopset:
                        T[teams[s]]["c"]["flops"] += 1
            elif typ == "act":
                _, s, a, v = e
                team = teams[s]
                st = STREETS[street]
                pot = sum(contrib)
                cost = max(0, mx-c[s])
                stack = h["start_stacks"][s]-contrib[s]
                delta = v-c[s] if a == "raise" else v if a == "call" else 0
                can_xr = (
                    cost > 0 and s in checked and s not in check_responded
                )
                assert delta >= 0 and delta <= stack
                obs = {
                    "team": team, "round": rn, "hand": h["n"],
                    "seat": s, "street": st, "action": a,
                    "pot": pot, "cost": cost, "delta": delta,
                    "to": v, "position": pos[s],
                    "faced_ratio": last_ratio, "faced_tag": last_tag,
                    "live": len(alive), "hu": len(alive) == 2, "N": N,
                    "checked": s in checked,
                    "own_street_bet": s in street_raisers,
                    "our_live": our in alive,
                    "opp": teams[last_bet] if last_bet is not None else None,
                    "our_opp": wager is not None and wager["seat"] == our,
                    "event": ei, "tags": [], "pf_nr": nr,
                    "own_pf_raise": raised_at.get(s),
                    "pf_callers": len(pf_callers),
                    "pf_agg_pos": pos.get(pfagg),
                    "wager": wager.copy() if wager else None,
                }

                if street == 0:
                    initial = s not in acted
                    if initial:
                        if (
                            nr == 0 and limpers == 0
                            and s != (h["button"]+2) % N
                        ):
                            add(team, "open", 1, a == "raise")
                            add(team, "open_"+pos[s], 1, a == "raise")
                            if a == "raise":
                                sizes(team, "open_"+pos[s], v)
                                fbet[s].append(("open", v, pos[s], 0))
                                obs["tags"].append("open")
                        if a == "call" and nr == 0:
                            add(team, "limp", 0, 1)
                            limpers += 1
                        acted.add(s)
                    if nr == 1 and s not in seen3:
                        add(team, "threebet", 1, a == "raise")
                        seen3.add(s)
                        if a == "raise":
                            sizes(team, "threebet_to", v)
                            sizes(team, "threebet_multiple", v/mx)
                            fbet[s].append(("threebet", v, mx, pos[s]))
                    if nr == 2 and s not in seen4:
                        add(team, "fourbet", 1, a == "raise")
                        seen4.add(s)
                    if nr == 2 and raised_at.get(s) == 1 and s not in fold3:
                        add(team, "fold_threebet", 1, a == "fold")
                        fold3.add(s)
                    if nr == 3 and raised_at.get(s) == 2 and s not in fold4:
                        add(team, "fold_fourbet", 1, a == "fold")
                        fold4.add(s)
                    if initial and cost > 0 and nr > 0 and pos[s] in ("SB", "BB"):
                        add(team, "defend_"+pos[s], 1, a != "fold")
                        if (
                            nr == 1 and pfagg is not None
                            and pos[pfagg] in ("CO", "BTN", "SB")
                            and limpers == 0
                        ):
                            add(team, "steal_defend_"+pos[s], 1, a != "fold")
                            add(team, "steal_threebet_"+pos[s], 1, a == "raise")
                        streetseen.add(s)
                    if a == "call":
                        vp.add(s)
                        if nr > 0:
                            pf_callers.add(s)
                    if a == "raise":
                        vp.add(s)
                        pfr.add(s)
                        nr += 1
                        raised_at[s] = nr
                        pfagg = s
                        pf_callers = set()
                        if nr == 1 and "open" not in obs["tags"]:
                            sizes(team, "iso_to", v)
                            sizes(team, "iso_base", v-20*limpers)
                        if nr == 2:
                            sizes(team, "threebet_formula_33", v-round(mx*3.3))
                            sizes(team, "threebet_formula_38", v-round(mx*3.8))
                        if nr == 3:
                            sizes(team, "fourbet_to", v)
                        if delta == stack:
                            add(team, "pf_shove", 0, 1)
                            if s in shown:
                                T[team]["d"]["pf_shove_shown"][
                                    hole_name(shown[s])
                                ] += 1
                else:
                    if cost == 0:
                        context = "HU" if len(flopset) == 2 else "MW"
                        if street == 1 and pfagg == s:
                            add(team, "cbet_"+context, 1, a == "raise")
                            obs["tags"].append("cbet_"+context)
                        if street in (2, 3) and prevbettor == s:
                            tag = "barrel_"+st
                            add(team, tag, 1, a == "raise")
                            obs["tags"].append(tag)
                            if street == 3 and bets_by_street.get(1) == s:
                                add(team, "triple", 1, a == "raise")
                                obs["tags"].append("triple")
                        if checked:
                            add(team, "checked_to_"+st, 1, a == "raise")
                            obs["tags"].append("checked_to")
                        if a == "raise":
                            ratio = delta/pot
                            obs["ratio"] = ratio
                            obs["bucket"] = bucket(ratio)
                            sizes(team, "bet_"+st, ratio)
                            add(team, "overbet_"+st, 0, ratio > 1)
                            add(team, "bets_"+st, 0, 1)
                            for tag in obs["tags"]:
                                sizes(team, "size_"+tag, ratio)
                            fbet[s].append((
                                "bet", round(ratio, 3), st, len(flopset)
                            ))
                            last_tag = (
                                "cbet"
                                if any(x.startswith("cbet") for x in obs["tags"])
                                else "barrel"
                                if any(x.startswith("barrel") for x in obs["tags"])
                                else "bet"
                            )
                    else:
                        facingraise = streetraises >= 2
                        kind = "vsraise" if facingraise else "vsbet"
                        key = kind+"_"+st+"_"+bucket(last_ratio)
                        T[team]["d"][key][a] += 1
                        T[team]["d"][kind+"_"+st][a] += 1
                        obs["defender_kind"] = kind
                        if facingraise and s in street_raisers:
                            T[team]["d"]["after_own_bet_"+st][a] += 1
                        if last_tag in ("cbet", "barrel"):
                            T[team]["d"]["vs"+last_tag+"_"+st][a] += 1
                        if can_xr:
                            add(team, "checkraise_"+st, 1, a == "raise")
                            check_responded.add(s)
                        if a == "raise":
                            tag = "checkraise" if can_xr else "raise"
                            obs["tags"].append(tag)
                            ratio = (
                                (delta-cost)/(pot+cost) if pot+cost else 0
                            )
                            obs["ratio"] = ratio
                            obs["bucket"] = bucket(ratio)
                            sizes(team, "raise_"+st, ratio)
                            last_tag = tag
                        elif a == "call":
                            streetcalled = True
                    if a == "check":
                        checked.add(s)
                    if a == "raise":
                        if firstbettor is None:
                            firstbettor = s
                            bets_by_street[street] = s
                        streetraises += 1
                        street_raisers.add(s)
                        last_bet = s
                        last_ratio = obs.get("ratio", 0)
                        if s in shown:
                            cat = CLASSES[rank(shown[s]+board)[0]]
                            final = CLASSES[rank(shown[s]+h["board"])[0]]
                            tags = [
                                x for x in obs["tags"]
                                if x.startswith(("cbet", "barrel"))
                                or x in ("raise", "checkraise")
                            ]
                            line = ",".join(tags) or "other_bet"
                            key = "shown_"+st+"_"+line+"_"+obs["bucket"]
                            T[team]["d"][key][cat] += 1
                            T[team]["d"][key+"_final"][final] += 1
                            T[team]["d"][key+"_holes"][
                                hole_name(shown[s])
                            ] += 1
                            obs["shown_class"] = cat
                            obs["shown_hole"] = hole_name(shown[s])
                if a == "raise":
                    wager = {
                        "seat": s, "pot": pot, "risk": delta, "to": v,
                        "oldmax": mx, "previous": c[s],
                        "live": len(alive), "ratio": obs.get("ratio", 0),
                    }
                if a == "fold":
                    alive.remove(s)
                contrib[s] += delta
                c[s] += delta
                if a == "raise":
                    mx = c[s]
                handobs.append(obs)
                DECISIONS.append(obs)

        assert [
            paid[s]-contrib[s] for s in range(N)
        ] == h["results"]
        QUALITY["cash_checks"] += 1
        for s in vp:
            add(teams[s], "vpip", 0, 1)
            T[teams[s]]["c"]["third%d_vpip" % third] += 1
            fbet[s].append(("vpip",))
        for s in pfr:
            add(teams[s], "pfr", 0, 1)
            T[teams[s]]["c"]["third%d_pfr" % third] += 1
        for s in shown:
            T[teams[s]]["c"]["showdowns"] += 1
            T[teams[s]]["c"]["showdown_wins"] += paid[s] > 0
            T[teams[s]]["d"]["shown_holes"][hole_name(shown[s])] += 1
        ranks = {s: rank(shown[s]+h["board"]) for s in shown}
        level = 0
        modelpaid = [0.0]*N
        flow = [0.0]*N
        for lev in sorted(set(contrib)-{0}):
            investors = [s for s in range(N) if contrib[s] >= lev]
            eligible = [s for s in investors if s in alive]
            assert eligible
            if len(eligible) == 1:
                winners = eligible
            else:
                assert all(s in ranks for s in eligible)
                high = max(ranks[s] for s in eligible)
                winners = [s for s in eligible if ranks[s] == high]
            layer = (lev-level)*len(investors)
            share = 1/len(winners)
            for s in winners:
                modelpaid[s] += layer*share
            for s in range(N):
                if s != our:
                    flow[s] += (lev-level)*(
                        (our in investors)*(s in winners)*share
                        - (s in investors)*(our in winners)*share
                    )
            level = lev
        err = max(abs(modelpaid[s]-paid[s]) for s in range(N))
        QUALITY["layer_max_abs_error"] = max(
            QUALITY["layer_max_abs_error"], err
        )
        QUALITY["layer_odd_hands"] += err > 1e-8
        if any(abs(modelpaid[s]-paid[s]) > N for s in range(N)):
            QUALITY["layer_mismatch"] += 1
        for s, team in enumerate(teams):
            if s != our:
                T[team]["c"]["flow_from_us"] += flow[s]
        assert abs(sum(flow)-(-h["results"][our])) <= N
        for s in range(N):
            sessions[s]["features"].append(fbet[s])

    assert (
        sum(h["results"][our] for h in d["hands"])
        == d["round"]["chips"]
    )
    assert len(d["hands"]) == d["round"]["hands"]
    QUALITY["round_checks"] += 1


def team_output(team):
    c = T[team]["c"]
    ds = T[team]["d"]
    rates = {}
    for key in ["vpip", "pfr", "limp", "pf_shove"]:
        rates[key] = rate(c[key+"_yes"], c["hands"])
    for key in sorted({
        k[:-2] for k in c if k.endswith("_n") and c[k] > 0
    }):
        rates[key] = rate(c[key+"_yes"], c[key+"_n"])
    rates["wtsd"] = rate(c["showdowns"], c["flops"])
    rates["showdown_hands"] = rate(c["showdowns"], c["hands"])
    rates["won_showdown"] = rate(c["showdown_wins"], c["showdowns"])
    for st in STREETS[1:]:
        rates["overbet_"+st] = rate(
            c["overbet_"+st+"_yes"], c["bets_"+st+"_yes"]
        )
    return {
        "counts": dict(c),
        "rates": rates,
        "distributions": {
            k: desc(unpack(v))
            if k.startswith((
                "open_", "threebet", "fourbet", "iso_",
                "bet_", "raise_", "size_",
            ))
            else dict(v)
            for k, v in ds.items()
        },
        "rounds": [
            s["round"] for s in SESSIONS if s["team"] == team
        ],
        "bb100": round(c["chips"]*5/c["hands"], 3),
        "thirds": [{
            "hands": c["third%d_hands" % j],
            "chips": c["third%d_chips" % j],
            "vpip": rate(c["third%d_vpip" % j], c["third%d_hands" % j]),
            "pfr": rate(c["third%d_pfr" % j], c["third%d_hands" % j]),
        } for j in range(3)],
    }


OUT = {
    "quality": dict(QUALITY),
    "manifest": manifest,
    "teams": {t: team_output(t) for t in PRIMARY+BRIEF},
    "allteams": len(T),
    "sessions": len(SESSIONS),
}


def near(x, values, tol=.012):
    return any(abs(x-v) <= tol for v in values)


def fingerprint(features, name):
    flat = [f for hand in features for f in hand]
    op = [f for f in flat if f[0] == "open"]
    th = [f for f in flat if f[0] == "threebet"]
    be = [f for f in flat if f[0] == "bet"]
    if name == "Gherkers":
        return (
            len(op) >= 8
            and sum(f[1] == 70 or 71 <= f[1] <= 77 for f in op)/len(op) >= .9
            and len(th) >= 5
            and sum(
                min(abs(f[1]-round(f[2]*q)) for q in (3.2, 3.8)) <= 1
                for f in th
            )/len(th) >= .9
            and len(be) >= 5
            and sum(near(f[1], (.33, .7, 1.1)) for f in be)/len(be) >= .8
        )
    if name == "Equity Engine":
        return (
            len(op) >= 8
            and all(f[1] == 70 for f in op)
            and len(be) >= 8
            and sum(near(f[1], (.45, .5, .8)) for f in be)/len(be) >= .9
            and sum(near(f[1], (.5,)) for f in be) >= 2
            and sum(near(f[1], (.8,)) for f in be) >= 2
        )
    late = [f for f in op if f[2] in ("BTN", "SB")]
    return (
        len(op) >= 8
        and len(late) >= 3
        and all(f[1] == 50 for f in late)
        and sum(f[1] in (40, 80) for f in op) >= 2
        and len(th) >= 5
        and sum(
            f[1] in (3*f[2], 4*f[2], 5*f[2]) for f in th
        )/len(th) >= .95
        and len(be) >= 8
        and sum(
            near(f[1], (.33, .66, 1, .308, .19, .155)) for f in be
        )/len(be) >= .8
    )


FP = {}
for name in PRIMARY:
    pos = []
    neg = []
    blockpos = []
    blockneg = []
    wrong = collections.Counter()
    for sess in SESSIONS:
        alerts = []
        for end in range(200, len(sess["features"])+1, 100):
            match = fingerprint(sess["features"][end-200:end], name)
            if match:
                alerts.append(end)
        matching = sess["team"] == name
        (pos if matching else neg).append(bool(alerts))
        if alerts and not matching:
            wrong[sess["team"]] += 1
        for start in range(0, len(sess["features"])-199, 200):
            (blockpos if matching else blockneg).append(
                fingerprint(sess["features"][start:start+200], name)
            )
    first = [
        next((
            e for e in range(200, 1001, 100)
            if fingerprint(s["features"][e-200:e], name)
        ), None)
        for s in SESSIONS if s["team"] == name
    ]
    FP[name] = {
        "session_TP": rate(sum(pos), len(pos)),
        "session_FP": rate(sum(neg), len(neg)),
        "block_TP": rate(sum(blockpos), len(blockpos)),
        "block_FP": rate(sum(blockneg), len(blockneg)),
        "wrong_teams": dict(wrong),
        "first_detection": first,
    }
OUT["fingerprints"] = FP

ROUNDINFO = {}
for name in PRIMARY:
    rows = []
    for sess in SESSIONS:
        if sess["team"] != name:
            continue
        f = [v for hand in sess["features"] for v in hand]
        th = [v for v in f if v[0] == "threebet"]
        be = [v for v in f if v[0] == "bet"]
        op = [v for v in f if v[0] == "open"]
        ds = [
            v for v in DECISIONS
            if v["team"] == name and v["round"] == sess["round"]
        ]
        cb = [v for v in ds if "cbet_HU" in v["tags"]]
        rows.append({
            "round": sess["round"],
            "chips": sess["net"],
            "vpip": sum(v[0] == "vpip" for v in f),
            "pfr": len({
                v["hand"] for v in ds
                if v["street"] == "preflop" and v["action"] == "raise"
            }),
            "open": collections.Counter(v[1] for v in op).most_common(),
            "threebet": len(th),
            "threebet_formula": rate(sum(
                min(abs(v[1]-round(v[2]*q)) for q in (3.2, 3.8)) <= 1
                for v in th
            ), len(th)),
            "overbet": rate(sum(v[1] > 1 for v in be), len(be)),
            "HU_cbet": rate(sum(v["action"] == "raise" for v in cb), len(cb)),
            "bet_modes": collections.Counter(v[1] for v in be).most_common(5),
        })
    ROUNDINFO[name] = rows
OUT["roundinfo"] = ROUNDINFO


def wilson(k, n):
    if not n:
        return None
    z = 1.96
    p = k/n
    den = 1+z*z/n
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    center = (p+z*z/(2*n))/den
    return [
        round(max(0, center-half), 4),
        round(min(1, center+half), 4),
    ]


def evmodel(ds, name):
    n = len(ds)
    f = sum(o["action"] == "fold" for o in ds)
    if not n:
        return {"n": 0}
    p = f/n
    H = T[name]["c"]["hands"]
    P = statistics.mean(o["wager"]["pot"] for o in ds)
    R = statistics.mean(o["wager"]["risk"] for o in ds)
    lo = wilson(f, n)[0]
    own = sum(o["our_opp"] for o in ds)
    weight = sum(1/(o["N"]-1) for o in ds)
    return {
        "fold": rate(f, n),
        "wilson": wilson(f, n),
        "P": round(P, 3),
        "risk": round(R, 3),
        "break_even": round(R/(P+R), 4),
        "ev_bb": round((p*P-(1-p)*R)/20, 4),
        "equal_seat_opps100": round(100*weight/H, 4),
        "model_bb100": round(100*weight/H*(p*P-(1-p)*R)/20, 4),
        "lower_model_bb100": round(100*weight/H*(lo*P-(1-lo)*R)/20, 4),
        "response_to_our_seat": own,
    }


CANDIDATES = {}
for name in PRIMARY:
    ds = [
        o for o in DECISIONS
        if o["team"] == name and o.get("wager")
        and o["hu"] and o["wager"]["live"] == 2
    ]
    rows = {}
    selectors = {
        "flop_bet80": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and abs(o["faced_ratio"]-.8) <= .012
        ),
        "flop_bet67": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and abs(o["faced_ratio"]-2/3) <= .012
        ),
        "flop_bet100": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and abs(o["faced_ratio"]-1) <= .012
        ),
        "flop_bet110": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and abs(o["faced_ratio"]-1.1) <= .012
        ),
        "flop_raise_3B": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
            and abs(o["wager"]["to"]-3*o["wager"]["oldmax"]) <= 1
            and o["wager"]["previous"] == 0
        ),
        "BB_vs_SB50": lambda o: (
            o["street"] == "preflop" and o["position"] == "BB"
            and o["pf_nr"] == 1 and o["wager"]["to"] == 50
        ),
        "BB_vs_SB40": lambda o: (
            o["street"] == "preflop" and o["position"] == "BB"
            and o["pf_nr"] == 1 and o["wager"]["to"] == 40
        ),
        "fold3_all": lambda o: (
            o["street"] == "preflop" and o["pf_nr"] == 2
            and o["own_pf_raise"] == 1
        ),
        "fold3_3x": lambda o: (
            o["street"] == "preflop" and o["pf_nr"] == 2
            and o["own_pf_raise"] == 1
            and abs(o["wager"]["to"]-3*o["wager"]["oldmax"]) <= 1
        ),
        "fold4_all": lambda o: (
            o["street"] == "preflop" and o["pf_nr"] == 3
            and o["own_pf_raise"] == 2
        ),
        "fold4_23": lambda o: (
            o["street"] == "preflop" and o["pf_nr"] == 3
            and o["own_pf_raise"] == 2
            and abs(o["wager"]["to"]/o["wager"]["oldmax"]-2.3) <= .15
        ),
        "flop_checked_80": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and o["checked"] and abs(o["faced_ratio"]-.8) <= .012
        ),
        "turn_checked_80": lambda o: (
            o["street"] == "turn"
            and o.get("defender_kind") == "vsbet"
            and o["checked"] and abs(o["faced_ratio"]-.8) <= .012
        ),
        "river_checked_80": lambda o: (
            o["street"] == "river"
            and o.get("defender_kind") == "vsbet"
            and o["checked"] and abs(o["faced_ratio"]-.8) <= .012
        ),
        "flop_checked_110": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and o["checked"] and abs(o["faced_ratio"]-1.1) <= .012
        ),
        "flop_after_bet_raise": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
        ),
        "flop_after_bet_raise_small": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
            and o["wager"]["oldmax"] /
            max(1, o["wager"]["pot"]-o["wager"]["oldmax"]) <= .5
        ),
        "flop_raise_pot": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
            and abs(o["faced_ratio"]-1) <= .012
        ),
        "flop_raise_75": lambda o: (
            o["street"] == "flop"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
            and abs(o["faced_ratio"]-.75) <= .012
        ),
        "turn_after_bet_raise": lambda o: (
            o["street"] == "turn"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
        ),
    }
    for key, fn in selectors.items():
        sample = [o for o in ds if fn(o)]
        row = evmodel(sample, name)
        if sample:
            row["size_modes"] = collections.Counter(
                round(
                    o["faced_ratio"] if o["street"] != "preflop"
                    else o["wager"]["to"]/o["wager"]["oldmax"],
                    3,
                )
                for o in sample
            ).most_common(5)
        rows[key] = row
    CANDIDATES[name] = rows
OUT["candidates"] = CANDIDATES
OUT["context"] = {
    "bb": 20, "sb": 10, "stack": 2000,
    "n_seats": sorted(set(m["seats"] for m in manifest)),
    "rounds": len(files), "hands": QUALITY["hands"],
    "first_slot": manifest[0]["slot"], "last_slot": manifest[-1]["slot"],
    "sample_min": 30, "fingerprint_window": 200,
    "fingerprint_stride": 100, "fingerprint_size_tolerance": .012,
}

EVIDENCE = {}
for name in PRIMARY:
    ds = [o for o in DECISIONS if o["team"] == name]
    picked = [
        next(o for o in ds if "open" in o["tags"]),
        next(
            o for o in ds
            if o["street"] == "flop"
            and o["action"] == "raise" and o["cost"] == 0
        ),
    ]
    EVIDENCE[name] = []
    for o in picked:
        raw = json.loads(
            (ROOT/("saturday_r%03d.json" % o["round"])).read_text()
        )
        h = next(h for h in raw["hands"] if h["n"] == o["hand"])
        EVIDENCE[name].append({
            "round": o["round"], "hand": o["hand"], "seat": o["seat"],
            "obs": o, "events": h["events"][:o["event"]+1],
        })
OUT["evidence"] = EVIDENCE
OUT["fingerprint_intervals"] = {
    t: {
        "session_FP": wilson(x["session_FP"]["yes"], x["session_FP"]["n"]),
        "block_FP": wilson(x["block_FP"]["yes"], x["block_FP"]["n"]),
    }
    for t, x in FP.items()
}
OUT["formula_checks"] = {}
for name in PRIMARY:
    ds = [
        o for o in DECISIONS
        if o["team"] == name and o["street"] == "preflop"
        and o["action"] == "raise" and o["pf_nr"] == 1
    ]
    OUT["formula_checks"][name] = {
        "3x": rate(sum(
            o["to"] == round(3*o["wager"]["to"]) for o in ds
        ), len(ds)),
        "3.2_or_3.8": rate(sum(
            min(
                abs(o["to"]-round(q*o["wager"]["to"]))
                for q in (3.2, 3.8)
            ) <= 1 for o in ds
        ), len(ds)),
    }
OUT["pot_odds"] = {
    str(b): {
        "bluff_fold_pct": round(100*b/(1+b), 2),
        "call_equity_pct": round(100*b/(1+2*b), 2),
    }
    for b in (.33, .5, 2/3, .7, .8, 1, 1.05, 1.1)
}
OUT["third_summary"] = {
    t: [{
        "hands": r["hands"], "chips": r["chips"],
        "bb100": round(r["chips"]*5/r["hands"], 3) if r["hands"] else None,
        "vpip_pct": r["vpip"]["pct"], "pfr_pct": r["pfr"]["pct"],
    } for r in OUT["teams"][t]["thirds"]]
    for t in PRIMARY
}
OUT["brief_summary"] = {
    t: {
        "rounds": x["rounds"], "hands": x["counts"]["hands"],
        "chips": x["counts"]["chips"], "bb100": x["bb100"],
        "flow": round(x["counts"]["flow_from_us"], 3),
        "vpip": x["rates"]["vpip"], "pfr": x["rates"]["pfr"],
        "threebet": x["rates"]["threebet"],
        "fold3": x["rates"].get("fold_threebet"),
        "cbet_HU": x["rates"].get("cbet_HU"),
    }
    for t, x in OUT["teams"].items() if t in BRIEF
}

FIRST = {}
for name in PRIMARY:
    for s in SESSIONS:
        if s["team"] == name:
            FIRST[name, s["round"]] = next((
                end for end in range(200, 1001, 100)
                if fingerprint(s["features"][end-200:end], name)
            ), 1001)


def gate_model(ds, name):
    gated = [
        o for o in ds if o["hand"] > FIRST[name, o["round"]]
    ]
    return evmodel(gated, name)


for name in PRIMARY:
    ds = [
        o for o in DECISIONS
        if o["team"] == name and o.get("wager")
        and o["hu"] and o["wager"]["live"] == 2
    ]
    samples = {
        "flop_bet80": [
            o for o in ds if o["street"] == "flop"
            and o.get("defender_kind") == "vsbet"
            and abs(o["faced_ratio"]-.8) <= .012
        ],
        "flop_raise_3B": [
            o for o in ds if o["street"] == "flop"
            and o.get("defender_kind") == "vsraise"
            and o["own_street_bet"]
            and abs(o["wager"]["to"]-3*o["wager"]["oldmax"]) <= 1
            and o["wager"]["previous"] == 0
        ],
        "turn_checked_80": [
            o for o in ds if o["street"] == "turn"
            and o.get("defender_kind") == "vsbet"
            and o["checked"] and abs(o["faced_ratio"]-.8) <= .012
        ],
        "fold3_3x": [
            o for o in ds if o["street"] == "preflop"
            and o["pf_nr"] == 2 and o["own_pf_raise"] == 1
            and abs(o["wager"]["to"]-3*o["wager"]["oldmax"]) <= 1
        ],
    }
    for key, sample in samples.items():
        OUT["candidates"][name][key]["after_detection"] = gate_model(
            sample, name
        )

OUT["sd_lines"] = {}
for name in PRIMARY:
    rows = {}
    for o in DECISIONS:
        if o["team"] != name or "shown_class" not in o:
            continue
        tags = [
            tag for tag in o["tags"]
            if tag.startswith(("cbet", "barrel"))
            or tag in ("checkraise", "raise", "checked_to")
        ]
        if not tags:
            tags = ["other_bet"]
        for tag in tags:
            key = o["street"]+" "+tag
            rows.setdefault(
                key, {b: collections.Counter() for b in BUCKETS}
            )[o["bucket"]][o["shown_class"]] += 1
    OUT["sd_lines"][name] = {
        key: {
            b: {"n": sum(c.values()), "classes": dict(c)}
            for b, c in bs.items() if c
        }
        for key, bs in rows.items()
    }

OUT["third_post"] = {}
for name in PRIMARY:
    rows = []
    for j in range(3):
        rr = {
            s["round"] for s in SESSIONS
            if s["team"] == name and s["third"] == j
        }
        ds = [
            o for o in DECISIONS
            if o["team"] == name and o["round"] in rr
        ]
        cb = [o for o in ds if "cbet_HU" in o["tags"]]
        bets = [
            o for o in ds
            if o["street"] != "preflop"
            and o["cost"] == 0 and o["action"] == "raise"
        ]
        f3 = [
            o for o in ds
            if o["street"] == "preflop"
            and o["pf_nr"] == 2 and o["own_pf_raise"] == 1
        ]
        rows.append({
            "rounds": sorted(rr),
            "cbet_HU": rate(
                sum(o["action"] == "raise" for o in cb), len(cb)
            ),
            "overbet": rate(sum(o["ratio"] > 1 for o in bets), len(bets)),
            "fold3": rate(sum(o["action"] == "fold" for o in f3), len(f3)),
        })
    OUT["third_post"][name] = rows

OUT["full_open"] = {
    name: {
        k: dict(v) for k, v in T[name]["d"].items()
        if k.startswith("open_")
    }
    for name in PRIMARY
}
OUT["sizing_formula"] = {}
order = {
    p: i for i, p in enumerate(
        ("SB", "BB", "UTG", "UTG1", "LJ", "HJ", "CO", "BTN")
    )
}
for name in PRIMARY:
    ds = [
        o for o in DECISIONS
        if o["team"] == name and o["street"] == "preflop"
        and o["action"] == "raise" and o["pf_nr"] in (1, 2)
    ]
    by = collections.defaultdict(collections.Counter)
    for o in ds:
        w = o["wager"]
        if o["pf_nr"] == 1:
            for q in (3, 3.2, 3.8, 4, 5):
                if abs(o["to"]-round(q*w["to"])) <= 1:
                    by["3-bet"][str(q)] += 1
        else:
            for q in (2.3, 2.5, 3):
                if abs(o["to"]-round(q*w["to"])) <= 1:
                    by["4-bet"][str(q)] += 1
    OUT["sizing_formula"][name] = {
        k: dict(v) for k, v in by.items()
    }

OUT["verification"] = {
    "chip_reconciliations": QUALITY["cash_checks"],
    "layer_mismatches": QUALITY["layer_mismatch"],
    "raw_checks": {
        name: [{
            "round": e["round"], "hand": e["hand"], "seat": e["seat"],
            "amount": e["obs"]["to"], "pot": e["obs"]["pot"],
            "pct": round(100*e["obs"]["to"]/e["obs"]["pot"], 2),
        } for e in es]
        for name, es in EVIDENCE.items()
    },
}
OUT["model_limits"] = {
    "wilson_z": 1.96, "minimum_opportunities": 30,
    "equal_seat_weight": "1/(N-1)", "chip_to_bb": 20,
    "stop_window": 30, "max_counter_bluffs_per100": 1,
    "post_size": .8, "raise_bet_multiple": 3,
    "threebet_open_multiple": 3,
}

OUT["context"].update({
    "final_hands_given": 5000, "final_seats_given": 8,
    "advancers_given": 2,
    "third_rounds": [[1, 15], [16, 30], [31, 45]],
})
OUT["round_specific"] = {}
for name in PRIMARY:
    rows = []
    for sess in SESSIONS:
        if sess["team"] != name:
            continue
        ds = [
            o for o in DECISIONS
            if o["team"] == name and o["round"] == sess["round"]
        ]
        opp3 = [
            o for o in ds
            if o["street"] == "preflop" and o["pf_nr"] == 1
        ]
        rows.append({
            "round": sess["round"],
            "vpip": rate(
                sum(
                    f[0] == "vpip"
                    for h in sess["features"] for f in h
                ),
                len(sess["features"]),
            ),
            "threebet": rate(
                sum(o["action"] == "raise" for o in opp3), len(opp3)
            ),
        })
    OUT["round_specific"][name] = rows

OUT["summary_counts"] = {
    t: {
        "rounds": x["counts"]["rounds"],
        "hands": x["counts"]["hands"],
        "chips": x["counts"]["chips"],
        "bb100": x["bb100"],
        "from_our_seat": round(x["counts"]["flow_from_us"], 3),
    }
    for t, x in OUT["teams"].items()
}
OUT["our_result"] = {
    "hands": T["Resonance Qt"]["c"]["hands"],
    "chips": T["Resonance Qt"]["c"]["chips"],
    "bb100": round(
        T["Resonance Qt"]["c"]["chips"]*5 /
        T["Resonance Qt"]["c"]["hands"], 3
    ),
}

for team in list(OUT["teams"]):
    if team not in PRIMARY:
        del OUT["teams"][team]
    else:
        OUT["teams"][team]["distributions"] = {
            k: v for k, v in OUT["teams"][team]["distributions"].items()
            if not k.startswith("shown_")
        }
OUT["ran_end_to_end"] = True

OUT["formula_detail"] = {}
for name in PRIMARY:
    ds = [
        o for o in DECISIONS
        if o["team"] == name and o["street"] == "preflop"
        and o["action"] == "raise" and o["pf_nr"] == 1
    ]
    ip = [
        o for o in ds
        if order[o["position"]] > order[o["pf_agg_pos"]]
    ]
    oop = [
        o for o in ds
        if order[o["position"]] < order[o["pf_agg_pos"]]
    ]
    OUT["formula_detail"][name] = {
        "3plus_callers": rate(sum(
            o["to"] == (3+o["pf_callers"])*o["wager"]["to"]
            for o in ds
        ), len(ds)),
        "IP_3.2": rate(sum(
            abs(o["to"]-round(3.2*o["wager"]["to"])) <= 1
            for o in ip
        ), len(ip)),
        "OOP_3.8": rate(sum(
            abs(o["to"]-round(3.8*o["wager"]["to"])) <= 1
            for o in oop
        ), len(oop)),
    }
    opens = [
        o for o in DECISIONS
        if o["team"] == name and "open" in o["tags"]
    ]
    OUT["formula_detail"][name]["open_size_counts"] = dict(
        collections.Counter(o["to"] for o in opens)
    )
OUT["ran_end_to_end"] = True

OUT["defender"] = {
    name: {
        key: {
            "n": sum(c.values()),
            "fold": c["fold"], "call": c["call"], "raise": c["raise"],
            "unreliable": sum(c.values()) < 30,
        }
        for key, c in T[name]["d"].items()
        if key.startswith((
            "vsbet", "vsraise", "vscbet", "vsbarrel", "after_own_bet"
        ))
    }
    for name in PRIMARY
}
OUT["checked_sizes"] = {}
for name in PRIMARY:
    OUT["checked_sizes"][name] = {}
    for st in STREETS[1:]:
        for tag in ("checked_to", "checkraise"):
            vals = [
                o["ratio"] for o in DECISIONS
                if o["team"] == name and o["street"] == st
                and o["action"] == "raise" and tag in o["tags"]
            ]
            OUT["checked_sizes"][name][st+"_"+tag] = desc(
                [round(v, 3) for v in vals]
            )
OUT["ran_end_to_end"] = True
print(json.dumps(OUT))
```
