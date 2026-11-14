# Findings from X (searched 2026-11-14 through Mehdi's logged in Chrome)

X has very little real pokerbot strategy. Almost every recent post is promotion for Sequoia, Citadel Securities and OpenAI's "No Limit" student pokerbot tournament (regionals 6 to 11 Nov 2026, finals 15 Nov in San Francisco). One post links a full write up by a team that finished 6th of 148. That write up is the only source used below.

Source: Dylan Nguyen and Samuel Choi, "Folding to the Visible Card", 8 Nov 2026, https://dylannguyen.xyz/no-limit (PDF), linked from https://x.com/dylann4500.

Their game differs from ours (three hole cards with a discard and an exposed card, sit and go scoring with rising blinds, 1 ms per decision). The numbers do not transfer. The process lessons do, because the setting is the same: 8 seats, 100 bb, student bots built in hours, rounds every 20 minutes, hand histories after each round.

## What transfers to our tournament

1. **Measure the field before trusting your priors.** Their first fix was changing the assumed fold to bet rate from 0.55 to 0.45 after one practice round. Real student bots called more than they expected.
2. **Their biggest single gain was folding more to flop and turn bets heads up.** Calling with no pair or draw lost 1.6 to 1.8 bb per call and middle pair lost 2.1 to 3.6 bb (about 9,000 hands). Their fold rate to flop bets was 34% while the top 12 teams' median was 61%. Fixing it moved them from 14th to 3rd in a round. Check our own fold to flop bet rate against what the field's bets turn out to be.
3. **Then they overshot.** After the fix they folded 73% of the time to a first bet while the field folded about 50%, and opponents started betting into them 90% of the time. Against bets under 40% of the pot they folded 57%; the leaders folded 22%. Lesson: tune the threshold from data, do not hard code "fold everything but top pair", and defend more against small bets.
4. **A version that crushed their own older bots scored 100th of 125 live.** It had learned to 3-bet 58% of the time because their old versions fold to aggression; the real field called 46% of the time with strong hands. Self play overfits. Benchmarks against our own versions are a regression check only, not proof of strength.
5. **Release gate with behaviour bands.** Before every upload they replayed identical tables with the candidate and the last good version and compared decision frequencies. A VPIP outside 22 to 35% or a PFR outside 17 to 27% blocked the release, and any frequency that moved more than 10 points had to be explained by the intended change. This catches bugs that a win rate number hides.
6. **Zero failed decisions is achievable and necessary.** They ran every Monte Carlo loop against a deadline of 30% of the limit, embedded all tables in the file, ran one throwaway decision of each type at import to warm up, and called `gc.freeze()` plus raised garbage collection thresholds, which removed a 2.6 ms pause. In our terms: deadline about 3 ms inside the 10 ms limit, and consider the garbage collection trick.
7. **Shrink opponent stats toward a field prior with a small pseudo count (they used 6)**, so the model reacts within tens of hands.
8. **Multiway equity as a product of heads up equities** is a cheap approximation they used with 120 to 300 trials per opponent.
9. **Bet or check by comparing expected values**, with the fold probability taken from the opponents' measured fold rates and equity when called discounted because calling ranges are stronger. They never bluffed the river into visible strength: those bluffs got folds only 10.5% of the time.
10. **Watch the field's 3-bet rate drift.** It rose from 6.9% to 12.3% over six rounds as teams adapted, and one team switched to a hyper aggressive bot in the last round (58% VPIP, 60% 3-bet). Teams that kept folding to 3-bets lost most to it. Our model should adapt per opponent, and we should recheck the field on Sunday morning.
11. **Wider late position steals lost value for them** (VPIP 28.5% to 33% cost about 1.2 points per table). Test before widening.
12. **Unit test anything borrowed from the kit.** A bug in the organisers' SDK cost them about 1.4 points. Our kit's engine is the tournament engine, so local results should match, but check edge cases such as raise clamping and all in handling.

## Variance note

They measured about ±2 points per table of noise over the first 1,000 tables and found practice rounds scored higher than counted rounds, because weaker experimental bots play in practice. Expect our counted round numbers to be lower than practice.
