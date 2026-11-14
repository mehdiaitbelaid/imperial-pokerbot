# Field report: us against the other teams, Saturday rounds 1–29

Written 17:45 Sat 14 Nov 2026 by Claude for Resonance Qt (Saeed, Mehdi, Riyad, Hassan).

**Data used:**
- **Leaderboard:** every 5-minute public snapshot (`rankings-history` branch, through R24) plus two pulls of the public API, at 17:06 (after R26) and 17:24 (after R29). That covers 44 teams.
- **Our hand files:** all 29 counted rounds, 29,000 hands. They include every seat's actions at our tables, so they cover 43 teams, 41 of whom we sat with in more than one round.
- **Scripts:** `tools/field_report/`. Hand files and the token are not committed.

**Labels used below:**
- **"Whale table"** means `ediz_slow` was at the table. It loses about 300 bb/100 every round.
- **"Non-whale mean"** on the leaderboard means a team's average over rounds R1–R24 where it scored +120 or less. The leaderboard can't show who sat where, so that cutoff stands in for whale tables.
- **±** is one standard error.

---

## 1. Summary

1. **On the board we are 4th of 40 at +34.5 bb/100** (17:24, after R29), behind Gherkers +51.1, Attention Is All In +45.4 and Equity Engine +36.2.
   - Excluding the whale, we rank **5th on skill: +23.0 ± 5.9** over R1–24.
   - The four ahead of us on skill are Gherkers (+42.1), Phil AIvey (+33.0, 8th on the board), AAST (+30.8) and Equity Engine (+28.2).
   - Attention Is All In is 10th on skill (+16.6). Five whale rounds put it 2nd.
2. **44% of our chips came from `ediz_slow`.** That is 87,400 of our 199,800, won in 6 of 29 rounds. Another 52% came from teams outside the top 10, and **only 4% from the other nine teams in the top 10.**
   - Against those nine we make **+1.0 ± 2.3 bb per 100 hands per opponent seat**, which is break-even.
   - This matters most for Sunday's top-2 table and for the final.
3. **Our biggest leak against good bots is paying off big turn and river bets.**
   - Of the field's river bets of two-thirds pot or more that reached showdown, **0–9% were bluffs**, depending on the team.
   - Calling turn or river bets of two-thirds pot or more with one pair or two pair cost us **31,200 chips compared with folding (−5.4 bb/100 over 29 rounds)**. Most of it was under V18; v14 still loses about 2.9 bb/100 there.
   - Attention Is All In, WBot, munchlax and Kojack each took 5,000–12,000 chips from us in **single-raised pots that went to showdown.**
4. **The field folds to our bets more than to anyone else's.**
   - Against bets of 45–80% pot, opponents fold **60% to us and 48% to everyone else**, over about 8,200 decisions.
   - Yet our aggression factor is 1.4, the lowest in the top 10 (Gherkers 2.9, Attention 3.6, AAST 4.7, WBot 7.5).
   - We are leaving value from betting on the table.
5. **Three playing styles are winning in this field** (section 5):
   - **Polarized sizing,** meaning one-third-pot bets plus overbets: Gherkers and AAST.
   - **Small, very frequent bets:** WBot, Attention, Astra.
   - **Solid tight-aggressive play:** Equity Engine, Phil AIvey, Kojack.

   We play a fourth style: bets of mostly 60–105% pot, at low frequency.
6. **Uploading mid-day hasn't helped on average.**
   - Across 152 version changes, a team's next 3 rounds averaged +4.7 bb/100 better than its previous 3, with a spread of ±45 per change, so the effect is noise. 84 of the 152 were followed by a better spell.
   - The number of uploads doesn't correlate with skill (r = 0.13).
   - One clear exception: **Attention Is All In's single upload at R22 (v3 to v4)**, after which it moved from about +1 to about +28 non-whale.
