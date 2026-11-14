# Handoff for the next Claude tab: Resonance Qt poker bot (Imperial AI Hack, Track 04)

Written Sat 14 Nov 2026, 16:50 UK time, by Claude. Read this first, then `pokerbots-rounds1-20-analysis.md`. Both are on GitHub branch `claude-v18r` and in the claude.ai project "Project Hackathon".

## 1. The job
- Team **Resonance Qt**: Saeed (the user), Mehdi, Riyad and Hassan.
- We write one `bot.py` (class `Agent`) that plays No-Limit Hold'em, 7–8 bots per table, 1,000 hands per round, every hand reset to 2,000 chips with blinds 10/20.
- **Saturday score:** bb/100 averaged over every counted round, 15:00–19:25, one round every 5 minutes, 54 rounds in total.
- **Uploads and teams lock at 19:30.**
- Sunday:
  - 20:30 Saturday: bucket tables announced.
  - 09:00–11:55: bucket tables, scored from zero; the **top 2 by chips** at each table reach the final.
  - Uploads close 12:00.
  - 12:05: final, 8 bots, 5,000 hands, most chips wins.
- **Hard limits:**
  - Python 3.12, standard library only, under 200 KB, no network or file access.
  - **10 ms per decision** and a **10 s thinking bank per round**.
  - The server is about **4–5× slower than our cloud sandbox**: the live bot's think time is about 2.2–2.8 s per round, against 0.4–0.6 s locally.
- **Rules:**
  - Never upload a bot yourself. Uploads go through Saeed or Mehdi on the website.
  - Never commit the data token or hand files.
  - AI tools are allowed. No collusion, and no attacking the site.

## 2. State right now (16:46)
- **Saturday rank: 10th of 39 at +28.8 bb/100** after 22 rounds, 31 timeouts, 0 errors. Top: Gherkers +43.4, Equity Engine +41.8, Attention Is All In +40.3. Rank 6 was at about +30.8 twenty minutes earlier.
- **Live bot: upload v8, SHA `70f64660654b`, Avengers v14** (`upload/bot_v14.py` on `fable-bot`). It was uploaded 16:43, after the round 1–20 analysis recommended going back to the v14 engine. Its first round, R22, was −12.0, which is noise for one round.
- **Upload history:**

  | Upload | Bot | Rounds | Result |
  |---|---|---|---|
  | v5 | Mehdi v1 | R1–R2 | −13.4 |
  | v6 | Avengers v14 | R3–R11 | +39.7 |
  | v7 | V18 chimera | R12–R21 | about +31 |
  | v8 | Avengers v14 again | R22– | |

- **Pending option:** upload `upload/bot_av14f.py` (SHA `ec92d4936d8f`). It is v14 with a CPU cap: the same play (+2.8 ± 5.7 bb/100 in a 30-round duel) and about half the slow decisions under a slow-server emulation. v14 had 10 timeouts in its first live round, R3, and 0–3 after that. This is a low-risk swap; mention it to Saeed.

## 3. Key findings so far (detail in `pokerbots-rounds1-20-analysis.md`)
1. **Luck-adjusted, without the whale (ediz_slow) tables, v14 made +44.6 bb/100 and V18 +3.3.** The gap is 41 ± 9.5, and V18's tables were weaker. V18's actual +33 was propped up by +15 bb/100 of all-in luck.
2. **V18 is a passive, calling postflop engine.** Its aggression factor is 1.1, against 1.7 for v14 and 2.3–3.7 for the top-3 teams. It c-bets 68% against v14's 86%, and loses about 18 bb/100 more in pots that never reach showdown.
3. **Leaks still open, in v14 as well:**
   - Calling pot-sized or bigger turn and river bets: about −7 bb/100 under V18; v14 made fewer such calls.
   - Stacking off with one pair against tight players' overbets.
   - Folding 68–75% of the time to 3-bets and 4-bets after raising.
   - The big blind is roughly break-even.
4. **Whale dependence:** ediz_slow gave about 37% of all our profit in 3 rounds. Sunday needs a bot that beats solid tables.
5. **Our sandbox got V18 vs v14 the wrong way round:** replicas said V18 was 11–32 bb/100 better. Until it is recalibrated (section 6), **judge bots on luck-adjusted live rounds** and use the sandbox only as a regression and safety check.
6. **Timeouts are fixed.** Keep every postflop engine at or under 0.5 ms CPU p95 locally.

