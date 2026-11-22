# Final bot report: findings and improvements for future versions

Imperial AI Hack, AI Poker Bots. Written Sat 14 Nov 2026, about 15:30, after building
`bot_final.py` (vastra-fable + quant EV layer). Read `docs/COMPETITION_CONTEXT.md` first
for the rules, API and engine facts; this file covers what we learned building and
testing the bots, and what to do next.

Labels: **[MEASURED]** run by us, method stated. **[CODE]** read from source.
**[DATA]** from Mehdi's 6,000 live practice hands (`docs/pressure-playbook.md`).
**[HYPOTHESIS]** reasoning not yet tested.

---

## 1. Where everything is

| Item | Location | Notes |
|---|---|---|
| Starter kit, preflop table | `main` @ a76fb6d | |
| Saeed's v2 (equity + opponent model) | `main` @ 983c5b2, `bot.py` | first live v2 |
| v3 = Saeed v2 + all-in calling fix | sent in chat (not committed) | |
| Mehdi v1, v2, vastra-fable | branch `v1` (tag `vastra-fable` @ 486a6b4), `versions/` | plus docs, sparring bots, tools |
| Another Claude session's bots and real-team replicas | branch `claude-bot` | `sparring/rep_*.py`; not used in our tests |
| **Final bot** | `bot_final.py` (sent in chat) | vastra-fable + quant layer, 66 KB |
| High-power paired tester | `ab_vf.py` (sent in chat) | common random numbers + all-in adjustment |
| Team release tools | branch `v1`: `tools/bench.py`, `tools/fuzz_act.py`, `tools/fold_analysis.py`, `tools/analyze_hands.py` | |

## 2. How to measure a change (most important lesson)

| Method | Noise (SE of the difference) | Source |
|---|---|---|
| One 1,000-hand round | about ±170 bb/100 for one bot | [MEASURED] |
| `tools/bench.py`, 16 seeds mirrored (32 tables) | ±15 to ±27 bb/100 | [MEASURED] |
| Same cards for both bots (paired) | 2.5 times less variance than unpaired | [MEASURED] |
| All-in luck adjustment (score all-in pots at equity) | 6 times less variance on all-in heavy tables | [MEASURED] |
| **`ab_vf.py`: paired + every bot's RNG reseeded from the game state before each decision (common random numbers) + all-in adjustment, 100 tables** | **±2.2 to ±2.7 bb/100** | [MEASURED] |

Consequences:
- The practice and counted leaderboards after a few rounds are mostly luck.
- `bench.py` can only detect changes of about 50 bb/100 or more. Every remaining improvement
  is smaller than that, so **use `ab_vf.py` as the release gate** (about 2 minutes per field on
  2 cores), plus the team's behaviour bands, fuzz and slow-sandbox checks.
- A test against bots that were calibrated from the same data the change exploits
  (`field_like` and the playbook) checks that the logic works; it does not prove the live gain.

## 3. Version results

All [MEASURED] with tournament time limits unless noted.

| Comparison | Field | Difference (bb/100) |
|---|---|---|
| v3 minus Saeed v2 | maniac + 6 tight house bots | +163 (all-in fix) |
| v3 minus Saeed v2 | 8,000 paired hands, mixed house field | +142, SE 46.5 |
| **vastra-fable minus v3** | `field` bench, 16 seeds | **+218, SE 26.9** |
| vastra-fable minus v3 | `tight` bench, 16 seeds | +27, SE 18 |
| final minus vastra-fable | `field`, ab_vf 100 tables | +1.8, SE 2.3 |
| final minus vastra-fable | `tight`, ab_vf 100 tables | +2.6, SE 2.7 |
| final minus vastra-fable | `house` bench | +82, SE 22 |
| final minus vastra-fable | `maniacs` bench | +188, SE 104 |
| final minus vastra-fable | `stations` bench | +33, SE 26 |

Final bot checks: 0 exceptions in about 42,000 fuzzed decisions (exceptions surfaced, all
betting structures, 6 to 8 seats); team fuzzer 0 illegal replies in 25,277 decisions, in-process
median 0.91 ms, max 2.9 ms; 0 timeouts at 4 ms / 4 s bank (slow sandbox rule); VPIP 27.4%,
PFR 23.0% on `field` (inside the 22 to 35% / 17 to 27% bands).

## 4. Findings in the code

### 4.1 Engine and house bots [CODE] [MEASURED]
- Every decision is charged to the 10 s bank, not just slow ones; `on_hand_end` time delays the
  next decision and counts against it.
- The bot never learns team names (seat numbers only); nothing carries over between rounds.
- `tight_aggressive.py` folds even AA to a full 100 bb shove (it can only re-raise, and a
  full shove leaves no raise). Bots copied from it share the bug. The live field, however,
  calls shoves: responders fold 0.88 to open shoves against a 0.98 break-even [DATA], so
  shove-bluffing is not worth exploiting.
- The starter `bot.py` raises 56.6% of hands on every street, ignoring the board.

### 4.2 Saeed's v2 (main) [CODE] [MEASURED]
- Strong engineering: prime-product 7-card lookup evaluator (0 disagreements with the engine
  over 100,000 comparisons), Bayesian-smoothed stats, 0.23 s import.
- Leak: the preflop call margin added 2 points per player still to act, so it called shoves
  with only about the top 6% of hands. v3 fixed this (+163 against a maniac table).
- Other issues: blocked opponent hands counted as losses in the equity loop; time budget
  started after range building; post-flop margin of 3 points per player still to act;
  opens wider against loose tables (the wrong direction).

