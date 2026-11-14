# Resonance Qt: full analysis of counted rounds 1–20

Written Sat 14 Nov 2026, 16:50 UK time, by Claude. The data is all 20,000 of our counted-round hands, pulled from the team API, plus the public standings at 16:41 (after round 21). Saeed holds the data token; never commit it. Analysis script: `tools/full_analysis.py` on this branch (needs the hand files in `hands/`).

## 1. Bottom line

1. **We're 6th of 39 at +30.8 bb/100 after 21 rounds.** Gherkers leads at +47.2, then Equity Engine +40.7 and Attention Is All In +39.0. The gap to 1st is about 16 bb/100, roughly 3,200 chips a round.
2. **On the real tables, the live bot (V18, upload v7) has done worse than the bot it replaced (Avengers v14, upload v6).** Both played 9 rounds:

   | | Actual bb/100 | All-in luck | Luck-adjusted | Luck-adjusted, without the ediz_slow tables |
   |---|---|---|---|---|
   | v6, Avengers v14 (R3–R11) | +39.7 | −7.8 | **+47.5** | **+44.6** (7 rounds) |
   | v7, V18 (R12–R20) | +33.1 | **+15.1** | **+18.0** | **+3.3** (8 rounds) |

   Without the whale tables the difference is **41 ± 9.5 bb/100 (t = 4.4)**.
   - The table draw does not explain it: V18's opponents were *weaker* (their average Saturday score was +2.9, against +9.0 for v14's, whale excluded).
   - Field drift over the afternoon may explain part of it, because teams improved their bots.
   - **V18's headline number is propped up by all-in luck.**
3. **Our sandbox ranked these bots the other way round** (V18 beat v14 by 11–32 bb/100 against replicas). The replicas are missing something that matters on the real tables. Most likely they are too passive or too sticky, so they reward V18's call-heavy postflop and under-reward v14's aggression (section 4).
4. **Recommendation:**
   - Put the v14 engine back live as **av14f**: v14 with a CPU cap, same play as v14 (+2.8 ± 5.7 in a duel). It is `upload/bot_av14f.py` on this branch, SHA `ec92d4936d8f`.
   - Then compare luck-adjusted over the next 6 rounds with `tools/full_analysis.py`.
   - **Do not upload V18r.** It is V18-based. If you must stay on V18, V18r is strictly a latency and river-call patch.
   - This is the team's call. The evidence is strong (t = 4.4) but comes from real-world, non-paired data.

## 2. Results by round

The upload changes from R3 (v6) and R12 (v7). "Luck" is all-in luck: actual chips minus expected value at the moment we were all in with cards known, via Monte Carlo. Bold rounds had ediz_slow at the table.

| Round | Upload | bb/100 | Luck | Luck-adjusted | Timeouts |
|---|---|---|---|---|---|
| R1 | v5, Mehdi v1 | −7.9 | +7.1 | −15.0 | 7 |
| R2 | v5 | −18.9 | +5.4 | −24.2 | 1 |
| **R3** | v6, Avengers v14 | +36.9 | −47.2 | +84.0 | 10 |
| R4 | v6 | +65.2 | +8.8 | +56.3 | 2 |
| R5 | v6 | +36.2 | −9.3 | +45.5 | 1 |
| R6 | v6 | +75.7 | +32.8 | +42.9 | 1 |
| R7 | v6 | +3.5 | −15.8 | +19.3 | 0 |
| R8 | v6 | +45.3 | −5.6 | +50.9 | 3 |
| R9 | v6 | +12.9 | −14.9 | +27.8 | 1 |
| R10 | v6 | +77.5 | +8.1 | +69.4 | 0 |
| **R11** | v6 | +3.9 | −27.1 | +31.0 | 0 |
| R12 | v7, V18 | +21.0 | +17.3 | +3.6 | 1 |
| R13 | v7 | +20.4 | +46.2 | **−25.8** | 1 |
| R14 | v7 | +28.0 | +29.0 | −1.1 | 1 |
| **R15** | v7 | +163.7 | +28.0 | +135.7 | 0 |
| R16 | v7 | +21.4 | +1.7 | +19.7 | 0 |
| R17 | v7 | +3.3 | +2.3 | +1.0 | 1 |
| R18 | v7 | +56.4 | +24.5 | +31.9 | 0 |
| R19 | v7 | −33.5 | −12.7 | −20.8 | 0 |
| R20 | v7 | +17.5 | −0.2 | +17.8 | 0 |

