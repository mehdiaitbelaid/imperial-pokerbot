# Brief: live V18 review after counted rounds 1–13 (Resonance Qt)

Written Sat 14 Nov 2026, 16:40 UK time, by Claude. It follows `claude/pokerbots-counted-rounds-hand-analysis.md` (rounds 1–8) and `BRIEF-timeouts-and-rounds.md` (branch `claude-timeouts`).

Branch: **`claude-v18r`**, cut from `fable-bot` at `57c166e` (V19 candidate).

## 1. Verdict

1. **The live bot, V18 (upload v7, SHA `4429f31fe495`, the Avengers chimera), is the best bot the team has.** On three tables refitted to the counted rounds it beats everything else (section 3).
2. **Suggested upload: `upload/bot_v18r.py`, SHA `8d9f2f2467e1`.** It is V18 with two changes in the postflop partner, `src/partner_hassan_var_r.py`:
   - Monte Carlo is capped at 0.45 ms instead of 0.9 ms (`MC_MAX`, `MC_COMMIT` 0.6 → 0.4 ms).
   - On the river, a bet of at least 90% of the pot needs 60% equity to call, unless a maniac is in the hand.
3. **Expected gain is small** and comes from two places:
   - About **4× fewer slow decisions** on a simulated slow server: 0 over 10 ms against 9–12 for V18, and 96 over 5 ms against 163–207.
   - Folding river calls of pot-sized bets that the real field almost never bluffs.
   - In the sandbox it plays level with V18: −0.7 ± 1.8 bb/100, pooled over 4 runs of 30 rounds.
4. **Don't upload V19 (Riyad, `57c166e`).** Its veto runs a second postflop engine on exactly the big decisions. It had 21 decisions over 10 ms (the most of any build) and was −7 ± 5 and +2 ± 4 against V18 in the sandbox.

## 2. Live data (team API, rounds R1–R13; token held by Saeed, never commit it)

| Round | Upload | bb/100 | Timeouts | Server think time (s) |
|---|---|---|---|---|
| R1–R2 | v5 (Mehdi v1) | −7.9, −18.9 | 7, 1 | 2.4, 2.0 |
| R3–R11 | v6 (Avengers v14) | +36.9, +65.2, +36.2, +75.7, +3.5, +45.3, +12.9, +77.5, +3.9 | 10, 2, 1, 1, 0, 3, 1, 0, 0 | 1.7–3.1 |
| R12–R13 | **v7 (V18)** | +21.0, +20.4 | 1, 1 | 2.2, 2.5 |

**Standing after 13 of 54 rounds: 5th of 39 at +28.6 bb/100, now ranked.** Top: Attention Is All In +55.6, Gherkers +52.3, Equity Engine +41.2, AAST +33.4.

Server think time is about 2.2–2.5 s per round. The same bots use 0.45–0.6 s per round in our sandbox, so **the server is about 4–5× slower than our container.** A 1 ms decision here is roughly 4–5 ms there, which is why the latency cap matters.

## 3. Sandbox, refitted to the counted rounds

Opponents are `field/c_*.py`: Riyad's `ProfileAgent` with every team's R1–R11 stats from `tools/analyze.py`, plus `sparring/ediz_like.py`. All duels are duplicate-deal, 1,000 hands per round. Each cell is V18 minus the candidate (paired, ± standard error); positive means V18 is better.

| Table (opponents) | Rounds | vs v14 | vs v16 | vs av14f | vs Mehdi v3 (`b11f117`) | vs vastra r4 |
|---|---|---|---|---|---|---|
| T1 top (Gherkers, Attention, WBot, Kojack, Equity, Durahim) | 30 | +11.5 ± 6.2 | +17.5 ± 6.4 | +11.3 ± 5.3 | **+21.5 ± 5.3** | +15.1 ± 6.5 |
| T2 whale (Gherkers, Attention, Vlad, matcha, AIl IN, ediz) | 30 | **+32.1 ± 6.6** | +17.2 ± 5.5 | +33.5 ± 6.8 | +39.1 ± 9.6 | +26.6 ± 9.7 |
| T3 weak (YSL, Joca, Red, GamesGone, Market Makers, Poké Bot) | 24 | +17.2 ± 5.7 | +22.0 ± 5.4 | – | +6.8 ± 6.8 | – |

V18 variants against V18 (candidate minus V18):

