# v3.0: candidate for the final table

Status, Sun 15 Nov 07:00 UK time: **candidate, tested in simulation, not live.** File: `upload/bot_v30.py` (same as `bots/v30.py`). Riad approves every upload. The final is one 5,000-hand game with eight bots at 12:05; uploads close at 12:00 and the finalists are only known after the 11:55 round, so this file should go up between 11:56 and 11:59.

## What v3.0 is

V22's engine (see `docs/v22-notes.md`) with four changes for the final:

1. **Nothing specific to one table.** `FINGERPRINTS = False`: no team is recognised and no Saturday statistics are preloaded. Every exploit is learned during the game from each seat's own actions, so it still works if a team changed its bot.
2. **Rules that used a label now use the seat's record.** 4-bet instead of calling against a seat that 3-bets 18% or more and has folded 55% or more of the 4-bets it faced; raise instead of calling when a seat's bets of that size have folded to raises 80% of the time over 8 or more cases.
3. **Time pacing for a long game.** In a game of more than 1,500 hands the bot estimates what the server has counted (its own clock plus 0.9 ms per decision) and spreads what is left over the remaining hands. `FINAL_BANK_S` is the bank it assumes for the whole game.
4. **End-game rank mode.** In the last quarter it follows every seat's chips (from the end-of-hand stacks). Outside the top two and more than half a standard deviation behind second place, it calls and shoves lighter; inside the top two and far ahead of third, it passes on big marginal calls.

## Open question that decides one constant

The kit says 10 ms per decision, including sending the state, and a 10-second bank per 1,000-hand round. On Saturday the server counted 1.6 to 3.2 seconds per 1,000 hands for our bot, so 5,000 hands need 8 to 16 seconds.

- If the final's bank is scaled (50 seconds): set `FINAL_BANK_S = 50.0` (`bots/v30_bank50.py`). The pacing then never binds.
- If it is 10 seconds for all 5,000 hands: keep `FINAL_BANK_S = 10.0`. The bot then thinks much less per decision, but still plays every hand while unpaced bots are auto-folded once their bank is empty.

Question for the organisers: "In the final, is the 10-second time bank for all 5,000 hands, or is it scaled?"

## Tests in final conditions

Games of 5,000 hands with eight agents, same cards and seats for every bot (`tools/bucket_sim.py --hands 5000`, `tools/final_report.py`). Opponents are replicas of likely finalists built from their real Saturday hands (`tabled/f_*.py`, calibration table in the replica builder's report; `tabled/FINAL_LINEUPS.txt`).

| Opponents | Games per bot | v3.0 | V22 minus v3.0 | V21 minus v3.0 | v14 minus v3.0 |
|---|---|---|---|---|---|
| (a) Top seeds: Attention, Gherkers, Market Makers, Equity Engine, Kojack, FisherMen, Anker | 80 | +40.9 | +2.3 ± 1.9 | -3.8 ± 2.1 | -14.7 ± 1.9 |
| (a) again, other cards | 70 | +40.7 | -2.3 ± 2.3 | | |
| (h) Same seven after fixing their folding leaks (`tabled/h_*.py`) | 80 | +38.5 | +2.3 ± 2.1 | +2.1 ± 1.9 | -2.6 ± 2.0 |
| (b) Mohil and Durahim instead of Kojack and FisherMen | 50 | +41.9 | -0.4 ± 2.8 | -6.2 ± 2.4 | -11.5 ± 2.4 |
| (c) also Phil AIvey instead of Equity Engine | 50 | +41.9 | -0.6 ± 2.6 | -5.9 ± 2.4 | -14.7 ± 2.4 |
| (s) Real bots: our v14, Mehdi's v3, Hassan's, Saeed's V18r, plus three replicas | 50 | +23.9 | -4.0 ± 2.3 | -6.2 ± 2.3 | |

- v3.0 and V22 are level against replicas and v3.0 is ahead against real bots. V22 cannot play the final as it is: no time pacing, and fingerprints made for the morning table.
- v3.0 is about 4 bb/100 ahead of V21 and 11 to 15 ahead of v14, except against opponents with no folding leaks left, where all our builds are within 3.
- First run with six builds (60 games each, top seeds): v3.0 +41.7, V22 +43.8, V21 +37.5, V20 +30.6, v14 +27.4, v14p +23.9.
- Pacing and rank mode cost nothing measurable here (70 games each): without pacing -0.3 ± 2.2, without rank mode -1.6 ± 1.9. A fast laptop cannot show the cost of thinking less on the slow server.

## End-game rank mode

Finals of 5,000 hands with a handicap of 42.5 bb/100 on our own chips, so that we sit in a close race (`tools/rank_report.py`):

| Build | Finals | First | Top 2 | Expected prize |
|---|---|---|---|---|
| Without rank mode | 480 | 11.9% | 24.6% | about £85 |
| **With rank mode (kept)** | 480 | 13.6% | 29.0% | about £98 |
| Refined variant (also chases first from second) | 240 | 12.9% | 26.2% | about £91 |

The kept form adds about 4 points of top-2 chance with no measurable cost in chips; the margin of error is about 3 points. The refined variant tested no better and was dropped.

## Honest outlook

The replicas are weaker than the real bots, so these numbers rank our builds; they do not predict the final. On real late-Saturday form the likely finalists average +44.7 (Attention Is All In), +30.9 (The Market Makers), +29.4 (FisherMen), +21.5 (Anker Batteries), +20.2 (Gherkers) against our +11.5. Redrawing the final from those real rounds, our chance of first place is about 3% at that level, 8% with +10 bb/100, 17% with +20 and 29% with +30.