### 4.3 Mehdi's vastra-fable [CODE]
- Already avoids all of the issues in 4.2: rejection sampling with the clock checked on
  attempts, deadline measured from the start of `act`, all-in margin 0.03 + 0.015 per player
  behind, a range-aware fallback when the Monte Carlo runs out of time.
- Robust safety net (`_legalise`), garbage collection frozen during play, a warm-up at import,
  opponent types (spammer, maniac, station, nit, minraiser), shove ranges from showdowns,
  priors calibrated to the live field.
- **Uses about 0.8 s of the 10 s bank per round** (`ROUND_TARGET = 1.3`, `MC_MAX = 0.9 ms`).
  That is deliberately safe for a sandbox assumed twice as slow, but it leaves most of the
  thinking time unused.

### 4.4 The quant layer added in the final bot [CODE] [MEASURED]
- Fold model: field fold rate per spot, shifted per seat in log odds by that seat's fold-to-bet
  rate, shrunk toward the seat's own record in the spot (beta-binomial, playbook pseudo counts).
- Bet rule: bet iff EV(bet) minus EV(check) > 2% of the pot, where
  `d = f + (1 - f - r)(ec(1 + 2s) - s) - r s - kappa * eq`; kappa is equity realisation by hand class
  (air 0.40, draw 0.60, weak pair 0.75, top pair 0.85; 1.0 when checking ends the river).
- First version used kappa = 0.85 for every hand. That cut c-bets from about 65% to 7%, so
  realisation by hand class is essential. When the engine evaluates a hand it nearly always bets
  (average d: air +0.19, draws +0.27, top pair +0.33 pot shares).
- Net effect is about +2 bb/100 on realistic fields. The spots are rare at 6 to 8 handed tables,
  and vastra-fable's old heuristics already c-bet often.

### 4.5 Live field facts that should drive future tuning [DATA]
- Profitable pressure (fold-through vs break-even): turn stab after the flop bettor checks
  0.67 vs 0.44; flop stab after the raiser checks 0.74 vs 0.45; river after the turn checks through
  0.62 vs 0.46; heads-up flop c-bet 0.53 vs 0.35; small blind steal at 2.5 bb or less 0.86 vs 0.57.
- Losing pressure: turn barrels (0.32), leads into the aggressor (0.29), 3-bets in general
  (0.44 vs 0.66), 4-bet bluffs (0.05), any bluff raise, shoves into pots over 10 bb.
- Big turn and river bets are value: monster 0.41, top pair 0.26, weak pair 0.17, draw 0.07, air 0.10.
- Opponents call big bets loosely (weak pair or air 0.44 of the time), so thin value pays.
- The field adapts: in another student tournament, 3-bet rates rose from 6.9% to 12.3% over six
  rounds. Recheck the field on Sunday morning.

## 5. Improvements for future versions, ranked

Each needs an `ab_vf.py` result above 2 SE with no field getting worse, plus the team gates.

| # | Change | Why | Expected size | Risk |
|---|---|---|---|---|
| 1 | **Recalibrate priors and SPOT rates from counted-round hands** (`fetch_hands`, then `tools/fold_analysis.py`) | Current numbers come from practice rounds, which run weaker experimental bots; counted rounds differ | Unknown, possibly largest | Low |
| 2 | **Spend more of the bank on big pots**: raise `MC_COMMIT` and the time on commitment decisions while the round total stays under about 4 s | Most chips are won or lost in stack-off spots; we use about 8% of the bank | Small to medium | Low, if the 4 ms slow-sandbox check stays at 0 timeouts |
| 3 | **EV-based value betting and raising**: equity against the calling range, size chosen from per-seat call rates by size | Value bets still use fixed equity thresholds; the field calls loosely, so thinner, bigger value bets should pay | Medium | Medium |
| 4 | **Per-opponent action models from showdowns**: learn P(action given hand class) per seat to replace fixed range weights (`BIG_BET_W` and others) | Showdowns reveal every live hand; weights are field averages | Medium vs outliers | Medium |
| 5 | **3-bet bluffs only against measured over-folders** (opener's shrunk fold to 3-bet of 0.75 or more after 8 observations; e.g. WBot 0.72, Attention 0.77 [DATA]) | Playbook estimates about +1.2 bb/100 | Small | Low with the stop rule |
| 6 | **Precomputed preflop equity against range width** (169 classes x widths x 1 to 3 opponents, about 60 KB) | Removes Monte Carlo noise and the heuristic `quick_equity` fallback preflop | Small | Low; file stays under 200 KB |
| 7 | **Exact river equity** by enumerating opponent hands with weights | Zero-noise decisions in the biggest pots | Small | Low |
| 8 | **Test against the `claude-bot` branch replicas of real teams** (`sparring/rep_*.py`) | Gives a second field model not built from the playbook | Better evidence | None |
| 9 | Bot fingerprinting (exact raise-size formulas) to recognise known opponents within a round | No names are given; a fast read beats waiting for stats | Unclear | High; keep out of the final-table bot |
| 10 | Final-table choice: upload the most robust tested version by Sunday 12:00 | 5,000 hands is about ±147 bb/100 of luck; avoid untested changes | n/a | n/a |

What not to do, on current evidence: shove-bluffing (fold 0.88 vs 0.98 needed), widening
button and cutoff steals as pure bluffs, bluff raises on any street, turn barrels with air,
judging changes by one round or by self-play alone.

## 6. Open questions
- Whether uploads reopen before Sunday 09:00 (bucket tables start then; team building starts 10:00).
- Whether counted-round fold rates match practice rates (item 1).
- Whether the downloaded hand data maps seats to team names (helps offline analysis only).
