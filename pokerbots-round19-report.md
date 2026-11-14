# Report for the next agent: counted round 19 and what to fix (Resonance Qt)

Written Sat 14 Nov 2026, 16:40 UK time, by Claude, from the team's hand data (API). Read `BRIEF-v18-review.md` on branch `claude-v18r` first. It has the sandbox, the tools and the V18r candidate.

## 1. Where we stand

- **Live bot:** upload v7 = **V18** (Avengers chimera: av17 preflop, Hassan's `partner_hassan_var` postflop). SHA `4429f31fe4954855`, loaded fine at 15:51.
- **Saturday standing after 19 of 54 rounds: 6th of 39 at +32.2 bb/100.** Top: Gherkers +51.5, Attention Is All In +41.3, Equity Engine +36.5, Kojack +35.1, Phil AIvey +32.2.
- **V18's live rounds (bb/100, timeouts):** R12 +21.0 (1), R13 +20.4 (1), R14 +28.0 (1), R15 +163.7 (0), R16 +21.4 (0), R17 +3.3 (1), R18 +56.4 (0), **R19 −33.5 (0)**. That's an average of +35.1 over 8 rounds. Timeouts are no longer a problem.
- **Candidate not yet uploaded:** `upload/bot_v18r.py` (SHA `8d9f2f2467e1`). It is V18 with Monte Carlo capped at 0.45 ms, and calls of river bets of at least 90% of the pot need 60% equity. It plays level with V18 in the sandbox and has 4× fewer slow decisions. **It would not have saved any of the R19 losses below.**

## 2. Round 19 (slot 16:30, table 4, our seat 2): −33.5 bb/100, −6,701 chips

| Team at our table | bb/100 this round | VPIP / PFR | Folds to bets (postflop) | Note |
|---|---|---|---|---|
| Equity Engine | +56.6 | 27 / 20 | 62% | took most of our chips with QQ |
| FisherMen | +28.9 | 35 / 29 | 60% | called our turn barrels twice |
| munchlax | +28.5 | 19 / 9 | 76% | new team, passive, raises rarely |
| Red | +9.7 | 21 / 14 | 58% | **tight**: flop shove with a set |
| **Resonance Qt** | **−33.5** | 22 / 16 | 46% | |
| Joca | −40.9 | 9 / 1 | 50% | nit, preflop shover |
| AIl IN | −49.4 | 26 / 18 | 35% | station |

**Three full-stack hands cost 6,000 of the 6,701 chips.** The rest of the round was about −3.5 bb/100.

| Hand | Line | Result | Verdict |
|---|---|---|---|
| r019#387, AhAs | FisherMen opens 65. Equity Engine 3-bets to 195. We 4-bet to 468. Equity Engine shoves 2,000 and we call. Board Ks 9d Kc Qc 6h; Equity Engine shows QsQd. | −2,000 | **Cooler.** Nothing to fix. |
| r019#134, AsAc | We open 60. munchlax and Red call. Flop Js Qd Ts: we bet 133 and munchlax calls. Turn 3h: we bet 342 and munchlax calls. River 2s: **we bet 969**, munchlax raises to 1,465, and we call 496. He shows KdAh, a straight. | −2,000 | **The river value bet was the error.** One pair on a Q-J-T board, after a passive player (raises 1% of the time) called twice, is too thin to bet big. Check, or bet small. The final call of 496 into about 3,900 was forced by the price. |
| r019#127, KsQc | We open 60. AIl IN and Red call. Flop 6h 2s Kd: **Red shoves 1,940 into about 180**. We call with top pair, second kicker, and AIl IN also calls. Red shows 6d6c, a set. | −2,000 | **Avoidable.** A tight player (21% VPIP) overbetting 10× the pot is almost never bluffing. |

**Two other leaks cost about 130 bb:**

| Hand | Line | Result |
|---|---|---|
| r019#135, 4cKc | We 3-bet FisherMen to 221 and he calls. Flop 5h Ac Ah: we bet 361 and he calls. Turn Th: we bet 821 and he calls. River 7c: we check, he bets 597, we fold. | −1,403 |
| r019#856, ThJd | Same line. Flop Qh 8d 4c: we bet 298 and he calls. Turn 3s: we bet 733 and he calls. River 7h: we check, he bets 748, we fold. | −1,252 |
| r019#405, 9cQc | Red opens 60 and we 3-bet to 168. Flop Jd 9d 4c: Red bets 183, we call. Turn 6s: Red bets 366, we call. River 5d: Red bets 732, we call. He shows AcJc. | −1,449 |

`tools/leaks.py` buckets for R19, in bb/100:

| Bucket | n | bb/100 |
|---|---|---|
| folded the river after betting | 7 | −23.1 |
| lost at showdown after our river call | 3 | −19.9 |
| lost at showdown, other lines | 10 | −19.0 |
| raised preflop, then folded to a re-raise | 29 | −18.0 |
| called the flop, folded the turn | 12 | −9.4 |
| won postflop without showdown | | +45.0 |
| won at showdown | | +39.3 |

## 3. What to fix, in order of value

All three are in the postflop partner, `src/partner_hassan_var_r.py` on `claude-v18r` (V18r's copy of `src/partner_hassan_var.py`). Build it with the V18-era chimera builder: `git show f7ee888:src/build_chimera.py`. Preflop source = the `_PRE_SRC` embedded in `upload/bot.py`.

### Fix A: flop overbets and shoves from tight players are value
In `_weights()` (about line 1378), the value-heavy range for big bets (`BIG_BET_W` / `BIG_RAISE_W`) applies only when `street in ("turn", "river")`.
- Extend it to the flop when the bet is at least `BIG_FLOP_FRAC` × pot. Try 1.5; Red's was about 10×.
- Apply it only when the bettor's `_bluffiness` < `BIG_BET_BLUFF_MAX` and the seat is not a maniac or spammer.

Check: replay r019#127 through the build. It must fold KQ there. Also replay every real flop call of a bet of at least 1.5× the pot from R3–R19 (adapt `tools/rivreplay.py` to the flop) and report folds and chips saved.

### Fix B: stop two-barrel bluffs into a seat that already called twice
`SPOT["barrel"] = (0.33, 42, 0.70, 0.12)` allows air (category 0) on the turn after our flop bet was called. FisherMen called the flop and the turn both times, and we then gave up the river, losing about 65 bb per hand. Try one of these:
- (a) Drop category 0 from `SPOT_CATS["barrel"]` when the opponent's measured fold rate on the turn is under 0.45.
- (b) Shrink the barrel size to 0.5 pot.
- (c) When we barrelled air and got called, use the river `stab_r`/`xr` logic so we don't bet the turn without a river plan.

Check: `tools/leaks.py` "folded the river after betting" should shrink on the real-hand replay, and the T1/T2 duels must not lose.

### Fix C: thin river value bets into passive callers on straightening boards
r019#134: AA bet 969 on the river of Js Qd Ts 3h 2s into a player who raises 1% of the time and had called twice.
- On the river, when the board has 3 or more connected ranks or a 4-flush, and our hand is one pair (category 3 or lower), cap the value bet at about 0.4 pot or check.
- Only bet bigger if our equity against the caller's range is at least `VALUE_EQ_RIVER` + 0.10.

Check: replay r019#134. River bets with one pair on those boards should shrink, and the duels must not lose.

### Watch, don't change yet
"Raised preflop, then folded to a re-raise" ran at −18 to −19.5 bb/100 in V18's rounds (29 times in R19, 73 times in R12–R13). V18's av17 preflop 3-bets about 17%. It is offset by more pots won preflop, so collect more rounds before touching it.

## 4. Testing protocol (unchanged)

1. Sandbox in Claude's `claude-bot` checkout, with refitted opponents in `field/c_*.py` (also on `claude-v18r`):
   - T1 top: c_gherkers, c_attentionisa, c_wbot, c_kojack, c_equityengine, c_durahim1453.
   - T2 whale: c_fishermen, c_attentionisa, c_vlad, c_astralavista, c_bigroddy, `sparring/ediz_like.py`.
   - Command: `python3 src/duel.py --cands bots/v18r.py bots/<candidate>.py --field <six bots> --rounds 30`.
   - Accept only if the candidate is not worse than V18r beyond 1 standard error on T1 and T2, **and** it fixes the real hands it targets on replay.
   - The profile replicas bluff big bets more than the real field does, so a big-bet fold rule will look slightly negative in the sandbox. The real-hand replay decides those rules.
2. Latency: run `tools/latency.py` under contention (one core plus two busy loops). Over-5 ms decisions must be no worse than V18r (about 97 in 3 rounds). The server is 4–5× slower than the sandbox.
3. `tools/fuzz_act.py` (branch `v1`): 0 illegal replies.
4. Uploads go through Saeed or Mehdi only. A new upload plays from the next round. Uploads lock at 19:30.

## 5. Data access

The cloud sandbox cannot reach imperialaihack.com, so use a browser tab on that site. Saeed holds the token; never commit it.
- `GET /api/poker/results` with header `Authorization: Bearer <token>` lists the rounds, with chips, timeouts, think_s and the version per round.
- `GET /api/poker/hands?ref=saturday/r019` returns one round of hands.
- Each round is about 570 KB of JSON (about 76 KB gzipped and base64-encoded), so fetch a few at a time.
- Public standings, with timeouts per team, are at `https://poker.imperialaihack.com/pokerbots/api/public`.
