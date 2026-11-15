# Final table: where we stand, what v15 changed, and what to do before 12:00

Written Sun 15 Nov 2026, about 10:40 UK time, by Claude for Resonance Qt (Saeed, Mehdi, Riyad, Hassan).

**Data used:**
- Our Sunday hands, rounds 1–13 (13,000 hands), and the public standings at 10:03.
- All 54 of our Saturday counted rounds (54,000 hands), re-read for the teams likely to reach the final.
- The two bot files: upload v14 (SHA `9a5d1af58a51e822`) and upload v15 (SHA `2298973fea29cff0`, live since round 8).

**Limits:** we only see hands from our own tables. For teams at other Sunday tables, the style numbers are from Saturday, and some of those teams have clearly changed their bots since.

---

## 1. Summary

1. **We lead our table on +83,473 after 13 of 36 rounds.** Anker is 2nd on +55,341 and Poke 3rd on +17,809. That is the highest chip count at any of the four tables.
2. **v15 is v14 with one new rule.** On the turn or river, a call of 500 chips or more with one pair or less now needs 15 points more equity. The only other change is a tighter rule for recognising Poke.
3. **v15's results are much better, but the code is not the main reason.**
   - v14, rounds 2–7: +26,569 (+22 bb/100). Without all-in luck: +12,486.
   - v15, rounds 8–13: +56,146 (+47 bb/100). Without all-in luck: +39,312.
   - The gap is about one standard error on six rounds each, so it is suggestive and not proven.
4. **96% of v15's chips came from the four losing bots** (WBot, YSL_TWIZZY, GamesGone, Anton). Against the three winning bots at the table (Anker, Poke, Chinese people can fly) v15 made +2,045 in six rounds, which is break-even.
5. **None of those four losing bots will be in the final.** On today's and Saturday's evidence, our edge against solid bots is close to zero. The final is 8 solid bots, so expect a close game decided by small edges and luck.
6. **The biggest risk in the final is the thinking bank.** The site says "10 s thinking per round". We use 2.2–2.9 s per 1,000 hands, so 5,000 hands would need 11–14 s. If the bank is 10 s for the whole final, the bot runs dry around hand 3,500–4,500. **Ask the organisers now.**
7. **The biggest remaining leak is the three-street bluff.** Betting flop, turn and river with less than top pair on the river: 30 hands over 12 rounds, −20,530. Solid players call it: Chinese people can fly and Anker made 14 of the 17 calls.
8. **Prizes are £500 for 1st and £200 for 2nd,** so the top two places count.

---

## 2. Where things stand (10:03, 13 of 36 rounds)

| Table | 1st | 2nd | 3rd | 4th |
|---|---|---|---|---|
| 1 | Astra La Vista +53,908 | Attention Is All In +36,915 | test −1,025 | gamblerlove −6,275 |
| 2 | Gherkers +40,650 | Phil AIvey +18,896 | Equity Engine +15,734 | SARS +7,177 |
| 3 | matcha mille crêpes cake +28,774 | Jump Street +26,514 | FisherMen +18,879 | 85p +16,627 |
| 4 | **Resonance Qt +83,473** | Anker Batteries +55,341 | Poke +17,809 | Chinese people can fly +8,568 |

- **Table 1 looks settled:** Astra and Attention.
- **Table 2:** Gherkers, plus Phil AIvey or Equity Engine.
- **Table 3 is open:** four teams within 12,000 chips.
- **Table 4:** we are 65,664 ahead of 3rd place with 23 rounds left. Poke would need to outscore us by about 2,900 chips a round. Qualifying is very likely but not certain.

**The final:** Sunday 12:05, 8 bots, 5,000 hands, places by total chips. Uploads close at 12:00 and the latest upload that loads is the one that plays. Limits shown on the site: 25 ms per decision, 10 s thinking bank per round.

---

## 3. What v15 changed, and what it did

### The code

