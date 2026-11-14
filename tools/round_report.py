"""Fetch new rounds and write one data report per counted round into reports/.

    python3 tools/round_report.py            # fetch, report every round not yet reported
    python3 tools/round_report.py --wait     # first wait (up to 9 min) until a new round exists

Needs the team data token in team.token (git-ignored). Each report holds: the platform's
numbers for the round, per-team stats at our table, where our chips went, our worst hands,
timeouts found by replaying our decisions through the live build (upload/bot.py), which
opponents look like the starter-kit bot, and who we won from. reports/field.txt is rebuilt
with every team's pooled stats over all counted rounds."""
import importlib.util, json, os, subprocess, sys, time, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "reports")
TOKEN = open(os.path.join(ROOT, "team.token")).read().strip()
LIVE = os.path.join(ROOT, "upload", "bot.py")


def api():
    req = urllib.request.Request("https://imperialaihack.com/api/poker/results",
                                 headers={"Authorization": "Bearer " + TOKEN, "User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def run(*args):
    return subprocess.run([sys.executable] + list(args), cwd=ROOT, capture_output=True, text=True, timeout=240).stdout


def kit_check(path):
    model = os.path.join(ROOT, "upload", "bot_v16.py")      # newest opponent model
    spec = importlib.util.spec_from_file_location("botmod", model if os.path.exists(model) else LIVE)
    M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    d = json.load(open(path)); P = d["players"]; n = len(P); me = d["seat"]; A = M.Agent()
    won = [0.0] * n; tot = [0] * n
    for h in d["hands"]:
        hist = []; street = "preflop"; posted = 0
        for e in h["events"]:
            if e[0] == "post":
                hist.append({"seat": e[1], "street": "preflop", "action": "small_blind" if posted == 0 else "big_blind", "amount": e[2]}); posted += 1
            elif e[0] == "board":
                street = e[1]
            elif e[0] == "act":
                hist.append({"seat": e[1], "street": street, "action": e[2], "amount": e[3]})
        shown = {k: v for k, v in h["hole"].items() if k in (h.get("showdown") or {})}
        A._learn({"history": hist, "board": h["board"], "shown": shown, "stacks": [0] * n})
        res = h["results"]; g = sum(r for r in res if r > 0)
        for j in range(n):
            tot[j] += res[j]
            if j != me and g > 0:
                if res[me] > 0 and res[j] < 0: won[j] += -res[j] * res[me] / g
                elif res[me] < 0 and res[j] > 0: won[j] -= -res[me] * res[j] / g
    out = ["%-24s %8s %9s | %-34s | fold to 3-bet, steal-fold, c-bet, fold by line [led-into, gave-up, called-last, checked-through, other]" % (
        "opponent", "bb/100", "we won", "looks like the kit bot")]
    for j in range(n):
        if j == me: continue
        S = A.st[j]
        kit = "KIT preflop + postflop (never folds)" if getattr(S, "exact_starter", S.starter)() else ("KIT preflop only" if S.starter() else ("limp-folder" if S.limp_folder() else "-"))
        lines = " ".join("%d/%d" % (S.ff[c], S.fo[c]) for c in range(5))
        out.append("%-24s %+8.1f %+9.1f | %-34s | f3b %d/%d, steal-fold %d/%d, cbet %d/%d, lines %s" % (
            P[j][:24], tot[j] / 20 / 10, won[j] / 20 / 10, kit, S.f3, S.f3_o, S.st_f, S.st_o, S.cb, S.cb_o, lines))
    return "\n".join(out)


def main():
    os.makedirs(REP, exist_ok=True)
    seen_path = os.path.join(REP, "reported.json")
    seen = json.load(open(seen_path)) if os.path.exists(seen_path) else []
    if "--wait" in sys.argv:
        t_end = time.time() + 540
        while time.time() < t_end:
            try:
                refs = [r["ref"] for r in api()["rounds"] if "practice" not in r["ref"]]
            except Exception:
                refs = []
            if any(r not in seen for r in refs):
                break
            time.sleep(15)
    run("fetch_hands.py", "--token", TOKEN)
    res = api()
    new = []
    for r in sorted(res["rounds"], key=lambda r: r["ref"]):
        if "practice" in r["ref"] or r["ref"] in seen:
            continue
        path = os.path.join(ROOT, "hands", r["ref"].replace("/", "_") + ".json")
        if not os.path.exists(path):
            continue
        name = r["ref"].split("/")[-1]
        txt = ["ROUND %s | our bot: platform v%s | result %+.1f bb/100 | timeouts %s | errors %s | think %ss | table %s seat %s" % (
            name, r["version"], r["bb100"], r["timeouts"], r["errors"], r["think_s"], r["table"], r["seat"]), "",
            "== TABLE STATS (analyze.py) ==", run("tools/analyze.py", path, "--me"),
            "== WHERE OUR CHIPS WENT (leaks.py) ==", run("tools/leaks.py", path, "--worst", "6"),
            "== TIMEOUTS BY REPLAY (replay.py, live build) ==", run("tools/replay.py", LIVE, path),
            "== OPPONENTS: KIT-BOT CHECK, WHAT WE WON FROM EACH (bb/100), THEIR RESPONSES ==", kit_check(path)]
        open(os.path.join(REP, "round_%s.txt" % name), "w").write("\n".join(txt))
        seen.append(r["ref"]); new.append(name)
    json.dump(seen, open(seen_path, "w"))
    counted = sorted(os.path.join(ROOT, "hands", f) for f in os.listdir(os.path.join(ROOT, "hands")) if f.startswith("saturday_r") or f.startswith("sunday"))
    if counted:
        open(os.path.join(REP, "field.txt"), "w").write("POOLED STATS OVER ALL COUNTED ROUNDS AT OUR TABLES\n" + run("tools/analyze.py", *counted))
    print("new reports:", " ".join(new) if new else "none", "| live bot sha", res["lastCheck"]["sha"], "platform v%s" % res["lastCheck"]["version"])


if __name__ == "__main__":
    main()
