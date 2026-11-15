# Sunday bucket table: every round so far (rounds 1–7)

Written Sun 15 Nov 2026, about 09:50 UK time, by Claude for Resonance Qt (Saeed, Mehdi, Riyad, Hassan).

**What this covers:** all 7 rounds played at our Sunday table (09:00–09:30), 7,000 hands. Round 1 was played by upload v13. Rounds 2–7 were played by upload v14 (SHA `9a5d1af58a51e822`, the "Avengers" bot with Sunday fingerprints).

**Not covered:** upload v15 (SHA `2298973fea29cff0`) loaded at 09:32:07 and plays from round 8. I have not seen that file, so nothing here describes it.

**Team codes used in every table:**

| Code | Team | Seat |
|---|---|---|
| RQ | Resonance Qt (us) | 0 |
| ANK | Anker Batteries | 1 |
| CPF | Chinese people can fly | 2 |
| WBT | WBot | 3 |
| GG | GamesGone | 4 |
| POK | Poke | 5 |
| ANT | Anton | 6 |
| YSL | YSL_TWIZZY | 7 |

Seats are the same every round. Anker acts directly after us, and YSL directly before us.

---

## 1. Summary

1. **We are 2nd of 8 on +27,327 chips after 7 of 36 rounds.** Anker leads on +40,875. Third is Chinese people can fly on +3,657, so our cushion for the second qualifying place is 23,670 chips.
2. **About half our total is all-in luck.** In hands where all the chips went in before the river and the cards were shown, we won 14,582 more than the odds gave us. Without that we would be on about +12,745. That still ranks 2nd, ahead of CPF's luck-adjusted +2,313.
3. **Anker's lead is not luck.** His all-in luck is −1,294, so his luck-adjusted total is +42,169. He wins +30 bb/100 on that measure against our +9.
4. **Our luck-adjusted result is +1,821 chips a round, plus or minus 1,865** (one standard error over 7 rounds). On this sample we cannot yet show the bot beats this table without luck.
5. **Where the chips come from:** Anton +19,287, YSL +11,809, Poke +5,542, GamesGone +3,262, CPF +1,318. We lose to WBot (−1,075) and to Anker (−12,816).
6. **What is working:**
   - Re-raising YSL before the flop: 423 times, he folded at once 267 times (63%), net +12,510.
   - Raising bets of 40% of the pot or more: 44 times, net +24,545.
   - Opening and then facing a re-raise: 234 times, net +13,889.
7. **What is losing chips:**
   - **Raising small bets** (under 40% of the pot): 94 times, won without a showdown only 38 times (40%), and those hands net −11,373. Against WBot it is 72 raises for −5,291. Against Anker it is 6 raises, none won, −4,813.
   - **Anker in general.** We saw 178 flops with him for −8,858. He called our re-raise 48 times, and those hands net −4,486.
   - **Calling big bets late in the hand.** River calls of 40% of the pot or more: 8, won 0, −8,220 against folding. Turn calls of two-thirds pot or more: 31, won 11, −3,742 against folding.
   - **The big blind.** We lose 1,998 more there than if we folded every hand. Anker's big blind is 17,230 better than folding every hand.
   - **Re-raising GamesGone:** 35 times, he folded at once 12 times, net −4,306.
8. **Timeouts are not a problem:** 1 in 7 rounds, with 2.2–2.6 s of the 10 s thinking bank used per round.

---

## 2. Round by round at a glance

| Round | Time | Upload | Chips | bb/100 | Place in round | Running total | Place overall | Timeouts | Think time (s) | All-in luck | Without luck |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 09:00 | v13 | +758 | +3.8 | 5 | +758 | 5 | 0 | 2.61 | +422 | +336 |
| 2 | 09:05 | v14 | +8,630 | +43.1 | 2 | +9,388 | 2 | 0 | 2.60 | +5,659 | +2,971 |
| 3 | 09:10 | v14 | +1,948 | +9.7 | 4 | +11,336 | 2 | 0 | 2.46 | −3,899 | +5,847 |
| 4 | 09:15 | v14 | +4,506 | +22.5 | 3 | +15,842 | 2 | 0 | 2.36 | +11,423 | −6,917 |
| 5 | 09:20 | v14 | −6,307 | −31.5 | 7 | +9,535 | 2 | 1 | 2.61 | −5,189 | −1,118 |
| 6 | 09:25 | v14 | +10,007 | +50.0 | 1 | +19,542 | 2 | 0 | 2.22 | +6,369 | +3,638 |
| 7 | 09:30 | v14 | +7,785 | +38.9 | 1 | +27,327 | 2 | 0 | 2.23 | −203 | +7,988 |

### Running totals for every team

| After round | RQ | ANK | CPF | WBT | GG | POK | ANT | YSL |
|---|---|---|---|---|---|---|---|---|
| 1 | +758 | +1,314 | −11,506 | +7,232 | −89 | +1,812 | +4,725 | −4,246 |
| 2 | +9,388 | +15,211 | −13,043 | +5,433 | −15,161 | +5,203 | −2,945 | −4,086 |
| 3 | +11,336 | +18,946 | −4,307 | +2,214 | −12,519 | −1,617 | −8,963 | −5,090 |
| 4 | +15,842 | +30,741 | −10,150 | −13,860 | −15,156 | +9,910 | −12,888 | −4,439 |
| 5 | +9,535 | +42,852 | −2,207 | −19,055 | −28,166 | +4,857 | +596 | −8,412 |
| 6 | +19,542 | +38,780 | +4,513 | −29,474 | −18,756 | +2,814 | −3,335 | −14,084 |
| 7 | +27,327 | +40,875 | +3,657 | −37,224 | −19,950 | −2,328 | +939 | −13,296 |

---

## 3. The table: every team over 7 rounds

| Team | Chips | bb/100 | All-in luck | Without luck | Hands played | Raised preflop | Re-raise rate | Folds to a re-raise (cases) | Bets and raises per call | Showdowns | Showdown chips | Non-showdown chips | Big blind chips |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RQ | +27,327 | +19.5 | +14,582 | +12,745 | 24% | 19% | 21% | 65% (234) | 3.2 | 157 | −8,055 | +35,382 | −19,498 |
| ANK | +40,875 | +29.2 | −1,294 | +42,169 | 21% | 13% | 10% | 41% (99) | 1.6 | 187 | +32,795 | +8,080 | −270 |
| CPF | +3,657 | +2.6 | +1,344 | +2,313 | 26% | 19% | 8% | 56% (335) | 1.6 | 247 | +9,155 | −5,498 | −9,238 |
| WBT | −37,224 | −26.6 | −18,002 | −19,222 | 29% | 20% | 5% | 66% (506) | 5.4 | 384 | −27,618 | −9,606 | −27,211 |
| GG | −19,950 | −14.3 | −9,033 | −10,917 | 23% | 14% | 3% | 51% (236) | 1.4 | 279 | +2,577 | −22,527 | −23,874 |
| POK | −2,328 | −1.7 | −3,167 | +839 | 22% | 13% | 7% | 65% (231) | 2.7 | 183 | −10,843 | +8,515 | −15,475 |
| ANT | +939 | +0.7 | +7,949 | −7,010 | 30% | 20% | 20% | 39% (93) | 2.2 | 170 | +50,897 | −49,958 | −11,300 |
| YSL | −13,296 | −9.5 | +7,582 | −20,878 | 16% | 12% | 4% | 83% (539) | 0.7 | 176 | −4,673 | −8,623 | −12,061 |

