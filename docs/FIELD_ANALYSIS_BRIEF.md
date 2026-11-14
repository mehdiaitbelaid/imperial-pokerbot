# Field analysis brief: opponents, versions and what the data implies

For the lead model. Purpose: give you the measured state of the field so you can design
our strategy for the remaining Saturday rounds, the Sunday table and the final. This file
reports data and the drafter's reading of it; the reading is open to challenge. Decide from
the numbers. Companion files: `docs/COMPETITION_CONTEXT.md` (rules, API, engine),
`FINAL_BOT_REPORT.md` (our versions, test methods), `PUNCH_THROUGH_BRIEF.md` (one candidate
strategy, for assessment only).

Sources: `rankings/standings-history.csv` on branch `rankings-history` (public leaderboard
snapshots every 5 minutes from 15:40, 41 teams, counted rounds 1 to 20, fetched 16:40 Sat
14 Nov 2026); `sparring/rep_*.py` on branch `claude-bot` (stat replicas of 17 real teams fitted
from hand data); `docs/pressure-playbook.md` on branch `v1` (6,000 live practice hands);
`sparring/ediz_like.py` on branch `fable-bot` (replica of the whale). Labels: [DATA] measured
from those sources; [READING] the drafter's interpretation; [OPEN] unknown.

Method notes [DATA]: a team's result for one round is the change in its chips between
consecutive snapshots divided by the hands played, in bb/100. "Whale round" means a round
scored above +120 bb/100, which in this field almost always means sharing a table with
`ediz_slow` (it loses 263 to 535 bb/100 every round, about 62,000 chips per round given to its
tablemates). "Non-whale mean" is the mean over the other rounds. Per-round standard deviation
for a typical team is about 42 bb/100, so a 19-round mean has a standard error of about 10.

---

## 1. Standings after counted round 20 [DATA]

Our team is Resonance Qt. Live bot is version 7 (Avengers V18: team preflop, our postflop
engine with the quant EV layer).

| Team | Total bb/100 | Version | Uploads in counted rounds | Rounds | Non-whale mean | Positive non-whale rounds | Whale rounds | Timeouts per round |
|---|---|---|---|---|---|---|---|---|
| Gherkers | +47.8 | 21 | 9 | 19 | +39.9 | 16/18 | 1 | 3.2 |
| Equity Engine | +41.1 | 10 | 3 | 19 | +33.4 | 15/17 | 2 | 1.4 |
| Attention Is All In | +39.5 | 3 | 0 | 19 | +9.0 | 10/16 | 3 | 1.5 |
| Kojack | +34.5 | 3 | 0 | 19 | +21.9 | 13/17 | 2 | 1.7 |
| Phil AIvey | +32.6 | 7 | 3 | 19 | +35.0 | 14/19 | 0 | 1.9 |
| Resonance Qt | +31.4 | 7 | 2 | 19 | +26.3 | 16/18 | 1 | 1.6 |
| WBot | +30.4 | 5 | 0 | 19 | +22.8 | 14/18 | 1 | 1.7 |
| The Market Makers | +29.4 | 8 | 1 | 19 | +13.0 | 10/17 | 2 | 2.1 |
| AAST | +28.6 | 4 | 2 | 19 | +29.6 | 16/19 | 0 | 1.2 |
| Astra La Vista | +27.6 | 10 | 4 | 19 | +29.1 | 13/19 | 0 | 0.8 |
| Anker Batteries | +26.6 | 3 | 2 | 18 | +18.3 | 11/17 | 1 | 1.6 |
| Mohil'sPokerBot | +22.7 | 4 | 2 | 19 | +14.6 | 9/18 | 1 | 1.9 |
| gamblerlove | +20.5 | 6 | 2 | 19 | +8.1 | 12/18 | 1 | 1.0 |
| Chinese people can fly | +20.4 | 12 | 5 | 19 | +11.2 | 10/18 | 1 | 2.7 |
| pokermon | +18.3 | 1 | 0 | 19 | +16.5 | 13/19 | 0 | 1.3 |
| munchlax | +14.3 | 4 | 3 | 11 | +17.6 | 7/11 | 0 | 0.9 |
| Claudebot | +11.7 | 2 | 1 | 19 | +13.9 | 13/19 | 0 | 2.0 |
| kaiserbot | +11.5 | 7 | 5 | 19 | +9.7 | 11/19 | 0 | 2.4 |
| Lehman Brothers | +10.8 | 14 | 8 | 19 | +11.9 | 14/19 | 0 | 1.9 |
| Jump Street | +8.7 | 11 | 4 | 19 | +13.3 | 13/19 | 0 | 2.4 |
| ND | +5.9 | 1 | 0 | 19 | -4.3 | 8/17 | 2 | 3.5 |
| Durahim 1453 | +5.7 | 17 | 14 | 19 | +2.9 | 11/19 | 0 | 4.7 |
| SmartBGerBot | +4.7 | 7 | 4 | 19 | +3.8 | 10/19 | 0 | 1.3 |
| Red | +4.1 | 3 | 1 | 19 | +2.6 | 11/19 | 0 | 2.6 |
| matcha mille crêpes cake | +1.8 | 20 | 11 | 19 | -5.1 | 8/19 | 0 | 5.2 |
| Vlad | -0.0 | 2 | 1 | 19 | +3.1 | 10/19 | 0 | 1.1 |
| aydine | -2.8 | 1 | 0 | 19 | -1.7 | 7/19 | 0 | 1.9 |
| supernut | -3.8 | 2 | 1 | 17 | -5.4 | 9/17 | 0 | 0.6 |
| GamesGone | -4.5 | 6 | 2 | 19 | -9.8 | 7/19 | 0 | 2.1 |
| FisherMen | -6.2 | 10 | 6 | 19 | -6.6 | 7/19 | 0 | 1.9 |
| test | -7.1 | 2 | 0 | 19 | -6.3 | 7/19 | 0 | 0.7 |
| Poke | -7.7 | 1 | 0 | 10 | -11.5 | 4/10 | 0 | 0.3 |
| Peanut Cookies | -10.9 | 4 | 2 | 19 | -9.3 | 8/19 | 0 | 1.3 |
| bigRoddy | -13.5 | 6 | 0 | 19 | -22.1 | 8/18 | 1 | 1.3 |
| SARS | -14.8 | 11 | 4 | 19 | -13.8 | 8/19 | 0 | 1.7 |
| YSL_TWIZZY | -15.5 | 4 | 1 | 19 | -16.2 | 8/19 | 0 | 2.2 |
| Poké Bot | -18.3 | 8 | 6 | 19 | -17.4 | 9/19 | 0 | 2.6 |
| Joca | -37.1 | 2 | 0 | 19 | -36.9 | 2/19 | 0 | 2.6 |
| AIl IN | -37.9 | 4 | 2 | 19 | -41.7 | 3/19 | 0 | 2.5 |
| Anton | -62.1 | 4 | 3 | 19 | -60.9 | 7/19 | 0 | 4.1 |
| ediz_slow | -285.1 | 2 | 0 | 19 | -287.4 | 0/19 | 0 | 2.4 |

