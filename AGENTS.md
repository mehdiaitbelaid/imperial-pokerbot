# Brief for coding agents: Resonance Qt, Imperial AI Hack poker bots

Written Sat 14 Nov 2026, 14:30 UK time, by Claude for Saeed and Mehdi (team **Resonance Qt**). Read this first. Times are UK local.

## 1. The task
Win Track 04 (AI Poker Bots) of Imperial AI Hack. One file, `bot.py`, with a class `Agent`, plays No-Limit Texas Hold'em against other teams' bots. No judges: results decide. Rules page: https://imperialaihack.com/pokerbots (rendered with JavaScript; a plain HTTP fetch returns an empty shell). `README.md` in this repo is the official kit documentation and lists every `state` field.

## 2. Hard constraints (do not break these)
- Python 3.12, **standard library only**, one file under **200 KB**, no network, no file access, 512 MB.
- **10 ms per decision** and a **10 s thinking bank per 1,000-hand round**. The tournament machine is about 2-3x slower than a laptop. Keep worst-case decisions under about 3 ms locally.
- An exception, timeout or illegal action becomes check, else fold. A crash or out-of-memory stops the bot for the round.
- A fresh `Agent()` per table per round: it can learn opponents for 1,000 hands, nothing persists.
- The organisers may switch to pot-limit or fixed-limit or cap raises; read `state["betting"]` and `state["raise_cap"]`.
- Event rules: all code must be written during the hackathon; AI tools are allowed; no collusion with other teams; no attacking the sandbox or site.
- **Never upload a bot yourself.** Uploads go through Saeed or Mehdi on the website. Never commit the team's hand-data token; ask Saeed for it.

## 3. Game and scoring
- 7 or 8 bots per table. Every hand starts each bot on 2,000 chips, blinds 10/20 (100 big blinds), so nobody busts.
- Score is bb/100 (big blinds won per 100 hands) averaged over **every counted hand**. A bad upload drags the whole day's average. Folding every hand is about -19 bb/100.

## 4. Schedule
| When | What |
|---|---|
| Sat 12:35-13:55 | Practice rounds (finished) |
| **Sat 15:00-19:25** | Counted rounds, one every 5 minutes, reseated each round. Need 12 rounds to be ranked. |
| Sat 19:30 | Uploads and teams lock |
| Sat 20:30 | Sunday bucket tables announced (Saturday ranking dealt across tables) |
| Sun 09:00-11:55 | Bucket tables, scored from zero; **top 2 by chips** at each table reach the final. Uploads close 12:00. |
| Sun 12:05 | Final: 8 bots, 5,000 hands, most chips wins |

## 5. Where things are
Repo: private, `mehdiaitbelaid/imperial-pokerbot`.

| Branch | Contents |
|---|---|
| `main` | Starter kit plus Claude's v2 as `bot.py` (obsolete) |
| `v1` (Mehdi) | `versions/v1.py` = Mehdi v1, **the live bot**. `bot.py` = Mehdi v2 (not uploaded). `tools/bench.py`, `tools/analyze_hands.py`, `tools/fuzz_act.py`, `sparring/`, `docs/` |
| `claude-bot` (this branch) | Sandbox and analysis tools, opponent replicas, Claude's bots v1-v5, copies of Mehdi's bots in `bots/mehdi_v1.py` and `bots/mehdi_v2.py` |
| `rankings-history` | Public leaderboard snapshots (`rankings/standings-history.csv`) |

On `claude-bot`:
- `bot.py` and `bots/v5.py`: Claude's v5. **Not live and not recommended** (see section 7). Built from `src/bot_template.py` by `python src/build.py`.
- `src/duel.py`: the sandbox. Each candidate plays the same seat with the same cards against the same line-up, and it prints paired differences with standard errors.
- `src/arena.py`: all bots at one table, bb/100 with standard errors.
- `src/timing.py`: per-decision time distribution of a bot.
- `src/replay.py`: replays real hand files through a candidate and lists where it now acts differently on our big losses.
- `src/analyze.py`, `src/raises.py`: per-opponent stats from hand files, and what opponents showed down behind big bets.
- `sparring/rep_*.py`: replicas of real opponents built from their measured stats (`replica_core.make(vpip, pfr, aggression, fold_to_bet, bluff)`). `sparring_m/`: Mehdi's sparring bots.

