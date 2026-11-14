"""Build a bot that plays one bot's preflop and another bot's postflop.

    python3 src/build_chimera.py PRE.py POST.py OUT.py

Both sources are embedded (compressed) and loaded into separate namespaces, so neither is
modified. Both keep learning from every hand; preflop decisions go to PRE, the rest to POST."""
import base64, sys, zlib

pre, post, out = sys.argv[1:4]
veto = int(sys.argv[sys.argv.index("--veto") + 1]) if "--veto" in sys.argv else 0   # chips; 0 = no veto
hybrid = "--hybrid" in sys.argv   # our engine bets when nothing is to call and may raise; partner handles calls
exploit = "--exploit" in sys.argv # partner plays postflop; our engine only adds two field-measured overrides
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


# The preflop bot also has a full postflop engine, calibrated on real showdowns. When the
# postflop partner wants to call this many chips or more and that engine would fold, we fold:
# on the real rounds such calls won about one time in seven.
VETO_MIN = %d
HYBRID = %s
EXPLOIT = %s


class Agent:
    def __init__(self):
        self.pre = _PRE["Agent"]()
        self.post = _POST["Agent"]()
        try:
            self.pre._budget = lambda st: 0.0008      # short simulation when asked for a second opinion
        except Exception:
            pass

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
            if state.get("street") == "preflop":
                out = self.pre.act(state)
            elif EXPLOIT:
                out = self.post.act(state)
                tc = state.get("to_call") or 0
                if tc > 0:
                    mine = self.pre.act(state)
                    if getattr(self.pre, "small_raise", False):
                        out = mine                         # raise a bet under 40 percent of the pot: its author folds 7 in 10
                    elif (out.get("action") == "call" and mine.get("action") == "fold"
                          and state.get("street") == "river" and getattr(self.pre, "last_cat", 9) <= 1):
                        raises = 0
                        for h in state.get("history") or ():
                            if h["street"] == "river" and h["action"] == "raise":
                                raises += 1
                        if raises >= 2 or tc >= 0.45 * (state.get("pot") or 1):
                            out = mine                     # one pair against a river raise or a pot-size river bet
            elif HYBRID:
                tc = state.get("to_call") or 0
                if tc <= 0:
                    out = self.pre.act(state)              # our own betting: small bets, stabs, value
                else:
                    mine = self.pre.act(state)
                    if mine.get("action") == "raise":
                        out = mine                         # value raise, or a raise of a small bet
                    else:
                        out = self.post.act(state)
                        if (out.get("action") == "call" and mine.get("action") == "fold"
                                and state.get("street") == "river" and tc >= 0.45 * (state.get("pot") or 1)):
                            out = mine                     # pot-size river bet that our engine will not pay
            else:
                out = self.post.act(state)
        except Exception:
            out = None
        a = out.get("action") if isinstance(out, dict) else None
        if a == "call" and VETO_MIN and state.get("street") != "preflop" and (state.get("to_call") or 0) >= VETO_MIN:
            try:
                if self.pre.act(state).get("action") == "fold":
                    a = "fold"
            except Exception:
                pass
        if a == "raise" and "raise" in legal:
            return out
        if a == "call" and "call" in legal:
            return {"action": "call"}
        if a == "check" and "check" in legal:
            return {"action": "check"}
        if a == "fold" and "check" not in legal:
            return {"action": "fold"}
        return {"action": "check"} if "check" in legal else {"action": "fold"}
''' % (pre.split("/")[-1], post.split("/")[-1], pack(pre), pack(post), veto,
       "True" if hybrid else "False", "True" if exploit else "False")
open(out, "w").write(src)
print("wrote", out, len(src.encode()), "bytes")
