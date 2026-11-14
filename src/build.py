"""Build bot.py from src/bot_template.py by embedding tools/preflop.json."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
pf = json.dumps(json.load(open(os.path.join(ROOT, "tools", "preflop.json"))), separators=(",", ":"))
src = open(os.path.join(HERE, "bot_template.py")).read().replace("__PF__", pf)
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "bot.py")
open(out, "w").write(src)
print("wrote", out, len(src.encode()), "bytes")
