# Brief: one candidate strategy for the Imperial AI Hack poker bot, for independent assessment

Audience: a large-context model asked to decide, from the data, how our team should play
the rest of the tournament. Section 4 is one candidate strategy, drafted by another model.
It is input, not a decision. Judge it on the evidence, reject any part of it that the data
does not support, and prefer your own approach wherever you expect it to do better. The
team wants the best plan, not this plan. Repo: `mehdiaitbelaid/imperial-pokerbot`. Written
Sat 14 Nov 2026, 16:35, after counted round 12 of 54. Team: Resonance Qt. Hard constraints
are in `docs/COMPETITION_CONTEXT.md` and the engine source; results and test methods in
`FINAL_BOT_REPORT.md`. Read both first, then form your own view before reading section 4.

Labels: [MEASURED] run by us; [DATA] Mehdi's 6,000 live hands (`docs/pressure-playbook.md`),
replica fits (`sparring/rep_*.py`, branch `claude-bot`) and `rankings/standings-history.csv`
(branch `rankings-history`); [CODE] read from source; [HYPOTHESIS] untested.

---

## 1. Objective, precisely

- Saturday (54 rounds, 1,000 hands each, reseated every round): average bb/100 across all
  rounds. Only seeds Sunday's tables ("dealt like cards" across tables).
- Sunday (36 rounds at one table): top 2 by total chips go to the final. Rank is what pays.
- Final (8 bots, 5,000 hands, one table): most chips wins. 1st £500, 2nd £200.
- Success = P(top 2 at the Sunday table) x P(1st in the final). Saturday rank matters only
  through seeding. Do not optimise Saturday average at the cost of Sunday robustness.

## 2. Where we stand [DATA, round 12]

| Rank | Team | bb/100 | Note |
|---|---|---|---|
| 1 | Attention Is All In | +54.5 | rounds: +189, +12, +144, -9, -17, -6, +10, +2, +6, +185, +11 |
| 2 | Gherkers | +54.4 | consistent (+51 +78 +76 +166 +72 +88 +5 -7 +5 +43 +5), version 15 |
| 3 | Equity Engine | +39.1 | consistent, version 9 |
| 4 | AAST | +37.4 | |
| 5 | ND | +31.2 | version 1 (static) |
| 7 | **Resonance Qt (us)** | **+29.3** | 1 losing round in 11; 27 timeouts, 0 errors; version 7 = Avengers V18 |
| 41 | ediz_slow | **-313.0** | loses 263 to 535 bb/100 every round |

Noise [MEASURED]: one 1,000-hand round has a standard error of about 170 bb/100 for one bot;
54 rounds about 23; the 5,000-hand final about 75. Treat single rounds as noise.

## 3. The central structural fact

`ediz_slow` gives away about 62,000 chips per round. With 41 teams and 5 to 6 tables, any
team sits with it about one round in six. The average tablemate takes +45 to +50 bb/100 from
it; Attention Is All In took +144 to +189 in its three whale rounds and about zero elsewhere.
**The Saturday leaderboard is largely a ranking of whale-extraction efficiency.**