Each round has a standard deviation of about 13.5 bb per hand, so a 1,000-hand round swings about ±43 bb/100 even after the luck adjustment. Judge bots over 6 or more rounds.

## 3. Where the chips come from

`tools/analyze.py --me`, grouped by how the hand ended, in bb/100 of all hands:

| | Ended preflop | Ended postflop, no showdown | Showdown |
|---|---|---|---|
| v6, Avengers v14 | −0.3 | **+8.1** | +31.8 (about +39.6 after luck) |
| v7, V18 | **−5.7** | **−4.1** | +42.9 (about +27.8 after luck) |

**V18 gives away about 18 bb/100 in pots that never reach showdown.** v14 took them.

**Dependence on the whale.** ediz_slow (−286 bb/100 overall) gave us +1,106 bb under v6 and +1,294 bb under v7. That is about 2,400 bb, **roughly 37% of all our counted-round profit, from 3 rounds.** Sunday's bucket tables may not include a whale, so we have to win against solid bots.

**Who we lose to.**
- v7: FisherMen −463 bb, Peanut Cookies −275, munchlax −270, Claudebot −196, Red −183, GamesGone −169. These are tight or passive teams; we pay them off.
- v6: Attention Is All In −406, WBot −263, Vlad −108.

**By position** (bb/100):

| | EP | HJ | CO | BTN | SB | BB |
|---|---|---|---|---|---|---|
| v6 | +42.7 | +13.6 | +94.1 | +87.3 | −38.1 | +33.4 |
| v7 | +14.5 | +40.7 | +52.3 | +44.5 | +57.4 | +1.2 |

V18 fixed the small blind (v14 lost there) but lost most of v14's late-position edge, and it makes nothing in the big blind.

## 4. What V18 does differently, and why it loses

Our stats from `tools/analyze.py`. The last column is the range for the top-3 teams on our tables.

| Stat | v6, Avengers v14 | v7, V18 | Gherkers / Attention / Equity Engine |
|---|---|---|---|
| VPIP / PFR | 23 / 17 | 26 / 20 | 29/22, 36/30, 23/17 |
| 3-bet % | 11 | **16** | 21, 12, 2 |
| Fold to a 3-bet % | 57 | **67** | 40, 68, 49 |
| C-bet % | **86** | 68 | 76, 65, 74 |
| Bet when checked to % | **57** | 42 | 55, 58, 45 |
| Fold to a postflop bet % | 47 | 42 | 57, 58, 50 |
| Aggression factor (bets and raises ÷ calls) | 1.7 | **1.1** | **3.7, 3.0, 2.3** |
| Goes to showdown % | 24 | 28 | 19, 24, 27 |
| Wins at showdown % | 59 | 54 | 56, 57, 44 |

The top-team numbers are from their hands at our tables in rounds 1–11 (`tools/analyze.py`).