7. **The field has learned to beat fixed bots.**
   - aydine (−58), ND (−50) and Red (−49) each fell about 50 bb/100 between R1–12 and R13–24 (2.4–2.8 standard errors). aydine and ND never uploaded, and Red only once.
   - Teams with more timeouts do worse (r = −0.35).

---

## 2. Leaderboard and true skill (top 17 of 40, 17:24)

| Board | Team | Total | Non-whale mean ± se | Whale rounds | R1–12 → R13–24 | Uploads (version) | Timeouts per round |
|---|---|---|---|---|---|---|---|
| 1 | Gherkers | +51.1 | **+42.1 ± 8.2** | 1 | +44 → +40 | 11 (v9→v22) | 2.2 |
| 2 | Attention Is All In | +45.4 | +16.6 ± 6.4 | **5** | +1 → **+28** | 1 (v3→v4) | 1.1 |
| 3 | Equity Engine | +36.2 | +28.2 ± 6.3 | 2 | +28 → +29 | 4 (v7→v12) | 0.9 |
| **4** | **Resonance Qt** | **+34.5** | **+23.0 ± 5.9** | 1* | +29 → +16 | 4 (v5→v10) | 1.1 |
| 5 | AAST | +30.3 | +30.8 ± 6.9 | 0 | +37 → +24 | 3 (v2→v5) | 0.8 |
| 6 | The Market Makers | +26.8 | +7.9 ± 8.0 | 3 | +1 → +15 | 2 (v7→v9) | 1.4 |
| 7 | Kojack | +26.7 | +17.3 ± 9.1 | 2 | +11 → +24 | 0 (v3) | 1.1 |
| 8 | Phil AIvey | +26.5 | **+33.0 ± 7.9** | 0 | +28 → +38 | 5 (v3→v8) | 1.3 |
| 9 | WBot | +26.4 | +19.9 ± 9.5 | 1 | +14 → +26 | 1 (v5→v6) | 1.4 |
| 10 | Anker Batteries | +24.7 | +15.3 ± 7.8 | 1 | +17 → +14 | 3 (v1→v4) | 1.0 |
| 11 | Chinese people can fly | +19.7 | +10.6 ± 8.4 | 2 | +8 → +14 | 6 (v7→v14) | 1.9 |
| 12 | gamblerlove | +17.8 | +14.5 ± 7.9 | 1 | +11 → +18 | 6 (v4→v10) | 0.7 |
| 13 | Astra La Vista | +17.3 | +18.9 ± 8.6 | 0 | +24 → +14 | 6 (v6→v12) | 0.7 |
| 14 | Poke | +17.3 | +10.5 ± 11.7 | 0 | +11 → +10 | 1 (v1→v2) | 0.7 |
| 15 | Mohil'sPokerBot | +15.9 | +13.1 ± 8.6 | 1 | +15 → +11 | 2 (v2→v4) | 1.3 |
| 16 | Claudebot | +15.9 | +15.4 ± 10.1 | 0 | −1 → **+32** | 3 (v1→v4) | 1.3 |
| 17 | pokermon | +15.0 | +18.3 ± 8.0 | 0 | +20 → +17 | 0 (v1) | 0.9 |

*The +120 cutoff undercounts some whale tables. We actually sat with `ediz_slow` in R3, R11 and R15, plus R25–27, but only R15 crossed +120. Our own exact figure from the hand files is in section 3.

**Notes on the table:**
- **Gherkers is the only team measurably better than us** (+19 ± 10, about 1.9 standard errors).
- **Phil AIvey, AAST and Equity Engine are level with us** within noise.
- **Attention Is All In's lead comes from whale tables.** Its v4 does look like a real improvement.

**Bottom of the board:** ediz_slow −289, Anton −55, AIl IN −36, Joca −28, Poké Bot −18, YSL_TWIZZY −14, bigRoddy −13 and SARS −12. These are where everyone's profit comes from.

---

## 3. Our own 29 rounds

