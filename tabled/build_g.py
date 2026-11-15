"""Three more finalist replicas (f_astra, f_matcha, f_jump), same method as build_f.py.

    python3 tabled/build_g.py              # rewrites the three files
    python3 tabled/build_g.py nodes DIR    # freeze their node class mixes into tabled/_nodes_g.py
    python3 tabled/build_g.py table DIR    # calibration table real / replica

Only imports build_f.py / calib_f.py / measure.py: no existing replica or node file is touched.
None of the three teams appears in hands/sunday_s1_r0*.json (our Sunday table), so the
parameters come from hands/saturday_r0*.json.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_f as BF  # noqa: E402
import measure as M  # noqa: E402

TEAMS_G = [("f_astra", "Astra La Vista"), ("f_matcha", "matcha mille crêpes cake"), ("f_jump", "Jump Street")]
BF.TEAMS_F = TEAMS_G


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "build"
    if mode == "build":
        FULL, LAST, info, out = BF.build()
        for short, team in TEAMS_G:
            _, P, doc, hand = out[short]
            path = BF.write(short, team, P, doc)
            src = open(path, encoding="utf-8").read().replace("_nodes_f", "_nodes_g").replace("build_f.py", "build_g.py")
            open(path, "w", encoding="utf-8").write(src)
            print("wrote", os.path.basename(path), "| %d rounds, %d hands | latest third %s" % (
                len(info[short][0]), int(FULL[short].v["hands"]), ",".join(info[short][1])))
            for x in BF.NOTES[short]:
                print("   note:", x)
            print("   canon", hand["canon"])
        for x in BF.B.LOG:
            print("   latest third:", x)
    elif mode == "nodes":
        sim, nf = M.measure_sim(sys.argv[2:])
        old = M.TEAMS
        M.TEAMS = TEAMS_G
        try:
            M.write_nodes(sim, os.path.join(HERE, "_nodes_g.py"))
        finally:
            M.TEAMS = old
        print("# %d files, wrote tabled/_nodes_g.py" % nf)
    else:
        import calib_f
        sys.argv = [sys.argv[0], "table"] + sys.argv[2:]
        calib_f.main()


if __name__ == "__main__":
    main()
