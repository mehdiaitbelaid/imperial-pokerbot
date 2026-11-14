# V22 candidate: notes for the team

Status, Sat 14 Nov 22:05 UK time: **candidate, not live.** The live bot is V21 (`upload/bot_v21.py`, SHA-256 `60320d2a…`). Riad approves every upload.

- File to upload if we go: `upload/bot_v22.py` (same as `bots/v22.py`), about 82 KB, stdlib only.
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
- A played-out test on a simulated Table D (replicas of the seven, in `tabled/`) is still running.

## How to re-run the checks

```
python3 tools/fuzz_mehdi.py upload/bot_v22.py --states 40000
python3 tools/labeltest.py upload/bot_v22.py hands/saturday_r0*.json
python3 tools/sizelearn_eval.py upload/bot_v21.py upload/bot_v22.py hands/saturday_r0*.json
```

The hand files are not in the repo; fetch them with `fetch_hands.py` and the team token.
