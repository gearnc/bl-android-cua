"""Measure what `hd see --diff` saves in the loop it is meant for: observe -> act -> observe.

For each app: open it, take a baseline `see`, then perform a few taps/swipes and compare the
cost of the follow-up observation as a full tree vs as a diff. Reports characters, since that
is what lands in the agent's context.
"""

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402

HD = ["python3", find_hd()]


def hd(*args):
    r = subprocess.run(HD + list(args), capture_output=True, text=True, env=ENV)
    return r.stdout


def launch(pkg):
    subprocess.run([ADB, "shell", "monkey", "-p", pkg, "-c",
                    "android.intent.category.LAUNCHER", "1"],
                   capture_output=True, env=ENV)
    time.sleep(4)


def clickables(tree):
    """Indexes of clickable rows in a rendered tree, most-recently-rendered order."""
    out = []
    for line in tree.splitlines():
        if "<C" in line and line.strip().startswith("["):
            out.append(int(line.strip()[1:line.strip().index("]")]))
    return out


def measure(pkg, n_actions=4):
    """Drive real state changes (taps into the app, then back) and price each re-observation."""
    launch(pkg)
    tree = hd("see")
    rows = []
    for i, idx in enumerate(clickables(tree)[2:2 + n_actions]):
        subprocess.run(HD + ["tap", str(idx)], capture_output=True, text=True, env=ENV)
        time.sleep(2)
        # Order matters: the diff has to run against the PRE-action tree, so it must come
        # first. Taking the full tree first refreshes the state file and makes every diff read
        # "no change", which is a measurement of nothing.
        d = hd("see")                    # the default is now the diff
        full = hd("see", "--no-diff")
        changed = "too much to diff" in d
        rows.append((f"tap {idx}", len(full), len(d), changed))
        subprocess.run(HD + ["key", "back"], capture_output=True, env=ENV)
        time.sleep(1.5)
        hd("see")
    return rows


if __name__ == "__main__":
    from suites import APPS
    which = sys.argv[1:] or ["markor", "fossify_notes", "seal", "unitto", "joplin"]
    tot_full = tot_diff = 0
    for key in which:
        pkg = APPS[key]["pkg"]
        try:
            rows = measure(pkg)
        except Exception as e:                                  # noqa: BLE001
            print(f"{key}: FAILED {e}")
            continue
        for act, f, d, turned in rows:
            tot_full += f
            tot_diff += d
            note = " (fell back to full tree)" if turned else ""
            print(f"{key:<16}{act:<12} full={f:>6}  diff={d:>6}  "
                  f"saved={1 - d / f:>6.0%}{note}")
    if tot_full:
        print(f"\nTOTAL full={tot_full} diff={tot_diff} saved={1 - tot_diff / tot_full:.0%}")
