# Team notes

The kit README describes the game and the bot interface. This file covers how we work on our bot.

## Files

`bot.py` is the bot we upload. Snapshots of every version we have uploaded or may compare against live in `versions/` (`v0_starter.py` is the untouched kit starter, `v1.py` is the first build, `v2.py` the current one). Sparring partners are in `sparring/`, each a standalone bot: maniac, allin_spammer, nit, calling_station_plus, minraiser, tag_basic, lag_basic and pot_odds_bot. Strategy research is in `docs/`.

## Parameters

Every number worth tuning is in the PARAMETERS block at the top of `bot.py`: preflop open thresholds by position, raise sizes, 3 bet and calling thresholds, postflop value and raise equity thresholds, bet sizes, bluff frequencies, opponent model priors and the time budget. Hand strength in that block is a percentile, so 0.10 means the best 10% of starting hands. Change one group at a time and benchmark it.

## Running things

Play bot.py against the house bots, with the tournament limits:

    python3 local_sim.py --rounds 20

Check timing against a slower machine than ours. The live sandbox is about twice as slow as a laptop, so this run must show 0 timeouts:

    python3 local_sim.py --timeout 4 --bank 4 --rounds 20

Benchmark against a field. The main field for decisions is `tight`, which looks like the live practice tables (nits, tight aggressive bots, a pot odds bot and one maniac, 6 to 8 seats with `--seats 0`). The others are regression checks: `mixed`, `house`, `stations`, `maniacs`, `nits`, `minraisers`, `tags`, `lags`, `potodds`, `random` and `self` (our own versions).

    python3 tools/bench.py bot.py --field tight --seats 0 --rounds 20

Compare two versions at the same tables. Each seed is played twice with the two bots swapping seats, and the paired difference line is the number to read:

    python3 tools/bench.py bot.py versions/v2.py --field tight --seats 0 --rounds 20

The accept or reject field for pressure changes is `field`: seats of `sparring/field_like.py` plus one maniac and one station. field_like is a model of the live practice field, not the field: its fold rates per spot come from `tools/fold_analysis.py` and are fitted with `tools/calibrate_field.py`. `fieldonly` drops the maniac and station, so heads up spots come up often enough to measure single rules. `tools/rule_accounting.py` counts the bets each named rule in `bot.py` makes and the chips they realise.

Other flags: `--betting pot_limit` or `fixed_limit`, `--raise-cap 3`, `--seed 42` for repeatable tables, `--hands 300` for a quick look, `--jobs N` for parallel tables. Jobs default to a third of the cores and are capped at half, because more parallel tables cause timeouts that are the laptop's fault, not the bot's. The output also shows our VPIP and PFR and flags them when they leave the bands 22 to 35% and 17 to 27%. Every run is appended to `results/bench.csv` with the commit hash, so commit that file with your work and the team builds up one record.

Fuzz the bot with random states, which must report 0 illegal replies:

    python3 tools/fuzz_act.py

Read the live hand histories. Download them with your data token (never commit the token or the hands folder), then summarise:

    python3 fetch_hands.py --token YOUR-DATA-TOKEN
    python3 tools/analyze_hands.py hands/

The analyzer prints each opponent's hands, VPIP, PFR, postflop aggression, fold to bet and the cards they showed, then our result by position and by the street the pot ended on.

## Upload rule

Upload only a version that beats the current live one over 20 rounds on the tight field, with 0 timeouts and 0 errors in that bench, 0 timeouts in the 4 ms local sim, a clean fuzz run, and VPIP and PFR inside the bands. Self play results are a regression check only; a bot that beats our own versions can still lose to the real field. Before uploading, copy the file to `versions/` under the next number.

## Branches

Never work on `main` directly. Make a branch per idea (`git checkout -b tune-steals`), commit small steps, push the branch and open a pull request. Merge into `main` only after the upload rule passes, and only `main` gets uploaded. Do not commit tokens, `.env` files or downloaded hand data.
