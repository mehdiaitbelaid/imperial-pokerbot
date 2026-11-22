# imperial-pokerbot

Before any research or code for this repo, read `docs/COMPETITION_CONTEXT.md`. It holds the
organisers' rules, the bot API, verified engine behaviour and measured findings on the example bots.

Non-negotiable constraints for anything that ends up in `bot.py`:
- One file, class `Agent`, Python 3.12 standard library only, under 200 KB.
- 10 ms per decision AND a 10 s bank per round that every decision draws from (about 4 ms average).
- No network, no files, one CPU core, no background threads; import and `Agent()` under 5 s each.
- The bot never learns opponent team names; adaptation happens within each 1,000-hand round.
- Betting structure may change (pot-limit, fixed-limit, raise caps): always size through
  `min_raise_to` / `max_raise_to`. Returning `check` facing a bet is a fold.
- Never commit the fetch_hands data token. No collusion, no attempts on the sandbox or site.

Briefs for strategy work, in reading order: `docs/FIELD_ANALYSIS_BRIEF.md` (measured field,
versions, leaks), `docs/PUNCH_THROUGH_BRIEF.md` (one candidate strategy, assess do not assume),
`docs/FINAL_BOT_REPORT.md` (our versions and test methods). Release gate: `tools/ab_vf.py`
(paired, common random numbers, all-in adjusted) plus the team bands, fuzz, and 0 timeouts at
`local_sim.py --timeout 4 --bank 4`.