**V18 is a postflop calling engine.** It bets less, c-bets less, folds less and goes to showdown more. The top three teams are far more aggressive after the flop (aggression 2.3–3.7, against V18's 1.1). The field folds 50–60% of the time to a postflop bet, so betting wins pots and calling pays off value hands.

**Preflop, V18 3-bets much more but then folds to 4-bets 75% of the time** (95 of 126), which cost −803 bb. It also opens and folds to 3-bets 68% of the time (208 of 307), which cost −635 bb. The 3-bets are still profitable overall (+3,059 bb), but the folds are what solid opponents exploit.

**Calling big bets.** The table shows the counterfactual gain of calling versus folding at that moment, summed over the rest of the hand:

| Street, bet size (share of pot) | v6 calls / won / gain | v7 calls / won / gain |
|---|---|---|
| flop, at least the pot | 32 / 12 / −67 bb | 72 / 27 / +37 bb |
| **turn, at least the pot** | 13 / 7 / +45 bb | **27 / 9 / −301 bb** |
| **river, at least the pot** | 4 / 1 / −128 bb | **17 / 5 / −322 bb** |
| any street, under the pot | profitable | profitable |

- **Calling pot-sized or bigger bets on the turn and river costs V18 about −7 bb/100.** v14 rarely faced or made those calls.
- Calls of smaller bets are profitable on every street. Keep them.

**Stacking off with one pair against tight players** (from the luck table, where our equity was near 0% when the money went in):
- r19#127: KQ called a 1,940 flop shove into about 180 from Red (21% VPIP). He had a set.
- r14#655: QQ on A-x-x-x against aydine's AQ.
- r20#150: AK on A-J-8 against gamblerlove, drawing dead.
- r20#848: K♣5♣ against WBot on a 4-club board, drawing dead.

## 5. Process flaws (what we as a team are doing wrong)

1. **We trust the sandbox over the live data.** Every upload since 15:50 was chosen on replica duels, and the replicas got the V18 vs v14 call backwards.
   - Fix: every candidate must also be judged on luck-adjusted live rounds (`tools/full_analysis.py`).
   - Fix: the replicas need recalibrating so that our bot's postflop aggression earns what it does live.
   - Check: `field/c_*.py` fold rates against *our* bets should match the real fold rates (`tools/calib.py` on `fable-bot`).
2. **We swap bots without a plan.** There have been 7 uploads, and two different engines live today. Decide on one engine, run it 6 or more rounds, measure luck-adjusted, then change.
3. **Profit depends on a whale.** 37% of profit came from ediz_slow in 3 rounds. Sunday is "top 2 by chips at one table", so the bot has to beat solid bots: aggressive postflop, fold to big bets from tight players.
4. **Timeouts are solved.** Rounds 12–20 had 5 in total, below the field median of about 30 over 21 rounds. Keep every postflop engine at or under 0.5 ms CPU p95; the server is 4–5× slower than our sandbox.

## 6. To-do list for the next agent, in priority order

1. **Decision now:** upload `upload/bot_av14f.py` (SHA `ec92d4936d8f`) via Saeed or Mehdi. Track R22 onward luck-adjusted and compare with v6's +44.6 (no whale).
2. **Recalibrate the sandbox to reality.** For each `field/c_*.py` profile, measure how often it folds to *our* c-bets, turn barrels and river bets on the real hands, by team. Adjust `fold_to_bet` and `cbet` until duels between v14 and V18 replay the live gap: v14 ahead by about 30–40 bb/100. Until they do, the sandbox can't choose bots.
3. **Fold to overbets on the turn and river from players who rarely bluff.**
   - Port the V18r river rule to v14's postflop, in `src/avengers.py`, `_postflop` facing a bet.
   - Extend it to turn bets of at least 0.9 × the pot, and to flop shoves of at least 1.5 × the pot, from seats with VPIP under 30% and measured river air under 15%.
   - Check by replaying the real calls (`tools/rivreplay.py`; adapt it per street).
4. **Fold less to 4-bets after 3-betting** (V18 folds 75%). Or 3-bet a more value-weighted range against seats that 4-bet, measured per seat.
5. **Big blind defence:** V18 makes +1.2 bb/100 in the big blind. Review `BB_DEFEND` and 3-bet-from-the-big-blind against late-position steals.
6. **Re-run this analysis every 5 rounds** (`tools/full_analysis.py`) and append the results to this file.

## 7. How the numbers were produced

- **Data:** `GET /api/poker/results` and `/api/poker/hands?ref=saturday/rNNN` with the team token, from a browser tab on imperialaihack.com (the cloud sandbox can't reach the site). Run `tools/full_analysis.py` with the hands in `hands/`.
- **All-in luck:** when all remaining players' cards are known and no further betting is possible, expected value = equity × total pot − our contribution. Equity is computed exactly on the turn and flop, and by 1,500-sample Monte Carlo preflop. Luck = actual − expected value. It covers 215 all-ins over rounds 1–20.
- **Opponent attribution:** a losing hand's loss is split among the winners in proportion to their winnings, and a winning hand's gain among the losers.
- **Table strength:** the mean Saturday score (at 16:41) of the 5–7 opponents at our table, whale excluded.
- **Caveat:** opponents and their bot versions changed during the afternoon. The v6 and v7 periods are consecutive, not interleaved. A paired live A/B test (alternating uploads round by round) would settle it best.