| Bot | Rounds | All rounds | Without whale tables |
|---|---|---|---|
| v5 (Mehdi v1) | R1–2 | −13.4 | −13.4 (n=2) |
| v6 (Avengers v14) | R3–11 | +39.7 | **+45.2** (n=7) |
| v7 (V18 chimera) | R12–21 | +31.6 | +16.9 (n=9) |
| v8 and v10 (v14 again) | R22–29 | +44.1 | +24.8 (n=5) |

- **Whale tables** (exact, from the hand files): R3 +37, R11 +4, R15 +164, R25 +146, R26 +96, R27 −13, averaging +72 (n=6).
  - Without them we average **+24.6 ± 5.9** (n=23).
  - Even at a whale table a round can come out flat (R11) or negative (R27), so whale tables don't guarantee a big round.
- **The live bot has not changed:** `lastCheck` reports version 10 with SHA `70f64660654b`, the same file as upload v8 (v14).
- **Timeouts:** 0–1 per round since R12.
- **Latest rounds:** R27 −12.8 (whale table, with WBot and The Market Makers), R28 +32.3, R29 +46.0.

---

## 4. Head-to-head: who we beat and who beats us

Each hand's losses are shared among that hand's winners in proportion to what they won (as in `tools/matrix.py`). Figures are bb per 100 hands that we shared a table with that team.

**Our five best and five worst opponents:**

| Opponent | Rounds together | Us against them | Chips | Their bb/100 at our tables |
|---|---|---|---|---|
| ediz_slow | 6 | **+72.9 ± 21** | +87,428 (44% of our net) | −334 |
| YSL_TWIZZY | 2 | +24.9 | +9,957 | −64 |
| SARS | 2 | +24.1 | +9,631 | −33 |
| Chinese people can fly | 4 | +14.9 ± 6.4 | +11,935 | −10 |
| aydine | 5 | +13.5 | +13,488 | −4 |
| … | | | | |
| Peanut Cookies | 4 | −5.8 | −4,623 | +4 |
| munchlax | 4 | −7.6 ± 4.3 | −6,095 | +15 |
| **Attention Is All In** | 6 | **−9.7 ± 6.3** | −11,656 | +45 |
| **WBot** | 5 | **−11.1 ± 9.4** | −11,120 | **+85** |

**The rest of the top 10:**

| Team | Us against them |
|---|---|
| The Market Makers | +10.4 ± 6.0 |
| Equity Engine | +6.7 ± 6.5 |
| AAST | +1.7 ± 7.1 |
| Gherkers | +1.2 ± 5.8 |
| Kojack | +0.8 ± 3.8 (7 rounds) |
| Phil AIvey | +3.3 (only 1 round together) |

**Pooled by group, per opponent seat:**

| Group | Our result | Share of our net chips |
|---|---|---|
| Board top 9 | +1.0 ± 2.3 | 4% |
| Everyone else | **+4.0 ± 1.3** | 52% |
| Whale | +72.9 ± 21 | 44% |

No single head-to-head loss reaches 2 standard errors. **The pattern across the strong teams, though, is consistent.**

**Where the chips go** (from `rivals.py`; pot type by preflop action, and whether both of us reached showdown):

| Rival | Lost in single-raised pots that went to showdown | What we win back |
|---|---|---|
| Attention Is All In | −7,992 over only 15 showdowns | +4,090 in 3-bet pots that ended without showdown |
| WBot | −12,187 over 41 showdowns | +4,485 from our 3-bets |
| munchlax | −4,783 over 10 showdowns | +1,794 from our 3-bets |
| Kojack | −7,271 over 12 showdowns | +9,664 when they fold, which is why we are level |

Each of these rivals bets big only when it has a hand, and we call. **Gherkers is different:** it takes −3,735 from us with **3-bets we fold to**. It 3-bets 19% of opens, and we fold to 3-bets 58% of the time.

**Other teams against each other** (pairs that shared at least 3 of our tables; these are thin samples):
- Kojack beat ediz_slow by +97.
- FisherMen beat Red by +11.
- Kojack beat The Market Makers by +4.
- Equity Engine beat Red by +4.
- Durahim 1453 beat matcha mille crêpes cake by +4.