The whale's play is effectively known (`sparring/ediz_like.py`, replica of the real bot)
[CODE]: preflop it raises any pair, ace-high or king-high every time to `min_raise_to +
pot // 2`, limps everything else, and calls only when the call is at most 2 big blinds;
postflop it keeps betting only with a made hand (pair or better) and folds to real bets
otherwise. Several other losing teams play the starter-kit pattern (V17 has a "starter-kit
whale counter").

## 4. One candidate strategy (drafted by another model; assess, do not assume)

The numbers below are the drafter's estimates unless labelled otherwise. The
"expected effect" in 4.5 is a hypothesis with no test behind it.

### 4.1 Exact-size whale isolation loop
- Whale limps (about 44% of its hands): raise to exactly 3 bb total. Its call is then exactly
  2 bb, so it calls with any two cards, while the field folds to a 3 bb open about 76% [DATA].
- Bet every flop at 50 to 66% pot. It continues only with pair or better (about a third of
  the time); otherwise we take about 7.5 bb. When it continues, value bet better than a weak
  pair, fold air.
- Whale raises (about 56%): 3-bet with the top 15% and stack off with top pair or better; it
  re-raises postflop with any made hand and never folds one.
- When the whale has entered and a third player raises, 3-bet the top of our range to get
  heads-up with the whale.
- Estimated value [HYPOTHESIS]: about 200 isolations a round at about +3 bb each, +60 bb/100
  at whale tables before stack-offs; about +10 to +15 bb/100 on our Saturday average over the
  remaining eight or so whale rounds.

### 4.2 Named opponent profiles and target selection
- Join `hands/` (every seat's chip result per round) with the standings CSV (every team's
  chip change per round, snapshots every 5 minutes from 15:40) by exact integer match, so
  every seat we have faced gets a team name. Then build per-team profiles and replicas.
- Known leaks of the leaders [DATA]:

| Team | VPIP/PFR | Aggr | Fold to bet | Bluff | Leak | Counter |
|---|---|---|---|---|---|---|
| Attention Is All In | .28/.22 | .48 | .70 | .20 | folds to 3-bets 0.77 (n=48), folds 70% to bets | 3-bet opens with blockers; c-bet and stab every board at 50% pot; never pay off its fight-back |
| Gherkers | .28/.19 | .64 | .50 | .25 | raises bets 0.27, check-raises 0.12 | no bluffs; thin value; call down top pair |
| Equity Engine | .24/.17 | .49 | .39 | .18 | few | small pots out of position; value only |
| ND (v1, static) | .21/.11 | .30 | .38 | .12 | never folds to 3-bets (0.03), rarely bluffs | value 3-bets only; fold to its bets; steal its blinds |
| Phil AIvey | .30/.20 | .20 | .45 | .08 | passive, honest | fold to its bets; bet when it checks |
| bigRoddy | .83/.34 | .45 | .54 | .35 | folds to c-bets 0.85, never to 3-bets | c-bet every flop; value 3-bets |
| Joca, AIl IN, Anton, YSL | loose | high | low | high | maniacs and stations, -25 to -57 bb/100 | wide calls, no bluffs, big value bets |

- Version stability from the CSV decides prior strength: ND, aydine, pokermon are on version
  1 (Saturday reads hold on Sunday); Gherkers v15 and matcha v17 are adapting (weak priors,
  fast in-round learning).
- Most bots decide from their own cards and do not adapt to us [DATA, playbook], so
  exploitation risk is low except against frequent uploaders.
- At 20:30, when Sunday tables are published, embed only our table's profiles: a 7-way
  identification from raise-size fingerprints and frequencies within 10 to 20 hands, then a
  precomputed best response per seat. Same for the likely finalists.

### 4.3 Rank-aware risk policy (play for rank when rank pays)
- The bot cannot see names or the leaderboard, but it sees `summary["stacks"]` after every
  hand, and stacks reset to 2,000, so it can keep every seat's running total within a round
  and therefore its own rank at the table at every hand [CODE].
- Final (one table, 5,000 hands; detect with `info["hands"] == 5000`): maximise P(1st), not
  expected chips. Leading late: avoid high-variance marginal spots. Trailing late: take every
  +EV high-variance spot and widen stack-offs; 3rd pays nothing.
- Sunday: totals across rounds are visible to the humans on the site. Prepare a lock-in build
  (low variance) and a push build (high variance, maximal whale pressure) tonight; at about
  11:15 upload whichever our table position needs. Uploads close at 12:00.

### 4.4 Already in place
- V18 (live): team preflop (steals, 3-bets by measured folds, kit-bot counter) + our postflop
  (vastra-fable engine + quant EV layer: per-spot fold model with log-odds seat shift and
  beta-binomial shrinkage, bet iff EV(bet) - EV(check) > 2% pot with equity realisation by
  hand class, hysteresis per seat, value-heavy read of big turn and river bets).
- Release gate: `ab_vf.py` (same cards, common random numbers, all-in luck adjustment; SE about
  2.5 bb/100 over 100 tables) plus the team bands (VPIP 22 to 35%, PFR 17 to 27%), fuzz, and
  0 timeouts at 4 ms / 4 s.

### 4.5 Expected effect [HYPOTHESIS]
Non-whale rounds from about +30 to about +60 via named exploitation; whale rounds from about
+50 to about +150. Remaining 42 rounds average about +75; Saturday average about +65 against a
likely +55 to +60 for the current leader. Plausible, not guaranteed, given the noise.

## 5. Known weaknesses and open questions (the drafter's own list; add your own)

1. 4.1 assumes the live `ediz_slow` matches the replica exactly. Verify its call threshold and
   sizes from the hand data before fixing the 3 bb size; if it calls 3 bb, isolate bigger.
2. 4.2's identification among 40 teams in-round is slow (about 60 hands); it is fast only once
   the Sunday table is known. Is there a better fingerprint than raise-size formulas?
3. 4.3's risk policy needs a variance model per decision type; none is built yet. Propose one
   that fits in the time budget (about 3 ms per decision, 10 s bank per round, 1 core).
4. Whale rounds are only about one in six. Is the non-whale lift to +60 realistic? Which
   exploits carry the most EV per 100 hands given opportunity counts (playbook section 5)?
5. Sunday tables mix strong and weak by design. If the whale is not at our table, the plan
   reduces to 4.2 and 4.3. Is there a better plan for a whale-free table?
6. The field adapts (3-bet rates rose from 6.9% to 12.3% over six rounds in a comparable
   tournament). Which of our exploits are robust to adaptation, and which should carry stop
   rules?
7. Anything here that violates the rules (no collusion, no sandbox or site attacks) must be
   dropped; everything above uses only our own hand data and the public leaderboard.

## 6. What to return

1. Your own assessment of what decides this tournament, from the data in sections 1 to 3
   and the repo, before considering section 4.
2. A verdict on each part of section 4: adopt, adapt, or reject, with the data points that
   support the verdict. Rejecting all of it is a valid outcome if your plan is better.
3. Your recommended strategy, ranked by expected bb/100 x feasibility within the constraints
   (standard library, 200 KB, 3 ms per decision, no names at runtime, fresh agent every round),
   whether it overlaps with section 4 or not.
4. A build order for tonight and Sunday morning, each item with the test that must pass in
   `ab_vf.py` and the team gates before upload.
5. Code where feasible for the items you recommend.
