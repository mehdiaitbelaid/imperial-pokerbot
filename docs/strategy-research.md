# Strategy research brief: AlgoSoc Pokerbots

Scope: No-Limit Hold'em, 7 or 8 bots, 100bb every hand, 1,000 hands per round against the same opponents, score in bb/100. Spec: `README.md` in this kit.

Conventions in this brief:

* **[src]** means the claim comes from the linked page.
* **[own]** means it is my reasoning or arithmetic, not a sourced fact. Treat [own] numbers as starting points to tune in `local_sim.py`.
* **[kit]** means it comes from files in this kit (`README.md`, `engine/`, `examples/`, `tools/preflop.json`).
* Hand ranges use standard notation: `66+` is 66 through AA, `ATs+` is ATs, AJs, AQs, AKs. A range written "A2s to A5s" lists both ends.
* No code from any repo is reproduced here. Everything below is ideas and numbers.

Context that shapes every recommendation:

* Strong equilibrium play wins little. Pluribus beat elite pros at 6-max by 48 mbb/game, which is 4.8 bb/100, and it does not adapt to opponents at all [src: https://par.nsf.gov/servlets/purl/10119653]. The README shows a bot at +879 bb/100 against the house bots [kit]. The money in this event is in exploiting weak bots, not in approaching equilibrium [own].
* Under total bankroll scoring, exploiting weak opponents is what wins; under elimination scoring, defending your stack matters more [src: https://spectrum.ieee.org/a-texas-hold-em-tournament-for-ais]. Saturday's bb/100 ranking is a total bankroll format [own].
* The kit's house bots are a pure calling station (never folds, never raises), a random bot (uniform over legal actions, raises between the minimum and 3x the minimum), and a simple tight aggressive bot [kit: `examples/`]. Facing a bet, legal actions are fold, call, raise, so the random bot folds one third of the time regardless of bet size; with no bet it checks or raises half the time each [kit: `engine/game.py` line 302].

---

## 1. Top 10 actions

Ranked by expected bb/100 gain per hour of work. Gain estimates are [own] and assume a field like the brief describes (several stations, random and all-in spam bots, a few competent ones).

### 1. Bulletproof action wrapper and time guard (30 min)

* **What:** Every `act` call goes through one function that (a) wraps the whole decision in try/except, (b) on any error or deadline returns `call` if `to_call` is at most 5% of the pot and our hand is above median, else `check` if legal, else `fold`, (c) never returns `check` when `to_call > 0`, (d) clamps raise amounts into `[min_raise_to, max_raise_to]` and remembers that amounts are "raise to" totals for the street, (e) reads `betting` and `raise_cap` and falls back to call when raising is not legal.
* **Numbers:** Hard deadline 6 ms per decision measured with `time.perf_counter()` from the top of `act`. Track the 10 s bank yourself: stop Monte Carlo entirely if the bank used exceeds `elapsed_hands / total_hands * 8 s`.
* **Why it wins:** Returning `check` facing a bet is an automatic fold, and timeouts auto check or fold [kit: README]. Every fold of a strong hand to a 1 bb bet is a large leak; one exhausted bank turns the rest of the round into always fold, which loses about 19 bb/100 [kit: README]. Student bots written in a day will hit these bugs; yours must not [own].
* **Sources:** README of this kit. Time budgeting by street and remaining actions was the approach in an MIT Pokerbots 2024 entry under a 30 s per 1,000 hands limit [src: https://github.com/gtowizard-ai/mitpoker-2024].

### 2. Embedded 169 class preflop table and tight positional raise or fold ranges (1 h)

* **What:** Embed a dict of 169 hand classes to equity vs 1, 3 and 6 random hands (the kit already ships one in `tools/preflop.json`; check with organisers whether reusing it counts as event code, or regenerate it during the event). Map seat to position from `button` and `num_players`. Open raise or fold from the ranges in section 2. Never open limp.
* **Numbers:** Open size 2.5bb (50 chips) at a normal table, 3.5bb when two or more opponents are classified as stations. Opening widths: UTG about 10%, UTG1 12%, MP 15%, HJ 19%, CO 27%, BTN 42%, SB 32%.
* **Why it wins:** Preflop is where loose bots bleed most: a station that calls every open with any two cards gives you about 0.6 to 0.7 equity heads up with a top 10% hand [kit: `tools/preflop.json`, e.g. 88 is 0.685 vs one random hand]. Pluribus learned to drop limping entirely except from the SB [src: https://par.nsf.gov/servlets/purl/10119653].
* **Sources:** https://par.nsf.gov/servlets/purl/10119653, http://www.thepokerbank.com/videos/wilcox/articles/preflop-opening-ranges/, https://esports.gg/guides/betting/poker-positions (search result only).

### 3. Value bet thin and big, never pure bluff, against callers (1 h)

* **What:** Postflop, bet when your equity against the hands that will call is above 0.5, and size up against players who do not fold.
* **Numbers:** Heads up, bet when Monte Carlo equity vs the opponent's range is at least 0.55 (0.52 against a confirmed station). Size 75% to 100% pot on turn and river against stations. 3 way, bet only at equity at least 0.45 vs both; 4 or more players, at least 0.40 [own thresholds]. Profit of a called value bet is `B * (2w - 1)` where `w` is your win rate against the calling range [src], so against a pure never fold bot EV rises linearly with size; jam the river at `w >= 0.65` against a confirmed pure station [own].
* **Why it wins:** Stations do not tighten their calls as your bet grows, so thin value becomes profitable and bigger sizes earn more per call [src: https://poker.academy/blog/post/crush-calling-stations-your-guide-to-success]. The kit's own calling station is exactly this opponent [kit].
* **Sources:** https://poker.academy/blog/post/crush-calling-stations-your-guide-to-success, https://ocw.mit.edu/courses/15-s50-how-to-win-at-texas-holdem-poker-january-iap-2016/pages/assignments/.

### 4. Call all-in spam bots with a pure equity threshold (45 min)

* **What:** Detect bots that shove often (section 4) and call their shoves using the preflop table, not your normal 3bet or 4bet ranges.
* **Numbers [own arithmetic]:** Calling 2,000 to win 2,000 plus 30 blinds needs 2000 / 4030 = 49.6% equity (49.1% from the BB). Against a bot shoving any two cards, heads up with nobody left to act: call when equity vs 1 random hand is at least 0.53, which is the top 36.5% of hands (weakest included: K3s, J8s, K5o, T9s). With one live player still to act behind you: at least 0.58 (top 20%). If another player has already called: at least 0.36 vs 3 random hands, which is the top 7% (88+, ATs+, KJs+, AQo+). The 2 to 4 point margin covers the shover's range being better than random once it is not exactly any two.
* **Why it wins:** A call at 0.60 equity against a 2,000 chip shove earns about 0.2 x 4,030 = 800 chips, 40 bb, per occurrence [own]. One spam bot shoving every hand at an 8 bot table offers that several times per orbit. Stacks reset each hand, so there is no risk of ruin and pure chip EV is correct [kit: README].
* **Sources:** equity values from `tools/preflop.json` [kit]; pot odds formula call / (pot + call) [src: https://www.pokerstrategy.com/glossary/Pot-Odds/, search result only].

### 5. Build a realistic opponent pool and replay data before tuning anything (1 h)

* **What:** Write five or six throwaway opponents for `local_sim.py` that mimic the expected field: any two shover, min raiser, always call, random, a nit, and a tight aggressive bot. Download practice round histories with `fetch_hands.py` (practice runs 12:35 to 1:55) and measure real opponents' VPIP, PFR, shove rate and fold to bet. Tune thresholds against that mix with `--rounds 20` and fixed seeds.
* **Numbers:** At least 20 rounds of 1,000 hands per configuration before trusting a difference smaller than about 10 bb/100 [own; measure the actual spread in your runs].
* **Why it wins:** Iteration speed beats sophistication when time is short; one student team spent its time on CFR that never transferred to the real game and shipped a simple adaptive bot instead [src: https://charlescardot.github.io/2024-05-04-Poker-Bot]. The ACPC organisers stress enough hands with memory wiped between matches so luck does not decide [src: https://spectrum.ieee.org/a-texas-hold-em-tournament-for-ais].
* **Sources:** above, plus README `fetch_hands.py` section [kit].

### 6. Monte Carlo equity against range conditioned opponents, with pot odds and a margin (1.5 h)

* **What:** Postflop, sample opponent holdings from their likely range rather than uniformly: keep only hole card classes inside their observed VPIP percentage (ranked by equity vs one random hand), narrowed to their PFR percentage if they raised preflop. Run Monte Carlo to the river within the time budget. Call when equity exceeds pot odds plus a margin.
* **Numbers:** Required equity = to_call / (pot + to_call) [src]. Margins [own]: +0.05 flop, +0.04 turn, +0.02 river; 0 against maniacs and spam bots; +0.10 against nits whose bets are strong. Budget: about 3 ms of simulation per decision. The kit evaluator ran about 240,000 seven card evaluations per second on my machine [own measurement], so 3 ms gives roughly 700 evaluations, about 200 to 350 rollouts at 1 to 2 opponents, a standard error near 0.03. Assume the sandbox core may be slower and measure `think s/rd`.
* **Why it wins:** Equity against a random hand overstates your strength against anyone who bets, and understates it against spam. Loki and Poki weighted each possible opponent holding by how likely the observed actions made it [src: https://www.cs.ualberta.ca/~games/poker/publications/AAAI98.pdf, search result only]. A Monte Carlo win rate with a 1/players call rule is the PyPokerEngine baseline and loses to a fish because it only plays strong hands passively [src: https://ishikota.github.io/PyPokerEngine/tutorial/estimate_card_strength], so add aggression from item 3.
* **Sources:** https://ishikota.github.io/PyPokerEngine/tutorial/estimate_card_strength, https://www.mit.edu/~jlrubin/projects/pokerbots (Monte Carlo accuracy was not their bottleneck), https://github.com/rickbutton/poker (EV of call from win probability times pot).

### 7. Per opponent stats with shrinkage and a small classifier (1.5 h)

* **What:** Track per seat counts (section 4), blend them with a population prior, classify each opponent every 25 hands, and switch exploit parameters per class.
* **Numbers:** Blend observed frequency with a prior as `(prior_rate * N_prior + count) / (N_prior + opportunities)` [src: https://www.cs.huji.ac.il/~jeff/aamas11/papers/B4_R56.pdf, which used N_prior = 5]. Use N_prior = 10 for preflop stats and 20 for postflop stats [own]. Do not act on a stat with fewer than 10 opportunities [src: https://www.blackrain79.com/2017/11/poker-hud-stat-sample-size.html says 5 to look, 10 to be confident].
* **Why it wins:** In the DBBR experiments, modelling plus best response raised win rate over the equilibrium baseline from 0.58 to 0.93 small bets per hand against AlwaysCall, 0.85 to as much as 2.29 against Random, and 0.79 to 1.39 against AlwaysRaise [src: https://www.cs.huji.ac.il/~jeff/aamas11/papers/B4_R56.pdf]. An MIT IAP team placed second by tracking stats and adjusting aggression and looseness to counter each opponent [src: https://www.mit.edu/~jlrubin/projects/pokerbots].
* **Sources:** above, plus https://arxiv.org/abs/1401.4591 on restricted Nash responses exploiting more than equilibrium while staying hard to exploit.

### 8. Isolate limpers and steal from nits (45 min)

* **What:** When one or more players limp, raise for value with a range about one position tighter than your open; steal the blinds when the remaining players are nits.
* **Numbers:** Iso size 3bb plus 1bb per limper online, plus 1bb more from the blinds; size up further if players call too often [src: https://pokertrainer.se/how-to-win-money-from-limpers/]. Against bots I would start at 4bb plus 1bb per limper, since limping bots rarely fold [own]. Steal from CO, BTN, SB with the BTN range (42%) or wider (up to 60%) when both blinds fold to steals at least 75% over 15 or more opportunities [own].
* **Why it wins:** Limpers are the loose passive bots; isolating them gets you heads up in position with a range advantage, and the linear 3bet idea gives the same effect against weak raisers [src: https://www.pokernews.com/strategy/the-three-betting-decision-most-players-never-make-52292.htm].
* **Sources:** https://pokertrainer.se/how-to-win-money-from-limpers/, https://ocw.mit.edu/courses/15-s50-how-to-win-at-texas-holdem-poker-january-iap-2016/pages/assignments/ (steal against blinds that fold unless strong).

### 9. Bluff only against measured folders, heads up, small (45 min)

* **What:** Turn on c-bet bluffs and river bluffs only against opponents whose measured fold rate beats the break-even fold frequency for the size you choose, and only heads up.
* **Numbers:** Break-even fold frequency = bet / (pot + bet): 25% pot needs 20%, 33% needs 25%, 75% needs 43%, 150% needs 60% [src: https://poker.academy/blog/post/crush-calling-stations-your-guide-to-success]. Rule [own]: bluff c-bet 33% pot when the opponent's shrunk fold to flop bet is at least 0.45 over 10 or more opportunities; second barrel only when fold to turn bet is at least 0.55 over 10 or more. Against the kit's random bot, which folds exactly one third to any bet, bluffs at half pot or less break even or better (half pot needs 33%) [own from kit engine]. Multiway: no pure bluffs.
* **Why it wins:** Bluffs against folders are pure profit; bluffs against stations are the main leak of weak exploiters [src: https://poker.academy/blog/post/crush-calling-stations-your-guide-to-success]. Multiway, solvers bet much less often and mostly small [src: https://www.pokernews.com/strategy/this-is-how-the-pro-s-play-multiway-pots-51467.htm].
* **Sources:** above.

### 10. Exploit min raisers and deterministic bots (1 h)

* **What:** Detect bots whose raises are almost always the legal minimum, and bots whose action is a fixed function of public state or bet size; exploit the fixed function.
* **Numbers [own]:** Min raiser if at least 70% of 8 or more raises equal the legal minimum: 3bet them for value with a linear range (88+, ATs+, KJs+, QJs, AJo+, KQo, the linear example given at https://www.pokernews.com/strategy/the-three-betting-decision-most-players-never-make-52292.htm), call their postflop min raises with any pair or 8 out draw, never fold top pair to them. Deterministic if, for one public situation key (street, facing bet size bucket, position), the same action appears at least 95% of the time over 15 or more observations. If its fold decision depends only on size (always folds to more than X pot, always calls at or below X), bet just over X with air and at X with value.
* **Why it wins:** Rule based bots built in a day are often threshold functions of `to_call` or `pot`. A threshold known exactly is exploited with zero risk [own]. Opponent models built only from observed action frequencies are designed to exploit after a small number of interactions, and in DBBR they did best against the naive fixed bots [src: https://www.cs.huji.ac.il/~jeff/aamas11/papers/B4_R56.pdf].
* **Sources:** above.

---

## 2. Preflop

### 2.1 Positions

Compute position as `(seat - button) mod num_players` over seats still in the hand at deal time [own]. For 8 players: 0 BTN, 1 SB, 2 BB, 3 UTG, 4 UTG1, 5 MP, 6 HJ, 7 CO. For 7 players drop UTG1.

### 2.2 Encoding

Two encodings work; use both [own]:

* **Hand class lists** below, built for this event by me from the 6-max TAG chart at http://www.thepokerbank.com/videos/wilcox/articles/preflop-opening-ranges/ (UTG 12.5%, CO 23.4%, BTN 40%, SB 22.5%) tightened for 8 handed early seats in line with 9-max UTG widths of about 8% to 12% and BTN 30% to 45% reported by https://esports.gg/guides/betting/poker-positions (search result only).
* **Percent by equity rank:** rank the 169 classes by equity vs one random hand from `tools/preflop.json`, accumulate combos (pairs 6, suited 4, offsuit 12, total 1,326) and cut at the target percentage. Cut points from that table [kit, computed by me]: top 3% ends at 88, 5% at AQs, 8% at ATs, 11% at K9s, 14% at A9o, 17% at 55, 22% at A6o, 28% at QTo, 35% at K5o, 45% at T7s. This ordering overrates offsuit aces and underrates suited connectors for multiway pots; for multiway use the equity vs 3 random hands ranking instead.

### 2.3 Open raise ranges, 8-max, 100bb, unopened pot

| Position | Approx % | Hands | Combos |
|---|---|---|---|
| UTG | 9.8% | 66+, ATs+, KTs+, QTs+, JTs, AQo+, KQo | 130 |
| UTG1 | 11.8% | UTG plus 55, A9s, T9s, AJo | 156 |
| MP | 15.2% | 22+, A9s+, A2s to A5s, KTs+, QTs+, JTs, T9s, AJo+, KJo+ | 202 |
| HJ | 19.5% | 22+, A2s+, K9s+, Q9s+, J9s+, T9s, 98s, 87s, ATo+, KJo+, QJo | 258 |
| CO | 26.7% | HJ plus K7s, K8s, Q8s, J8s, T8s, 97s, 76s, 65s, 54s, A8o, A9o, KTo, QTo, JTo | 354 |
| BTN | 42.4% | 22+, A2s+, K2s+, Q5s+, J7s+, T7s+, 96s+, 86s+, 75s+, 64s+, 54s, 43s, A2o+, K8o+, Q9o+, J9o+, T9o, 98o | 562 |
| SB (raise or fold) | 31.5% | 22+, A2s+, K5s+, Q8s+, J8s+, T8s+, 97s+, 86s+, 75s+, 65s, 54s, A5o+, K9o+, QTo+, JTo | 418 |

Sizing [own]: 2.5bb from UTG to BTN, 3bb from SB. Against tables with two or more stations, 3.5bb to 4bb with the same range, since stations call regardless of size and a value range gains from a bigger pot [src for the principle: https://poker.academy/blog/post/crush-calling-stations-your-guide-to-success].

### 2.4 Facing one raise: 3bet, call, fold

Default (opener unknown or normal, VPIP 15% to 35%) [own, shaped by the polarized vs linear guidance at https://www.pokernews.com/strategy/the-three-betting-decision-most-players-never-make-52292.htm]:

| Opener's position | 3bet for value | Call (in position or BB) | 3bet bluff |
|---|---|---|---|
| UTG, UTG1 | QQ+, AKs, AKo | 22 to JJ, AQs, AJs, KQs, QJs, JTs (BB also AQo, ATs, KJs) | none |
| MP, HJ | JJ+, AQs+, AKo | 22 to TT, ATs to AJs, KJs+, QJs, JTs, T9s, AQo | A5s, A4s only vs folders |
| CO, BTN, SB steal | TT+, AJs+, KQs, AQo+ | 22 to 99, A2s to ATs, KTs+, QTs+, J9s+, T9s, 98s, 87s, AJo, KQo | A5s to A2s vs folders |

* 3bet size: 3x the open in position, 4x out of position [own convention].
* BB defend vs a 2.5bb steal: you call 1.5bb to win 4bb, needing 27% equity [own arithmetic with the pot odds formula]. Defend roughly the top 40% by equity vs one random hand against openers with VPIP above 35%; top 25% against normal openers [own].
* Against loose openers (VPIP at least 35% with 50 or more hands) and stations: switch to a linear 3bet range: 88+, ATs+, KJs+, QJs, AJo+, KQo [src: https://www.pokernews.com/strategy/the-three-betting-decision-most-players-never-make-52292.htm, linear example]. Linear is also recommended out of position and against habitual callers [same src].
* Against min raisers: same linear range, size 4x their raise [own].

### 2.5 Facing a 3bet

* 4bet for value: KK+, AKs; add QQ and AKo against 3bettors with 3bet rate at least 10% over 50 or more opportunities [own].
* 4bet size: 2.2x to 2.5x the 3bet in position, 2.5x to 3x out of position [search result summary of 3bet and 4bet guides, low confidence; listed in Sources].
* Call the 3bet: JJ, TT, AQs, AJs, KQs in position. Fold the rest [own].
* Facing a 4bet: jam or call with QQ+, AK; fold everything else unless the 4bettor is a spammer [own].

### 2.6 Facing a preflop all-in

Use section 1 item 4 thresholds. Summary [own from `tools/preflop.json`]:

| Situation | Call if equity vs random at least | Approx share of hands |
|---|---|---|
| Any two shover, heads up, nobody behind | 0.53 (vs 1) | 36.5% |
| Any two shover, one player still to act | 0.58 (vs 1) | 20% |
| Any two shover plus one caller already in | 0.36 (vs 3) | 7% |
| Shover with tighter shown hands (avg shown equity vs 1 above 0.60) | treat as a top 20% range: call QQ+, AKs, AKo only | 3% |

### 2.7 Adjustments by table type

**Loose passive table** (three or more opponents with VPIP above 40% and PFR below 10%) [own unless marked]:

* Tighten UTG and UTG1 by about 2 points (drop 66, KTs, QTs) because you will see multiway pots out of position.
* Widen value: raise larger, 3.5bb to 4bb, and iso limpers at 4bb plus 1bb per limper [src: https://pokertrainer.se/how-to-win-money-from-limpers/ for the 3bb plus 1bb base].
* Never open speculative hands to "see a cheap flop": the iso raise with a value range is the profit source.
* Do not widen opens with hands that only win by making the station fold later [src: https://poker.academy/blog/post/crush-calling-stations-your-guide-to-success].

**Maniac or all-in spam table** (one or more opponents shoving or raising more than 30% of hands) [own unless marked]:

* Tighten opens from all seats to about the HJ range or tighter when the spammer is still to act behind you; your open will often face a shove and you want to be calling with equity at least 0.58.
* Open with the hands you are happy to call a shove with; fold the bottom of the range rather than open and fold to the shove.
* Trap: with QQ+, AK in the BB or facing a maniac's open, flat or min 3bet to let them keep betting [src: Card Player articles on maniacs, search result only; see Sources].
* Bluff catch wider postflop: call margin 0 against their bets [src: https://www.blackrain79.com/2023/01/crazy-poker-player.html, search result only].

---

## 3. Postflop

### 3.1 Inputs

At each postflop decision compute [own]:

* `n` active opponents.
* `eq`: Monte Carlo equity vs the range conditioned opponents of section 1 item 6, within the time budget.
* `req` = to_call / (pot + to_call) [src: https://www.pokerstrategy.com/glossary/Pot-Odds/, search result only].
* Each opponent's class from section 4.

### 3.2 Sizing rules

| Spot | Size | Basis |
|---|---|---|
| Heads up c-bet, value or bluff vs folders | 33% pot | small bets need few folds: 33% needs 25% [src: poker.academy station guide] |
| Heads up value vs stations, turn and river | 75% to 100% pot; jam river at eq at least 0.65 vs pure station | stations do not fold more to bigger bets [src: same] |
| Multiway c-bet (3 or more players) | 33% pot, value only | solver prefers about 20% to 33% multiway and checks most hands [src: https://www.pokernews.com/strategy/this-is-how-the-pro-s-play-multiway-pots-51467.htm] |
| Raise for value facing a bet | raise to 3x the bet | [own] |
| Wet board with a strong made hand vs callers | 75% pot | charge draws [own] |

A sizing set of 2 to 4 sizes is enough; a bot designer reported using two sizes 95% to 98% of the time [src: https://mattmazur.com/2010/10/04/poker-bot-strategy-for-postflop-play/]. Use 33%, 75% and all-in [own].

### 3.3 Continuation bets

* **Heads up as the preflop raiser [own]:** bet when eq at least 0.55 (value), or eq at least 0.35 with a draw of 8 or more outs (semi bluff), or the opponent's shrunk fold to flop bet is at least 0.45 (pure bluff, 33% pot). Otherwise check.
* **Multiway [own, consistent with the solver summary in https://www.pokernews.com/strategy/this-is-how-the-pro-s-play-multiway-pots-51467.htm]:** bet only when eq vs all at least 0.45 with 2 opponents or at least 0.40 with 3 or more. No bluffs. Out of position multiway, check most hands and check raise strong ones.
* **Turn barrel:** value only against stations and maniacs; against folders barrel with eq at least 0.30 when fold to turn bet at least 0.55 [own].

### 3.4 Value vs bluff by opponent type

| Opponent | Value threshold (heads up) | Bluff | Notes |
|---|---|---|---|
| Station | eq at least 0.52 vs their range | never pure; semi bluff only strong draws | lead or check raise strong hands out of position rather than hoping they bet [src: poker.academy station guide] |
| Folder / nit | eq at least 0.60 (they call only strong) | yes, 33% pot, flop and turn | fold to their bets unless eq beats req + 0.10 [own] |
| Maniac / spammer | eq at least 0.55; prefer check call to let them bet | never | call margin 0; trap [src: Card Player and blackrain79, search results] |
| Random bot | eq at least 0.55, size big | half pot or less breaks even | folds exactly one third of the time facing any bet [kit] |
| Unknown / solid | eq at least 0.58 | c-bet 33% only heads up in position | play straightforward |

Caveat: some stations reach the turn wide then fold most of it to a further bet, so their river range is strong; check river fold rates per opponent before value betting thin on the river [src: Jonathan Little, Card Player, search result only; see Sources].

### 3.5 Calling and raising facing a bet

* Call when `eq >= req + margin`; margins +0.05 flop, +0.04 turn, +0.02 river; 0 vs maniac or spammer; +0.10 vs nit [own].
* Raise when eq vs their betting range is at least 0.70 (0.65 vs maniacs) [own].
* Multiway: a bet into several players represents strength; add +0.05 to the margin per extra live opponent behind you [own].
* Facing all-in postflop: call when eq at least req, no margin, against spammers; req + 0.05 otherwise [own].

---

## 4. Opponent modelling

### 4.1 Stats to track per seat

Count opportunities, not hands. Sample sizes are the HUD guidance from https://www.blackrain79.com/2017/11/poker-hud-stat-sample-size.html [src]; the "act from" column is mine [own] because one round gives 1,000 hands per opponent and the DBBR paper shows waiting too long forfeits most of the edge while acting too early on thin data caused an early dip against AlwaysRaise [src: https://www.cs.huji.ac.il/~jeff/aamas11/papers/B4_R56.pdf].

| Stat | Definition | Source sample | Act from (with shrinkage) |
|---|---|---|---|
| VPIP | put chips in voluntarily preflop / hands dealt | 20 hands | 20 hands |
| PFR | raised preflop / hands dealt | 20 hands | 20 hands |
| Shove rate | all-in raises / hands dealt | not covered | 10 hands, or 3 shoves |
| Min raise share | raises equal to legal minimum / raises | not covered | 8 raises |
| AF | (bets + raises) / calls, postflop | 100 hands | 40 postflop actions |
| 3bet % | 3bets / chances to 3bet | 100 hands | 30 chances |
| Fold to 3bet | folds / times facing 3bet | 100 hands | 10 chances |
| Fold to flop c-bet | folds / times facing a flop bet | 100 hands | 10 chances |
| Fold to turn bet | folds / times facing a turn bet | 300 hands | 10 chances |
| Fold to river bet | folds / times facing a river bet | 1,000 hands | 15 chances |
| Fold by size bucket | fold rate facing bets of at most 0.5 pot, 0.5 to 1 pot, over 1 pot, all-in | not covered | 8 per bucket |
| Showdown hands | equity vs random of every shown hand, tagged with the line taken | n/a | every showdown |

Shrink every rate toward a population prior as in DBBR: `(prior * N_prior + count) / (N_prior + opportunities)` [src: https://www.cs.huji.ac.il/~jeff/aamas11/papers/B4_R56.pdf, N_prior = 5 there]. Set the priors from practice round data pulled with `fetch_hands.py` [own].

### 4.2 Classes, thresholds and exploits [own thresholds unless marked]

| Class | Detection | Exploit |
|---|---|---|
| All-in spammer | shove rate at least 15% after 20 hands, or at least 50% of its raises are all-in with 4 or more raises, and shown hands average below 0.55 equity vs random | call shoves per section 2.6; open only hands you would call a shove with; never bluff |
| Always call (station) | fold rate facing a bet below 5% over 20 or more bets faced, raise rate below 5% | value bet down to eq 0.52, size 75% to 100%, jam river at 0.65; zero bluffs |
| Min raiser | at least 70% of 8 or more raises equal the legal minimum | linear 3bet, raise their min bets for value, call down with any pair |
| Random | facing a bet: fold, call and raise each near one third (each within 0.23 to 0.43) over 30 or more decisions; raise sizes spread between minimum and 3x minimum; VPIP about 65% or higher | value bet big, bluff only at half pot or less, call its raises with eq above the median |
| Deterministic / threshold | same action at least 95% of the time for one public situation key over 15 or more observations; or fold rate by size bucket is near 0 below some size and near 1 above it | find the threshold X and bet just over X with air, at or below X with value |
| Nit | VPIP below 12% after 50 hands | steal its blinds with up to 60% of hands; fold to its raises unless top 3% (88+, AQs+, AKo); bluff c-bet when it calls preflop then folds flop |
| Maniac | VPIP above 45% and PFR above 25%, or AF above 3 over 40 actions | call down wider (margin 0), trap with strong hands, no bluffs [src: maniac articles in Sources] |
| Loose passive | VPIP above 40%, PFR below 10%, AF below 1 | treat as station preflop and postflop; iso raise its limps |
| Folder | fold to flop c-bet at least 0.60 or fold to 3bet at least 0.70 | bluff c-bet 33%, steal, 3bet light with A2s to A5s |
| Solid | VPIP 15% to 30%, PFR/VPIP above 0.7 | baseline ranges; no fancy exploits; avoid big pots without strong hands |

Detection notes [own]:

* Infer each raise's legal minimum from the history: the minimum raise to is the current bet plus the larger of the last raise increment on that street and the big blind (README betting rules).
* A deterministic bot has a near zero entropy action distribution per situation key; random has near maximum entropy. Compute both from counts.
* Showdowns are the only window into hidden cards. A bot that open shoves and shows 72o or 83o is random in range even if its action frequencies look tight.
* Re-classify every 25 hands and let a class change only after two consecutive checks agree, to avoid flapping [own].
* Cap the deviation: keep baseline play until a stat crosses its "act from" count, and only switch on bluff exploits after you are winning against that seat. The DBBR authors suggest enabling exploitation against strong opponents only when the win rate passes a threshold [src: https://www.cs.huji.ac.il/~jeff/aamas11/papers/B4_R56.pdf]. Restricted Nash responses formalise the trade of exploitation against exploitability [src: https://arxiv.org/abs/1401.4591; original NIPS 2007 paper at https://www.cs.ualberta.ca/~games/poker/publications/NIPS07-rnash.pdf, not opened]. A Fullhouse Hackathon 2026 finalist describes the same design, adapting per opponent but capped near a baseline [src: https://www.linkedin.com/in/akbw, search snippet only].

---

## 5. Tournament structure plays

### 5.1 Stacks reset every hand

* Effective stack is always 100bb at the start of every hand; there are no short stack push or fold spots and no ICM [kit: README]. Each hand is independent, so maximise chip EV per hand. Take every positive EV all-in, including coin flips with a small edge [own].
* Busting is impossible, so opponents never tighten for survival and spam bots never run out of chips: their leak persists all round [own].

### 5.2 Saturday: bb/100 over all counted rounds

* Counted rounds run every 5 minutes from 3:00 to 7:25, so about 54 rounds, around 54,000 hands [own count from README times]. At that volume EV dominates; play pure EV [own].
* Memory is wiped each round, so the first 50 to 100 hands of every round run on priors. Good priors from practice data are worth more than a clever late game model [own].
* Uploads apply from the next round, so you can fix a leak found in the hand histories mid afternoon [kit: README].

### 5.3 Sunday bucket table: top 2 by chips

* You must finish ahead of 5 or 6 of the 7 others, not first. Exploiting the weakest bots at the table is still the main lever [own].
* The bot cannot see cumulative standings (no network, memory wiped). Variance control has to come from the team swapping uploads between rounds [own]:
  * Comfortably in the top 2 late: upload a lower variance version that skips marginal all-in calls (equity within 0.03 of break-even) and marginal bluffs.
  * Third or worse late: upload a version that takes every flip with equity at least break-even and widens shove calls by 2 to 3 points.
* Keep both versions built and tested before Sunday morning [own].

### 5.4 Final: 5,000 hands, most chips

* Read `hands` from `on_table_start` info and never hardcode 1,000; rescale the time budget to the bank actually reported or observed [own].
* If the 5,000 hands are one round with one `Agent`, the model keeps learning for 5,000 hands: the "act from" thresholds in section 4 become cheap, and late exploitation can be sharper [own].
* Variance [own estimate, measure it]: if the per 100 hands standard deviation is around 100 to 150 bb in a field with spam all-ins, the standard deviation over 5,000 hands is about 7 times that, roughly 700 to 1,050 bb. An edge of 20 bb/100 over a rival gives 1,000 bb expected, about one standard deviation. Small edges are not safe in the final; the bot with the largest exploitation edge wins most often.
* When to gamble [own]: never deliberately add variance with the bot itself, since it cannot see standings. Finalists are the strongest bots, so expect fewer spammers and more solid players; keep bluff exploits gated on measured fold rates.

---

## 6. Traps

* **Timeouts and the time bank.** 10 ms per decision includes the state transfer; anything over is auto check or fold, and an empty bank auto plays the rest of the round [kit: README]. Monte Carlo without a deadline, rebuilding tables inside `act`, and heavy printing are the usual causes [own].
* **Wrong action semantics.** `check` facing a bet folds; raise amounts are "raise to" totals; `all_in` becomes a call when raising is not allowed [kit: README].
* **Hardcoding the format.** Tables are 7 or 8 bots; organisers may switch to pot limit, fixed limit or a raise cap; read `betting`, `raise_cap`, `num_players` every time [kit: README].
* **Over bluffing stations.** Pure bluffs against calling stations lose; even semi bluffs need care [src: https://poker.academy/blog/post/crush-calling-stations-your-guide-to-success; PokerStrategy glossary on calling stations, search result only].
* **Multiway bluffs and wide multiway c-bets.** Betting frequency drops sharply multiway [src: https://www.pokernews.com/strategy/this-is-how-the-pro-s-play-multiway-pots-51467.htm].
* **Fancy play.** Slowplaying against passive bots loses value because they will not bet for you; lead or check raise instead [src: poker.academy station guide]. Polarized 3bet bluffing is wasted against bots that never fold [own].
* **Folding too much.** A Fullhouse Hackathon 2026 finalist reports its bot played too cautiously in the finals and folded too often in close spots [src: https://www.linkedin.com/in/akbw, search snippet only]. Against spam, wide calls are correct.
* **Acting on thin data.** Early exploitation from an unexplored model cost DBBR money against AlwaysRaise for several hundred hands [src: https://www.cs.huji.ac.il/~jeff/aamas11/papers/B4_R56.pdf]. An opponent can also play one way to bait an exploit, the "get taught and exploited" problem described there [same src].
* **Building CFR in a day.** One student team could not make its abstracted CFR transfer to the real game and dropped it [src: https://charlescardot.github.io/2024-05-04-Poker-Bot]. Even a strong MIT 2024 entry reports that a heuristic equity evaluation at the depth limit was not strong enough, and that a precomputed blueprint would have been better given more time [src: https://github.com/gtowizard-ai/mitpoker-2024]. The winning MIT 2017 bot used CFR with hand bucketing [src: https://github.com/Fro116/Pokerbots], but over a month, not a day.
* **Sandbox misuse.** CPU use off turn, memory over 512 MB, or flooding the dealer stops the bot for the round [kit: README]. No threads, no background work [own].
* **Nondeterminism surprises.** Python string hashing is randomised per process; do not key anything that must be stable on `hash()` of strings [own].
* **Trusting equity vs random.** Equity vs a random hand overrates your hand against anyone who bets and raises; condition on range [own; see section 1 item 6].

---

## 7. Sources

Fetched and read during this task:

* https://par.nsf.gov/servlets/purl/10119653 : Pluribus paper (Science 2019). 48 mbb/game vs pros, no opponent adaptation, limping dropped from the blueprint, frequent donk bets, 1 to 14 bet sizes per decision.
* https://www.cs.huji.ac.il/~jeff/aamas11/papers/B4_R56.pdf : Ganzfried and Sandholm, DBBR. Dirichlet shrinkage with N_prior = 5, 1,000 hand warmup, model updated every 50 hands, win rates vs Random, AlwaysCall, AlwaysRaise, early dip from unexplored lines, gating exploitation on win rate.
* https://arxiv.org/abs/1401.4591 : MCRNR abstract. Restricted Nash responses exploit more than equilibrium while staying hard to exploit.
* https://www.mit.edu/~jlrubin/projects/pokerbots : MIT IAP 2nd place new team bracket. Stats tracking to adjust aggression and looseness; Monte Carlo equity accuracy was not the bottleneck.
* https://github.com/Fro116/Pokerbots : MIT Pokerbots 2017 winner. CFR with hand bucketing and off tree handling.
* https://github.com/gtowizard-ai/mitpoker-2024 : MIT 2024 entry. Per street time manager under a 30 s per 1,000 hands budget, equity heuristic limits, blueprint would have been stronger.
* https://charlescardot.github.io/2024-05-04-Poker-Bot : student bot postmortem. CFR abstraction failed to transfer; a simple adaptive bot converged in 500 to 1,000 hands; Python too slow for heavy Monte Carlo.
* https://github.com/ngnnah/python_AutonomousPokerbot : MIT student bot. Precomputed hand strengths, randomisation, pot odds, tight aggressive.
* https://github.com/rickbutton/poker : Purdue 5 hour hackathon bot. EV of call from win probability and pot, more aggression above 50% win probability.
* https://github.com/pedro-hdt/htb19 : Hack The Burgh 2019 second place. Probability plus a bluffing heuristic; little detail.
* https://ishikota.github.io/PyPokerEngine/tutorial/estimate_card_strength : PyPokerEngine Monte Carlo win rate and the "call if win rate at least 1/players" rule, which lost to a fish.
* https://spectrum.ieee.org/a-texas-hold-em-tournament-for-ais : ACPC total bankroll rewards exploitation, instant runoff rewards defence; many duplicate hands with memory wiped.
* https://www.pokernews.com/strategy/poker-ai-2016-annual-computer-poker-competition-24246.htm : ACPC 2016. Top four used CFR; equilibrium bots cannot exploit; Slumbot won instant runoff.
* https://poker.academy/blog/post/crush-calling-stations-your-guide-to-success : break-even fold frequencies by size, `B(2w-1)` value formula, thinner and bigger value, no bluffs, lead strong hands out of position.
* https://www.blackrain79.com/2017/11/poker-hud-stat-sample-size.html : HUD stat sample sizes (VPIP and PFR 20 hands, AF and c-bet 100, turn 300, river 1,000; 5 opportunities to look, 10 to trust).
* http://www.thepokerbank.com/videos/wilcox/articles/preflop-opening-ranges/ : 6-max TAG opening hand lists and percentages, base for section 2.3.
* https://www.pokernews.com/strategy/this-is-how-the-pro-s-play-multiway-pots-51467.htm : solver multiway output: small c-bets around 20%, polarized turn, mostly checking the middle.
* https://www.pokernews.com/strategy/the-three-betting-decision-most-players-never-make-52292.htm : polarized vs linear 3bets, linear example range, linear against callers and out of position.
* https://pokertrainer.se/how-to-win-money-from-limpers/ : iso raise 3bb plus 1bb per limper online, plus 1bb from the blinds, tighter range out of position and multiway.
* https://ocw.mit.edu/courses/15-s50-how-to-win-at-texas-holdem-poker-january-iap-2016/pages/assignments/ : MIT OCW poker course; value bet callers, bluff folders, steal from blinds that fold too much.
* https://mattmazur.com/2010/10/04/poker-bot-strategy-for-postflop-play/ : bot design memo; weighted ranges, two bet sizes most of the time.
* Kit files: `README.md` (rules, limits, scoring), `examples/` (house bots), `engine/game.py` (legal actions), `tools/preflop.json` (equity of 169 classes vs 1, 3, 6 random hands, used for all cut points here).

**Not verified (appeared in search results only; the page could not be opened or was not opened):**

* https://www.cs.ualberta.ca/~games/poker/publications/NIPS07-rnash.pdf : Johanson, Zinkevich, Bowling, restricted Nash response (NIPS 2007). Redirects ended in 404.
* https://www.cs.ualberta.ca/~games/poker/publications/AAAI98.pdf : Billings et al., opponent modelling in Loki with per opponent weight tables. Redirects ended in 404.
* https://esports.gg/guides/betting/poker-positions : 9-max opening widths (UTG 8% to 12%, CO 20% to 28%, BTN 30% to 45%). Fetch returned 403.
* https://www.linkedin.com/in/akbw : Fullhouse Hackathon 2026 finalist post (Thorp bot): capped adaptation, too many folds in close spots in the finals. Snippet only.
* https://arxiv.org/pdf/1701.01724 : DeepStack, continual re-solving with a value network; first to beat pros at heads up no limit. Context only.
* https://www.ijcai.org/proceedings/2017/772 : Libratus, blueprint plus nested subgame solving plus self improver; 147 mbb/hand (14.7 bb/100) over 120,000 hands. Context only.
* https://www.pokerstrategy.com/glossary/Pot-Odds/ : pot odds formula call / (pot + call).
* https://www.blackrain79.com/2023/01/crazy-poker-player.html and https://cardplayer.com/cardplayer-poker-magazines/65706-glen-chorny-21-10/articles/17540-playing-against-a-maniac : call down wider, do not bluff maniacs, control pot size to induce bluffs.
* https://cardplayer.com/poker-news/21274-poker-strategy-with-jonathan-little-combating-calling-stations : some stations fold most of their range to a turn or river bet, so their river range is strong.
* https://www.pokerstrategy.com/glossary/Calling-station/ : never bluff a calling station, be careful with semi bluffs.
* https://vip-grinders.com/how-to-3-bet : 4bet sizing 2.2x to 2.5x in position, 2.5x to 3x out of position (low confidence summary).

X/Twitter: `x.com` search returned HTTP 402, the nitter.net mirror returned only a project notice, and site filtered web searches returned no posts. No X content is used in this brief.
