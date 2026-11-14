# Field report scripts

Analysis behind `pokerbots-field-report-r29.md`.

**Inputs** (keep them out of git; the folder's `.gitignore` covers them):
- `hands/saturday_rNNN.json`: our team's hand files, fetched through the browser as in `HANDOFF-next-tab.md` section 5. Never commit them or the token.
- `standings-history.csv`: get it with `git show origin/rankings-history:rankings/standings-history.csv > standings-history.csv`.
- `public_r*.json`: pulls of the public standings API (`https://poker.imperialaihack.com/pokerbots/api/public`), which needs no token. Two are committed here.

**Run order:**
1. `python3 rounds.py`
2. `python3 -I field.py hands`
3. Then any of: `summarize.py`, `ourtables.py`, `vs.py`, `rivals.py [team ...]`, `python3 -I rivercalls.py`, `pooled.py`, `python3 -I foldsize.py`

**Other scripts:**
- `decode.py OUTDIR FILE...` turns saved browser-tool results (gzip plus base64 JSON) into hand files.
- `tables.py` is the attempt to rebuild every table's line-up from the leaderboard's zero-sum chip changes. It is ambiguous and could not recover our own table blind, so don't trust its output.
