"""Bench: what a re-observation costs when nodes DISAPPEAR or are renumbered in bulk.

The 2026-08-16 A/B/C measured 413 "screen changed too much to diff" lines against 194 deltas
actually printed across the 12 hybrid runs — 68% of the delta-capable looks paid for a whole
tree. `bench_scroll_diff.py` fixed the scrolled-list half of that (a row that only moved is one
`~` line); this is the other half. A delta re-printed every removed node IN FULL, so closing a
menu — 28 nodes gone, nothing else changed — cost 2,482 characters against a 2,313-character
tree, and `see` correctly discarded the delta for the tree. The caller is already holding those
28 lines; the news is one index each.

The fix under test prints a removal as `- [i] "label"` (the index in the tree the caller read)
and collapses a contiguous constant-shift renumbering into one `~ [a-b]->[c-d]` line.

Drives menu/dialog open-and-close on real apps against both revisions of `hd.py`, prices each
re-observation, and checks the three things the fix must not break:

  * a screen that genuinely turned over still prints the whole tree, not a bigger delta;
  * every `- [i]` names a node that WAS in the tree the caller read and is gone now;
  * every collapsed `~ [a-b]->[c-d]` run names the same node under each pair of indexes, so a
    renumbered row stays tappable without being reprinted.

Usage:  python3 evals/bench_delta_shape.py [app ...]
        HD_PY_OLD=/path/to/old/hd.py  (default: this file's revision as of git HEAD)
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from env import ADB, ENV, find_hd  # noqa: E402
from suites import APPS  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
STATE = "/tmp/hd_last_tree.json"
GONE = re.compile(r"^- \[(\d+)\]")
RUN = re.compile(r"^~ \[(\d+)-(\d+)\]->\[(\d+)-(\d+)\]")
LABEL = re.compile(r"^\s*\[(\d+)\]\s(.*?)\s\(\d+,\d+\)$")

# Open something that ADDS nodes over the screen, then dismiss it, which removes them again.
# The dismissals are the case: the tree underneath is the one the caller already read.
MOVES = [("overflow menu", ("tap", "680", "184")),
         ("dismiss menu", ("keyevent", "4")),
         ("drawer", ("tap", "56", "184")),
         ("dismiss drawer", ("keyevent", "4")),
         ("scroll down", ("swipe", "360", "900", "360", "500", "300")),
         ("home", ("keyevent", "3"))]


def adb(*args):
    return subprocess.run([ADB, *args], capture_output=True, text=True, env=ENV).stdout


def hd(path, *args):
    return subprocess.run(["python3", path, *args],
                          capture_output=True, text=True, env=ENV).stdout


def launch(pkg):
    adb("shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(4)


def old_revision():
    """The pre-fix `hd.py`, so the bench compares two revisions and not two flags."""
    if os.environ.get("HD_PY_OLD"):
        return os.environ["HD_PY_OLD"]
    out = subprocess.run(["git", "show", "HEAD:skills/android-hybrid-navigation/hd.py"],
                         cwd=REPO, capture_output=True, text=True)
    if out.returncode:
        sys.exit("no HD_PY_OLD and `git show HEAD:...hd.py` failed")
    p = Path("/tmp/hd_old_delta.py")
    p.write_text(out.stdout)
    return str(p)


def labels_by_index(lines):
    return {m.group(1): m.group(2) for ln in lines for m in [LABEL.match(ln)] if m}


def delta_is_honest(before_lines, delta):
    """Removals and collapsed renumberings must address the tree the caller actually read."""
    after = labels_by_index(json.load(open(STATE))["lines"])
    before = labels_by_index(before_lines)
    for ln in delta.splitlines():
        m = GONE.match(ln.strip())
        if m:
            i = m.group(1)
            if i not in before:
                return False, f"{ln.strip()}  names an index the caller never saw"
            if after.get(i) == before[i]:
                return False, f"{ln.strip()}  reported gone but still at [{i}]"
            continue
        m = RUN.match(ln.strip())
        if m:
            o1, o2, n1, n2 = (int(g) for g in m.groups())
            if o2 - o1 != n2 - n1:
                return False, f"{ln.strip()}  ranges are different lengths"
            for o, n in zip(range(o1, o2 + 1), range(n1, n2 + 1)):
                if before.get(str(o)) is None or before[str(o)] != after.get(str(n)):
                    return False, (f"{ln.strip()}  [{o}]={before.get(str(o))!r} -> "
                                   f"[{n}]={after.get(str(n))!r}")
    return True, ""


def observe(hd_path, stash, check=False):
    """One revision's `hd see` against its OWN baseline, on whatever is on screen now.

    Both revisions have to be priced on the SAME screens or the comparison is between two walks
    of the app, not between two diffs. They share one hard-coded state file, so each revision's
    baseline is stashed and restored around its turn.
    """
    if Path(stash).exists():
        shutil.copy(stash, STATE)
    elif Path(STATE).exists():
        os.remove(STATE)
    before_lines = json.load(open(STATE))["lines"] if Path(STATE).exists() else []
    out = hd(hd_path, "see")
    honest = delta_is_honest(before_lines, out) if check else (True, "")
    shutil.copy(STATE, stash)
    return len(out), "too much to diff" in out, honest


def measure(old, new, pkg):
    launch(pkg)
    for p in ("/tmp/hd_bench_old.json", "/tmp/hd_bench_new.json"):
        Path(p).unlink(missing_ok=True)
    observe(old, "/tmp/hd_bench_old.json")
    observe(new, "/tmp/hd_bench_new.json")
    rows = []
    for i, (label, cmd) in enumerate(MOVES):
        adb("shell", "input", *cmd)
        # Settle before either look: a menu caught mid-animation renders fewer nodes, and the
        # two revisions observe seconds apart, so an unsettled screen prices the animation.
        time.sleep(3)
        adb("shell", "uiautomator", "dump", "/dev/null")
        # Alternate which revision looks first, so what is left of that skew does not all land
        # on one of them.
        if i % 2:
            n_new, w_new, honest = observe(new, "/tmp/hd_bench_new.json", check=True)
            n_old, w_old, _ = observe(old, "/tmp/hd_bench_old.json")
        else:
            n_old, w_old, _ = observe(old, "/tmp/hd_bench_old.json")
            n_new, w_new, honest = observe(new, "/tmp/hd_bench_new.json", check=True)
        rows.append((label, n_old, w_old, n_new, w_new, honest))
    return rows


def main(which):
    old, new = old_revision(), find_hd()
    tot_old = tot_new = whole_old = whole_new = steps = 0
    for key in which:
        try:
            rows = measure(old, new, APPS[key]["pkg"])
        except Exception as e:                                        # noqa: BLE001
            print(f"{key}: FAILED {e}")
            continue
        for label, n_old, w_old, n_new, w_new, honest in rows:
            tot_old, tot_new = tot_old + n_old, tot_new + n_new
            whole_old, whole_new, steps = whole_old + w_old, whole_new + w_new, steps + 1
            assert honest[0], f"{key} {label}: dishonest delta — {honest[1]}"
            print(f"{key:<10}{label:<15} was={n_old:>6} now={n_new:>6} "
                  f"saved={1 - n_new / max(n_old, 1):>6.0%}"
                  f"{'   [whole tree both]' if w_old and w_new else ''}"
                  f"{'   [delta now printed]' if w_old and not w_new else ''}")
    if tot_old:
        print(f"\nTOTAL was={tot_old} now={tot_new} saved={1 - tot_new / tot_old:.0%}")
        print(f"whole-tree fallbacks: was {whole_old}/{steps} now {whole_new}/{steps}")
        assert tot_new <= tot_old, "re-observation got more expensive"
        assert whole_new <= whole_old, "the fix printed MORE whole trees"


if __name__ == "__main__":
    main(sys.argv[1:] or ["markor", "amaze", "seal", "unitto", "joplin", "lesspass"])
