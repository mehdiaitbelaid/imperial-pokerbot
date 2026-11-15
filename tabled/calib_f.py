"""Calibration helpers for the finalists' replicas (tabled/f_*.py), parallel to measure.py.

    python3 tabled/calib_f.py nodes DIR [DIR ...]   # freeze the f_* replicas' node class mixes into tabled/_nodes_f.py
                                                    # (run it only on games of the replicas; _nodes.py is not touched)
    python3 tabled/calib_f.py table DIR [DIR ...]   # calibration table real / replica, "!" = more than 10 points apart

DIR is a directory written by tools/selfplay.py --out.  The statistics are measure.py's.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build as B  # noqa: E402
import build_f as BF  # noqa: E402
import measure as M  # noqa: E402

STREETS = ("flop", "turn", "river")


def auto_sizes(short, F, canon):
    """Main sizes, and the sizes after which the fewest / the most top pairs or better were shown."""
    sizes = sorted(set(s for st in STREETS for s in canon[st] if s != BF.A))
    share = dict((s, max(M.size_share(F, st, (s, round(s - 0.01, 2))) or 0.0 for st in STREETS)) for s in sizes)
    main = [s for s in sorted(sizes, key=lambda s: -share[s]) if share[s] >= 0.08][:5] or sizes[:1]
    tp = {}
    for s in main:
        r = M.tp_share(F, [(st, (s, round(s - 0.01, 2))) for st in STREETS])
        if r[1] >= 10:
            tp[s] = r[0]
    lo = min(tp, key=tp.get) if tp else main[0]
    hi = max(tp, key=tp.get) if tp else main[0]
    pair = lambda s: (s, round(s - 0.01, 2))  # noqa: E731
    return dict(bluff=pair(lo), value=pair(hi), main=tuple(pair(s) for s in main))


def main():
    mode, dirs = sys.argv[1], sys.argv[2:]
    sim, nf = M.measure_sim(dirs)
    print("# %d game files" % nf)
    if mode == "nodes":
        old = M.TEAMS
        M.TEAMS = BF.TEAMS_F
        try:
            M.write_nodes(sim, os.path.join(HERE, "_nodes_f.py"))
        finally:
            M.TEAMS = old
        print("# wrote tabled/_nodes_f.py")
        return
    FULL, LAST, info = BF.measure()
    for short, team in BF.TEAMS_F:
        if short not in sim:
            continue
        hand = BF.auto_hand(short, FULL[short], LAST[short])
        M.SIZES[short] = S = auto_sizes(short, FULL[short], hand["canon"])
        a, b = M.rows(FULL[short], short), M.rows(sim[short], short)
        print("\n%s (%s): real %d rounds / replica %d hands; size A %g, size B %g" % (
            team, short, len(info[short][0]), int(sim[short].v["hands"]), S["bluff"][0], S["value"][0]))
        line = []
        for (k, x), (_, y) in zip(a, b):
            flag = "!" if (x is not None and y is not None and abs(x - y) > 0.10) else ""
            line.append("%s %s/%s%s" % (k, M.pc(x).strip(), M.pc(y).strip(), flag))
        print("  " + " | ".join(line))
    print("\n%-12s %7s %7s" % ("seat", "hands", "bb/100"))
    for name in sorted(sim, key=lambda k: -sim[k].v["chips"] / max(1, sim[k].v["hands"])):
        print("%-12s %7d %+7.1f" % (name, sim[name].v["hands"], sim[name].v["chips"] / max(1, sim[name].v["hands"]) * 5))


if __name__ == "__main__":
    main()