We tried to rebuild every table's line-up from the leaderboard, since each table's chip changes sum to exactly zero. It doesn't work: every round has many zero-sum ways to split the teams into tables, and the method failed to recover our own table blind. So **the public board can't tell us who sat with whom at other tables.** Our hand files are the only head-to-head source.

---

## 5. How the teams play: styles and what's working

**Stats measured at our tables:**

| Team | Hands | VPIP/PFR | 3-bet | Fold to 3-bet | C-bet | Bet when checked to | Postflop bet sizes | Aggression factor | WTSD/W$SD |
|---|---|---|---|---|---|---|---|---|---|
| **Resonance Qt** | 29k | 24/18 | 12 | 58 | 78 | 49 | 60–105% pot: 72%, overbets 10% | **1.4** | 25/56 |
| Gherkers | 4k | 28/21 | **19** | 38 | 73 | 54 | **⅓ pot 39%, overbet 41%** | 2.9 | 20/55 |
| AAST | 3k | 24/15 | 4 | 56 | 59 | 49 | **⅓ pot 25%, overbet 51%** | 4.7 | 27/52 |
| Anker Batteries | 4k | 22/16 | 8 | 29 | 81 | 52 | ⅓ pot 15%, overbet 44%, all-in 10% | 1.3 | 25/50 |
| WBot | 5k | 32/22 | 5 | 54 | **99** | **92** | **under 30% pot: 52%** | **7.5** | 34/54 |
| Attention Is All In | 6k | 30/23 | 12 | 70 | 69 | 61 | 45% pot or less: 55% | 3.6 | 21/53 |
| Astra La Vista | 4k | 20/15 | 5 | 53 | 84 | 67 | ⅓ pot 50% | 2.3 | 36/46 |
| Chinese people can fly | 4k | 37/23 | 5 | 76 | 72 | 70 | ⅓ pot 72%, pot 25% | 4.3 | 30/44 |
| Equity Engine | 5k | 24/17 | 3 | 53 | 74 | 46 | 45–105% pot, opens 3.5 bb | 2.5 | 24/48 |
| Kojack | 7k | 20/17 | 7 | 59 | 70 | 43 | 30–80% pot, opens 2.5 or 5 bb | 1.3 | 32/61 |
| The Market Makers | 6k | 20/12 | 5 | 30 | 83 | 70 | 45–105% pot | 2.8 | 29/45 |
| Phil AIvey | 1k | 22/17 | 4 | 80 | 61 | 37 | (too few hands) | 1.0 | 24/67 |
| munchlax | 4k | 19/9 | 3 | 37 | 30 | 26 | half pot 63% (fixed sizes) | 0.9 | 29/54 |
| Peanut Cookies | 4k | 17/14 | 5 | 20 | 44 | 41 | **95% at ⅔ pot** (one size only) | 1.0 | 30/57 |
| bigRoddy | 6k | 30/22 (20 limp) | 16 | 51 | 54 | 38 | 34% all-in; 12% of opens are 100 bb shoves | 1.9 | 40/53 |
| Joca | 7k | 12/4 | 3 | 65 | 45 | 26 | 33% all-in; 17% of opens are 100 bb shoves | 1.5 | 35/47 |
| ediz_slow | 6k | 75/32 (66 limp) | 31 | 0 | 100 | 51 | half pot (starter-kit bot) | 3.5 | 43/40 |

**The styles, and how they're doing:**
- **A. Polarized sizing:** Gherkers, AAST, Anker Batteries, and partly Durahim 1453.
  - They bet either about a third of the pot or more than the pot, and almost never in between.
  - This is a solver-style idea: small bets with a wide range, overbets with a polarized one.
  - It's the most successful style: Gherkers is #1 on skill and AAST #3.
  - It is hard to call against without hand-reading, and the overbets win big pots against bots that call by pot odds.
