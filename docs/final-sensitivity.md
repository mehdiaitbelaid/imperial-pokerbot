# Final table: sensitivity sweep, the weak bots, and what to play

Written Sun 15 Nov 2026, about 11:10 UK time, by Claude for Hassan (Resonance Qt). Live data
through bucket round 20 (`rankings/sunday-bucket-rounds.csv`, branch `rankings-history`).
Simulations use the tools and replicas on this branch. ± is one standard error.

## 1. Summary

1. **V24's surge was a hot streak plus a real but small rule.** Over all its rounds (8 to 20) V24
   averages +22.4 bb/100; V22 averaged +22.1 over rounds 2 to 7. Difference: +0.2 ± 20.
2. **Our chips at Table D come from four losing bots, and three of them have stopped losing.**
   None of the four will be in the final.
3. **The final is five fresh 1,000-hand blocks** (organisers' answer, `docs/v32-notes.md`): fresh
   `Agent()` and a fresh 10 s bank each block. No time pacing is needed, the end-game rank mode
   cannot work, and everything learned resets each block. Preloaded seeds matter.
4. **v3.2 is the best build we have for that table:** +6.6 ± 4.4 bb/100 over V24 on the exact
   current top-two line-up (independent re-run; the team measured +7.3 ± 2.4 on a similar one).
5. **Expect a close game.** Against solid bots our live edge is about zero. At zero edge the
   simulated chance of a top-two finish is about 15 to 20%; at +10 bb/100 about 35%; at +20
   about 60%.

## 2. Sensitivity: opponents or strategy?

V24 = V22 plus one rule (turn or river calls of 500+ chips with one pair or less need 15 points
more equity), live from round 8. V25 (live from 10:37) adds a no-third-barrel rule against Anker.

| Rounds | Build | Our chips per round | bb/100 | Four losing bots, per round | Our share of their losses |
|---|---|---|---|---|---|
| 2 to 7 | V22 | +4,428 | +22.1 | −12,859 | 34% |
| 8 to 15 | V24 | +7,859 | +39.3 | −12,737 | 62% |
| 16 to 20 | V24 | −946 | −4.7 | −9,137 | none (we lost) |
| 8 to 20 | V24, all rounds | +4,472 | +22.4 | −11,352 | 39% |

- **Rounds 8 to 15:** the pot was the same size as before; we took 62% of it instead of 34%, at
  the expense of Anker and Chinese people can fly. The hand files (`pokerbots-final-strategy.md`,
  branch `claude-v18r`) put 96% of those chips on the four losing bots, +2,045 in six rounds on
  the three solid ones, and 16,834 chips on all-in luck.
- **Rounds 16 to 20:** the share went back. Our single-round standard deviation is about
  10,100 chips, so a five-round swing of this size is ordinary.
- **The rule itself is real:** on identical cards it is worth about +10 bb/100 in 5,000-hand
  games against finalist replicas (v3.0 with the rule minus v3.0: +10.0 ± 3.9, 16 games).

## 3. The weak bots at Table D

Chips per round, by period:

| Team | Rounds 2 to 7 | Rounds 8 to 15 | Rounds 16 to 20 |
|---|---|---|---|
| WBot | −7,409 | −5,413 | −1,314 |
| GamesGone | −3,310 | −3,266 | +1,519 |
| Anton | −631 | −392 | +1,613 |
| YSL_TWIZZY | −1,508 | −3,666 | −10,955 |
| Anker Batteries | +6,594 | +2,702 | +5,504 |
| Chinese people can fly | +2,527 | −755 | +4,740 |
| Poke | −690 | +2,932 | −162 |

- WBot, GamesGone and Anton stopped losing after round 15 (new uploads or variance; not known).
- YSL collapsed, and its chips went to Anker and Chinese people can fly, not to us.
- Standing after round 20: Anker +90,011, **Resonance Qt +85,466**, Chinese people can fly
  +21,314, Poke +20,320. Cushion over third: about 64,000 chips with 16 rounds left. Rough chance
  of being passed: 1% if averages hold, 8% with no edge either way, 13% on the last five rounds'
  trend.

## 4. How the final differs

Projected finalists after round 20: Astra La Vista, Attention Is All In (Table A); Gherkers plus
one of JoCal, Phil AIvey, Equity Engine, all within 2,000 chips (Table B); FisherMen, Jump Street
(Table C); Anker Batteries and us (Table D).

| Simulated table (1,000-hand blocks, fresh agent each block) | Blocks | V24 | v3.2 | v3.2 minus V24 |
|---|---|---|---|---|
| Replica of Table D (Anker, CPF, WBot, GamesGone, Poke, Anton, YSL) | 30 | +55.1 ± 7.3 | +60.3 | +5.2 ± 6.6 |
| Projected final (Astra, Attention, Gherkers, Equity Engine, FisherMen, Jump Street, Anker) | 70 | +30.9 ± 4.2 | +37.5 ± 3.2 | **+6.6 ± 4.4** |
| Same, with folding leaks fixed (`tabled/h_*.py`) | 40 | +34.0 ± 6.8 | +38.2 ± 5.3 | +4.2 ± 6.2 |

- **No weak bots:** the same bot makes about 24 bb/100 less at the final table than at Table D,
  even against replicas. Live, it is closer to zero: break-even against today's solid three and
  against Saturday's top ten.
- **No memory across blocks:** each block starts cold, so seeds and fingerprints that work from
  hand one are worth more than rules that need 200 hands of evidence.
- **Who pays in simulation:** FisherMen (−22 to −35), Jump Street (−9 to −15), Attention (−4 to
  −8). Gherkers and Astra win. The replicas are built from Saturday hands; Astra and Jump Street
  have improved since, so read these as leads.
- **The replicas are weaker than the real bots.** The +30s rank our builds; they do not forecast.

Chance of finishing first or in the top two over five blocks, resampling simulated blocks and
moving our edge to a chosen level (chips taken from us go equally to the seven others):

| Our edge at the final table | V24: 1st / top two | v3.2: 1st / top two |
|---|---|---|
| As simulated (+31 / +38) | 61% / 84% | 80% / 95% |
| +20 bb/100 | 37% / 63% | 39% / 65% |
| +10 bb/100 | 19% / 39% | 16% / 37% |
| 0 | 8% / 19% | 5% / 14% |

At a fixed edge the two builds are equivalent within noise; v3.2's value is that it raises the edge.

## 5. What we can do to compensate

1. **Play v3.2 in the final.** Finalist fingerprints and seeds work from the first hands of each
   block; 4-bets against seats that give up their 3-bets; bluff-raises of pot-size bets only on
   the seat's own record. It costs nothing at Table D in simulation (+5.2 ± 6.6), so it can go up
   before the bucket rounds end and get live rounds as a check.
2. **Carry V25's third-barrel rule into the final build.** v3.2 was cut from V24 before V25.
   Three-street bluffs lost 20,530 chips on 30 hands today, and the two solid players made 14 of
   the 17 calls; the final has seven solid players. Tested in section 6: no measurable effect against replicas.
3. **Stop paying for information.** Rules that fire only after 8 or more observed cases see few
   cases in 1,000 hands. Where a finalist has no seed (Jump Street, JoCal), the default should be
   the cautious line: fewer bluff-raises and fewer river bluffs, not more.
4. **Do not chase variance.** With no chip memory between blocks the bot cannot know its rank;
   nothing in the build should take −EV gambles.
5. **Timing.** Nothing new after 11:50. Before any upload: `tools/fuzz_mehdi.py` with 0 illegal
   replies.

## 6. V25's rule inside v3.2

Projected final line-up, the first 50 blocks of seed 21, same cards and seats as v3.2 (+34.7 on those blocks):

| Build | bb/100 | Minus v3.2 | Minus V24 |
|---|---|---|---|
| v3.2 + V25 rule (Anker only) | +33.4 ± 4.1 | -1.3 ± 4.7 | +2.7 ± 6.2 |
| v3.2 + rule against any seat | +32.8 ± 3.8 | -1.8 ± 4.5 | +2.2 ± 5.5 |

- **No measurable effect either way.** The rule fires on a handful of hands per block, and the
  replicas do not call three streets the way Anker and Chinese people can fly did today, so this
  test cannot confirm the live evidence. It also shows no harm.
- **Decision for the team:** v3.2 as committed is the tested build. Adding the Anker-only rule is
  a four-line change with live evidence (he folded the river 4 times in 16) and no simulated
  cost; the any-seat version has no evidence of its own. The two test files were not committed;
  the patch is V25's block inserted at the same place in `bots/v32.py`.

## 7. Method and limits

- Live figures: per-round chips are differences of the cumulative standings; "four losing bots"
  = WBot, YSL_TWIZZY, GamesGone, Anton.
- Simulations: `tools/bucket_sim.py` (paired by seed, same seat order), blocks of 1,000 hands,
  seeds 21 (final), 22 (Table D), 23 (leaks fixed). Final odds: `tools/final_odds.py`, 20,000
  resampled five-block finals per line.
- Limits: 30 to 70 blocks per comparison; replicas come from Saturday hands, so tests of seeded
  rules show the mechanism, not the size of the live gain; a finalist that changed its bot gives
  nothing until the live counters catch up.
