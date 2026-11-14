"""Build bot.py from src/bot_template.py by embedding tools/preflop.json."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
pf = json.dumps(json.load(open(os.path.join(ROOT, "tools", "preflop.json"))), separators=(",", ":"))
tpl = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "bot_template.py")
src = open(tpl).read().replace("__PF__", pf)
re_path = os.path.join(ROOT, "tools", "range_eq.json")
if os.path.exists(re_path):
    src = src.replace("__RE__", open(re_path).read().strip())
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "bot.py")
open(out, "w").write(src)
print("wrote", out, len(src.encode()), "bytes")