- **B. Small bets, very often:** WBot, Attention Is All In, Astra La Vista, Chinese people can fly.
  - **WBot** c-bets 99% of the time, bets 92% when checked to, makes half its bets under 30% pot, and raises 28% of bets it faces. It wins +85 bb/100 at our tables and beats us. Most bots fold too often to tiny bets, and WBot collects those folds.
  - **Attention Is All In** mixes ⅓-pot bets with bigger ones. It folds 81% to our bets, yet still beats us at showdown.
- **C. Solid tight-aggressive:** Equity Engine, Kojack, Phil AIvey, The Market Makers. Conventional ranges and sizes that are steady and consistently profitable. This is closest to us.
- **D. Fixed, rule-based bots:** Peanut Cookies, munchlax, Red, GamesGone, ediz_slow. They use one bet size, and the field is now beating them (see the declines in section 6).
- **E. Shovers:** bigRoddy, Joca, pokermon (21% of bets all-in). They lose slowly; correct calling ranges punish them.
- **Us:** value-heavy, big bets, low frequency.
  - Our 3-bet rate (12%) is high, but we bet only 49% of the time when checked to, and our aggression factor is 1.4.
  - We are the only bot in this sample whose big river bets that reached showdown were 14% bluffs (n=77). Everyone else's were 0–9%.

---

## 6. What the teams are doing against each other

**1. Hardly anyone bluffs big rivers.** Here is the share of river bets of two-thirds pot or more, shown down, that were bluffs (no pair, straight or flush):

| Team | Share bluffs |
|---|---|
| The Market Makers | 0% (n=31) |
| Chinese people can fly | 0% (28) |
| ND | 0% (21) |
| GamesGone | 0% (19) |
| aydine | 0% (19) |
| AIl IN | 0% (15) |
| Vlad | 3% (35) |
| Attention Is All In | 4% (23) |
| WBot | 6% (16) |
| Equity Engine | 8% (13) |
| FisherMen | 9% (22) |

In this field a big river bet means a strong hand.

**2. Bots fold to small bets.** Against a bet under 45% pot, the field folds only 29% of the time. That is why WBot's and Attention's ⅓-pot bets work as cheap probes and value bets rather than as bluffs.

**3. Bots fold more to us.**
- Against bets of 45–80% pot, opponents fold 60% to us (n=1,145) and 48% to others (n=7,078).
- Against bets of 80% pot or more, they fold 65% to us and 61% to others.
- Bots never see team names, so this is not targeting. It reflects when and how we bet.
- A ⅔-pot bluff needs 40% folds to break even. At 60% we can bet more often, though the fold rate will fall as we do.

**4. The 3-bet war.**
- The field 3-bets 6.2% of our opens and 6.7% of everyone else's.
- Gherkers 3-bets 19.5% of opens against others but only 8.4% against ours (n=131).
- Durahim 1453 does the same: 12.7% against others, 3.2% against us.
- Our 3-bet pots without showdown are profitable against almost every strong team (+1,800 to +4,600 chips each).

**5. Iteration.**
- **Uploads:**
  - **Heavy iterators** are Gherkers (v9→v22), Durahim 1453 (v1→v17), matcha mille crêpes cake (v9→v20), Lehman Brothers (v6→v16) and Jump Street (v6→v15).
  - **Static bots** are Kojack (v3), pokermon (v1), ND (v1) and aydine (v1).
  - Median non-whale result: 0–1 uploads +10.5, 2–5 uploads +6.4, 6 or more +7.5. The differences are noise.
  - **After Gherkers' version changes at R19 and R20, its next 3 rounds averaged 57 and 62 bb/100 worse than the 3 before.** It recovered later. Fast iteration can break a working bot.
  - **Attention Is All In made one upload, at R22, and it worked:** its next 3 rounds averaged 54 bb/100 better than the 3 before. It is now the most dangerous of the improving teams.