## 4. Where things are
- **Repo:** `mehdiaitbelaid/imperial-pokerbot` (private). Attach it with the `add_repo` tool, then clone with `--no-single-branch`.

| Branch | Owner | Contents |
|---|---|---|
| `fable-bot` | Riyad | Avengers source (`src/avengers.py`), `src/build.py`, `src/build_chimera.py`, `upload/bot.py` (V19 candidate) plus `bot_v14.py` and `bot_v16.py`, `field/` profile replicas (`profile_base.py`), `tools/analyze.py`, `leaks.py`, `replay.py`, `whatif.py`, `calib.py`, `round_report.py` |
| `v1` | Mehdi | his bots: `bot.py` = Mehdi v3, `versions/vastra-fable.py` r4, `tools/fuzz_act.py`, `tools/bench.py` |
| `claude-bot` | Claude | sandbox: `src/duel.py` (paired duplicate-deal duels), `src/arena.py`, `src/timing.py`, `sparring/rep_*.py` (old practice replicas), `AGENTS.md` brief |
| `claude-timeouts` | Claude | av14f build (`upload/bot.py`), `tools/latency.py`, timeout brief |
| **`claude-v18r`** | Claude | **latest:** this handoff; `pokerbots-rounds1-20-analysis.md`; `pokerbots-round19-report.md`; `BRIEF-v18-review.md`; `upload/bot_av14f.py`; `upload/bot_v18r.py` (no longer recommended); `field/c_*.py` (34 counted-round profiles); `tools/full_analysis.py`, `rivreplay.py`, `latency.py`; `results/` duel logs |
| `rankings-history` | | public standings snapshots every 5 minutes |

- **Project docs**, newest first: `pokerbots-rounds1-20-analysis.md`, `pokerbots-round19-report.md`, `pokerbots-v18-review.md`, `pokerbots-counted-rounds-hand-analysis.md` (R1–R8), `pokerbots-brief-timeouts-rounds.md`, `pokerbots-handoff-brief.md` (14:30, outdated).

## 5. How to get the data
- **The cloud sandbox cannot reach imperialaihack.com** (proxy 403). Use the **built-in browser on Saeed's Mac.** Load the `built-in-browser` skill, then the `mcp__remote-devices__Claude_Browser__*` tools. A tab on `https://imperialaihack.com/pokerbots` works; it does not need to be logged in.
- **Token:** Saeed's team data token. It was pasted in the earlier chat "Imperial AI hackathon poker bot" in this project. Find it with `conversation_search("fetch_hands token")`, or ask Saeed. Use it only in the browser as `Authorization: Bearer <token>`. Never write it to a file or commit it.
- **Endpoints** (same origin, run with `javascript_tool`):
  - `/api/poker/results` lists rounds with chips, bb/100, timeouts, think_s and version. `lastCheck` shows the live bot's SHA.
  - `/api/poker/hands?ref=saturday/r022` returns one round, about 570 KB of JSON.
  - Public standings (no token): `https://poker.imperialaihack.com/pokerbots/api/public`.
- **Moving hand files into the sandbox:**
  1. In the page, gzip with `CompressionStream` and base64-encode; that is about 76 KB per round.
  2. Return up to 3 rounds per `javascript_tool` call. Results over about 250 KB get truncated.
  3. Oversized results are saved to `/tmp/claude-tool-results/...txt`.
  4. Decode them with a small Python script: `json.JSONDecoder().raw_decode` on the text, then base64, gunzip and save to `hands/saturday_rNNN.json`.

  The JS helper used today:
  ```js
  window.__H={headers:{Authorization:'Bearer '+TOKEN}};
  window.__res=await (await fetch('/api/poker/results',window.__H)).json();
  window.__dl=async(ref)=>{const d=await (await fetch('/api/poker/hands?ref='+encodeURIComponent(ref),window.__H)).json();
    d.round=window.__res.rounds.find(r=>r.ref===ref);const s=JSON.stringify(d);
    const cs=new Blob([s]).stream().pipeThrough(new CompressionStream('gzip'));
    const buf=new Uint8Array(await new Response(cs).arrayBuffer());let b='';
    for(let i=0;i<buf.length;i+=0x8000)b+=String.fromCharCode.apply(null,buf.subarray(i,i+0x8000));return btoa(b);};
  // then: const o={}; for(const r of [...refs]) o[r]=await window.__dl(r); JSON.stringify(o)
  ```