What stands out:

- **We and Anker win in opposite ways.** We win +35,382 when nobody shows cards and lose 8,055 when cards are shown. Anker wins +32,795 at showdown.
- **We re-raise 21% of the time we can.** Only Anton (20%) is close. Anker re-raises 10%.
- **YSL still folds 83% of the time to a re-raise,** over 539 cases. That play has not stopped working.
- **CPF folds to a re-raise 56% of the time today.** The bot starts from Saturday's 84% for him.
- **WBot has been the unluckiest team** (−18,002) and is still the biggest loser without luck.
- **Anton wins +50,897 at showdown and loses 49,958 without one.** He raises a lot, gives up a lot, and has the goods when called.

### Who won chips from whom

Each row shows what that team won from (+) or lost to (−) each other team. When several players win or lose in one hand, the chips are shared in proportion.

| | RQ | ANK | CPF | WBT | GG | POK | ANT | YSL |
|---|---|---|---|---|---|---|---|---|
| RQ | — | −12,816 | +1,318 | −1,075 | +3,262 | +5,542 | +19,287 | +11,809 |
| ANK | +12,816 | — | −2,225 | +16,121 | −1,411 | +7,125 | +2,048 | +6,401 |
| CPF | −1,318 | +2,225 | — | +6,486 | −7,761 | −7,189 | +5,104 | +6,110 |
| WBT | +1,075 | −16,121 | −6,486 | — | −8,450 | −492 | −9,777 | +3,027 |
| GG | −3,262 | +1,411 | +7,761 | +8,450 | — | −16,134 | −8,703 | −9,473 |
| POK | −5,542 | −7,125 | +7,189 | +492 | +16,134 | — | −14,259 | +783 |
| ANT | −19,287 | −2,048 | −5,104 | +9,777 | +8,703 | +14,259 | — | −5,361 |
| YSL | −11,809 | −6,401 | −6,110 | −3,027 | +9,473 | −783 | +5,361 | — |

Anker's two biggest sources are WBot (+16,121) and us (+12,816).

### The big blind, every team

"Against folding" compares the result with losing 20 chips on every big-blind hand.

| Team | Big blind chips | Against folding every hand | Folds to a raise | Calls | Re-raises |
|---|---|---|---|---|---|
| RQ | −19,498 | −1,998 | 72% | 21% | 7% |
| ANK | −270 | +17,230 | 47% | 46% | 7% |
| CPF | −9,238 | +8,262 | 66% | 27% | 8% |
| WBT | −27,211 | −9,711 | 62% | 35% | 2% |
| GG | −23,874 | −6,374 | 61% | 36% | 3% |
| POK | −15,475 | +2,025 | 63% | 28% | 10% |
| ANT | −11,300 | +6,200 | 50% | 21% | 28% |
| YSL | −12,061 | +5,439 | 86% | 9% | 5% |

Our own big blind over 7 rounds, by first action: folded 620 times (−12,400), called 185 (−6,113, which is 2,413 worse than folding those hands), raised 58 (−724, which is 436 better than folding), checked 12 (−261).

---

## 4. Our play over 7 rounds

- **Before the flop:** played 24.1% of hands, raised 19.5%, re-raised 630 of 2,979 chances (21.1%).
- **By seat:** button +21,369, small blind −2,147, big blind −19,498, other five seats +27,603.
- **How our hands ended:** before the flop 6,129 (−2,251); saw a flop with no showdown 714 (+37,633); showdown 157, won 70 (−8,055).
- **Our bets after the flop:** 657, and everyone folded to 335 of them (51%).
- **Full stacks:** won 38, lost 31.
- **All-in before the river with cards shown:** 54 hands.

### Re-raises before the flop, by who opened

| Opener | Re-raises | He folded at once | Net chips |
|---|---|---|---|
| YSL | 423 | 267 (63%) | +12,510 |
| WBT | 78 | 36 (46%) | +160 |
| POK | 48 | 26 (54%) | +3,022 |
| GG | 35 | 12 (34%) | −4,306 |
| CPF | 22 | 7 (32%) | +1,076 |
| ANT | 22 | 11 (50%) | +1,973 |
| ANK | 2 | 0 | −340 |

Who else called our re-raise matters. When nobody but the opener continued (536 hands) we made +12,677. When Anker called it (48 hands) we made −4,486. Anton calling it (12 hands) gave +3,896, GamesGone (28 hands) +1,165 and WBot (9 hands) +1,012.

### When we opened and were re-raised

234 times: folded 151 (65%), called 43, re-raised again 40. Net +13,889. The re-raise-again count rose to 12 in round 6 and 14 in round 7, from 0–6 in earlier rounds.

### Our raises over someone's bet after the flop

"Won" means we took the pot without a showdown and nobody raised again. "Net" is the whole result of those hands.

| Size of the bet we raised | Raises | Won | Net chips |
|---|---|---|---|
| Under 40% of the pot | 94 | 38 (40%) | −11,373 |
| 40–90% of the pot | 35 | 24 (69%) | +17,325 |
| Over 90% of the pot | 9 | 2 | +7,220 |

The small-bet raises by bettor: WBot 72 (won 29, −5,291), CPF 8 (won 7, +1,365), Poke 7 (won 1, −2,952, all in round 1), Anker 6 (won 0, −4,813), Anton 1 (won 1, +318).

The bot's code (`RAISE_SMALL`) assumes the author of a small bet gives up roughly 65–75% of the time when raised, and starts WBot's smallest bets at 80% from Saturday. Today the raise wins outright 40% of the time against WBot.

### Our calls after the flop, against folding

"Against folding" is the hand's final result plus the chips we had already put in before the call. It shows what continuing was worth compared with folding at that point. Only the first call on each street is counted.

| Street | Bet size (share of pot) | Calls | Hands won | Against folding |
|---|---|---|---|---|
| Flop | under 40% | 21 | 8 | +2,572 |
| Flop | 40–66% | 68 | 36 | +9,700 |
| Flop | 66–100% | 48 | 25 | +1,764 |
| Flop | over 100% | 14 | 11 | +7,899 |
| Turn | under 40% | 19 | 7 | +5,169 |
| Turn | 40–66% | 33 | 18 | +6,730 |
| Turn | 66–100% | 18 | 6 | −473 |
| Turn | over 100% | 13 | 5 | −3,269 |
| River | under 40% | 20 | 7 | +5,856 |
| River | 40–66% | 3 | 0 | −2,581 |
| River | 66–100% | 3 | 0 | −2,811 |
| River | over 100% | 2 | 0 | −2,828 |

Turn and river calls of two-thirds pot or more, by who bet: Anker 7 (won 1, −5,469), CPF 7 (won 1, −1,111), GamesGone 7 (won 2, −1,115), WBot 7 (won 3, −645), Poke 5 (won 2, −708), Anton 3 (won 2, −333). In total 36 calls, 11 won, −9,381.