| Table | V18f (CPU cap only) | V18r (cap + river rule) | V19 (veto) |
|---|---|---|---|
| T1, 3 runs | +10.4 ± 4.0, +0.8 ± 4.8 | −2.9 ± 3.8, −2.3 ± 3.2 | −7.3 ± 4.6 |
| T2 variants, 3 runs | +3.3 ± 4.9, −7.7 ± 4.2 | −2.5 ± 3.1, +4.8 ± 4.0 | +2.4 ± 4.0 |

**Latency on a simulated slow server** (`tools/latency.py`: one core, two busy loops, 3 rounds, same table):

| Build | Over 10 ms | Over 5 ms | CPU p95, in-process |
|---|---|---|---|
| V18 | 9–12 | 163–207 | 0.93 ms |
| V19 | 21 | 185 | 0.93 ms (p99 1.73) |
| V18f | 1–3 | 104–143 | 0.47 ms |
| **V18r** | **0–3** | **96–97** | **0.47 ms** |
| starter kit (floor) | 0–1 | 24–27 | ~0 |

Fuzz test (`tools/fuzz_act.py` on the `v1` branch): V18r gives 0 illegal replies.

## 4. What the real hands say

Rounds R3–R13 (v6 and v7), 11,000 hands. `tools/leaks.py` gives exclusive buckets:
- **Lost at showdown after our river call: about −18 bb/100.** The rest of the "showdown lost" buckets are big pots against made hands.
- **River calls of bets of at least 90% of the pot:** 10 calls, 2 won.
- Replaying those exact spots through each build (`tools/rivreplay.py`, 5 votes each):

  | Build | Folds | Chips saved |
  |---|---|---|
  | V18 | 2 of 10 | +148 bb |
  | V19 | 5 of 10 | +327 bb |
  | V18r | 7 of 10 | +422 bb |

  V18r is therefore about +2.5 bb/100 better than V18 here. **This is in-sample:** the rule was written from these hands. Independent support comes from the practice data in `AVENGERS.md`, where callers of river bets of 80% of the pot or more won 15% of the time over 34 samples.
- Calls of smaller river bets (89 calls) are roughly break-even. Leave them alone.
- **V18's first two rounds:** "raised preflop then folded to a re-raise" happened 73 times in 2,000 hands, costing −19.5 bb/100. Under v14 it was 170 in 9,000 hands, costing −8.6. V18's preflop (av17) 3-bets 17% and gets 4-bet often (Anton 3-bets 22%, bigRoddy 17%, FisherMen 13%). It is offset by winning more pots preflop uncontested (+77.6 against +63.4 bb/100). Only 2 rounds so far: watch it, don't change it yet.
- **The R3 whale table** (ediz_slow) cost 8 stacks on preflop shoves over his 3-bets with 77 to QQ and A9o. See the 15:42 report.

## 5. Next steps for the next agent

1. **After 3–4 rounds of V18r, compare it with V18 on real data:** bb/100, timeouts per round and think time. Pull the rounds with the browser (Route B in `BRIEF-timeouts-and-rounds.md`).
2. **Refit `field/c_*.py` every 5 rounds.** Run `tools/analyze.py` on the hand files and rebuild the profiles, using the script in section 6.
3. **Preflop re-raise leak:** in av17, test a smaller 3-bet range against seats with a measured 4-bet rate (or fold to 3-bet below 40%). Accept only on duels against T1 and T2 with 30 rounds, plus replay on real hands.
4. **What Attention Is All In does:** 36% VPIP, 30% PFR, 12% 3-bet, folds 58% of the time to bets, and is the leader. The field is tight, so loose-aggressive preflop play with disciplined postflop folding wins. Our steal and 3-bet logic should lean that way. Test it, don't assume it.
5. **Keep every postflop engine at or under about 0.5 ms CPU p95.** The server is 4–5× slower than our sandbox.

## 6. Rebuilding the counted-round field

```
python3 tools/analyze.py hands/saturday_r0*.json > /tmp/stats.txt
# each table row -> field/c_<team>.py with ProfileAgent P = {vpip, pfr, limp, three_bet, fold_to_3bet,
# open_size_bb (cap 6), cbet, bet, bet_size (cap 1.6), fold_to_bet, raise_vs_bet, air}; percentages / 100
```

Rebuild V18r from source with the V18-era `build_chimera.py` (`git show f7ee888:src/build_chimera.py`). The current one adds the V19 veto. Use preflop = the `_PRE_SRC` embedded in `upload/bot.py`, and postflop = `src/partner_hassan_var_r.py`.
