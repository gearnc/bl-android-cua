"""Smoke test + bench: `accessibility-cli` against `hd see`, per app in the matrix.

Runs before any matrix that includes the `acli` arm, for the same reason `test_dumps.py` does:
an arm named after a binary that errors on this snapshot measures the agent's fallback, not the
binary. It also prices one observation in each tool, in characters, since that is what lands in
the agent's context.

Compared, per app:
    hd see              the default delta (first look after a launch is a full tree)
    hd see --no-diff    the whole tree
    accessibility-cli --platform android --llm      its compact output
    accessibility-cli --platform android            its default tree output

Usage: python3 evals/test_acli.py [app ...]
"""
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_acli, find_hd  # noqa: E402
from plan import DEFAULT_APPS  # noqa: E402
from suites import APPS  # noqa: E402

HD = ["python3", find_hd()]
ACLI = [find_acli(), "--platform", "android"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, env=ENV, timeout=180)
    return r.returncode, r.stdout


def launch(pkg):
    subprocess.run([ADB, "shell", "monkey", "-p", pkg, "-c",
                    "android.intent.category.LAUNCHER", "1"], capture_output=True, env=ENV)
    time.sleep(4)


if __name__ == "__main__":
    which = sys.argv[1:] or list(DEFAULT_APPS)
    print(f"{'app':<12}{'hd see':>9}{'hd full':>9}{'acli llm':>10}{'acli tree':>11}   problems")
    bad = 0
    for key in which:
        launch(APPS[key]["pkg"])
        rc_hd, hd_diff = run(HD + ["see"])
        _, hd_full = run(HD + ["see", "--no-diff"])
        rc_llm, llm = run(ACLI + ["--llm"])
        rc_tree, tree = run(ACLI + ["--format", "tree"])
        problems = [n for n, rc, out in (("hd", rc_hd, hd_diff), ("acli --llm", rc_llm, llm),
                                         ("acli tree", rc_tree, tree))
                    if rc != 0 or not out.strip()]
        bad += bool(problems)
        print(f"{key:<12}{len(hd_diff):>9}{len(hd_full):>9}{len(llm):>10}{len(tree):>11}   "
              f"{', '.join(problems) or 'none'}")
    sys.exit(1 if bad else 0)
