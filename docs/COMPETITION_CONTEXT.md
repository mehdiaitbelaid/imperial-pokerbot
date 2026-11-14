# Competition context: Imperial AI Hack, AI Poker Bots (Track 04)

Purpose: shared context for research agents combining open-source poker research with the
organisers' own specification. Every fact below comes from the organisers' website
(imperialaihack.com/pokerbots, read Sat 14 Nov 2026 13:05) or from the starter kit code
(`engine/`, `examples/`, `bot.py`, `local_sim.py`, `fetch_hands.py`).

Labels used:
- **[SPEC]** stated by the organisers (website or README).
- **[CODE]** read directly from the starter kit source (file named).
- **[TESTED]** measured by running the kit (method given). Measured on a cloud workspace,
  Python 3.13, NOT tournament hardware (tournament: Python 3.12, one CPU core).
- **[HYPOTHESIS]** an inference for strategy work. Must be tested before relying on it.
- **[OPEN]** unknown; do not assume.

---

## 1. Objective and schedule [SPEC]

- No-Limit Texas Hold'em, 7 or 8 bots per table. Prizes: 1st £500, 2nd £200 (Amazon vouchers),
  plus sponsor items. Sponsors: Optiver, Jump Trading, with AlgoSoc.
- A **round** = 1,000 hands at one table. **Every hand** starts every bot on 2,000 chips
  (100 big blinds), blinds fixed at 10/20. Nobody busts; no tournament/ICM dynamics.
- Score = chips won, reported as **bb/100** (big blinds won per 100 hands) over every hand played.
- Folding every hand loses the blinds: 30 chips / 8 seats = 0.1875 bb per hand
  = **-18.75 bb/100 at 8 seats** (-21.4 at 7). Beating 0 means winning.

| Stage | When (Sat 14 / Sun 15 Nov) | What counts |
|---|---|---|
| Practice rounds | Sat 12:35 to 13:55, every 5 min | Nothing. For finding bugs. |
| Counted rounds | Sat 15:00 to 19:25, every 5 min (54 rounds) | Average bb/100. Everyone reseated each round, so you meet everyone. Need 12 counted rounds to be ranked. |
| Buckets | Sat 20:30 | Saturday ranking dealt across Sunday tables "like cards" (each table mixes strong and weak bots). |
| Bucket tables | Sun 09:00 to 11:55, every 5 min (36 rounds) | Each table scores from zero; **top 2 by chips go to the final**. |
| Uploads close | Sun 12:00 | The bot live at 12:00 plays the final. |
| Final | Sun 12:05 | 8 bots, 5,000 hands, most chips wins. |

- Uploads: a new upload plays from the next round; rounds already played keep their scores.
  Teams (up to 4 people, one team per person) are fixed at Sat 19:30; the site shows uploads
  open "until Sat 19:30". **[OPEN]** whether/when uploads reopen on Sunday morning.
- Hackathon building hours (team constraint, not poker rules): Sat until 21:00, no overnight
  hacking, Sun from 10:00. Sunday bucket tables start at 09:00.
- AI tools are allowed while building. **Colluding with another team or attacking the
  sandbox/site gets a team removed.** Organisers see bot files; nobody else does.

## 2. Hard constraints on the bot