### Hands where we saw a flop with each opponent

| Opponent in the hand | Flops | Our net chips |
|---|---|---|
| ANT | 155 | +15,410 |
| GG | 229 | +10,289 |
| CPF | 201 | +9,492 |
| POK | 162 | +6,587 |
| YSL | 63 | +640 |
| WBT | 219 | −1,712 |
| ANK | 178 | −8,858 |

A hand with two opponents counts in both rows.

---

## 5. Every round in detail

In each round table, "We won from or lost to" is our row of the chip-flow table for that round. "All-in luck" is actual chips minus expected chips in hands where everyone left was all in before the river and the cards were shown.

The hand tables list every hand where we won or lost 1,500 chips or more. "All-in" gives the street the chips went in and our chance of winning at that moment.

### Round 1 · 09:00 · upload v13

**+758 chips (+3.8 bb/100), 5th of 8 in the round. Running total +758, place 5.** Timeouts 0, think time 2.61 s.

| | RQ | ANK | CPF | WBT | GG | POK | ANT | YSL |
|---|---|---|---|---|---|---|---|---|
| This round | +758 | +1,314 | −11,506 | +7,232 | −89 | +1,812 | +4,725 | −4,246 |
| Running total | +758 | +1,314 | −11,506 | +7,232 | −89 | +1,812 | +4,725 | −4,246 |
| We won from (+) or lost to (−) | — | −1,525 | +2,480 | −2,027 | +1,168 | −1,618 | +958 | +1,322 |
| All-in luck | +422 | −1,587 | −3,023 | +2,261 | −595 | +3,578 | +958 | −2,057 |

- **Before the flop:** played 21% of hands, raised 16%. Re-raised 70 of 421 chances (17%).
- **Re-raises by opener** (count, folded at once, net): YSL 46, 35, +2,386; GG 8, 3, −324; ANT 5, 3, −1,442; WBT 5, 4, −276; CPF 4, 2, +2,916; POK 1, 0, −1,334; ANK 1, 0, −170.
- **We opened and were re-raised** 27 times: folded 19, called 6, re-raised again 2. Net −434.
- **By seat:** button −1,042, small blind +1,552, big blind −3,062, other five seats +3,310.
- **Big blind, first action:** folded 87 (−1,740), called 22 (−1,046), raised 8 (−386), checked 8 (+110).
- **How our hands ended:** before the flop 897 (+1,688); saw a flop, no showdown 84 (−121); showdown 19, won 7 (−809).
- **Our bets after the flop:** 74, everyone folded to 30 (41%).
- **Our raises over a bet** (count, won without showdown, net): bet under 40% of pot 13, 5, −3,460; 40–90% 5, 4, +2,852; over 90% none. By bettor: POK small 7, 1, −2,952; WBT small 3, 2, −189; CPF small 2, 1, −637; POK medium 2, 1, +2,184; GG medium 2, 2, +556; ANT small 1, 1, +318; WBT medium 1, 1, +112.
- **Turn or river calls of two-thirds pot or more:** 3, won 0, −2,335 against folding.
- **All-in before the river with cards shown:** 5 hands, actual +2,100, expected +1,678, luck +422.
- **Full stacks:** won 3, lost 2.

| Hand | Result | Our cards | Board | Shown by | Action | All-in |
|---|---|---|---|---|---|---|
| #250 | +2,070 | QhKh | Ks 4c Kc 2h Js | ANT Kd5d | pre: RQ raises to 60, CPF calls 60, ANT calls 40 / flop: ANT bets 1940, RQ calls 1940 | flop, 80% |
| #397 | +2,020 | Ad8d | 8h 8s 4d 7h 3h | CPF 9h9d | pre: CPF raises to 50, RQ raises to 170, CPF calls 120 / flop: RQ bets 180, CPF calls 180 / turn: RQ bets 1650, CPF calls 1650 | turn, 95% |
| #401 | +2,010 | AdAs | 3c 4d 8s Qc Tc | POK 6s6h | pre: RQ raises to 60, POK calls 40 / flop: POK bets 71, RQ raises to 315, POK calls 244 / turn: POK bets 250, RQ raises to 1625, POK calls 1375 | turn, 95% |
| #410 | −2,000 | QsQh | 2h 5d 4d 4s 6s | POK 6c3c | pre: RQ raises to 60, WBT calls 60, POK calls 50 / flop: POK bets 320, RQ calls 320 / turn: POK bets 1620, RQ calls 1620 | turn, 9% |
| #911 | −2,000 | JdJc | 8d 7d 7c 5h 9d | ANT QhQd | pre: POK calls 20, ANT raises to 100, RQ raises to 300, ANT raises to 690, RQ calls 390 / flop: ANT bets 1310, RQ calls 1310 | flop, 10% |

### Round 2 · 09:05 · upload v14

**+8,630 chips (+43.1 bb/100), 2nd of 8 in the round. Running total +9,388, place 2.** Timeouts 0, think time 2.60 s.

| | RQ | ANK | CPF | WBT | GG | POK | ANT | YSL |
|---|---|---|---|---|---|---|---|---|
| This round | +8,630 | +13,897 | −1,537 | −1,799 | −15,072 | +3,391 | −7,670 | +160 |
| Running total | +9,388 | +15,211 | −13,043 | +5,433 | −15,161 | +5,203 | −2,945 | −4,086 |
| We won from (+) or lost to (−) | — | −851 | +688 | +51 | +4,835 | −1,408 | +3,204 | +2,111 |
| All-in luck | +5,659 | +1,075 | −2,905 | −5,076 | −6,507 | +2,331 | +3,550 | +1,882 |

- **Before the flop:** played 27% of hands, raised 22%. Re-raised 111 of 463 chances (24%).
- **Re-raises by opener** (count, folded at once, net): YSL 76, 37, +1,968; POK 10, 4, +2,294; ANT 7, 4, +1,204; WBT 7, 4, −2,178; GG 6, 2, +1,726; CPF 4, 1, −440; ANK 1, 0, −170.
- **We opened and were re-raised** 35 times: folded 26, called 7, re-raised again 2. Net +2,342.
- **By seat:** button +9,765, small blind −1,019, big blind −1,419, other five seats +1,303.
- **Big blind, first action:** folded 82 (−1,640), called 31 (+883), raised 10 (−231), checked 2 (−431).
- **How our hands ended:** before the flop 850 (−3,431); saw a flop, no showdown 121 (+8,370); showdown 29, won 13 (+3,691).
- **Our bets after the flop:** 115, everyone folded to 69 (60%).
- **Our raises over a bet** (count, won without showdown, net): bet under 40% of pot 12, 3, −1,103; 40–90% 5, 3, +4,719; over 90% 4, 1, +2,640. By bettor: WBT small 12, 3, −1,103; GG big 3, 1, +4,640; ANT medium 3, 2, +2,518; WBT big 1, 0, −2,000; WBT medium 1, 0, +2,066; POK medium 1, 1, +135.
- **Turn or river calls of two-thirds pot or more:** 7, won 2, −2,092 against folding.
- **All-in before the river with cards shown:** 12 hands, actual +12,516, expected +6,857, luck +5,659.
- **Full stacks:** won 11, lost 6.

