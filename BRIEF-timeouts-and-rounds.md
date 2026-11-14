# Brief for the next agent: timeouts, bot ranking and what went wrong (Resonance Qt)

Written Sat 14 Nov 2026, 15:30 UK time, by Claude for Saeed, Mehdi and Riyad. It follows `AGENTS.md` on the `claude-bot` branch, which still holds the hard constraints (stdlib only, 10 ms per decision, 10 s bank per round, 200 KB, never upload yourself, never commit the data token).

Branch for this work: **`claude-timeouts`** (cut from Riyad's `fable-bot` at `874bb54`).

## 1. Bottom line

1. **Upload candidate: `upload/bot.py` on this branch (Avengers v14 with a CPU cap, called av14f below).** SHA-256 starts `ec92d4936d8f`, size 67,124 bytes. It plays the same as Avengers v14 (paired difference +2.8 ± 5.7 bb/100). Its compute is halved: p95 0.47 ms in-process, against 0.93 ms for v14, 0.92 ms for Mehdi v3 and 2.24 ms for Mehdi v1. The fuzz test gives 0 illegal replies.
2. The timeout problem was mostly in **rounds 1–3**: about 18 timeouts, roughly 6 per round. **Rounds 4–6 had only 4 timeouts, about 1.3 per round,** against a field median of about 5 per round. Upload v6 already fixed most of it. av14f cuts the remaining tail roughly in half.
3. **Avengers is the strongest bot we have on every table tested** (section 4). Vastra-fable and Mehdi v3 are level with Mehdi v1 at best, and well behind Avengers on any table containing a starter-kit bot.
4. **Not done yet: real hand analysis.** We never got the team data token, so per-hand analysis of the counted rounds (which decisions timed out, where the chips went) is still open. Section 6 gives the exact procedure. It is task 1 for the next agent.

## 2. Live results so far (public API, no token needed)

Source: `https://poker.imperialaihack.com/pokerbots/api/public` (JSON, polled by the site; fetch it from a browser tab on imperialaihack.com, because the cloud sandbox proxy blocks this domain). Per-round values below are differences between cumulative snapshots: chips = bb/100 × hands / 100 × 20.

| Rounds | Our upload | bb/100 in those rounds | Our cumulative timeouts | Note |
|---|---|---|---|---|
| R1–R2 (15:00, 15:05) | v5 | −13.4 avg | ? | 24th after R2 |
| R3 (15:10) | v5 or v6 | +37 | 18 after R3 | v6 was showing by 15:11 |
| R4–R5 | v6 | +50.6 avg | 21 after R5 | |
| R6 (15:25) | v6 | +75.7 | 22 after R6 | **6th of 39 at +31.2** |

Field after 6 rounds: Gherkers +86 (48 timeouts), Attention Is All In +74 (24 timeouts), AAST +48, matcha +44 (79 timeouts), Equity Engine +43. The median team has 30 timeouts after 6 rounds; we have 22.

**The field changed between practice and counted rounds.** The practice fish were fixed: FisherMen went from −110 to about −19, Lehman Brothers from −231 to +32, Joca from −275 to −24 and bigRoddy from −412 to −21. The only big loser left is ediz_slow (about −300). Our practice profit came mostly from those fish, and the `sparring/rep_*` replicas on `claude-bot` are fitted to the practice versions. Treat the solid-field results in section 4 as the main guide.

**Unknown, ask the team:** which file is v5 and which is v6? Compare the SHA-256 on the site's "Your Bot" panel with these:

| File | SHA-256 prefix |
|---|---|
| Avengers v13 (`bot__1_.py`) | `bac03ed0e3d4` |
| Avengers v14 (`fable-bot` `upload/bot.py`) | `70f64660654b` |
| av14f (this branch) | `ec92d4936d8f` |
| Mehdi v1 | `4b74d1acbae0` |
| Mehdi v3 | `f58760c2dc89` |
| vastra-fable (Saeed's file, `bot_vastra-fable.py`) | `e0f6383ec88a` |

If v5 was Mehdi v1, that alone explains the early timeouts (section 3).

## 3. Timeouts: mechanism, measurement, fix

**How the dealer counts time** (`engine/players.py`, the same engine the tournament runs):
- The clock starts before the dealer serialises the `act` message. It stops when the reply line is read.
- So it includes the pipe, the runner's `json.loads` of the state, `Agent.act`, and the reply.
- `hand_end` is sent fire-and-forget with no reply. Any `on_hand_end` work still running when the next `act` arrives also counts against that decision.
- A timeout plays check, else fold.

**Why compute matters more than the average suggests.** On a shared box, a bot that needs more than one scheduler slice of CPU gets pre-empted and waits for the other processes, so a 1–2 ms decision can show up as 7–12 ms at the dealer. These are the Monte Carlo decisions: postflop, chips in the pot, often a strong hand. A timeout there means folding, which makes them the most expensive decisions to lose.

**Emulating a slow, shared server:** run the whole table pinned to one core, alongside two busy-loop processes. That gives each bot about a third of a core, roughly the 2–3× slowdown we expect. The tool is `tools/latency.py`. It records dealer-side latency with a 500 ms limit, so the tail is measured rather than turned into timeouts. Same table, 8 seats, 3 rounds:

```
taskset -c 0 python3 -c "while 1: pass" &  taskset -c 0 python3 -c "while 1: pass" &
taskset -c 0 python3 tools/latency.py --rounds 3 upload/bot.py <other bots...> ; pkill -f "while 1: pass"
```

| Bot | CPU p95 / max, in-process, uncontended (ms) | Dealer >5 ms (3 rounds, contended) | Dealer >10 ms |
|---|---|---|---|
| Mehdi v1 | 2.24 / 3.61 | 372 | **106** |
| Mehdi v3 | 0.92 / 0.99 | 174–192 | 11–13 |
| Avengers v13 | 0.94 / 1.63 | 127–144 | 2–4 |
| Avengers v14 | 0.93 / 1.46 | 121–141 | 3–7 |
| **av14f (this branch)** | **0.47 / 0.72** | **63** | 2 |
| vastra-fable r3 | 0.32 / 1.87 | 40–57 | 0–2 |
| starter kit (floor) | ~0 | 38–62 | 0 |

The ">5 ms" column is the useful proxy for timeout exposure. The ">10 ms" counts are small and noisy here. The real server is harsher than this emulation: starter-kit bots still get about 1 timeout per round there.

**Root cause in Avengers:**
- `_budget()` starts from 8 s ÷ (hands left × 0.45), which is about 17 ms, so it always hit its 1.6 ms cap. Every postflop decision ran 1.6 ms of Monte Carlo.
- Before that, `_tier()` builds and sorts up to 200 combos per opponent with no time limit.
- The Monte Carlo loop also ran at least 23 iterations, checking the clock only every 8.

**The fix (3 lines in `src/avengers.py`, rebuilt into `upload/bot.py`):**

```
_budget cap      0.3–1.6 ms   ->  0.2–0.45 ms
MC clock check   every 8, min 23 iterations  ->  every 4, min 15
_tier combo cap  200 / 130 / 90 (1–2 / 3 / 4+ opps)  ->  120 / 90 / 60
```

Strategic cost on a duplicate-deal duel against Avengers v14 (30 rounds): +2.8 ± 5.7 bb/100, so none measurable. Thinking time per round dropped from 0.51 s to 0.33 s.

**Further latency work, if still needed after the real data:**
1. Skip Monte Carlo when the pot is under 6 bb and nobody has bet; use the made-hand category instead. Mehdi's vastra r3 does this.
2. Start from the time already spent: read `time.perf_counter() - t0` before building tiers, and skip Monte Carlo if over 1 ms.
3. Move the `gc.collect(0)` every 64 hands out of `on_hand_end`, or drop it. It is unacknowledged work that can delay the next act.
4. Cache `_tier` results per seat per street, since the board does not change within a street.

## 4. Bot comparison (sandbox, duplicate deals)

All 1,000-hand rounds, 6 opponents, the same seat and cards for every candidate. Per-round swing is about ±60 bb/100, so only trust gaps above 2 standard errors. Tools: `src/duel.py` and `src/arena.py` on `claude-bot`.

| Table (30 rounds unless noted) | Result |
|---|---|
| Solid, no fish (attention, matcha, equity, gherkers, jump, wbot replicas) | **av14f − vastra r3 = +20.1 ± 5.4**; av14f − Mehdi v3 = +13.3 ± 6.8; av14f − Avengers v13 = +7.8 ± 4.8 |
| Solid + 1 real starter-kit bot | **av14f − vastra r3 = +122 ± 19; av14f − Mehdi v3 = +121 ± 18**; av14f − v14 = +2.8 ± 5.7 |
| Realistic replicas (5 solid + Joca replica) | v13 − Mehdi v1 = +15 ± 9; v13 − Mehdi v3 = +17 ± 10; vastra and v3 level with v1 |
| Fish-heavy replicas | all within ±13, no difference |
| Riyad's `field/` profiles | v13 − Mehdi v1 = +14 ± 10; v13 − Mehdi v3 = −10 ± 11; vastra and v3 were +25 over v1 |
| Arena, all at one table plus 3 solid bots (40 rounds) | Avengers v13 +28 ± 5, vastra +16 ± 5, Mehdi v3 +13 ± 6, Mehdi v1 −4.5 ± 5.5 |

Why Avengers wins:
- Postflop it compares the expected value of check, several bet sizes, call and raise, using each opponent's measured fold rate by street and line.
- It builds each opponent's range from his preflop line, re-ranks it on the board, and narrows it by his actions.
- It detects bots running the unchanged starter kit, and limp-folders, and exploits them.

Vastra-fable, by contrast, loses about 100 bb/100 against a starter-kit bot relative to Avengers, because it has no detection for it.

## 5. Shortcomings found

1. **Timeouts in rounds 1–3** (about 6 per round) came from Monte Carlo budgets of 0.9–2.3 ms CPU per decision (section 3). Mostly fixed in v6; av14f is the next step.
2. **The sandbox opponents are stale.** `sparring/rep_*` and `field/*` were fitted to practice hands, where four bots were fish. In the counted rounds those bots were fixed. Refit them from counted-round hands before trusting fish-table results.
3. **The upload decision is unclear.** We don't know which file v5 and v6 are. Keep a log: upload number, file, SHA, time.
4. **Mehdi v1's leaks** (from the 14:30 brief, still unverified on counted hands): calling big bets and raises from tight bots with one pair, and calling 2,000 preflop with KTo or TT against tight shovers.
5. **The ±60 bb/100 noise per round** means six rounds can't separate bots 20 bb/100 apart. Rely on duplicate-deal duels and the real-hand replay, not the leaderboard.

## 6. Task 1 for the next agent: real hand data, every round

**Token:** Saeed or Mehdi copies it from the AI Poker Bots page under "Your table's data", once logged in. Never commit it.

**Route A, a laptop with normal internet:**
```
python3 fetch_hands.py --token <TOKEN>     # saves hands/<ref>.json, one per round; round metadata includes timeouts and think_s
python3 tools/analyze.py hands/*.json --me  # per-team stats (fable-bot)
python3 tools/replay.py upload/bot.py hands/saturday_*.json   # Riyad: lists passive plays the bot would not make = likely timeouts
python3 tools/matrix.py ...                 # who wins from whom
```

**Route B, a cloud agent (its shell is blocked from imperialaihack.com):**
1. Open `https://imperialaihack.com/pokerbots` in the user's built-in browser.
2. Run this in the page:
   ```js
   const H={headers:{Authorization:'Bearer '+TOKEN}};
   const res=await fetch('/api/poker/results',H).then(r=>r.json());
   ```
3. For each `res.rounds[i].ref`, fetch `/api/poker/hands?ref=<ref>` and return one round per call. Results over about 250 KB are truncated; large results are saved under `/tmp/claude-tool-results/`, where they can be read back with Python.

**Then, for every counted round:**
1. List each timeout. Use the round metadata, and `tools/replay.py` to locate them. Note street, pot and result, and estimate the chips lost.
2. Compute bb/100 by position and by the street the pot ended on. List the 20 biggest losing hands, with the line each opponent took and what they showed.
3. Per opponent: VPIP, PFR, fold to bet by street, and what they showed behind big bets. Refit the replicas from this (`replica_core.make(...)` on `claude-bot`, or the `field/` profiles on `fable-bot`).
4. Look at the top teams (Gherkers, Attention Is All In, AAST) at our tables. Note their sizing, how often they 3-bet and how often they barrel. Copy what works against the current field.
5. Re-run the section 4 duels against the refitted field before any upload.

## 7. Upload rule (unchanged)

Recommend an upload only if all of these hold:
- It beats the live bot by more than 2 standard errors in a 30-round duel on the solid table.
- It does not lose on a table with a starter-kit bot.
- The fuzz test gives 0 illegal replies, and `tools/latency.py` under contention shows ">5 ms" no worse than the live bot.
- Saeed or Mehdi does the upload.