| Constraint | Value | Source |
|---|---|---|
| File | One `bot.py`, class `Agent`, max 200 KB | [SPEC] |
| Language | Python 3.12, **standard library only** (no numpy) | [SPEC] |
| Sandbox | Own container, no network, no files except its own read-only `bot.py`, small `/tmp` wiped every round, 512 MB RAM, 32 processes, **1 CPU core** | [SPEC] README |
| Per decision | **10 ms**, measured from when the dealer sends the state until it receives the reply (transport included) | [SPEC], [CODE] `players.py` |
| Time bank | **10 s per round, and EVERY decision's time is deducted from it**, not only overruns: `self.bank -= min(spent, limit)` | [CODE] `players.py` |
| Bank empty | Every remaining decision in that round is auto-played (check, else fold) | [CODE] `players.py` |
| Load / setup | Module import must finish within 5 s; `Agent()` + `on_table_start` within 5 s | [CODE] `players.py` `setup_timeout=5.0` |
| Background CPU | Using lots of CPU when it isn't your turn stops the bot for the round and flags it. No background threads. | [SPEC] README |
| Memory across rounds | None. A fresh `Agent()` per table per round; state on `self` lasts 1,000 hands with the same opponents. | [SPEC] |
| Betting structure | Organisers **may switch to Pot-Limit or Fixed-Limit, or cap raises per street**. Read `state["betting"]` and `state["raise_cap"]` every decision. | [SPEC] README |

### Derived time budget [TESTED + HYPOTHESIS]

Decisions per bot per round measured with the house bots (method in section 8):
1,523 (tight_aggressive) to 4,484 (calling_station). A selective bot will likely make
roughly 1,500 to 2,500. At 2,500 decisions the 10 s bank allows **4 ms average per decision,
transport included**. Transport for an instant bot averaged 0.14 to 0.16 ms, but single
decisions spiked to 8.6 ms on a loaded machine.
Working budget: about 3 ms of compute per decision, a self-enforced cut-off near 5 ms,
larger spends only for big-pot decisions and only while the bank has room.

## 3. Bot interface

### Methods [SPEC], [CODE] `bot_runner.py`

| Method | When | Required | Failure behaviour [CODE] |
|---|---|---|---|
| `Agent()` + `on_table_start(info)` | once per table | no (on_table_start) | **An exception here marks the bot dead for the whole round** (every decision auto check/fold). |
| `act(state)` | each turn | yes | Exception, bad output or timeout: auto check if legal, else fold. |
| `on_hand_end(summary)` | after every hand | no | Exceptions are silently swallowed. **Its run time is not free**: messages are processed in order, so if the next `act` arrives while `on_hand_end` is still running, that time counts against the 10 ms and the bank. Keep it well under 1 ms. |

### Return values [SPEC], [CODE]

```python
{"action": "fold"} | {"action": "check"} | {"action": "call"}
{"action": "raise", "amount": 200}   # raise TO 200 total this street
{"action": "all_in"}                 # raise to max_raise_to
```
- `bot_runner.normalise` also accepts a plain string (`"fold"`) or a tuple/list
  (`("raise", 200)`). The engine also accepts aliases `bet` and `allin`. [CODE]
- `all_in` never appears in `legal_actions`; it is a raise when raising is allowed, else a call.

Engine handling of mistakes [SPEC], confirmed in [CODE] `game.py`:

| You return | Engine does |
|---|---|
| raise outside `[min_raise_to, max_raise_to]` | clamps to nearest legal amount |
| raise/all_in when raising isn't allowed | call (or check if nothing to call) |
| `call` with nothing to call | check |
| **`check` facing a bet** | **fold** |
| anything else / error / timeout | check if possible, else fold |

Protocol limits [CODE] `players.py`: a reply line over 64 KB, or more than 1,000 queued
lines, is treated as flooding (bot stopped). More than 2,000 unread messages means the bot
stalled (stopped). `print()` is redirected to stderr and cannot corrupt the protocol.

### `state` fields (passed to `act`) [SPEC], [CODE] `game.py`