| Hand | Result | Our cards | Board | Shown by | Action | All-in |
|---|---|---|---|---|---|---|
| #11 | −2,000 | KsAd | 3h Qh As Td 7h | WBT Ac7s | pre: RQ raises to 60, WBT calls 50, GG calls 40 / flop: WBT bets 180, RQ raises to 666, WBT calls 486 / turn: WBT bets 226, RQ calls 226 / river: WBT bets 1048, RQ calls 1048 | |
| #49 | +2,030 | 8s8d | 7d 4c 8h 2s Ad | GG 7s7c | pre: GG raises to 44, RQ calls 44 / flop: GG bets 118, RQ raises to 436, GG raises to 1956, RQ calls 1520 | flop, 95% |
| #77 | +2,010 | QhKh | Qd Qc 7c 8d Jc | ANT AdAh | pre: RQ raises to 60, ANT raises to 216, RQ calls 156 / flop: ANT bets 353, RQ raises to 1784, ANT calls 1431 | flop, 91% |
| #129 | +2,030 | KsKh | Th Kc 8h 4s 7h | GG KdTd | pre: GG raises to 44, RQ raises to 132, GG calls 88 / flop: GG bets 294, RQ raises to 1087, GG raises to 1868, RQ calls 781 | flop, 100% |
| #133 | −2,000 | TsTd | Qd 6s 9c Qs 9s | ANT Qc8h | pre: RQ raises to 60, ANT calls 40 / flop: ANT bets 104, RQ calls 104 / turn: ANT bets 1836, RQ calls 1836 | turn, 5% |
| #215 | +2,010 | 9cTc | 8d Qd 9h Jd 3c | WBT AsAc | pre: WBT raises to 70, RQ calls 50 / flop: WBT bets 150, RQ calls 150 / turn: RQ bets 225, WBT calls 225 / river: WBT bets 135, RQ raises to 1555, WBT calls 1420 | |
| #218 | −2,000 | JcJd | 9d Qd 7h 3h 4s | WBT 7s9c | pre: RQ raises to 44, WBT calls 24 / flop: WBT bets 98, RQ calls 98 / turn: RQ bets 470, WBT raises to 1858, RQ calls 1388 | turn, 18% |
| #358 | +2,090 | 7h7d | 4d 4s 2h 8d Ts | WBT 6c6d | pre: RQ raises to 60, WBT calls 60, GG calls 60 / flop: RQ bets 336, WBT raises to 1218, RQ calls 882 / turn: WBT bets 396, RQ calls 396 / river: WBT bets 326, RQ calls 326 | |
| #431 | +2,080 | QcTs | 8c Qs 4s Qh Tc | WBT KdQd | pre: WBT raises to 70, POK calls 70, RQ calls 50 / turn: RQ bets 176, WBT raises to 1930, RQ calls 1754 | turn, 14% |
| #486 | −2,000 | 9sTs | Qd 2h Tc 6d Jc | POK KhJh | pre: RQ raises to 60, POK calls 60, ANT calls 50 / flop: RQ bets 160, POK calls 160 / turn: POK bets 520, RQ calls 520 / river: RQ bets 1260, POK calls 1260 | |
| #494 | +2,030 | AdAs | Kd 6h 9c 2s 2h | CPF QcQd | pre: RQ raises to 60, CPF raises to 180, RQ raises to 468, CPF raises to 2000, RQ calls 1532 | pre, 82% |
| #501 | +2,070 | AcQh | Qd 3h 8s 6h 3d | WBT JdTd | pre: RQ raises to 60, WBT calls 60, ANT calls 40 / flop: RQ bets 304, WBT raises to 1102, RQ raises to 1940, WBT calls 838 | flop, 77% |
| #504 | −2,000 | QcKs | 2c 2h Ac 9d 2d | WBT Ad8d | pre: WBT raises to 70, RQ raises to 238, WBT calls 168 / flop: RQ bets 396, WBT calls 396 / turn: RQ bets 1366, WBT calls 1366 | turn, 0% |
| #536 | +2,135 | 8c8h | 8d Qh 5c Qs Ac | YSL 9c9h | pre: POK raises to 45, ANT calls 45, YSL calls 45, RQ calls 35, ANK calls 25 / flop: RQ bets 360, YSL calls 360 / turn: RQ bets 1595, YSL calls 1595 | turn, 91% |
| #649 | +2,065 | TsAh | Ac Th Kc As 2s | ANK Ad9s | pre: POK raises to 45, RQ raises to 125, ANK calls 115 / flop: ANK bets 126, RQ calls 126 / turn: ANK bets 1749, RQ calls 1749 | turn, 94% |
| #807 | −2,000 | 9hAs | 4s 2h Th Ac 3h | WBT 5d5c | pre: WBT raises to 70, ANT calls 70, RQ calls 50 / flop: WBT bets 72, RQ raises to 216, WBT calls 144 / turn: RQ bets 326, WBT calls 326 / river: WBT bets 1388, RQ calls 1388 | |
| #818 | +2,066 | 6s7d | 6d Jd Kd 6c 3h | WBT KsAs | pre: YSL raises to 56, RQ raises to 156, WBT calls 136 / flop: WBT bets 378, RQ calls 378 / turn: WBT bets 680, RQ raises to 1466, WBT calls 786 | turn, 95% |

### Round 3 · 09:10 · upload v14

**+1,948 chips (+9.7 bb/100), 4th of 8 in the round. Running total +11,336, place 2.** Timeouts 0, think time 2.46 s.

| | RQ | ANK | CPF | WBT | GG | POK | ANT | YSL |
|---|---|---|---|---|---|---|---|---|
| This round | +1,948 | +3,735 | +8,736 | −3,219 | +2,642 | −6,820 | −6,018 | −1,004 |
| Running total | +11,336 | +18,946 | −4,307 | +2,214 | −12,519 | −1,617 | −8,963 | −5,090 |
| We won from (+) or lost to (−) | — | −3,868 | −1,405 | +1,023 | −1,155 | +2,782 | +4,968 | −397 |
| All-in luck | −3,899 | −289 | +1,691 | +558 | −2,098 | −7,371 | +6,827 | +4,566 |

- **Before the flop:** played 24% of hands, raised 18%. Re-raised 99 of 445 chances (22%).
- **Re-raises by opener** (count, folded at once, net): YSL 58, 36, −2,156; WBT 32, 16, +1,746; GG 3, 1, −1,428; POK 3, 1, +568; CPF 2, 0, +455; ANT 1, 0, +756.
- **We opened and were re-raised** 22 times: folded 16, called 6, re-raised again 0. Net +1,270.
- **By seat:** button −1,193, small blind +5,670, big blind −5,638, other five seats +3,109.
- **Big blind, first action:** folded 86 (−1,720), called 29 (−2,974), raised 10 (−944), checked 0.
- **How our hands ended:** before the flop 867 (+81); saw a flop, no showdown 114 (+6,819); showdown 19, won 7 (−4,952).
- **Our bets after the flop:** 105, everyone folded to 52 (50%).
- **Our raises over a bet** (count, won without showdown, net): bet under 40% of pot 14, 9, −502; 40–90% 6, 5, +1,185; over 90% none. By bettor: WBT small 9, 6, −424; ANT medium 3, 3, +439; CPF small 3, 3, +1,174; GG medium 2, 2, +731; ANK small 2, 0, −1,252; YSL medium 1, 0, +15.
- **Turn or river calls of two-thirds pot or more:** 6, won 3, −1,145 against folding.
- **All-in before the river with cards shown:** 7 hands, actual −1,678, expected +2,221, luck −3,899.
- **Full stacks:** won 4, lost 4.
- **Anker called our re-raise 14 times this round,** and those hands net −5,915.