| Change | Where | Effect |
|---|---|---|
| `BIGPAIR_CALL = 500`, `BIGPAIR_MARGIN = 0.15` | `_postflop`, just before the final call test | Turn or river calls of 500+ chips with one pair or less (or two pair on a paired board) need 15 points more equity |
| Poke label | `seat_label` | A limper is labelled `POKE` only if it also opens 2.5 big blinds |

Everything else is identical to v14, line for line.

### The results, six rounds each

| | v14 (rounds 2–7) | v15 (rounds 8–13) |
|---|---|---|
| Chips | +26,569 | +56,146 |
| All-in luck | +14,083 | +16,834 |
| Without luck | +12,486 | +39,312 |
| Showdowns: number, won, chips | 138, 63, −7,246 | 149, 81, +14,457 |
| Non-showdown chips | +33,815 | +41,689 |
| Big blind chips | −16,436 | +6,836 |
| Full stacks won / lost | 35 / 29 | 33 / 26 |

**The new rule's own footprint** (turn or river calls of 500+ chips with one pair or less):

| | v14 | v15 |
|---|---|---|
| Calls made | 21 | 16 |
| Calls won | 5 | 11 |
| Chips against folding | −10,682 | +16,951 |
| Folds in the same spot | 41 | 29 |

That swing of 27,600 chips is about the size of the whole gap between the two versions. Winning 11 of 16 is partly luck, though: the rule only raises the bar, it cannot pick winners that well.

### Where the chips came from

| Opponent | v14 | v15 |
|---|---|---|
| WBot | +952 | +21,934 |
| YSL_TWIZZY | +10,487 | +17,627 |
| GamesGone | +2,094 | +10,578 |
| Anton | +18,329 | +3,962 |
| Poke | +7,160 | +2,813 |
| Anker Batteries | −11,291 | +1,689 |
| Chinese people can fly | −1,162 | −2,457 |

What changed without any code change:

- **YSL:** 430 re-raises in rounds 8–13, and he folded at once 301 times (70%), for +21,294. In rounds 2–7 it was 377, 232 (62%) and +10,124. YSL lost 36,881 in rounds 8–13.
- **WBot:** raising his small bets now wins outright 29 times in 57 (51%), for +3,313. In rounds 2–7 it was 27 in 69 (39%), for −5,102. WBot is losing about 7,000 a round to the table in both periods.
- **Anker:** we stopped losing to him. He also ran badly, with −9,549 of all-in luck in rounds 8–13.

**So why are we up by so much?** Two bots at the table are collapsing and we are the main collector, we had 16,834 chips of all-in luck, and the new rule stopped the big one-pair calls from losing.

### Leaks still open in v15

| Leak | v14 | v15 | Total |
|---|---|---|---|
| Three-street bluffs (bet flop, turn, river; under top pair at the river) | 15 hands, −8,639 | 15 hands, −11,891 | 30 hands, −20,530 |
| River bluff bets that got called | 14, −9,023 | 18, −11,417 | 32, −20,440 |
| Re-raising GamesGone | 27, −3,982 | 16, −4,542 | 43, −8,524 |

- River bluffs as a whole still make money, because 49 of 81 were folded to (pots worth 32,737).
- The losses are concentrated on two callers: Chinese people can fly called 10 river bluffs (−8,444) and Anker called 9 (−6,505).
- In the three-street bluffs, those two made 14 of the 17 calls.

---

## 4. The likely finalists

Style numbers are from Saturday hands at our tables, unless marked. "Folds when raised" means the team folded after its own bet was raised.

