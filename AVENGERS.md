# Avengers bot (branch `fable-bot`)

`upload/bot.py` is the file to upload. Its source is `src/avengers.py`; build with

    python3 src/build.py upload/bot.py src/avengers.py

(the build embeds `tools/preflop.json` and `tools/range_eq.json`).

## What it does

- Preflop: position charts, instant. Facing raises and shoves it uses the equity of the hand
  against the raiser's estimated range (`tools/range_eq.json`), not pot odds.
- Postflop: each opponent gets a range from his preflop line, re-ranked on the board and
  narrowed by his actions and his stats this round. Equity is exact on the river and Monte
  Carlo before. Decisions compare the expected value of check, several bet sizes, call and raise.
- Per seat it learns during the round: fold to bets by street, fold to raises, fold to 3-bets,
  blind fold to steals, bet and raise frequency, how often aggressive hands shown down were air.

## Findings from the real practice hands (about 6,000)

- **bigRoddy and Joca run the starter kit's example bot unchanged.** They raise every time with
  any pair, ace or king (570 of 570 shown hands) and fold everything else to any bet above
  2 big blinds (about 980 of 980). FisherMen also folds every limp to a raise (433 of 434).
  The bot detects this (`St.starter()`, `St.limp_folder()`), raises their limps with any two
  cards, calls their raises to see flops, and gets all in above 50% against pair/ace/king.
- The field folds 56% / 40% / 50% to a 40-80% pot bet on flop / turn / river, and no more to a
  bigger bet. Blinds fold 71% each to a late open whatever the size.
- A river bet under 80% of the pot comes from a weak range (callers win 46%), a bet of 80% or
  more from a strong one (callers win 15%, only 34 samples).

## Tools

    python3 tools/selfplay.py A.py field/x.py ... --vs B.py C.py --rounds 20   # same seat, same cards
    python3 tools/selfplay.py A.py --pool <bots> --vs B.py --rounds 30         # tournament mode
    python3 tools/analyze.py hands/*.json --me                                  # per-team stats
    python3 tools/calib.py upload/bot.py                                        # predicted vs real folds
    python3 tools/calib_call.py upload/bot.py                                   # equity facing river bets
    python3 tools/matrix.py sim/run/*.json                                      # who wins from whom

`field/` holds sparring bots whose measured stats match real opponents. Caveat: they fold less
on turn and river than the real field and their bet sizes do not track hand strength, so a
change calibrated on real hands can look a few bb/100 worse against them.

`fetch_hands.py` sends a browser User-Agent: the site answers 403 to Python's default.
