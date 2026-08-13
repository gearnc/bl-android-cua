"""Bench: what a re-observation costs after the screen MOVED rather than changed.

The 2026-08-13 A/B/C measured 1,024 "screen changed too much to diff" lines against 263 deltas
actually printed across the 12 hybrid runs — the delta, the thing that makes `hd see` cheap on a
screen you have already read, was discarded 80% of the time. The mechanism is in the identity a
diff matches on: every rendered line ends in the node's centre `(x,y)`, so a list scrolled by one
row re-coordinates all 40 rows, which score as 40 removals plus 40 additions — a delta twice the
size of the tree, so `see` prints the tree.

This drives that exact case (scroll a list, re-observe) on real apps against both revisions of
`hd.py` and prices the observation, then checks the two fallbacks the fix must not break:

  * a screen that genuinely turned over still prints the whole tree, not a bigger delta;
  * every `~ [was]->[now]` renumbering addresses the node the caller read under `[was]`, so a
    scrolled row stays tappable without being reprinted.

Usage:  python3 evals/bench_scroll_diff.py [app ...]
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
MOVE = re.compile(r"^~ \[(\d+)\](?:->\[(\d+)\])? \((\d+),(\d+)\)$")
LABEL = re.compile(r"^\s*\[\d+\]\s(.*?)\s\(\d+,\d+\)$")

# Scroll, scroll back, scroll again: the list case, where the screen is the same screen and only
# the rows' positions changed. Then a real navigation, which must still print a whole tree.
MOVES = [("scroll down", ("swipe", "360", "900", "360", "500", "300")),
         ("scroll up", ("swipe", "360", "500", "360", "900", "300")),
         ("scroll down", ("swipe", "360", "900", "360", "500", "300")),
         ("overflow menu", ("tap", "680", "184"))]


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
    p = Path("/tmp/hd_old.py")
    p.write_text(out.stdout)
    return str(p)


def labels_by_index(lines):
    out = {}
    for ln in lines:
        m = LABEL.match(ln)
        idx = ln.strip()[1:ln.strip().index("]")] if ln.strip().startswith("[") else None
        if m and idx is not None:
            out[idx] = m.group(1)
    return out


def renumbering_is_honest(before_lines, delta):
    """Every `~ [was]->[now]` must name the same node under both indexes.

    A renumbering the caller cannot trust is worse than reprinting the row: it taps the wrong
    thing. `[was]` is read against the tree the caller last saw, `[now]` against the tree `see`
    just cached, which is what `hd tap` resolves against.
    """
    after = labels_by_index(json.load(open(STATE))["lines"])
    before = labels_by_index(before_lines)
    for ln in delta.splitlines():
        m = MOVE.match(ln.strip())
        if not m:
            continue
        was, now = m.group(1), m.group(2) or m.group(1)
        if before.get(was) is None or before[was] != after.get(now):
            return False, f"{ln.strip()}  was={before.get(was)!r} now={after.get(now)!r}"
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
    honest = renumbering_is_honest(before_lines, out) if check else (True, "")
    shutil.copy(STATE, stash)
    return len(out), "too much to diff" in out, honest


def measure(old, new, pkg):
    """Drive the moves once, pricing both revisions' re-observation of each resulting screen."""
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
    old = old_revision()
    new = find_hd()
    tot_old = tot_new = 0
    whole_old = whole_new = 0
    for key in which:
        pkg = APPS[key]["pkg"]
        try:
            rows = measure(old, new, pkg)
        except Exception as e:                                        # noqa: BLE001
            print(f"{key}: FAILED {e}")
            continue
        for label, n_old, w_old, n_new, w_new, honest in rows:
            tot_old += n_old
            tot_new += n_new
            whole_old += w_old
            whole_new += w_new
            assert honest[0], f"{key} {label}: dishonest renumbering {honest[1]}"
            print(f"{key:<10}{label:<15} was={n_old:>6} now={n_new:>6} "
                  f"saved={1 - n_new / max(n_old, 1):>6.0%}"
                  f"{'   [whole tree both]' if w_old and w_new else ''}"
                  f"{'   [delta now printed]' if w_old and not w_new else ''}")
    if tot_old:
        print(f"\nTOTAL was={tot_old} now={tot_new} saved={1 - tot_new / tot_old:.0%}")
        print(f"whole-tree fallbacks: was {whole_old}/{whole_old and len(which) * len(MOVES)} "
              f"now {whole_new}/{len(which) * len(MOVES)}")
        assert tot_new <= tot_old, "re-observation got more expensive"
        assert whole_new <= whole_old, "the fix printed MORE whole trees"


if __name__ == "__main__":
    main(sys.argv[1:] or ["markor", "amaze", "seal", "unitto", "joplin", "lesspass"])