| Team | Saturday at our tables | Opens | Plays / raises | Re-raise rate | Folds to a re-raise | Folds to a 4-bet | Folds blind to a steal | What we took per round |
|---|---|---|---|---|---|---|---|---|
| Attention Is All In | +38.8 bb/100 | 2.5 bb | 29% / 21% | 14% | 71% (570) | 84% (77) | 51% | −1,325 |
| Gherkers | +23.4 | 3.5 bb | 23% / 18% | 13% | 44% (171) | 81% (62) | 63% | +45 |
| Astra La Vista | +2.1 | 3.0 or 2.5 bb | 20% / 15% | 5% | 57% (221) | 23% (22) | 78% | +694 |
| Phil AIvey | +3.4 | 3.0 or 2.5 bb | 20% / 15% | 6% | 69% (124) | 92% (12) | 75% | −89 |
| Equity Engine | +1.8 | 3.5 bb | 25% / 17% | 3% | 63% (412) | 13% (16) | 63% | +1,105 |
| matcha mille crêpes cake | +10.5 | 2.5 bb | 20% / 13% | 7% | 53% (131) | 22% (23) | 74% | −256 |
| Jump Street | +6.6 | 2.5 or 3.0 bb | 20% / 14% | 6% | 51% (107) | 38% (21) | 69% | −220 |
| FisherMen | +35.7 | 3.3 bb | 30% / 24% | 13% | 51% (487) | 84% (86) | 53% | +167 |
| 85p | −16.5 | 2.5 bb | 14% / 10% | 5% | 74% (137) | 80% (10) | 78% | +206 |
| Anker Batteries (Sunday) | +21.3 | 2.5 bb | 22% / 13% | 10% | 42% (234) | 82% (71) | 54% | −856 |

**Astra and matcha have changed since Saturday.** They finished 16th and 22nd on Saturday and lead their tables today, so treat their rows as out of date.

### How each one bets, and the opening it leaves

| Team | Usual bet sizes | Folds when raised | Share of strong hands behind the bet | Opening |
|---|---|---|---|---|
| Attention | A third of the pot (45%), pot (12%) | Third-pot bets 82% (83); 65–90% bets 75% (40) | Third-pot 60%; pot 93% | Raise its small and medium bets. Re-raise its opens and 4-bet its re-raises. Fold to its pot bets. |
| Gherkers | A third (33%), overbets (43%) | Third-pot 61% (41); overbets 30% (23) | Third-pot 59%; overbets 79% | The hardest opponent. Calls re-raises and raises 22% of bets. Only the 4-bet works (81% folds). |
| Astra | A third (49%) | Third-pot 74% (62) | Third-pot only 36% | Raise its small bets. Steal its blinds. |
| Phil AIvey | Half pot (80% of bets) | Half-pot 73% (22) | 79% | Steal its blinds and re-raise its opens. |
| Equity Engine | 42–65% (42%), 65–90% (53%) | 42–65% bets 91% (44); 65–90% bets 65% (48) | 42–65% bets only 32% | Raise its half-pot bets. |
| matcha | Half pot (45%), 65–90% (25%) | Third-pot 85% (13); half-pot 39% (23) | 76–91% | Little to attack. Its bets are honest. |
| Jump Street | Pot (35%), half (30%) | 41–55% | 52–95% | Little to attack. |
| FisherMen | A third (31%), pot (40%) | Third-pot 97% (35); 65–90% bets 93% (14); pot 32% (25) | Pot 88% | Raise anything under pot size. 4-bet its re-raises. Fold to pot bets. |
| 85p | 65–90% (92%) | 19% (27) | 85% | Never bluff-raise. Steal its blinds and re-raise its opens. |
| Anker (Sunday) | 24–42% (32%), pot (25%), big overbets (12%) | Small 34% (79); pot-size 83% (29) | Small 83%; pot-size 65%; big overbets 95% | Never raise his small bets. Raise his pot-size bets. Fold to his big overbets. 4-bet his re-raises. |

### What the bot's fingerprints will do with these teams

The labels in `seat_label` were written for today's table. Replaying Saturday's hands through the same rules gives this:

