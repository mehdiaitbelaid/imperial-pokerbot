# v3.2: candidate for the final table

Status, Sun 15 Nov 10:30 UK time: **candidate, tested in simulation, not live.** File: `upload/bot_v32.py` (same as `bots/v32.py`). Riad approves every upload. Live at Table D: V24 (`upload/bot_v24.py`).

## What changed since the v3.0 plan

The organisers confirmed that the final is five blocks of 1,000 hands with a fresh `Agent()` and a fresh 10-second bank per block. So the final is five normal rounds: no time pacing is needed, the end-game rank mode cannot work (the bot forgets the chips), and whatever the bot learns resets every block. Knowing the finalists in advance matters again.

## What v3.2 is

V24 (the bot leading Table D) with three changes:

1. **Fingerprints and seeds for the likely finalists** instead of the Table D teams: Anker Batteries (from today's rounds), Attention Is All In, Gherkers, Equity Engine, Phil AIvey, FisherMen, Astra La Vista, The Market Makers (from their last six Saturday rounds at our tables). `seat_label` recognises a seat from its open sizes and bet sizes; `SEED` preloads, per bet-size bucket, how often its bet folded when raised and how strong the hands it showed were (at most 12 pseudo-observations, so live play corrects it).
2. **4-bet instead of calling against any seat that gives up its 3-bets**: at least 6 cases and 70% folds, seeded per team in `F4SEED` (Attention 46 of 50, FisherMen 55 of 63, Phil AIvey 11 of 12, Anker 25 of 32). The same rule against Anton won 12,800 chips this morning (67 folds in 74).
3. **Bluff-raise a pot-size bet** (0.90 to 1.30 pot) only when that seat's record shows 72% folds over 8 or more cases. Aimed at Anker (20 folds in 23 today).

Recognition on real rounds (`tools/labeltest_final.py`): Gherkers 7 of 7, Equity Engine 6 of 6, Market Makers 7 of 7, Anker 12 of 13, FisherMen 6 of 7, Astra 4 of 6, Phil AIvey 3 of 4, Attention 3 of 6 (the other 3 get the maniac profile, which plays the same exploits). Jump Street is not recognised and has no clear leak.

## Tests in the final's format

Blocks of 1,000 hands, fresh agent each block, same cards and seat for every bot (`tools/bucket_sim.py`, `tools/final_report.py`), 240 blocks per bot:

| Opponents (replicas) | v3.2 | V24 | V22 | v3.2 minus V24 |
|---|---|---|---|---|
| Current leaders: Astra, Attention, Gherkers, Equity Engine, matcha, Jump Street, Anker | +38.2 | +30.9 | +32.1 | **+7.3 ± 2.4** |
| Saturday top seeds: Attention, Gherkers, Market Makers, Equity Engine, Kojack, FisherMen, Anker | +45.2 | +36.3 | | **+8.8 ± 2.6** |

Before v3.2, all our builds were within 3 bb/100 of each other in this format.

## Limits

- The replicas are built from the same Saturday hands as the seeds, so the test shows that the mechanism works, not the size of the real gain. A finalist that changed its bot gives nothing; the live counters then switch the rule off.
- A test against replicas with their folding leaks fixed (`tabled/h_*.py`) is running; result to be added here.
- Fuzzer: 0 illegal replies in 30,000 states.

## Re-run

```
python3 tools/fuzz_mehdi.py upload/bot_v32.py --states 30000
python3 tools/final_seeds.py bots/v24.py hands/saturday_r0*.json hands/sunday_s1_r0*.json
python3 tools/labeltest_final.py bots/v32.py hands/saturday_r0*.json
```