| Field | Meaning |
|---|---|
| `hole_cards`, `board` | e.g. `["As","Kd"]`; board has 0, 3, 4 or 5 cards |
| `street` | `preflop`, `flop`, `turn`, `river` |
| `seat`, `button` | indices into `stacks`, `bets`, `folded` |
| `stacks` | chips left, **excluding** bets in front of each seat |
| `bets` | chips each seat put in **this street** |
| `folded` | bool per seat |
| `pot` | all chips put in this hand, **including** this street's bets |
| `to_call` | chips to add to call (capped at your stack) |
| `min_raise_to`, `max_raise_to` | legal raise-to range, `None` if you can't raise |
| `legal_actions` | subset of `fold`, `check`, `call`, `raise` |
| `small_blind`, `big_blind`, `blind_level` | 10, 20, always 0 |
| `hand_number` | 1 to 1,000 |
| `betting`, `raise_cap`, `raises_this_street` | structure in force |
| `history` | every action this hand: `{"seat","street","action","amount"}`; `action` in `small_blind, big_blind, fold, check, call, raise`; **raise amount = raise-to total, call amount = chips added** |

`info` (on_table_start) [CODE]: `seat`, `num_players`, `format` ("fixed_hands"), `hands`,
`starting_stack`, `stacks_reset_each_hand`, `small_blind`, `big_blind`, `betting`, `raise_cap`.
**It contains no team names or opponent identities.** [CODE] `FixedHandsTable.play`

`summary` (on_hand_end): `hand_number`, `board`, `shown` (hole cards keyed by seat string),
`winners` (list of `{seat, amount, hand}`), `stacks`, full `history`.
**Every player still in at showdown is shown; nobody can muck.** [CODE] `game.py`

Cards [SPEC]: rank then suit, ranks `23456789TJQKA`, suits `cdhs`.

## 4. Engine mechanics [CODE] `engine/game.py`

- **Tournament format** = `FixedHandsTable`: stacks reset to 2,000 before every hand; the
  button starts at a random seat and moves one seat per hand, so each seat holds each position
  about 125 times per round.
- **Action order**: SB = seat after button, BB = next. Preflop first to act = seat after BB.
  Postflop first to act = first live seat after the button.
- **Min raise**: `min_raise_to = current_bet + min_inc`; `min_inc` starts at 1 BB and becomes the
  size of the last full raise. A short all-in (less than a full raise) does not reopen raising
  for players who already acted.
- **Max raise**: No-Limit = your stack; Pot-Limit = `current + pot + to_call` (pot after
  calling); Fixed-Limit = one step (1 BB preflop/flop, 2 BB turn/river), cap 4 unless set.
- Raising also requires at least one other player who can still act.
- Uncalled bets are refunded. Side pots are built by contribution level; odd chips go to the
  first winner left of the button.
- **Deal determinism [TESTED]**: in `FixedHandsTable` the RNG only drives the button and the
  shuffles, so the same seed gives identical hole cards, boards and button per seat regardless
  of which bots play or what they do (checked: 200/200 hands identical across two different
  bot line-ups). This enables "duplicate" testing: replay the same seed with bots rotated
  through every seat to cancel card luck. The tournament itself uses unpredictable shuffles
  (`random.SystemRandom()`, per the `SitAndGo` docstring); do not try to predict cards.
- `SitAndGo`, rising blinds and `icm.py` are a legacy format. **Not used in this tournament.**

## 5. Hand evaluator [CODE] `engine/cards.py`, [TESTED]

- Cards as ints 0 to 51: `rank_index * 4 + suit_index`. `evaluate(cards)` scores the best
  5-card hand from 5 to 7 cards as a comparable tuple (higher wins).
- Speed: **4.07 microseconds per 7-card hand** (20,000 random hands, Python 3.13, this
  workspace). Expect slower on the tournament's single 3.12 core.
- The sandbox contains only `bot.py`, so any evaluator **must be copied into bot.py**; the
  bot cannot import `engine`.
- Implication: in a 3 ms budget, roughly 150 to 250 Monte Carlo run-outs against 2 opponents,
  i.e. equity standard error about 0.035. A faster evaluator (lookup tables built at import,
  within the 5 s load limit) directly buys accuracy.

## 6. The example bots, in detail

The organisers' house bots fill empty seats in `local_sim.py`. Many teams' bots are likely
derived from these files or from the starter `bot.py`, so their behaviour patterns are worth
recognising in the live field. **[HYPOTHESIS]**