| Team | Label the bot would give (rounds) | Consequence |
|---|---|---|
| Anker (Sunday) | ANKER 12 of 13 | Correct |
| FisherMen | ANTON 7 of 11 | Mostly helpful: it folds to 4-bets 84% |
| Attention | ANTON 4, CPF 3, none 3 | Mostly helpful: it folds to 4-bets 84% and to re-raises 71% |
| Gherkers | ANTON 3 of 10 | Mixed: the 4-bet works, the bluff-raise of medium bets does not (58% folds) |
| Jump Street | CPF 2, ANTON 1, none 4 | A few wasted light re-raises, then it corrects |
| Astra, Phil AIvey, Equity Engine, 85p | none | The bot learns them from scratch |
| Poke (Sunday) | GG 10 of 13 | Wrong today, small cost |

The wrong labels are mostly harmless, because every seed is capped at 12 pseudo-observations and live play overrides it. Over 5,000 hands at one table the bot's own learning will dominate.

---

## 5. What I would do, in order

### 1. Settle the thinking bank (do this first)

Ask the help desk (Huxley, floor 2) or algo.trade@imperial.ac.uk:

- Is the 10 s thinking bank in the final for all 5,000 hands, or does it reset every 1,000 hands?
- Will `on_table_start` report `hands = 5000`?

If the bank is 10 s for all 5,000 hands, the bot must use a third less time per hand. In `_budget` the cap is 1.6 ms and `BIG_BUDGET` is 3.5 ms. Candidate values are a 0.8 ms cap and a 2.0 ms `BIG_BUDGET`, checked with `tools/latency.py`. The bot's own governor only starts to throttle near hand 3,000, which is too late to be safe.

If the bank resets every 1,000 hands, change nothing.

### 2. Keep the v15 engine

It has 13 clean rounds: 3 timeouts in total, no errors, no flags. Do not swap engines for the final.

### 3. Damp the third bluff barrel (highest value, small change)

In `_postflop`, in the branch where we can bet (`c == 0`), on the river: if we already bet twice this hand (`L[3][me] >= 2`) and an opponent called twice (`L[5][s] >= 2`), halve that opponent's fold probability before the expected-value comparison. Value bets still go through, because their value comes from being called.

Evidence: 30 hands, −20,530 in 12 rounds, with the calls coming from the two most solid players at the table. The final has seven such players.

### 4. Refresh Anker's seed with today's numbers (data only)

Computed the same way as the existing seeds. The method reproduces the current `ANKER` entry exactly from Saturday's hands.

```python
"ANKER": ([0, 12, 12, 12, 12, 5], [0, 4.1, 1.85, 6, 9.93, 0], [4, 12, 12, 12, 12, 12], [3, 10.02, 11.61, 10, 7.76, 11.43]),
```

The main change: his small bets fold to a raise 34% of the time today, not 48%.

### 5. Consider 4-betting any frequent re-raiser who folds to 4-bets (medium risk)

Today the 4-bet-instead-of-call rule fires only for a seat labelled `ANTON`. Attention, Gherkers, FisherMen and Anker all fold to 4-bets 81–84% of the time, on 62–86 cases each. A candidate rule is to apply it to any seat with at least 6 observed 4-bet spots and 70% folds. This needs a duel test before use.

### 6. Leave the finalist fingerprints out unless there is spare time

Seeds for the other finalists are below. They need new label rules and new open-size counters (3.0, 3.3 and 3.5 big blinds), and they describe Saturday's bots. Over 5,000 hands the gain is small.