## 2. What the numbers say

### 2.1 Skill ranking differs from the leaderboard [DATA]
Non-whale means of the top group: Gherkers +39.9 (16 of 18 rounds positive), Phil AIvey
+35.0, Equity Engine +33.4, AAST +29.6, Astra La Vista +29.1, Resonance Qt +26.3 (16 of 18
positive), Kojack +21.9, Attention Is All In +9.0 (3 whale rounds of +144 to +189 carry its
total of +39.5).
[READING] Attention Is All In is a mid-table bot with whale luck; Gherkers, Phil AIvey and
Equity Engine are the real top tier; Phil AIvey, AAST and Astra are statistically level with us.
Sunday seeding uses whale-inflated totals, so Attention will be seeded above its skill.

### 2.2 Uploads during the tournament do not help on average [DATA]
114 version changes in counted rounds. Mean of the three rounds after minus the three before:
+4.3 bb/100, standard deviation 45, positive in 61 of 114. Notable cases: Durahim 1453 made 14
uploads and sits at +5.7; matcha mille crepes cake 11 uploads, +1.8; Lehman Brothers 8 uploads,
+10.8 and drifting down; Gherkers' last two uploads (v19 to v20, v20 to v21) were followed by
-71 and -77 and its total fell from +54.4 at round 12 to +47.8. Clearly positive uploads were
fixes to broken bots: Anton v3 to v4 (+239 from -131), ours v5 to v6 (+65, the all-in calling
fix), The Market Makers v7 to v8 (+70). Our v6 to v7 (V18) measured -8, within noise.
[READING] Most teams upload reactively after a bad round and then regress to the mean. Fast
iteration at the top can break what works. Upload only on evidence from paired tests
(`ab_vf.py`, standard error about 2.5 bb/100), never after a single bad round.