- **Static weak-to-middling bots are being exploited:**
  - aydine went from +21 (R1–12) to −37 (R13–24), ND from +11 to −39, and Red from +27 to −23.
  - Over the same period, some mid-table bots improved: Claudebot −1 → +32 and Kojack +11 → +24.
- **Timeouts:**
  - Timeouts per round and skill correlate at r = −0.35.
  - The slowest bots are matcha mille crêpes cake (3.4 per round), Durahim 1453 (3.1), Anton (2.8) and ND (2.3); all are below +8 non-whale.
  - The public API now gives `decision_ms: 25` (the earlier handoff said 10 ms). This is worth checking with the organisers before cutting CPU any further.

---

## 7. What this means for us

In priority order. All of these need testing first: duels plus replay of real hands, as in handoff section 6.

1. **Fold one pair and weak two pair to big turn and river bets** from any seat other than the whale.
   - This is worth about **+3 bb/100 under v14** and about +9 under V18.
   - The evidence: the field's big river bets are 0–9% bluffs, and these calls lost 31,200 chips compared with folding.
   - This is handoff step 3. The data now says to apply it to every non-whale seat, not only seats with VPIP under 30%.
2. **Bet more often.**
   - Raise the share of bets when checked to (49% now, against 61–92% for the small-ball winners).
   - Add a small (⅓-pot) bet for thin value and probes on boards where we currently check. Folds against our 45–80% pot bets are 60%.
   - Test against T1 replicas whose `fold_to_bet` is set from section 6's numbers.
3. **Against Gherkers-type 3-bettors** (19%), defend more of our opening range: 4-bet for value and call more in position. We fold to 3-bets 58% of the time.
4. **Against Attention- and WBot-type bots** (small bets, then big bets with strong hands): call their small bets lighter, fold to their big ones, and bluff them more. Attention folds 81% to our bets.
5. **Don't upload because of one round.** Upload only through the gates: duel, fuzz test and latency. That is also the lesson from Gherkers at R19 and R20.
6. **Sunday.**
   - Tables are dealt from the Saturday ranking "like cards". **[OPEN]:** whether the deal is straight or snake, and how many tables.
   - If we stay in the top 4, Gherkers and Attention go to other tables. We would face one of ranks 5–9: AAST, The Market Makers, Kojack, Phil AIvey or WBot.
   - Against that group we are break-even today (+1.0 ± 2.3), so **reaching the final depends on fixing items 1–3**, not on the whale.
   - After 20:30, profile our table's teams from these hand files: `tools/field_report/` plus `tools/analyze.py`.

---

## 8. Method and caveats

- **Head-to-head figures** share each hand's losses among its winners in proportion. That is fair overall but blurs multiway pots. Per-pair samples are 1,000–7,000 hands, so differences under about ±10 bb/100 are noise.
- **Style stats** come only from our tables. Most teams have 3,000–7,000 hands there; Phil AIvey, Mohil'sPokerBot and kaiserbot have only 1,000.
- **"Bluff"** means a hand shown down with no pair using a hole card and no straight or flush. Bluffs that won without showdown are not counted, so the true bluff rate is somewhat higher than shown.
- **The call-versus-fold value** is the hand's result plus the chips we had already put in when we called. It includes later streets.
- **Leaderboard figures for R25–26 and R27–29** come from snapshots that span several rounds. The "non-whale" and "early → late" columns therefore use R1–24 only.

**To reproduce** (hand files fetched through the browser as in the handoff; never commit them):

```
cd tools/field_report
python3 rounds.py          # leaderboard snapshots -> global_rounds.json (needs standings-history.csv, public_r*.json)
python3 -I field.py hands  # our hand files -> out/field.json
python3 summarize.py; python3 ourtables.py; python3 vs.py; python3 -I rivercalls.py; python3 rivals.py; python3 pooled.py; python3 -I foldsize.py
python3 tables.py          # table-reconstruction attempt (ambiguous: kept for the record)
```