Example:
```
python src/duel.py --cands bots/mehdi_v1.py bots/candidate.py \
  --field sparring/rep_claudebot.py sparring/rep_equity.py sparring/rep_gherkers.py \
          sparring/rep_astra.py sparring/rep_jumpstreet.py sparring/rep_joca.py sparring/rep_philaivey.py \
  --rounds 30 --seed 11
```
Hand data: `python fetch_hands.py --token <TOKEN>` saves one JSON per round to `hands/` (git-ignored). Each hand has all actions, the board, results per seat, our hole cards, and opponents' cards only at showdown. The file also names the team in each seat.

## 6. What has happened so far
| Round | Live bot | bb/100 |
|---|---|---|
| Practice 12, 13, 14 | Claude v2 | +109, +37, -62 |
| Practice 15, 16, 17 | Mehdi v1 | +20, +188, +27 |

Practice rank at 14:08: 10th of 32 at +53. Every team shows a few timeouts per round, so they look like platform jitter.

## 7. Current decision: Mehdi v1 stays live for 15:00
Sandbox, duplicate deals, 1,000-hand rounds, bb/100:

| Table | Mehdi v1 | Mehdi v2 | Claude v5 |
|---|---|---|---|
| Realistic mix: 5 solid + 2 fish (14 rounds) | **+140** | +119 | +106 |
| Fish-heavy (8 rounds) | **+245** | +197 to +220 | +183 |
| Solid, no fish (8 rounds) | +94 | **+103** | +75 |
| Mehdi's sparring bots (8 rounds) | +445 | **+472** | +436 |

Paired: v1 minus v2 = +21 +/- 10 (realistic), +48 +/- 14 (fish-heavy), -9 +/- 9 (solid). The opponents are crude replicas and the same bot re-run on the same deals moves by about +/-20, so gaps under 20 bb/100 are noise. Four single-parameter changes to Mehdi v2 (wider maniac classification, longer Monte Carlo, no air-fold rule, looser VPIP prior) made no measurable difference on the fish table.

## 8. What the real hands show (6 practice rounds)
- Most bots play 15-25% of hands. The fish: bigRoddy (-412 bb/100), Joca (-275), Lehman Brothers (-231), FisherMen (-110).
- Profit comes mainly from tables with a maniac (round 16: every solid bot made +130 to +280).
- Teams change bots between rounds (bigRoddy went from 83% to 17% VPIP), so learn within the round; do not hard-code per-team profiles.
- Big postflop re-raises from non-fish bots were 61% two pair or better and 0% air. bigRoddy's big bets were air 45-48% of the time.
- **Leak in the live bot:** calling big bets and raises from tight bots with one pair (TT on a king-high flop against a 1,640 raise; JJ calling three streets on an ace-high board; 22 calling three streets), and calling 2,000 preflop with KTo and TT against tight shovers.

## 9. What to do next
1. Base all work on Mehdi v1 (`versions/v1.py`; its `PARAMETERS` block is the tuning surface).
2. First candidate: tighten calls against big bets and shoves from opponents measured as tight, while keeping the wide calls against maniacs that make v1 strong on fish tables. Mehdi v2 tried this and lost value on fish tables; find which v2 change caused that.
3. Test every candidate with `src/duel.py` over **30 or more rounds** on the realistic table and the fish-heavy table. Recommend an upload only if it beats the live bot by more than 2 standard errors on the realistic table, does not lose on the fish-heavy one, and shows 0 errors and 0 timeouts with a worst decision under 3 ms (`src/timing.py`). Also run Mehdi's `tools/fuzz_act.py`.
4. After each batch of counted rounds, refit `sparring/rep_*.py` from the new hand files (`src/analyze.py`) and replay the biggest losses (`src/replay.py`).
5. Overnight: tune for Sunday, where the target is top 2 by total chips at one mixed table, so extracting the most from the weakest bots matters more than a steady average.

## 10. Lessons already paid for
- House bots in `examples/` are far weaker than the field; scores against them mean nothing.
- One 1,000-hand round swings by roughly +/-60 bb/100 from luck. Never judge a bot on one round.
- Garbage-collection pauses caused multi-millisecond spikes; freeze or disable the collector after building lookup tables.
- No LLM can run inside the bot. AI helps only offline: code, hand analysis, parameter tuning by duel.