Measured results [TESTED]: 8 seats, two copies of each of the four bots below, seats
shuffled each round, 4 rounds of 1,000 hands (8,000 hands per bot type), real subprocess
players with tournament time limits. Four rounds is a small sample; signs and magnitudes are
reliable, decimals are not.

| Bot | bb/100 | Decisions per round | Avg / max latency |
|---|---|---|---|
| starter `bot.py` | **+988.8** | 2,237 | 0.152 / 4.26 ms |
| `tight_aggressive.py` | +232.3 | 1,523 | 0.158 / 2.33 ms |
| `calling_station.py` | -265.6 | 4,484 | 0.140 / 5.44 ms |
| `random_bot.py` | -955.5 | 2,514 | 0.149 / 8.59 ms |

### 6.1 `examples/calling_station.py`
- Behaviour: checks if possible, otherwise calls. Never folds, never raises. Sees every
  showdown it reaches with any two cards.
- Exploit: never bluff; value bet thin and large. Against a pure caller, betting B with equity
  e against its (random) holding changes EV by B(2e - 1), so with e > 0.5 larger is strictly
  better, up to all-in. Multiway pots need equity against all callers.

### 6.2 `examples/random_bot.py`
- Behaviour: uniform choice over `legal_actions`. Facing a bet with raising allowed:
  fold/call/raise each 1/3 **regardless of bet size**; if raising isn't allowed: fold/call 1/2.
  With nothing to call: check/raise 1/2. Raise size uniform in `[min_raise_to, 3 * min_raise_to]`
  (capped at max).
- Exploit: value bets get called or raised 2/3 of the time at any size, so size up with strong
  hands. A bluff of size B into pot P wins P with probability 1/3 and loses at least B
  otherwise, so it is profitable only if B < P/2. Its raises carry no information: call down
  with medium-strength made hands.

### 6.3 `examples/tight_aggressive.py`
- Preflop strength: pairs `0.5 + r/24`; non-pairs `(r1+r2)/24 + 0.06 if suited - 0.04 if gap > 4`
  (rank index 0 = deuce, 12 = ace). Exact ranges [TESTED by enumerating all 1,326 combos]:
  - **Raise or re-raise (s >= 0.8), 11.0% of hands**: TT+, ATo+, KJo+, A9s+, K9s+, QTs+.
    Size: `min_raise_to + 2 BB`. It re-raises again every time it can, so two strong hands
    escalate until one raise reaches the maximum.
  - **Call only if `to_call <= 3 BB` (0.62 <= s < 0.8), 21.6%**: 55 to 99 plus many broadway
    and suited-ace/king hands (full list: 55 66 77 88 99 T8s T9s T9o J7s J8s J8o J9s J9o JTs
    JTo Q7s Q8s Q8o Q9s Q9o QTo QJo K6s K7s K7o K8s K8o K9o KTo A5s A6s A6o A7s A7o A8s A8o A9o).
  - Everything else: check or fold.
- Postflop: "pair or better" = a hole card's rank appears at least twice in hole + board
  (pocket pair, or pairing the board). With it: bet `min_raise_to + pot//2` if unbet, else call
  any bet (never raises facing a bet, never folds). Without it: check, or fold to any bet.
  It never bluffs.
- **Bug: it folds even AA to a 100 BB all-in.** If an opponent shoves the full stack,
  raising becomes illegal (`max_raise_to` would not exceed the current bet); the code then
  only calls when `to_call <= 3 BB`, so it folds. [TESTED] An always-shove bot against seven
  copies won **+378.0 bb/100 over 5,000 hands**; the copies faced 22,464 shove decisions,
  never called, and folded QQ/KK/AA 418 times.
- Exploits: (a) its postflop check means no pair, so it folds to any bet: small bets win
  those pots; (b) its postflop bet or call means pair or better; (c) a full shove preflop
  wins the pot unless it can still re-raise; (d) its preflop raise range is 11.0% and known.