| Hand | Result | Our cards | Board | Shown by | Action | All-in |
|---|---|---|---|---|---|---|
| #53 | +2,030 | 9h9d | 2d 6c 9c 2h Kh | CPF QsQd | pre: RQ raises to 60, CPF raises to 180, RQ calls 120 / flop: RQ bets 624, CPF calls 624 / turn: RQ bets 1196, CPF calls 1196 | turn, 95% |
| #108 | −2,000 | KsAc | Qc 9d 6h 5h Jd | ANK QhQs | pre: GG raises to 44, RQ raises to 167, ANK calls 167, GG calls 123 / flop: ANK bets 451, RQ calls 451 / turn: ANK bets 1382, RQ calls 1382 | turn, 0% |
| #122 | +2,272 | AcAd | 6d 5c Qd 5d 4c | POK KdKh | pre: POK raises to 70, ANT raises to 252, RQ raises to 2000, POK calls 1930 | pre, 81% |
| #338 | +2,020 | Ts4d | 5h 7c Tc 7d 9s | WBT KcAc | pre: WBT raises to 70, RQ raises to 238, WBT calls 168 / flop: RQ bets 396, WBT raises to 1684, RQ calls 1288 / turn: RQ bets 78, WBT calls 78 | turn, 66% |
| #564 | +2,064 | 6c5c | Ks 6d 4c 5d Ts | ANK KcJd | pre: RQ raises to 44, ANK calls 44, CPF calls 34 / flop: RQ bets 121, ANK calls 121 / turn: RQ bets 630, ANK calls 630 / river: RQ bets 1205, ANK calls 1205 | |
| #620 | −2,000 | 7c7d | 3h 2h 5c Qd As | CPF KsAh | pre: ANT calls 20, RQ raises to 120, ANK calls 120, CPF raises to 380, ANT raises to 873, RQ raises to 2000, CPF calls 1620 | pre, 56% |
| #721 | −2,000 | Jh9s | 6s 3s Jc 7d Ah | WBT QhAs | pre: WBT raises to 70, RQ raises to 238, WBT calls 168 / flop: RQ bets 388, WBT raises to 1650, RQ calls 1262 / turn: RQ bets 112, WBT calls 112 | turn, 86% |
| #979 | −2,000 | Qh9c | Th 4s Qd 3h Ks | ANK QcTd | pre: YSL raises to 56, RQ raises to 156, ANK calls 146 / flop: ANK bets 271, RQ calls 271 / turn: ANK bets 1573, RQ calls 1573 | turn, 0% |

### Round 4 · 09:15 · upload v14

**+4,506 chips (+22.5 bb/100), 3rd of 8 in the round. Running total +15,842, place 2.** Timeouts 0, think time 2.36 s.

| | RQ | ANK | CPF | WBT | GG | POK | ANT | YSL |
|---|---|---|---|---|---|---|---|---|
| This round | +4,506 | +11,795 | −5,843 | −16,074 | −2,637 | +11,527 | −3,925 | +651 |
| Running total | +15,842 | +30,741 | −10,150 | −13,860 | −15,156 | +9,910 | −12,888 | −4,439 |
| We won from (+) or lost to (−) | — | +3,221 | −1,544 | +2,894 | −756 | −2,301 | +2,250 | +742 |
| All-in luck | +11,423 | +3,359 | −1,703 | −7,018 | −3,572 | +2,245 | −7,531 | +2,779 |

- **Before the flop:** played 20% of hands, raised 16%. Re-raised 63 of 415 chances (15%).
- **Re-raises by opener** (count, folded at once, net): WBT 18, 8, +2,860; YSL 18, 9, −282; POK 15, 10, −863; GG 9, 5, −438; CPF 2, 2, +130; ANT 1, 0, −168.
- **We opened and were re-raised** 26 times: folded 17, called 5, re-raised again 4. Net +5,035.
- **By seat:** button +4,434, small blind −3,965, big blind −1,931, other five seats +5,968.
- **Big blind, first action:** folded 90 (−1,800), called 22 (−39), raised 13 (−92), checked 0.
- **How our hands ended:** before the flop 899 (−2,203); saw a flop, no showdown 80 (+6,140); showdown 21, won 10 (+569).
- **Our bets after the flop:** 69, everyone folded to 38 (55%).
- **Our raises over a bet** (count, won without showdown, net): bet under 40% of pot 16, 6, +4,555; 40–90% 3, 1, +2,261; over 90% 1, 0, −2,000. By bettor: WBT small 16, 6, +4,555; POK medium 1, 0, +2,055; GG medium 1, 1, +201; WBT medium 1, 0, +5; POK big 1, 0, −2,000.
- **Turn or river calls of two-thirds pot or more:** 8, won 3, +1,151 against folding.
- **All-in before the river with cards shown:** 9 hands, actual +4,276, expected −7,147, luck +11,423.
- **Full stacks:** won 5, lost 4.
- **This was our luckiest round.** We won four all-ins as a big underdog: #151 (19%), #556 (23%), #806 (18%) and #919 (14%). Re-raises of YSL dropped to 18 this round, from 58–79 in the rounds around it.