### 2.3 Static teams are predictable; fast iterators are not [DATA]
No uploads in counted rounds: Attention Is All In (v3), Kojack (v3), WBot (v5), ND (v1),
pokermon (v1), aydine (v1), Joca (v2), ediz_slow (v2), bigRoddy (v6), test (v2), Poke (v1).
Eight or more uploads: Gherkers (9), Durahim 1453 (14), matcha (11), Lehman Brothers (8).
[READING] Profiles of static teams built from Saturday hands remain valid on Sunday and in the
final; use strong priors and precomputed exploits. For fast iterators use weak priors and
in-round learning, and expect behaviour to change between rounds.

### 2.4 Measured leaks of specific opponents [DATA, replicas and playbook]
| Team | VPIP/PFR | Aggression | Fold to bet | Bluff share | Other |
|---|---|---|---|---|---|
| Attention Is All In | .28/.22 | .48 | .70 | .20 | folds to 3-bets 0.77 (n=48) |
| Gherkers | .28/.19 | .64 | .50 | .25 | raises bets 0.27, check-raises 0.12 |
| Equity Engine | .24/.17 | .49 | .39 | .18 | raise vs bet 0.17 |
| ND | .21/.11 | .30 | .38 | .12 | folds to 3-bets 0.03 (n=32) |
| Phil AIvey | .30/.20 | .20 | .45 | .08 | 3-bets against it fold through 0.39 |
| WBot | n/a | n/a | n/a | n/a | folds to 3-bets 0.72 (n=128), raises bets 0.21 |
| bigRoddy | .83/.34 | .45 | .54 | .35 | folds to c-bets 0.85, folds to 3-bets 0.03 |
| Joca | .66/.32 | .48 | .46 | .35 | folds to 3-bets 0.00 (n=39) |
| YSL_TWIZZY | n/a | n/a | .21 (n=116) | n/a | calling station |
| FisherMen | .42/.07 | n/a | n/a | air at showdown .26 | station pattern |
| ediz_slow | starter-kit pattern | | | | see `sparring/ediz_like.py` |

Field averages [DATA]: fold to a first postflop bet 0.51; fold to heads-up flop c-bet 0.55;
fold to turn barrel 0.32; fold to 3-bet 0.44 (break-even 0.66); fold to 4-bet 0.05; blinds
fold to steals 0.61 to 0.81 by position; big turn and river bets at showdown are monster 0.41,
top pair 0.26, weak pair 0.17, draw 0.07, air 0.10. Most bots decide from their own cards
and do not adapt to the opponent [READING from the playbook].

### 2.5 The field is not converging [DATA]
Standard deviation of round results across teams, by round: 103, 76, 80, 64, 58, 75, 66, 101,
67, 80, 59, 82, 77, 89, 67, 79, 60, 43, 60. No narrowing trend.
[READING] Nobody has found a large edge; gains are small and steady. Consistency beats bold
changes.

### 2.6 Timeouts [DATA]
Per round: Gherkers 2.9, Attention 1.5, Resonance Qt 1.2, Equity Engine 1.2, Astra 0.7.
Each timeout is an auto check or fold. Not a priority for us.

## 3. Structural facts about the format that interact with the above [DATA from the rules]
- Saturday average only seeds Sunday tables ("dealt like cards", mixing strong and weak).
- Sunday: top 2 by total chips at the table over 36 rounds go to the final.
- Final: 8 bots, 5,000 hands, most chips wins; 1st 500 pounds, 2nd 200, 3rd nothing.
- The bot never sees team names; a fresh agent is created every round; it can track every
  seat's running total within a round from `summary["stacks"]` (stacks reset to 2,000 each hand).
- Uploads: a new upload plays from the next round; uploads close Sunday 12:00. [OPEN] whether
  uploads reopen before Sunday 09:00.
- Hand histories (`fetch_hands.py`) give every seat's chip result per round; joined with the
  standings CSV by exact chip match, every seat we have faced can be given a team name.

## 4. Questions for you
1. From sections 1 and 2, which opponents matter most for (a) the rest of Saturday, (b) a
   Sunday table that mixes ranks, (c) the final, and what is the highest-EV adjustment against
   each, given opportunity counts per 100 hands?
2. How should prior strength per opponent depend on upload history (section 2.3), and how fast
   should in-round learning override it?
3. Given section 2.2, what release policy should we follow tonight and tomorrow morning?
4. What is the best way to use the Sunday table announcement at 20:30 and the final-table
   composition, within the constraint that the bot sees no names at runtime?
5. Anything in the data that contradicts the drafter's readings above.

## 5. What to return
A ranked strategy for the remaining Saturday rounds, Sunday and the final, with the data each
item rests on, the expected size in bb/100 where you can estimate it, the test each item must
pass before upload, and code where feasible. Reject or rewrite any reading above that the data
does not support.