### 6.4 Starter `bot.py`
- "Strong" = pocket pair or top card J or better, from hole cards only: **56.6% of hands**
  [TESTED by enumeration]. It **ignores the board completely**.
- If strong and raising is legal: raise to `min_raise_to + pot//2`, **on every street, every
  time it acts**, so pots escalate quickly. Otherwise: check if possible; call if
  `to_call <= 2 BB` or strong; else fold.
- Why it won +988.8 in the house-bot test: relentless aggression with an above-average range
  extracts huge pots from the station and random bots.
- Exploits: its raises carry little information (56.6% range, board-blind), so call down and
  re-raise with made hands; never bluff it when it holds a "strong" hand (it never folds those);
  it folds non-strong hands to bets above 2 BB.

## 7. Tools in the kit [CODE]

### `local_sim.py`
- Runs your bots plus random picks from the three house bots (`tight_aggressive`,
  `calling_station`, `random_bot`) to fill 8 seats, shuffles seats each round, plays
  `FixedHandsTable` rounds with real subprocess players and tournament limits
  (`--timeout 10`, `--bank 10`).
- Options: `--rounds`, `--hands`, `--seed`, `--betting no_limit|pot_limit|fixed_limit`,
  `--raise-cap`, `--show-prints`.
- Limits: each file can be named once (copy a file to seat two copies); only the first error
  per bot is printed; no duplicate/seat-rotation mode; random house fill adds variance. For
  version comparisons, call `FixedHandsTable` directly with fixed seeds and rotated seating
  (see section 4).
- Output columns: chips, bb/100, timeouts, errors, bank out, think s/rd (worst round's total
  thinking time; must stay well under 10 s).

### `fetch_hands.py`
- `python fetch_hands.py --token TOKEN` (token from the site, under "Your table's data").
  **Never commit the token.**
- Calls `GET /api/poker/results` (list of rounds with `ref`, `chips`) then
  `GET /api/poker/hands?ref=...`; saves `hands/<ref>.json` with `hands` and `round`.
- Per hand: every action at the table, board, every seat's chip result (`results`), your own
  cards, opponents' cards only when they reached showdown.
- Event format: `["post", seat, amount]`, `["act", seat, action, amount]` (call = chips added,
  raise = raise-to total), `["board", street, cards]`, `["refund", seat, amount]`,
  `["win", seat, amount, hand_name or null]`.
- **[OPEN]** whether the downloaded data maps seats to team names. Check the keys of `round`
  and of each hand on the first download. Even if it does, the bot itself never learns names.

## 8. Field evidence [SPEC], snapshot

Practice standings at Sat 13:05 (practice round 6 of 17; practice does not count), 13 teams:
best +195.4, then +87.6, +83.1, +77.9, +77.3, +62.4, +47.0, +23.0, -26.7, -35.2, -60.8,
-143.6, worst -194.3 bb/100, on 1,000 to 6,000 hands each.
[HYPOTHESIS] Losses near 2 BB per hand indicate badly exploitable bots (spewing or calling
everything). The practice leader's +195 is far below the starter bot's +989 against house bots,
so the live field is much tougher than the house bots: never judge a version by its score
against house bots alone.

## 9. Strategy implications of these findings [HYPOTHESIS]

1. **The bot learns opponents only within a round.** No names, no memory across rounds, so
   classification must converge within the first 50 to 150 hands from frequencies (VPIP, PFR,
   aggression, fold-to-bet, showdown hands). Offline data can only set priors and thresholds.
   Possible extension: behavioural fingerprints (e.g. exact raise-size formulas such as
   `min_raise_to + pot//2` or `min_raise_to + 2 BB`) to recognise known bot families quickly.
2. **Showdowns are fully revealed**, so the opponent model can learn what each line means
   (bet with pair+, raise with any J-high, etc.) directly from `summary["shown"]`.
3. **Value over bluff in soft fields**: stations and random bots pay off; bluffs only work
   against opponents measured to fold.