| Hand | Result | Our cards | Board | Shown by | Action | All-in |
|---|---|---|---|---|---|---|
| #151 | +2,020 | QsAs | 6c Js Ac Qh 3d | ANT JhAd | pre: RQ raises to 60, ANT raises to 216, RQ calls 156 / flop: ANT bets 1784, RQ calls 1784 | flop, 19% |
| #229 | −2,000 | JdAc | Kh Jh Qd 3h 4h | WBT Ah6h | pre: RQ raises to 60, WBT calls 60, POK calls 40 / flop: RQ bets 152, WBT calls 152 / turn: WBT bets 1788, RQ calls 1788 | turn, 0% |
| #485 | +2,076 | 4d4s | 2s 4c Kc 2h 5s | YSL QhAc | pre: YSL raises to 56, RQ calls 56, GG calls 46 / flop: RQ bets 300, YSL calls 300 / turn: RQ bets 1644, YSL calls 1644 | turn, 100% |
| #556 | +2,055 | 9hAh | 9c 9s Td Jc Ad | POK QcKs | pre: POK raises to 45, RQ calls 45, GG calls 25 / flop: POK bets 72, RQ raises to 332, POK calls 260 / turn: POK bets 1623, RQ calls 1623 | turn, 23% |
| #609 | −2,000 | ThAc | Kd 5s Jd Kc 2c | POK TdTc | pre: POK raises to 45, RQ raises to 153, POK calls 108 / flop: RQ bets 260, POK calls 260 / turn: RQ bets 676, POK calls 676 / river: RQ bets 911, POK calls 911 | |
| #700 | −2,000 | AhAd | 7s Kc Kh Tc 2c | CPF QhKd | pre: RQ raises to 60, ANK calls 60, CPF calls 60 / flop: RQ bets 168, CPF raises to 632, RQ calls 464 / turn: CPF bets 1308, RQ calls 1308 | turn, 5% |
| #806 | +2,030 | KhKc | Ts Qs Ks 2d 7h | ANK AhAc | pre: RQ raises to 60, ANK raises to 192, RQ raises to 499, ANK raises to 2000, RQ calls 1501 | pre, 18% |
| #919 | +2,090 | AsJc | 4d 8h 6d 8c Js | WBT 7d7s | pre: RQ raises to 60, CPF calls 60, WBT calls 60 / flop: RQ bets 168, WBT calls 168 / turn: RQ bets 436, WBT raises to 1772, RQ calls 1336 | turn, 14% |
| #949 | −2,000 | 6d6s | Ah 6c 9c 8d 4c | POK 9d9s | pre: RQ raises to 60, CPF calls 60, POK calls 40 / flop: POK bets 190, RQ raises to 703, POK raises to 1940, RQ calls 1237 | flop, 4% |

### Round 5 · 09:20 · upload v14

**−6,307 chips (−31.5 bb/100), 7th of 8 in the round. Running total +9,535, place 2.** Timeouts 1, think time 2.61 s.

| | RQ | ANK | CPF | WBT | GG | POK | ANT | YSL |
|---|---|---|---|---|---|---|---|---|
| This round | −6,307 | +12,111 | +7,943 | −5,195 | −13,010 | −5,053 | +13,484 | −3,973 |
| Running total | +9,535 | +42,852 | −2,207 | −19,055 | −28,166 | +4,857 | +596 | −8,412 |
| We won from (+) or lost to (−) | — | −4,940 | −3,695 | −6,672 | −1,469 | +3,509 | +2,812 | +4,148 |
| All-in luck | −5,189 | −2,215 | +2,311 | +1,811 | −2,129 | +49 | +5,178 | +183 |