## 6. Next steps, in priority order
1. **Track v8 (v14) live.** After every round, pull it and run `HANDS=hands python3 tools/full_analysis.py`. Compare luck-adjusted bb/100 with v14's earlier +44.6 (no whale) and V18's +3.3. Report to Saeed every 3–4 rounds. Suggest av14f if any round shows more than 3 timeouts.
2. **Recalibrate the sandbox to reality.**
   - On the real hands, measure per team how often they fold to *our* c-bets, turn barrels and river bets.
   - Set `fold_to_bet` and `cbet` in `field/c_*.py` (Riyad's `ProfileAgent`) so that a 30-round duel of v14 against V18 reproduces the live gap: v14 ahead by about 30–40 bb/100.
   - Only then trust duels for choosing bots.
3. **Fix the big-bet calls in v14's postflop** (`src/avengers.py` on `fable-bot`, `_postflop`, the facing-a-bet branch):
   - Fold one pair or two pair to turn and river bets of at least 0.9 × the pot, and to flop shoves of at least 1.5 × the pot.
   - Apply this only to seats with VPIP under 30% and low measured river bluffing.
   - Validate by replaying real calls (`tools/rivreplay.py`, extended per street) plus T1/T2 duels.
   - Build with `python3 src/build.py upload/bot_X.py src/avengers.py`.
4. **Preflop:** cut the 4-bet folds (75% under V18; check v14's rate) with a value-weighted 3-bet range against seats that 4-bet.
5. **Sunday prep, after 19:30:** at 20:30 get our bucket table's line-up. Pull those teams' Saturday stats from our hands, build replicas, and tune for top-2-by-chips at that table. Uploads stay open until 12:00 Sunday.
6. **Before any upload recommendation:**
   - `tools/fuzz_act.py` (branch `v1`) gives 0 illegal replies.
   - `tools/latency.py` under contention (one core plus two busy loops) is no worse than the live bot.
   - No loss on the T1/T2 duels.
   - Give Saeed the file and its SHA-256 prefix.

## 7. Sandbox recipes (cloud container)
- Duel tables built from counted-round stats (opponents in `field/`, needing `profile_base.py` next to them):
  - **T1 top:** c_gherkers, c_attentionisa, c_wbot, c_kojack, c_equityengine, c_durahim1453.
  - **T2 whale:** c_fishermen, c_attentionisa, c_vlad, c_astralavista, c_bigroddy, `sparring/ediz_like.py`.
  - **T3 weak:** c_ysltwizzy, c_joca, c_red, c_gamesgone, c_themarketmak, c_pokbot.
- Command (from a `claude-bot` checkout with `field/` copied in): `python3 src/duel.py --cands bots/A.py bots/B.py --field <six paths> --rounds 30 --seed N`. One table-round takes about 2.5–3 s per candidate. The container has 2 cores, so run 2 duels at once at most, or timeouts get distorted.
- Latency: `taskset -c 0` with two `python3 -c "while 1: pass"` burners, then `tools/latency.py --rounds 3 <8 bots>`. Compare the ">5 ms" column.
- Chimera builds (V18 family) use `src/build_chimera.py PRE.py POST.py OUT.py`. V18's sources can be extracted from the base64 `_PRE_SRC` and `_POST_SRC` blocks in its file.

## 8. Lessons already paid for
- One round swings about ±43 bb/100 even after luck adjustment. Judge bots on 6 or more rounds, luck-adjusted.
- Sandbox replicas misjudge postflop aggression versus calling. Always cross-check against live data.
- The server is 4–5× slower than the sandbox. CPU per decision drives timeouts, and a timeout means a fold, usually in a big pot.
- Teams change bots during the day: the practice fish were fixed by 15:00. Refit opponents from recent rounds.
- Keep the user's token out of files and commits. Use it only inside the browser tab.
