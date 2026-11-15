# Which finalist profiles can we trust? A drift test from the public standings

Written Sun 15 Nov 2026, about 11:00 UK time, by Claude for Hassan (Resonance Qt). Data: the
public standings only, Saturday (`rankings/standings-history.csv`) and Sunday through bucket
round 23 (`rankings/sunday-bucket-rounds.csv`), both on branch `rankings-history`. Re-run with
`tools/opp_drift.py` (command at the end).

## 1. What this adds to the plan

Riad's plan (chat, 10:40): seed each likely finalist from its Saturday hands, recognise it from a
consistent pattern in the first hands of a block, and play normally if no pattern shows. Mehdi's
concern: teams change their bots, so Saturday patterns should carry little weight.

Both are right, and the standings can say **for which teams**. We cannot see hands from other
tables, but we can see every team's chips every round. If a bot still plays as it did on
Saturday, its Sunday result should match what its Saturday rating predicts against the teams at
its table. A large miss in either direction means it is not the bot we profiled.

**Method.** For each team: expected Sunday bb/100 = its Saturday rating minus the average Saturday
rating of everyone at its Sunday table (a table is zero-sum). Ratings use each team's last 18
Saturday rounds with whale rounds (above +120, the `ediz_slow` tables) removed; without that step
Attention looks like a changed bot when it is not. Residual = actual minus expected; z = residual
over its standard error from the team's own round-to-round spread.

## 2. Results for the likely finalists

| Team | Table | Saturday rating | Sunday actual | Expected | Residual | z | Trust in Saturday profile |
|---|---|---|---|---|---|---|---|
| Astra La Vista | A | −2.7 | +16.3 | −11.3 | +27.6 | **+4.0** | **None: a different bot** |
| Jump Street | C | −2.1 | +13.8 | −3.6 | +17.3 | **+2.1** | **Low: probably changed** |
| matcha mille crêpes cake | C | −4.2 | +5.8 | −5.7 | +11.5 | +1.8 | Medium |
| Equity Engine | B | −0.1 | +4.5 | −2.3 | +6.8 | +1.3 | High |
| JoCal | B | +2.4 | +6.6 | +0.2 | +6.3 | +1.3 | High (only 28 Saturday rounds; no hand profile) |
| Phil AIvey | B | +6.1 | +6.7 | +3.9 | +2.8 | +0.6 | High |
| Attention Is All In | A | +32.9 | +19.6 | +24.3 | −4.7 | −0.8 | High |
| Gherkers | B | +18.4 | +11.2 | +16.2 | −5.0 | −0.8 | High |
| Anker Batteries | D | +26.3 | +19.7 | +27.0 | −7.3 | −1.0 | High (and we have today's hands) |
| FisherMen | C | +30.0 | +17.7 | +28.6 | −10.8 | −1.2 | High |

bb/100. Rule of thumb: |z| under 2, trust; 2 to 3, low weight; over 3, drop.

**Three more signals from the same data:**
- **Style.** Per-round spread fell from 35 to 22 for Phil AIvey and from 37 to 25 for Equity
  Engine: tighter play today, results unchanged. Astra's fell from 40 to 33.
- **Who feeds whom.** Astra and Attention trade chips directly (round results correlate −0.57):
  when one wins, the other loses. Phil AIvey and Equity Engine do the same (−0.43). These pairs
  will both be dangerous to each other in the final, not just to us.
- **Uploads during the morning.** No finalist shows a change point in its Sunday rounds. The
  Market Makers (r6, z +5.1) and Claudebot (r6, z −3.8) did, but neither is in contention.

## 3. What to do with it in v3.2

v3.2 applies each team's Saturday seed at full weight (12 pseudo-observations per bet-size
bucket) as soon as a seat is labelled after 20 hands. Proposed change, about six lines in
`_learn` where the seed is added: scale the seed by a per-team trust factor.

```python
TRUST = {"ASTRA": 0.0, "JUMP": 0.25, "ANTON": 0.25}   # every other label: 1.0
w = TRUST.get(code, 1.0)
# multiply F4SEED[code][0], F4SEED[code][1] and each zo/zf/zn/zs[b] by w before adding
```

- **Astra 0:** if a changed Astra still opens and bets the old sizes, the label fires and the
  seed misleads for the rest of the block. With weight 0 it is learned live like an unknown seat.
- **Jump Street 0.25:** v3.2 has no Jump Street seed today, so this matters only if one is added.
- **Riad's recognition stays as is.** The trust factor only decides how much a recognised label
  is allowed to say before the seat's own record takes over.

## 4. Hedge: do not carry Table D's success into the final

Our Sunday lead was built on weak bots that will not be at the final table. The final build must
not lean on anything learned from them.

| What | Evidence it came from weak bots | Hedge |
|---|---|---|
| Our planning edge | +28.9 bb/100 today, but break-even against Anker, Poke and Chinese people can fly (hand files, rounds 8 to 13) and against Saturday's top ten | Plan the final on an edge of 0 to +10, not +29 |
| The `ANTON` seed and maniac rules (4-bet instead of calling, raise his bets) | Seeded from Anton, who lost all morning. The label fires on any seat that 3-bets 18% or more over 25 chances, so Attention (14%) or FisherMen (13%) can trip it on a loose stretch | Trust 0.25 for the `ANTON` seed; keep the rules only where the seat's own 4-bet record supports them (v3.2 already requires 6 cases and 70% folds for the general 4-bet rule) |
| Re-raising and small-bet raises | +21,294 from re-raising YSL and +3,313 from raising WBot's small bets; but raising small bets lost 11,373 overall, and 6 raises into Anker won none | No change to the code: these fire on each seat's own fold record, so they switch off against solid bots. Do not add seeds that turn them on early |
| Three-street bluffs | −20,530 on 30 hands; the solid players made 14 of 17 calls | Keep V25's third-barrel restraint in mind for solid callers; it tested neutral against replicas (`docs/final-sensitivity.md`) |
| Test fields | Table D replicas flatter every build by about 24 bb/100 | Judge final builds only on the finalist and leaks-fixed line-ups (`tabled/f_*`, `tabled/h_*`) |

A build passes the hedge if it does no worse than V24 on the leaks-fixed finalist line-up. v3.2
does: +4.2 ± 6.2 bb/100 over 40 blocks.

## 5. Limits

- Standings only: a residual can be luck. 23 rounds give a standard error of about 6 bb/100
  per team, so z above 3 is solid, 2 to 3 suggestive.
- Saturday ratings mix opponents of different strength across reseated rounds; the expected
  value is a zero-sum approximation, not a model of each pairing.
- JoCal has no hand-based profile at all; trust here only means its results look consistent.

## 6. Re-run (takes seconds; do it again at about 11:45)

```
git show origin/rankings-history:rankings/standings-history.csv > /tmp/sat.csv
git show origin/rankings-history:rankings/sunday-bucket-rounds.csv > /tmp/sun.csv
python3 tools/opp_drift.py /tmp/sat.csv /tmp/sun.csv
```
