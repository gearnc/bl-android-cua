"""Bench: what the DEFAULT observation verb costs in the observe -> act -> observe loop.

The 24-run eval showed the saving `--diff` offers went unclaimed: across 12 hybrid runs agents
typed `hd see --diff` 8 times in total and never once in 8 of those runs, while spending 217
plain/`--full` re-reads. So the flag, not the mechanism, was the problem. This measures the verb
an agent actually types (`hd see`) against the pre-fix behaviour (`hd see --no-diff`), over real
state changes, and checks the fallbacks still hold:

  * a screen that turned over must print the whole tree, not a bigger delta;
  * a baseline older than DIFF_MAX_AGE must print the whole tree.
"""

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ENV, find_hd  # noqa: E402
from test_diff import clickables, launch  # noqa: E402

HD = ["python3", find_hd()]


def hd(*args):
    return subprocess.run(HD + list(args), capture_output=True, text=True, env=ENV).stdout


def loop(pkg, n_actions=4):
    """Tap, then re-observe the way an agent does: `hd see`, no flag."""
    launch(pkg)
    tree = hd("see")
    rows = []
    for idx in clickables(tree)[2:2 + n_actions]:
        subprocess.run(HD + ["tap", str(idx)], capture_output=True, env=ENV)
        time.sleep(2)
        default = hd("see")               # what the agent types
        before = hd("see", "--no-diff")   # what it used to get
        rows.append((f"tap {idx}", len(before), len(default),
                     "too much to diff" in default))
        subprocess.run(HD + ["key", "back"], capture_output=True, env=ENV)
        time.sleep(1.5)
        hd("see")
    return rows


def check_stale_baseline(pkg):
    """A baseline past DIFF_MAX_AGE must not be diffed against."""
    sys.path.insert(0, str(Path(find_hd()).parent))
    from hd import DIFF_MAX_AGE, STATE  # noqa: PLC0415
    launch(pkg)
    hd("see")
    import json  # noqa: PLC0415
    st = json.load(open(STATE))
    st["ts"] -= DIFF_MAX_AGE + 5
    json.dump(st, open(STATE, "w"))
    out = hd("see")
    return "diff vs last see" not in out


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    which = sys.argv[1:] or ["markor", "amaze", "seal", "unitto", "joplin"]
    tot_before = tot_after = 0
    for key in which:
        try:
            rows = loop(APPS[key]["pkg"])
        except Exception as e:                                   # noqa: BLE001
            print(f"{key}: FAILED {e}")
            continue
        for act, before, after, turned in rows:
            tot_before += before
            tot_after += after
            note = " (screen turned over -> whole tree)" if turned else ""
            print(f"{key:<10}{act:<10} was={before:>6}  now={after:>6}  "
                  f"saved={1 - after / before:>6.0%}{note}")
            assert after <= before + 200, "default observation got more expensive"
    if tot_before:
        print(f"\nTOTAL was={tot_before} now={tot_after} "
              f"saved={1 - tot_after / tot_before:.0%}")
    ok = check_stale_baseline(APPS[which[0]]["pkg"])
    print(f"stale baseline falls back to the whole tree: {'yes' if ok else 'NO'}")
    assert ok