```python
"ATTN":   ([1, 12, 4, 12, 12, 0], [1, 9.83, 4, 9, 6.86, 0], [12, 12, 12, 12, 12, 12], [12, 7.21, 5.08, 9.07, 11.18, 8.87]),
"GHERK":  ([0, 12, 0, 12, 12, 0], [0, 7.32, 0, 7, 3.65, 0], [3, 12, 6, 12, 12, 7], [3, 7.05, 6, 8.57, 9.53, 6]),
"ASTRA":  ([0, 12, 12, 7, 2, 0], [0, 8.9, 3.56, 1, 0, 0], [3, 12, 12, 12, 4, 7], [3, 4.28, 8.59, 10.7, 3, 6]),
"PHIL":   ([0, 0, 12, 2, 2, 0], [0, 0, 8.73, 0, 0, 0], [1, 2, 12, 11, 1, 1], [1, 2, 9.45, 11, 1, 1]),
"EQENG":  ([0, 0, 12, 12, 4, 0], [0, 0, 10.91, 7.75, 0, 0], [10, 5, 12, 12, 6, 0], [9, 4, 3.82, 10.17, 6, 0]),
"MATCHA": ([0, 12, 12, 10, 7, 0], [0, 10.15, 4.7, 2, 1, 0], [1, 12, 12, 12, 11, 2], [1, 7, 9.15, 10.91, 10, 2]),
"JUMP":   ([0, 11, 12, 6, 12, 0], [0, 6, 5, 0, 4.94, 0], [0, 12, 12, 12, 12, 4], [0, 10.2, 6.18, 11.4, 8.73, 4]),
"FISHER": ([0, 12, 0, 12, 12, 0], [0, 11.66, 0, 11.14, 3.84, 0], [1, 12, 3, 12, 12, 4], [1, 7.37, 3, 8.6, 10.6, 4]),
"P85":    ([0, 0, 0, 12, 0, 0], [0, 0, 0, 2.22, 0, 0], [2, 3, 6, 12, 0, 0], [1, 3, 5, 10.21, 0, 0]),
```

### Timing

- A new upload plays from the next round, so anything uploaded by about 11:40 gets three or four live rounds as a check before uploads close.
- Do not upload anything new after 11:50. If a late upload fails to load or misbehaves, there is no time to recover.
- Before any upload: `tools/fuzz_act.py` with 0 illegal replies, and `tools/latency.py` no worse than v15.

---

## 6. What to expect in the final

- **Baseline:** 8 bots and two paid places, so 1 in 4 for a prize if all were equal.
- **Our edge against solid bots is about zero so far.** v15 made +2,045 in six rounds against Anker, Poke and Chinese people can fly combined. On Saturday we were break-even against the top ten.
- **Luck is as large as skill over 5,000 hands.** One 1,000-hand round swings by about 8,000 chips on luck, so 5,000 hands swing by about 18,000. The skill gaps between finalists are of the same size or smaller.
- **Who to fear:** Attention took 1,325 chips a round from us on Saturday, the most of any finalist. Gherkers is the hardest to exploit. Anker has beaten us over today's 13 rounds (−856 a round), though not since round 8.
- **Where chips are available:** Attention's, Astra's, FisherMen's and Equity Engine's small and medium bets fold to raises 74–97% of the time on Saturday's data, and Phil AIvey, Astra and 85p give up their blinds 75–78% of the time. The bot already has the machinery for both and will learn them during the final.

---

## 7. How these numbers were made

- **Sources:** the team data API through the browser, and the public standings API. The token and hand files are not in this repository.
- **All-in luck:** actual chips minus expected chips in hands where everyone left was all in before the river and cards were shown. Flop and turn cases are exact; preflop cases use 12,000 random boards.
- **"Without luck"** removes only that all-in luck. It does not remove any other kind of luck.
- **Chip flow:** in each hand, losers' chips are assigned to winners in proportion to what each won.
- **Finalist stats and seeds:** a line-for-line port of the bot's own `_learn` counters and `seat_label` rules, run over the hand files. As a check, it reproduces the bot's existing `ANKER` seed exactly from Saturday's hands, and it assigns today's labels as expected (Anker, WBot, Anton and GamesGone 12 of 13 rounds, YSL 13 of 13).
- **Samples are small.** Six rounds per bot version, and 5–11 Saturday rounds per finalist. Treat single numbers as leads, not facts.
