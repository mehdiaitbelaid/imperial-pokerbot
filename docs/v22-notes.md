# V22 candidate: notes for the team

Status, Sun 15 Nov 04:15 UK time: **candidate, tested, not live.** The live bot is V21 (`upload/bot_v21.py`, SHA-256 `60320d2a…`). Riad approves every upload.

- File to upload if we go: `upload/bot_v22.py` (same as `bots/v22.py`), 84 KB, stdlib only.
- Built for Sunday's bucket table (Table D). Opponent profiles: `docs/table-d-dossier.md`.

## What V22 adds to V21

1. **Per-seat bet-size learning.** For each seat and each size bucket (under 0.24 pot, 0.24-0.42, 0.42-0.65, 0.65-0.90, 0.90-1.30, 1.30 and more) the bot counts how often the seat folds when that bet is raised and how strong the hands it showed after that size were. The range model then uses the seat's own record for the size it is betting. A size that shows stronger than the model is believed after 3 hands; weaker needs 6 hands and is never applied to pot-size bets.
2. **Seat fingerprints.** The seven Table D teams are recognised from their own open sizes and bet sizes (`seat_label`), then start from that team's Saturday record (`SEED`, at most 12 pseudo-observations, so live play corrects it).
3. **Bluff-raise instead of folding** against a bet of 0.42 to 0.90 pot when that seat's bets of that size have been folding to raises.
4. **3-bet any two cards** against an opener who folded to 3-bets 4 times in 5 over 8 or more cases, with at most three players left behind and no frequent 3-bettor among them.
5. **Against the recognised 3-bet maniac (Anton's profile):** 4-bet the hands we would call his 3-bet with, and raise his bets of 0.42 to 0.90 pot instead of calling.

Switches at the top of the file: `SIZE_LEARN`, `FINGERPRINTS`, `THREEBET_ANY`, `MANIAC_RULES`.

## Evidence so far

Replay of our 52 counted Saturday rounds, V22 against V21 (`tools/sizelearn_eval.py`):

| Change | bb/100 | How sure |
|---|---|---|
| Extra folds to sizes that proved honest | +3.2 | exact: 154 calls we really made, which lost 1,680 big blinds |
| New preflop 3-bets | +2.3 | estimate: each opener's measured fold rate, zero equity otherwise |
| Postflop bluff raises replacing folds | +1.2 | estimate, same method |
| 4-bets against the maniac profile | +0.8 | estimate |
| Extra calls | about -0.6 | rough |

- Against the seven Table D teams, summing each team's rate at its own tables: about +2 exact and +10 estimated. The largest parts are the 3-bets against Chinese people can fly (+5.7) and YSL_TWIZZY (+4.6).
- Fingerprints on real rounds (`tools/labeltest.py`): right label in 58 of 62 seat-rounds, usually between hand 43 and hand 100, and no wrong label among the seven.
- Safety: fuzzer 0 illegal replies in 40,000 states; strict clock 0 timeouts, 0 errors.
- Generic simulated tables, seat-swapped duels against V21: -0.3 ± 5.8 and +10.4 ± 6.1.

## What is not proven

- Most of the gain is an estimate. It assumes these opponents fold tomorrow as they did on Saturday; the live counters switch a rule off when a seat stops folding.
- **The fingerprints are wrong for other tables:** 22% of other teams' seats get a label (Attention Is All In as CPF or ANTON, FisherMen as ANTON, pokermon and kaiserbot as WBOT). For the final, set `FINGERPRINTS = False` and `MANIAC_RULES = False`, or re-target them, and upload before 12:00.
- The simulated Table D below tests the mechanism, not the size of the gain: the replicas copy each team's frequencies and size tells but are weaker than the real bots (V21 wins +55 bb/100 there, while the real WBot beat us).

## Played-out test on a simulated Table D

`tabled/` holds replicas of the seven opponents, calibrated on their real Saturday hands (fold to 3-bet, bet sizes by hand strength, folds when raised, by size; most figures within a few points of the real ones, see `tabled/measure.py`). Same seat and same cards for both builds:

| Comparison | Paired hands | Result, bb/100 |
|---|---|---|
| V22 against V21 | 200,000 | **+9.3 ± 3.0** (V22 +64.5, V21 +55.2) |
| V22 without the any-two 3-bets | 150,000 | -4.9 ± 3.4 |
| V22 without the maniac rules | 150,000 | -4.6 ± 3.6 |
| V22 without fingerprints and maniac rules | 150,000 | -4.4 ± 3.6 |
| V22 without size learning | 150,000 | -4.2 ± 3.6 |

Every part helps and none hurts. To re-run:

```
python3 tools/selfplay.py bots/v22.py tabled/anker.py tabled/cpf.py tabled/wbot.py tabled/gg.py tabled/poke.py tabled/anton.py tabled/ysl.py --vs bots/v21.py --rounds 200 --par 9
```

## How to re-run the checks

```
python3 tools/fuzz_mehdi.py upload/bot_v22.py --states 40000
python3 tools/labeltest.py upload/bot_v22.py hands/saturday_r0*.json
python3 tools/sizelearn_eval.py upload/bot_v21.py upload/bot_v22.py hands/saturday_r0*.json
```

The hand files are not in the repo; fetch them with `fetch_hands.py` and the team token.

## Update, Sun 15 Nov 04:15: live stop on the 4-bet rule, and a "they changed overnight" test

- The 4-bet rule against the maniac profile now stops once that seat has folded fewer than 45% of the 4-bets it faced after 3-betting (new counters `f4_o`, `f4`, seeded with Saturday's 62%).
- Simulated Table D, opponents as on Saturday, 200,000 paired hands: **V22 +11.4 ± 3.1 bb/100 over V21** (the earlier build measured +9.3 ± 3.0).
- Stress test, 200,000 paired hands: four of the seven replicas changed against everything V22 expects (`tabled/x_cpf.py` and `x_ysl.py` defend against 3-bets, `x_cpf.py` and `x_gg.py` swap their bluff and value sizes, `x_anton.py` stops folding to 4-bets and raises) while keeping the same fingerprints. **V22 +0.7 ± 3.5 over V21**: no loss in the worst case we could build. Before the live stop the same test gave -4.0 ± 3.3.
- Fingerprints unchanged: right label in 58 of 62 real seat-rounds, none wrong among the seven.
- New SHA-256 of `upload/bot_v22.py`: see the commit message.
