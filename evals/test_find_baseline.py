"""Bench + regression: a `--find` between two `see`s used to cost the whole tree.

`hd see --find` renders the full tree (it has to, so `hd tap` indexes stay valid) and used to
store its baseline under `mode="find"`. The delta path required `prev["mode"] == mode`, so the
next plain `hd see` had no baseline of its own kind and printed the entire compact tree instead
of a delta — silently, without even the "screen changed too much" line.

That is not a rare interleaving. `--find` is the verb agents type most: over the 12 hybrid runs
of the 2026-08-10 A/B/C, 356 of 628 observation calls were `hd see --find`, and 73 of the 185
plain `hd see` re-observations (39%) directly followed a `--find`/`--full`/`-q`.

The fix keys baselines off the RENDERING (compact vs full) rather than the verb, and has a
forced-full render also remember the compact view of the same nodes — no extra dump, one extra
format pass. This file measures the difference on real screens:

    python3 evals/test_find_baseline.py [app ...]

Set `$HD_PY` to another revision of hd.py to price the fix against it (that is what the
`unfixed=` column does automatically when the plugin cache still holds the old copy).
"""

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402
from test_diff import clickables, launch  # noqa: E402

STATE = "/tmp/hd_last_tree.json"


def run(hd_py, *args):
    r = subprocess.run(["python3", hd_py, *args], capture_output=True, text=True, env=ENV)
    return r.stdout


def loop(hd_py, pkg, pat, targets):
    """observe -> act -> `--find` -> act -> observe, the way agents actually drive.

    The second action is the point: the final plain `see` has a real change to report, so a
    whole tree there is the delta path failing, not an honest full render.
    Returns one (action, chars, delta?) row per re-observation.
    """
    launch(pkg)
    rows = []
    for idx in targets:
        run(hd_py, "see")
        run(hd_py, "tap", str(idx))
        time.sleep(2)
        run(hd_py, "see", "--find", pat)      # the interleaved verb under test
        run(hd_py, "key", "back")
        time.sleep(2)
        out = run(hd_py, "see")               # what it costs to re-observe after it
        rows.append((f"tap {idx}", len(out), "diff vs last see" in out))
        time.sleep(1)
    return rows


def test_find_keeps_the_compact_baseline():
    """A `--find` must not destroy the baseline a following `see` would diff against."""
    src = Path(find_hd()).read_text()
    assert '"baselines"' in src, "state file no longer keeps per-rendering baselines"
    assert 'prev.get("mode") == mode' not in src, "the diff is gated on the verb again"


if __name__ == "__main__":
    from suites import APPS  # noqa: E402

    test_find_keeps_the_compact_baseline()
    print("regression: --find keeps the compact baseline  OK\n")

    fixed = find_hd()
    unfixed = os.environ.get("HD_PY_OLD", "")
    which = sys.argv[1:] or ["markor", "amaze", "seal", "unitto"]
    tot_fix = tot_old = n = deltas = old_deltas = 0
    for key in which:
        pkg, pat = APPS[key]["pkg"], "Button|Text|View|Menu"
        try:
            launch(pkg)
            targets = clickables(run(fixed, "see"))[1:4]
            rows = loop(fixed, pkg, pat, targets)
            old = {r[0]: r for r in loop(unfixed, pkg, pat, targets)} if unfixed else {}
        except Exception as e:                                   # noqa: BLE001
            print(f"{key}: FAILED {e}")
            continue
        for act, chars, delta in rows:
            n += 1
            deltas += delta
            tot_fix += chars
            tot_old += old[act][1] if act in old else chars
            old_deltas += old[act][2] if act in old else delta
            was = (f"  unfixed={old[act][1]:>6} ({'delta' if old[act][2] else 'whole tree'})"
                   if act in old else "")
            print(f"{key:<10}{act:<10} fixed={chars:>6} "
                  f"({'delta' if delta else 'whole tree'}){was}")
    if n:
        print(f"\nTOTAL over {n} re-observations after a `--find`: fixed printed "
              f"{deltas}/{n} deltas in {tot_fix} chars")
        if unfixed:
            print(f"unfixed hd.py: {old_deltas}/{n} deltas in {tot_old} chars — "
                  f"saved {1 - tot_fix / tot_old:.0%} "
                  f"({(tot_old - tot_fix) / 4:,.0f} tokens over {n} re-observations)")
            assert tot_fix <= tot_old, "the fix made re-observation after --find more expensive"
            assert deltas >= old_deltas, "the fix printed fewer deltas than the old revision"