- **Before the flop:** played 27% of hands, raised 23%. Re-raised 111 of 398 chances (28%).
- **Re-raises by opener** (count, folded at once, net): YSL 79, 54, +6,183; POK 14, 9, +2,602; WBT 8, 2, −1,988; ANT 4, 2, +1,354; CPF 4, 1, −1,555; GG 2, 0, −338.
- **We opened and were re-raised** 47 times: folded 32, called 9, re-raised again 6. Net −1,162.
- **By seat:** button +524, small blind −3,091, big blind −6,884, other five seats +3,144.
- **Big blind, first action:** folded 90 (−1,800), called 25 (−4,084), raised 9 (−1,040), checked 1 (+40).
- **How our hands ended:** before the flop 870 (−475); saw a flop, no showdown 101 (+2,442); showdown 29, won 11 (−8,274).
- **Our bets after the flop:** 87, everyone folded to 44 (51%).
- **Our raises over a bet** (count, won without showdown, net): bet under 40% of pot 9, 2, −3,459; 40–90% 7, 5, +469; over 90% none. By bettor: WBT small 7, 1, −3,450; GG medium 2, 2, +955; ANT medium 2, 1, −508; POK medium 2, 1, −90; ANK small 1, 0, −254; WBT medium 1, 1, +112; CPF small 1, 1, +245.
- **Turn or river calls of two-thirds pot or more:** 6, won 1, −3,920 against folding.
- **All-in before the river with cards shown:** 7 hands, actual −1,930, expected +3,259, luck −5,189.
- **Full stacks:** won 5, lost 7.
- **Our only losing round.** Three of the seven lost stacks were all in before the flop at 45–57% (#271, #446, #598). The other four were calls or bets into a made hand: #288, #359, #607 and #720.

| Hand | Result | Our cards | Board | Shown by | Action | All-in |
|---|---|---|---|---|---|---|
| #221 | +2,030 | KsKh | 9d 7s As Ac 9s | WBT QdQh | pre: RQ raises to 60, WBT raises to 195, RQ raises to 507, WBT raises to 2000, RQ calls 1493 | pre, 82% |
| #271 | −2,000 | QcQd | 8s 7h Ah 9s 3s | CPF KhAd | pre: CPF raises to 50, RQ raises to 185, CPF raises to 2000, RQ calls 1815 | pre, 57% |
| #288 | −2,000 | KcAd | 5h Ah Td 9c 6c | WBT 5d5c | pre: WBT raises to 70, RQ calls 60, ANK calls 50 / flop: RQ bets 105, WBT raises to 945, RQ calls 840 / turn: WBT bets 985, RQ calls 985 | turn, 0% |
| #359 | −2,000 | 8c9c | 7c Js Ts Jc Kd | CPF JhKh | pre: CPF raises to 50, POK calls 50, RQ calls 30 / flop: RQ bets 80, CPF calls 80, POK calls 80 / turn: RQ bets 640, CPF calls 640 / river: CPF bets 1230, RQ calls 1230 | |
| #390 | +2,030 | AsAc | Js 6c 9c Ah 8c | POK AdJd | pre: RQ raises to 60, POK calls 60 / flop: RQ bets 75, POK raises to 225, RQ calls 150 / turn: RQ bets 960, POK raises to 1715, RQ calls 755 | turn, 100% |
| #446 | −2,000 | KhAh | 4s 7h 6d 7s Ts | GG QhQd | pre: RQ raises to 60, GG raises to 180, ANT raises to 413, RQ raises to 2000, GG calls 1820 | pre, 45% |
| #590 | +2,020 | JcAh | Td Qd 4h 3c Ks | ANT QhJd | pre: RQ raises to 60, ANT raises to 216, RQ calls 156 / flop: ANT bets 361, RQ calls 361 / turn: ANT bets 645, RQ calls 645 / river: RQ bets 778, ANT calls 778 | |
| #598 | −2,000 | KsAs | Js Qc 7c Jd 8s | WBT ThTd | pre: RQ raises to 60, CPF calls 60, WBT calls 60, ANT raises to 336, RQ raises to 2000, WBT calls 1940 | pre, 46% |
| #607 | −2,000 | 8sAc | Qs 6s 8c Qd Qh | ANK AdAs | pre: ANK raises to 50, RQ calls 30 / flop: RQ bets 88, ANK raises to 259, RQ calls 171 / turn: RQ bets 502, ANK calls 502 / river: ANK bets 1189, RQ calls 1189 | |
| #720 | −2,000 | AhQc | 5s Ac Kh 7c Ks | ANK KdQd | pre: RQ raises to 50, ANK calls 30 / flop: RQ bets 160, ANK calls 160 / turn: ANK bets 462, RQ calls 462 / river: RQ bets 672, ANK raises to 1328, RQ calls 656 | |
| #777 | +2,231 | Ac4d | Ks 3d 6s 7h 5d | YSL TcTh | pre: ANT calls 20, YSL raises to 72, RQ raises to 201, ANT calls 181, YSL calls 129 / turn: RQ bets 506, YSL calls 506 / river: RQ bets 1293, YSL calls 1293 | |
| #967 | +2,010 | TdJh | Js 4s Tc 7h 9d | ANT Jc4d | pre: ANT raises to 50, RQ calls 30 / flop: RQ bets 176, ANT raises to 1950, RQ calls 1774 | flop, 91% |

### Round 6 · 09:25 · upload v14

**+10,007 chips (+50.0 bb/100), 1st of 8 in the round. Running total +19,542, place 2.** Timeouts 0, think time 2.22 s.

| | RQ | ANK | CPF | WBT | GG | POK | ANT | YSL |
|---|---|---|---|---|---|---|---|---|
| This round | +10,007 | −4,072 | +6,720 | −10,419 | +9,410 | −2,043 | −3,931 | −5,672 |
| Running total | +19,542 | +38,780 | +4,513 | −29,474 | −18,756 | +2,814 | −3,335 | −14,084 |
| We won from (+) or lost to (−) | — | −5,015 | +2,307 | +2,597 | −108 | +3,747 | +3,400 | +3,079 |
| All-in luck | +6,369 | −4,739 | +5,565 | −7,362 | +5,173 | −2,041 | −2,178 | −765 |

- **Before the flop:** played 25% of hands, raised 21%. Re-raised 94 of 417 chances (23%).
- **Re-raises by opener** (count, folded at once, net): YSL 79, 52, +3,753; WBT 4, 1, +88; GG 4, 0, −4,161; CPF 4, 1, −440; POK 2, 1, −50; ANT 1, 0, −251.
- **We opened and were re-raised** 27 times: folded 11, called 4, re-raised again 12. Net +3,033.
- **By seat:** button +6,801, small blind −1,543, big blind −3,248, other five seats +7,997.
- **Big blind, first action:** folded 93 (−1,860), called 28 (−1,254), raised 3 (−154), checked 1 (+20).
- **How our hands ended:** before the flop 865 (+1,657); saw a flop, no showdown 112 (+9,200); showdown 23, won 10 (−850).
- **Our bets after the flop:** 116, everyone folded to 58 (50%).
- **Our raises over a bet** (count, won without showdown, net): bet under 40% of pot 15, 6, −4,064; 40–90% 4, 2, +4,544; over 90% 2, 0, +4,090. By bettor: WBT small 11, 5, −1,095; ANK small 3, 0, −3,307; YSL medium 1, 1, +293; POK medium 1, 1, +135; CPF small 1, 1, +338; CPF big 1, 0, +2,070; ANK medium 1, 0, +2,086; POK big 1, 0, +2,020; WBT medium 1, 0, +2,030.
- **Turn or river calls of two-thirds pot or more:** 3, won 2, +1,993 against folding.
- **All-in before the river with cards shown:** 8 hands, actual +8,286, expected +1,917, luck +6,369.
- **Full stacks:** won 7, lost 6.
- **Anker took 5,015 from us in a round he lost overall.** In #69, #455 and #681 we re-raised an opener with a weak hand, Anker called behind us, we bet all three streets and he called every time. That is 6,000 chips in three hands. #309 started the same way and we won it as a 7% underdog on the turn.

| Hand | Result | Our cards | Board | Shown by | Action | All-in |
|---|---|---|---|---|---|---|
| #3 | +2,030 | AhAd | 2c Kd 5s Ac 7h | POK KcQc | pre: RQ raises to 60, POK calls 60 / flop: RQ bets 240, POK raises to 870, RQ raises to 1940, POK calls 1070 | flop, 77% |
| #69 | −2,000 | Kd7d | 4s 2d 2s 9h Js | ANK QsQc | pre: GG raises to 44, RQ raises to 149, ANK calls 129 / flop: RQ bets 273, ANK calls 273 / turn: RQ bets 710, ANK calls 710 / river: RQ bets 868, ANK calls 868 | |
| #275 | −1,605 | 6d6s | 4s 5d 7h Kh Jc | WBT KcQs | pre: RQ raises to 60, WBT calls 60, GG calls 60 / flop: WBT bets 210, GG calls 210, RQ calls 210 / turn: WBT bets 126, RQ raises to 378, WBT calls 252 / river: WBT bets 957, RQ calls 957 | |
| #309 | +2,050 | ThQh | Jd 2c Ah 4s Kh | ANK AsKs | pre: YSL raises to 50, RQ raises to 170, ANK calls 150 / flop: RQ bets 624, ANK calls 624 / turn: RQ bets 1206, ANK calls 1206 | turn, 7% |
| #352 | +2,070 | QcKs | 9s Qd 3h 5s Kh | CPF AcQh | pre: RQ raises to 60, CPF calls 60, GG calls 40 / flop: CPF bets 190, RQ raises to 703, CPF calls 513 / turn: CPF bets 1237, RQ calls 1237 | turn, 7% |
| #393 | +2,080 | KsAd | 6d 7h Ah 6s Td | WBT 2dAc | pre: RQ raises to 60, WBT calls 60, GG calls 50 / flop: RQ bets 100, WBT calls 100 / turn: RQ bets 640, WBT calls 640 / river: RQ bets 1200, WBT calls 1200 | |
| #455 | −2,000 | 2h3d | Ad 3h Jd Kh Qs | ANK AsTs | pre: YSL raises to 56, RQ raises to 156, ANK calls 156 / flop: RQ bets 318, ANK calls 318 / turn: RQ bets 517, ANK calls 517 / river: RQ bets 1009, ANK calls 1009 | |
| #681 | −2,000 | 4c7c | Qs 9h 6c 2d 5c | ANK 9dAc | pre: YSL raises to 56, RQ raises to 156, ANK calls 156 / flop: RQ bets 318, ANK calls 318 / turn: RQ bets 517, ANK calls 517 / river: RQ bets 1009, ANK calls 1009 | |
| #712 | +2,086 | AhJd | Jc Qd As 3h 6s | ANK 7hAd | pre: YSL raises to 56, RQ raises to 156, ANK calls 156 / flop: RQ bets 636, ANK calls 636 / turn: ANK bets 668, RQ raises to 1208, ANK calls 540 | turn, 97% |
| #735 | −2,000 | KcKd | 7s Th Jc 5s Ac | GG QdAd | pre: GG raises to 44, RQ raises to 132, GG raises to 2000, RQ calls 1868 | pre, 69% |
| #738 | +2,020 | JdJc | 4d 2c 7d 7c 8s | POK AdKh | pre: RQ raises to 60, POK raises to 240, RQ calls 180 / flop: POK bets 250, RQ calls 250 / turn: POK bets 1000, RQ raises to 1510, POK calls 510 | turn, 86% |
| #798 | +2,030 | 3d3s | 2d Jd 3h 8c 6d | WBT 8dAc | pre: WBT raises to 70, RQ calls 70 / flop: WBT bets 102, RQ raises to 438, WBT raises to 1484, RQ raises to 1930, WBT calls 446 | flop, 95% |
| #932 | −2,000 | Jd9d | 5c 7d Jh 2h Jc | ANK JsKs | pre: ANK raises to 50, GG calls 50, RQ calls 30 / flop: ANK bets 99, RQ calls 99 / turn: ANK bets 143, RQ raises to 429, ANK raises to 1851, RQ calls 1422 | turn, 7% |

### Round 7 · 09:30 · upload v14

**+7,785 chips (+38.9 bb/100), 1st of 8 in the round. Running total +27,327, place 2.** Timeouts 0, think time 2.23 s.

| | RQ | ANK | CPF | WBT | GG | POK | ANT | YSL |
|---|---|---|---|---|---|---|---|---|
| This round | +7,785 | +2,095 | −856 | −7,750 | −1,194 | −5,142 | +4,274 | +788 |
| Running total | +27,327 | +40,875 | +3,657 | −37,224 | −19,950 | −2,328 | +939 | −13,296 |
| We won from (+) or lost to (−) | — | +162 | +2,487 | +1,059 | +747 | +831 | +1,695 | +804 |
| All-in luck | −203 | +3,102 | −592 | −3,176 | +695 | −1,958 | +1,145 | +994 |

- **Before the flop:** played 25% of hands, raised 20%. Re-raised 82 of 420 chances (20%).
- **Re-raises by opener** (count, folded at once, net): YSL 67, 44, +658; WBT 4, 1, −92; GG 3, 1, +657; ANT 3, 2, +520; POK 3, 1, −195; CPF 2, 0, +10.
- **We opened and were re-raised** 50 times: folded 30, called 6, re-raised again 14. Net +3,805.
- **By seat:** button +2,080, small blind +249, big blind +2,684, other five seats +2,772.
- **Big blind, first action:** folded 92 (−1,840), called 28 (+2,401), raised 5 (+2,123), checked 0.
- **How our hands ended:** before the flop 881 (+432); saw a flop, no showdown 102 (+4,783); showdown 17, won 12 (+2,570).
- **Our bets after the flop:** 91, everyone folded to 44 (48%).
- **Our raises over a bet** (count, won without showdown, net): bet under 40% of pot 15, 7, −3,340; 40–90% 5, 4, +1,295; over 90% 2, 1, +2,490. By bettor: WBT small 14, 6, −3,585; GG medium 3, 3, +1,285; POK medium 2, 1, +10; GG big 1, 1, +430; CPF small 1, 1, +245; WBT big 1, 0, +2,060.
- **Turn or river calls of two-thirds pot or more:** 3, won 0, −3,033 against folding.
- **All-in before the river with cards shown:** 6 hands, actual +4,175, expected +4,378, luck −203.
- **Full stacks:** won 3, lost 2.
- **Our best round on merit:** +7,988 without all-in luck, and a profit against all seven opponents. Both lost stacks started with a raise of a small WBot bet (#365 and #438).

| Hand | Result | Our cards | Board | Shown by | Action | All-in |
|---|---|---|---|---|---|---|
| #365 | −2,000 | TcJd | Ts 6d 4s 6c 4d | WBT Ad4c | pre: RQ raises to 44, WBT calls 24 / flop: WBT bets 32, RQ raises to 96, WBT raises to 386, RQ calls 290 / turn: WBT bets 130, RQ calls 130 / river: WBT bets 1440, RQ calls 1440 | |
| #438 | −2,000 | 8d9d | 5d Kd 3h As Jc | WBT ThAc | pre: ANT raises to 90, RQ calls 90, WBT calls 80, GG calls 70 / flop: WBT bets 54, RQ raises to 162, WBT calls 108 / turn: RQ bets 1748, WBT calls 1748 | turn, 20% |
| #536 | +2,030 | QcQd | Qs 8h Kc 3h 2c | CPF 9d9s | pre: RQ raises to 60, CPF raises to 180, RQ raises to 468, CPF calls 288 / flop: RQ bets 1532, CPF calls 1532 | flop, 98% |
| #691 | +2,070 | 5h5d | 6h 5c 5s 2d 8h | WBT As7d | pre: WBT raises to 70, RQ calls 60, ANK calls 50 / flop: RQ bets 336, WBT raises to 1218, RQ raises to 1930, WBT calls 712 | flop, 100% |
| #806 | +2,060 | KhKd | 9s 4h 2d 6d 3s | WBT ThAs | pre: RQ raises to 60, WBT calls 50, GG calls 40 / flop: WBT bets 180, RQ raises to 666, WBT raises to 1940, RQ calls 1274 | flop, 86% |

---

## 6. What to test next

These are candidates for the people working on the bot. None is tested, and uploads go through Saeed or Mehdi. Check first whether upload v15 already changes any of them.

1. **Stop raising WBot's and Anker's small bets.** In `bot.py` this is the `RAISE_SMALL` block in `_postflop`. Either skip it for seats labelled `WBOT` and `ANKER`, or lower the `WBOT` seed in `SEED` (first two lists, first entry: 12 raised, 9.65 folded). Evidence: 78 raises against those two, −10,104.
2. **Do not re-raise light when Anker is still to act.** The any-two-cards re-raise (`THREEBET_ANY`) checks only for frequent re-raisers behind us (`hot`). Anker calls behind us and then calls three bets. Evidence: 48 hands, −4,486, including three full stacks in round 6.
3. **Stop betting three streets as a bluff into Anker.** He reaches showdown with winners: +32,795 at showdown over 7 rounds.
4. **Fold more to river bets of 40% of the pot or more.** Evidence: 8 calls, 0 won, −8,220. The sample is small, but Saturday's field report found the same leak.
5. **Stop re-raising GamesGone light.** He folded at once 12 times in 35, and it cost 4,306.

What to leave alone: the YSL re-raise, the Anton rules, raises of medium and big bets, flop calls, and small river calls. All are clearly profitable.

---

## 7. How these numbers were made

- **Source:** the team data API (`/api/poker/results` and `/api/poker/hands?ref=sunday/s1/rNNN`), read through the browser at about 09:35. The token and hand files are not in this repository.
- **Checks passed:**
  - Our chips in each round's hand file equal the server's round result, all 7 rounds.
  - Every hand's results add to zero.
  - Running totals after round 5 equal the public standings pulled at 09:23.
  - The hand evaluator used for the luck figures picked the same winners as the server in all 855 showdown hands.
- **All-in luck:** for hands that reached showdown with no betting possible after the flop or turn (or before the flop), each shown hand's chance of winning was computed at the moment the last chips went in. Flop and turn cases are exact. Preflop cases use 20,000 random boards, so those figures can move by a few dozen chips. Luck is actual chips minus (chance × pot − chips put in). It does not measure any other kind of luck, such as which cards we were dealt.
- **Chip flow:** in each hand, every loser's chips are assigned to the winners in proportion to what each won.
- **"Folded at once"** for a re-raise means the hand ended before the flop with us winning.
- **Limits:**
  - Opponents' cards are visible only at showdown.
  - The round data gives a timeout count but not which hand it was.
  - Seven rounds is a small sample. A single round swings by several thousand chips on luck, so treat every per-opponent figure as a lead to test, not a proven fact.