4. **All-in handling bugs are a field-wide risk**: bots copying the tight_aggressive pattern
   fold to full shoves. Track fold-to-shove per opponent; consider cheap probes.
5. **Board-blind raisers** (starter-bot pattern) make raises nearly meaningless as information.
6. **Compute is the binding constraint**: precomputed preflop tables, a fast evaluator, small
   Monte Carlo, and extra time only in big pots.
7. **Structure may change**: size every bet through `min_raise_to`/`max_raise_to`; test with
   `--betting pot_limit`, `--betting fixed_limit`, `--raise-cap 3`.
8. **Evaluate with duplicate seeding** and seat rotation; a candidate should beat the current
   live version by more than 2 standard errors before upload.

## 10. Combining with open-source research

Filter every open-source approach through these questions before recommending it:
1. Does it run in pure Python 3.12 standard library (no numpy, no compiled extensions)?
2. Does everything shipped (code + tables + weights) fit in 200 KB, or can it be rebuilt at
   import in under 5 s and under 512 MB?
3. Does a decision cost about 3 ms or less (4 ms average budget including transport)?
4. Does it work for 7 to 8 players, No-Limit, 100 BB deep, and degrade gracefully under
   Pot-Limit, Fixed-Limit or raise caps?
5. Does it adapt within 1,000 hands with no opponent names?
6. Is the licence compatible with submitting the code to the organisers?

Feasibility guide [HYPOTHESIS, to verify per source]:

| Approach family | Likely verdict | Reason |
|---|---|---|
| Preflop equity tables / charts (169 hand classes x opponent counts) | Feasible | Tiny table; zero runtime cost. The repo's `tools/` holds a preflop equity table. |
| Monte Carlo equity with a pure-Python evaluator | Feasible | About 150 to 250 run-outs in 3 ms (section 5). |
| Lookup-table evaluators built at import (Cactus Kev style, pure-Python ports) | Feasible if import stays under 5 s | Faster equity = more accuracy per ms. |
| Very large precomputed evaluator tables (hundreds of MB) | Not feasible | 200 KB file, 5 s load, 512 MB RAM. |
| Equilibrium / CFR blueprints and real-time search for multiplayer NLHE | Not feasible | Compute, table size and per-decision time. Ideas (bet abstraction, sizing sets) may still transfer. |
| Neural network policies | Only tiny pure-Python nets | No numpy; weights must fit 200 KB; inference well under 1 ms. |
| Opponent modelling: frequency stats, weighted hand ranges, effective hand strength / hand potential, Bayesian archetypes | Feasible, core | Cheap counters plus range-weighted equity. |
| Offline self-play / RL to tune parameters | Feasible offline | The result must compress to rules or small tables. |
| LLM calls at runtime | Not feasible | No network in the sandbox. |

Questions the research should answer for this competition:
- Best-practice opening, calling and 3-bet ranges by position at 8-handed 100 BB, and how to
  widen or tighten them against measured opponent types.
- Range-weighted equity methods that run in 1 to 3 ms in pure Python.
- How quickly frequency-based opponent classification becomes reliable, and robust priors.
- Optimal value-bet sizing given an estimated call probability per bet size.
- Proven exploits of rule-based bots (calling stations, maniacs, nits, random players).

## 11. Open items [OPEN]

- **Repo layout not decided.** Option A: modules in `src/` combined into `bot.py` by a build
  script (fewer merge conflicts, testable modules). Option B: one `bot.py` with clearly owned
  sections. Either way the uploaded artefact is a single standard-library `bot.py` under 200 KB.
- Contents and format of the repo's `tools/` preflop equity table (not reviewed for this file).
- Whether uploads reopen before Sunday 09:00, and whether bucket dealing is straight or snake.
- Whether downloaded hand data maps seats to team names.
- Whether house bots ever fill seats in the live tournament (the site says 7 or 8 bots per table).
