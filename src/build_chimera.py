"""Build a bot that plays one bot's preflop and another bot's postflop.

    python3 src/build_chimera.py PRE.py POST.py OUT.py

Both sources are embedded (compressed) and loaded into separate namespaces, so neither is
modified. Both keep learning from every hand; preflop decisions go to PRE, the rest to POST."""
import base64, sys, zlib

pre, post, out = sys.argv[1:4]
def pack(path):
    raw = open(path, "rb").read()
    b = base64.b64encode(zlib.compress(raw, 9)).decode()
    return "\n".join('    "%s"' % b[i:i + 100] for i in range(0, len(b), 100))

src = '''"""Avengers chimera (Resonance Qt): preflop from %s, postflop from %s.

Preflop: position charts, steals and 3-bets driven by what each seat folds to, and the
starter-kit bot counter (see the embedded source). Postflop: the embedded partner bot.
Both learn from every hand of the round. Standard library only."""
import base64
import zlib

_PRE_SRC = (
%s
)
_POST_SRC = (
%s
)
_PRE = {"__name__": "pre"}
_POST = {"__name__": "post"}
exec(compile(zlib.decompress(base64.b64decode(_PRE_SRC)), "pre", "exec"), _PRE)
exec(compile(zlib.decompress(base64.b64decode(_POST_SRC)), "post", "exec"), _POST)
del _PRE_SRC, _POST_SRC


class Agent:
    def __init__(self):
        self.pre = _PRE["Agent"]()
        self.post = _POST["Agent"]()

    def on_table_start(self, info):
        for a in (self.pre, self.post):
            f = getattr(a, "on_table_start", None)
            if f:
                try:
                    f(info)
                except Exception:
                    pass

    def on_hand_end(self, summary):
        for a in (self.pre, self.post):
            f = getattr(a, "on_hand_end", None)
            if f:
                try:
                    f(summary)
                except Exception:
                    pass

    def act(self, state):
        legal = state.get("legal_actions") or ()
        try:
            out = (self.pre if state.get("street") == "preflop" else self.post).act(state)
        except Exception:
            out = None
        a = out.get("action") if isinstance(out, dict) else None
        if a == "raise" and "raise" in legal:
            return out
        if a == "call" and "call" in legal:
            return {"action": "call"}
        if a == "check" and "check" in legal:
            return {"action": "check"}
        if a == "fold" and "check" not in legal:
            return {"action": "fold"}
        return {"action": "check"} if "check" in legal else {"action": "fold"}
''' % (pre.split("/")[-1], post.split("/")[-1], pack(pre), pack(post))
open(out, "w").write(src)
print("wrote", out, len(src.encode()), "bytes")
